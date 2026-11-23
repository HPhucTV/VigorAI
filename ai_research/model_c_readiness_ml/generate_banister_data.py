# [OWNER: M4] Bo sinh du lieu tong hop theo mo hinh Banister Fitness-Fatigue (T-M4-02)
"""Sinh ~15.000 mau chuoi 7 ngay (co 28 ngay lich su de tinh ACWR) cho AI Model C.

Moi mau gom:
  - 12 dac trung dau vao (dung ten nhu `ReadinessFeatures12` trong feature_extractor.py)
  - nhan `readiness_score` (0-100) + `readiness_level`
  - 11 nhan do moi co `fatigue_Mat_Muscle_*` (0.0-1.0) cho Ban do Phuc hoi 3D

Chay:
    python generate_banister_data.py --n-samples 15000 --seed 42 --check

LUU Y CONG THUC (khac voi docs/system-design-spec.md muc 5.2.3):
  Spec viet exp(-dt / (tau * RecoveryFactor)). Voi RecoveryFactor < 1 (thieu ngu/thieu dam)
  cong thuc do cho tau_hieu_dung NHO HON -> co hoi phuc NHANH HON, nguoc voi yeu cau
  "thieu ngu/thieu dam lam cham hoi phuc". Ban nay dung exp(-dt / (tau / RecoveryFactor)),
  tuc RecoveryFactor < 1 keo dai thoi gian phuc hoi. Ham `check_recovery_direction`
  kiem tra tu dong chieu nay.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------- #
# Hang so theo hop dong AGENTS.md / system-design-spec.md
# --------------------------------------------------------------------------- #
MUSCLE_KEYS = (
    "Chest",
    "Shoulders",
    "Biceps",
    "Triceps",
    "Back_Lats",
    "Traps",
    "Abs_Core",
    "Glutes",
    "Quads",
    "Hamstrings",
    "Calves",
)
MUSCLE_MATERIALS = tuple(f"Mat_Muscle_{k}" for k in MUSCLE_KEYS)

LARGE_MUSCLES = {"Chest", "Back_Lats", "Quads", "Hamstrings", "Glutes"}
TAU_LARGE_H = 48.0
TAU_SMALL_H = 36.0
FATIGUE_WINDOW_H = 72.0
SESSION_DURATION_H = 1.25

FEATURE_NAMES = (
    "sleep_hours_last_night",
    "sleep_avg_3d",
    "hydration_ratio_yesterday",
    "steps_ratio_yesterday",
    "protein_compliance_3d",
    "calorie_balance_ratio_3d",
    "volume_load_72h_normalized",
    "avg_rpe_last_session",
    "hours_since_last_workout",
    "target_muscle_fatigue_raw",
    "acute_chronic_workload_ratio",
    "weight_delta_7d_pct",
)

FEATURE_RANGES: dict[str, tuple[float, float]] = {
    "sleep_hours_last_night": (0.0, 14.0),
    "sleep_avg_3d": (0.0, 14.0),
    "hydration_ratio_yesterday": (0.0, 2.0),
    "steps_ratio_yesterday": (0.0, 2.5),
    "protein_compliance_3d": (0.0, 2.0),
    "calorie_balance_ratio_3d": (0.4, 1.8),
    "volume_load_72h_normalized": (0.0, 3.0),
    "avg_rpe_last_session": (1.0, 10.0),
    "hours_since_last_workout": (0.0, 240.0),
    "target_muscle_fatigue_raw": (0.0, 1.0),
    "acute_chronic_workload_ratio": (0.0, 2.5),
    "weight_delta_7d_pct": (-5.0, 5.0),
}

# Muc do tham gia (0-1) cua tung nhom co trong tung dang buoi tap.
TEMPLATES: dict[str, dict[str, float]] = {
    "PUSH": {"Chest": 0.9, "Shoulders": 0.6, "Triceps": 0.8, "Abs_Core": 0.1},
    "PULL": {
        "Back_Lats": 0.9,
        "Traps": 0.6,
        "Biceps": 0.8,
        "Shoulders": 0.15,
        "Abs_Core": 0.1,
    },
    "LEGS": {
        "Quads": 0.9,
        "Glutes": 0.8,
        "Hamstrings": 0.7,
        "Calves": 0.5,
        "Abs_Core": 0.3,
    },
    "UPPER": {
        "Chest": 0.7,
        "Back_Lats": 0.7,
        "Shoulders": 0.6,
        "Biceps": 0.5,
        "Triceps": 0.5,
        "Traps": 0.4,
        "Abs_Core": 0.1,
    },
    "LOWER": {
        "Quads": 0.8,
        "Glutes": 0.8,
        "Hamstrings": 0.8,
        "Calves": 0.5,
        "Abs_Core": 0.3,
    },
    "FULL": {
        "Chest": 0.5,
        "Back_Lats": 0.5,
        "Shoulders": 0.4,
        "Biceps": 0.3,
        "Triceps": 0.3,
        "Quads": 0.6,
        "Glutes": 0.5,
        "Hamstrings": 0.4,
        "Abs_Core": 0.3,
        "Traps": 0.2,
        "Calves": 0.2,
    },
    "CHEST_DAY": {"Chest": 0.95, "Triceps": 0.5, "Shoulders": 0.4},
    "BACK_DAY": {"Back_Lats": 0.95, "Traps": 0.7, "Biceps": 0.6},
    "SHOULDER_ARMS": {
        "Shoulders": 0.9,
        "Biceps": 0.7,
        "Triceps": 0.7,
        "Traps": 0.4,
        "Abs_Core": 0.15,
    },
}

SPLITS: dict[str, list[str]] = {
    "FULL": ["FULL"],
    "UL": ["UPPER", "LOWER"],
    "PPL": ["PUSH", "PULL", "LEGS"],
    "BRO": ["CHEST_DAY", "BACK_DAY", "LEGS", "SHOULDER_ARMS"],
}
SPLIT_BY_K: dict[int, list[str]] = {
    2: ["FULL"],
    3: ["FULL", "PPL"],
    4: ["UL", "BRO"],
    5: ["BRO", "PPL"],
    6: ["PPL"],
}
DOW_PATTERNS: dict[int, list[int]] = {
    2: [1, 4],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
}
LEVELS = {
    "beginner": {"p": 0.30, "k": (2, 3), "rpe": 6.6},
    "intermediate": {"p": 0.45, "k": (3, 5), "rpe": 7.5},
    "advanced": {"p": 0.25, "k": (4, 6), "rpe": 8.2},
}
SESSION_HOURS = np.array([6, 7, 12, 17, 18, 19, 20], dtype=float)
SESSION_HOUR_P = np.array([0.10, 0.10, 0.08, 0.20, 0.22, 0.20, 0.10])

HORIZON_DAYS = 35  # 28 ngay lich su + 7 ngay gan nhat
READINESS_READY = 75.0
READINESS_MODERATE = 45.0


# --------------------------------------------------------------------------- #
# Cong thuc loi (giu nguyen ten ham cua khung ban dau)
# --------------------------------------------------------------------------- #
def compute_recovery_factor(sleep_hours: float, protein_compliance: float) -> float:
    """RecoveryFactor = clip(0.6 + 0.25*sleep/8 + 0.15*protein, 0.65, 1.15).

    protein_compliance duoc chan o [0, 1]: an du dam khong giup hoi phuc nhanh hon muc 100%.
    """
    protein = max(0.0, min(1.0, protein_compliance))
    raw = 0.6 + 0.25 * (sleep_hours / 8.0) + 0.15 * protein
    return max(0.65, min(1.15, raw))


def tau_for(muscle_key: str) -> float:
    return TAU_LARGE_H if muscle_key in LARGE_MUSCLES else TAU_SMALL_H


def compute_muscle_fatigue(
    intensities: list[float],
    hours_elapsed: list[float],
    tau_hours: float,
    recovery_factor: float,
    window_h: float = FATIGUE_WINDOW_H,
) -> float:
    """Fatigue = clamp(sum I_s * exp(-dt_s / (tau / RF)), 0, 1) tren cua so 72h.

    RF < 1 (thieu ngu / thieu dam) -> tau hieu dung dai hon -> phuc hoi cham hon.
    """
    effective_tau = tau_hours / max(recovery_factor, 1e-6)
    total = 0.0
    for intensity, dt in zip(intensities, hours_elapsed):
        if dt < 0.0 or dt > window_h:
            continue
        total += intensity * math.exp(-dt / effective_tau)
    return max(0.0, min(1.0, total))


# --------------------------------------------------------------------------- #
# Mo phong lich tap
# --------------------------------------------------------------------------- #
@dataclass
class Session:
    day: int
    hour: float
    template: str
    rpe: float
    vol_scale: float

    @property
    def start_h(self) -> float:
        return self.day * 24.0 + self.hour

    @property
    def end_h(self) -> float:
        return self.start_h + SESSION_DURATION_H

    @property
    def load(self) -> float:
        return self.vol_scale * (self.rpe / 10.0) * 100.0


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def simulate_sessions(rng: np.random.Generator) -> tuple[list[Session], float]:
    """Tra ve (danh sach buoi tap trong 35 ngay, chi so loi song q in [0,1])."""
    level_names = list(LEVELS)
    level = str(rng.choice(level_names, p=[LEVELS[n]["p"] for n in level_names]))
    k_lo, k_hi = LEVELS[level]["k"]
    k = int(rng.integers(k_lo, k_hi + 1))
    split = str(rng.choice(SPLIT_BY_K[k]))
    cycle = SPLITS[split]
    offset = int(rng.integers(0, 7))
    base_rpe = LEVELS[level]["rpe"] + float(rng.normal(0, 0.3))
    mode = str(rng.choice(["normal", "overreach", "light"], p=[0.70, 0.15, 0.15]))
    last_week_start = HORIZON_DAYS - 7

    train_days = [
        d for d in range(HORIZON_DAYS) if (d + offset) % 7 in DOW_PATTERNS[k]
    ]
    train_days = [d for d in train_days if rng.random() > 0.08]
    if mode == "light":
        train_days = [
            d for d in train_days if d < last_week_start or rng.random() > 0.6
        ]
    elif mode == "overreach":
        extra = rng.choice(
            np.arange(last_week_start, HORIZON_DAYS), size=2, replace=False
        )
        train_days = sorted(set(train_days) | {int(e) for e in extra})

    sessions: list[Session] = []
    for i, d in enumerate(train_days):
        in_last_week = d >= last_week_start
        boost = mode == "overreach" and in_last_week
        rpe = _clip(float(rng.normal(base_rpe + (0.7 if boost else 0.0), 0.8)), 5.0, 10.0)
        vol = float(rng.uniform(0.6, 1.25)) * (1.15 if boost else 1.0)
        hour = float(rng.choice(SESSION_HOURS, p=SESSION_HOUR_P)) + float(
            rng.uniform(0.0, 0.9)
        )
        sessions.append(Session(d, hour, cycle[i % len(cycle)], rpe, vol))

    q = float(rng.beta(2.2, 2.0))
    return sessions, q


@dataclass
class Lifestyle:
    sleep_last: float
    sleep_avg_3d: float
    hydration: float
    steps: float
    protein_3d: float
    calorie_3d: float
    weight_delta_pct: float


def sample_lifestyle(rng: np.random.Generator, q: float) -> Lifestyle:
    sleep_base = 5.6 + 2.6 * q + float(rng.normal(0, 0.3))
    nights = np.clip(rng.normal(sleep_base, 0.9, size=3), 3.0, 11.0)
    protein_days = np.clip(rng.normal(0.62 + 0.5 * q, 0.18, size=3), 0.2, 2.0)
    diet_phase = float(rng.normal(1.0, 0.17))
    calorie_days = np.clip(rng.normal(diet_phase, 0.12, size=3), 0.4, 1.8)
    hydration = _clip(float(rng.normal(0.6 + 0.55 * q, 0.25)), 0.1, 2.0)
    steps = _clip(float(rng.normal(0.55 + 0.7 * q, 0.4)), 0.0, 2.5)
    calorie_mean = float(calorie_days.mean())
    slope = 1.8 * (calorie_mean - 1.0) + float(rng.normal(0, 0.35))
    weight_delta = _clip(slope + float(rng.normal(0, 0.45)), -5.0, 5.0)
    return Lifestyle(
        sleep_last=float(nights[-1]),
        sleep_avg_3d=float(nights.mean()),
        hydration=hydration,
        steps=steps,
        protein_3d=float(protein_days.mean()),
        calorie_3d=calorie_mean,
        weight_delta_pct=weight_delta,
    )


# --------------------------------------------------------------------------- #
# Tinh dac trung & nhan
# --------------------------------------------------------------------------- #
def fatigue_map_for(
    sessions: list[Session], target_h: float, recovery_factor: float
) -> dict[str, float]:
    recent = [s for s in sessions if 0.0 <= target_h - s.end_h <= FATIGUE_WINDOW_H]
    result: dict[str, float] = {}
    for muscle in MUSCLE_KEYS:
        intensities: list[float] = []
        elapsed: list[float] = []
        for s in recent:
            involvement = TEMPLATES[s.template].get(muscle, 0.0)
            if involvement <= 0.0:
                continue
            intensities.append(involvement * (s.rpe / 10.0) * s.vol_scale)
            elapsed.append(target_h - s.end_h)
        result[muscle] = compute_muscle_fatigue(
            intensities, elapsed, tau_for(muscle), recovery_factor
        )
    return result


def compute_readiness(
    feats: dict[str, float], fatigue: dict[str, float], rng: np.random.Generator
) -> float:
    values = list(fatigue.values())
    mean_f = sum(values) / len(values)
    max_f = max(values)
    penalty = 65.0 * (0.6 * mean_f + 0.4 * max_f)
    penalty += 8.0 * max(0.0, 7.5 - feats["sleep_hours_last_night"])
    penalty += 4.0 * max(0.0, 7.5 - feats["sleep_avg_3d"])
    penalty += 40.0 * max(0.0, feats["acute_chronic_workload_ratio"] - 1.3)
    penalty += (
        2.0
        * max(0.0, feats["avg_rpe_last_session"] - 8.0)
        * math.exp(-feats["hours_since_last_workout"] / 48.0)
    )
    penalty += 10.0 * max(0.0, 0.8 - feats["hydration_ratio_yesterday"])
    penalty += 12.0 * max(0.0, 0.85 - feats["calorie_balance_ratio_3d"])
    penalty += 6.0 * max(0.0, feats["calorie_balance_ratio_3d"] - 1.3)
    penalty += 8.0 * max(0.0, 0.8 - feats["protein_compliance_3d"])
    penalty += 3.0 * max(0.0, feats["steps_ratio_yesterday"] - 1.8)
    penalty += 2.0 * max(0.0, abs(feats["weight_delta_7d_pct"]) - 2.0)
    score = 100.0 - penalty + float(rng.normal(0.0, 1.5))
    return _clip(score, 0.0, 100.0)


def classify_readiness_level(score: float) -> str:
    if score >= READINESS_READY:
        return "READY"
    if score >= READINESS_MODERATE:
        return "MODERATE"
    return "REST_RECOMMENDED"


def build_sample(rng: np.random.Generator) -> dict[str, object]:
    sessions, q = simulate_sessions(rng)
    life = sample_lifestyle(rng, q)
    target_h = HORIZON_DAYS * 24.0 + float(rng.uniform(5.0, 12.0))

    last = max(sessions, key=lambda s: s.end_h)
    hours_since = _clip(target_h - last.end_h, 0.0, 240.0)

    acute = sum(s.load for s in sessions if target_h - s.start_h <= 168.0)
    chronic_weekly = sum(s.load for s in sessions if target_h - s.start_h <= 672.0) / 4.0
    load_72h = sum(s.load for s in sessions if target_h - s.start_h <= 72.0)
    if chronic_weekly > 0.0:
        acwr = _clip(acute / chronic_weekly, 0.0, 2.5)
        vol72 = _clip(load_72h / (chronic_weekly * 3.0 / 7.0), 0.0, 3.0)
    else:
        acwr, vol72 = 1.0, 1.0

    rf = compute_recovery_factor(life.sleep_avg_3d, life.protein_3d)
    fatigue = fatigue_map_for(sessions, target_h, rf)
    primary = max(TEMPLATES[last.template], key=lambda m: TEMPLATES[last.template][m])

    feats = {
        "sleep_hours_last_night": life.sleep_last,
        "sleep_avg_3d": life.sleep_avg_3d,
        "hydration_ratio_yesterday": life.hydration,
        "steps_ratio_yesterday": life.steps,
        "protein_compliance_3d": life.protein_3d,
        "calorie_balance_ratio_3d": life.calorie_3d,
        "volume_load_72h_normalized": vol72,
        "avg_rpe_last_session": _clip(last.rpe, 1.0, 10.0),
        "hours_since_last_workout": hours_since,
        "target_muscle_fatigue_raw": fatigue[primary],
        "acute_chronic_workload_ratio": acwr,
        "weight_delta_7d_pct": life.weight_delta_pct,
    }
    score = compute_readiness(feats, fatigue, rng)

    row: dict[str, object] = {name: round(feats[name], 4) for name in FEATURE_NAMES}
    row["readiness_score"] = round(score, 2)
    row["readiness_level"] = classify_readiness_level(score)
    row["target_muscle"] = f"Mat_Muscle_{primary}"
    for muscle in MUSCLE_KEYS:
        row[f"fatigue_Mat_Muscle_{muscle}"] = round(fatigue[muscle], 4)
    return row


def generate_dataset(n_samples: int, seed: int) -> list[dict[str, object]]:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for i in range(n_samples):
        row = build_sample(rng)
        r = rng.random()
        split = "train" if r < 0.70 else ("val" if r < 0.85 else "test")
        rows.append({"sample_id": i, "split": split, **row})
    return rows


def csv_columns() -> list[str]:
    return (
        ["sample_id", "split"]
        + list(FEATURE_NAMES)
        + ["readiness_score", "readiness_level", "target_muscle"]
        + [f"fatigue_Mat_Muscle_{m}" for m in MUSCLE_KEYS]
    )


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=csv_columns())
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# Sanity check quy luat sinh ly
# --------------------------------------------------------------------------- #
def check_recovery_direction(seed: int = 7, n: int = 400) -> dict[str, object]:
    """Cung 1 lich tap: thieu ngu / thieu dam phai cho do moi co CAO HON (phuc hoi cham hon)."""
    rng = np.random.default_rng(seed)
    sleep_cases = protein_cases = strict_sleep = strict_protein = 0
    violations = 0
    for _ in range(n):
        sessions, _q = simulate_sessions(rng)
        target_h = HORIZON_DAYS * 24.0 + float(rng.uniform(5.0, 12.0))
        good = fatigue_map_for(sessions, target_h, compute_recovery_factor(8.0, 1.0))
        poor_sleep = fatigue_map_for(sessions, target_h, compute_recovery_factor(5.0, 1.0))
        poor_protein = fatigue_map_for(sessions, target_h, compute_recovery_factor(8.0, 0.4))
        for m in MUSCLE_KEYS:
            if good[m] <= 0.0:
                continue
            sleep_cases += 1
            protein_cases += 1
            if poor_sleep[m] < good[m] - 1e-12 or poor_protein[m] < good[m] - 1e-12:
                violations += 1
            if poor_sleep[m] > good[m] + 1e-12 or good[m] >= 1.0:
                strict_sleep += 1
            if poor_protein[m] > good[m] + 1e-12 or good[m] >= 1.0:
                strict_protein += 1
    return {
        "cases": sleep_cases,
        "violations": violations,
        "strict_poor_sleep_ratio": round(strict_sleep / max(sleep_cases, 1), 4),
        "strict_poor_protein_ratio": round(strict_protein / max(protein_cases, 1), 4),
        "passed": violations == 0
        and strict_sleep == sleep_cases
        and strict_protein == protein_cases,
    }


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def check_dataset(rows: list[dict[str, object]]) -> dict[str, object]:
    col = {name: np.array([float(r[name]) for r in rows]) for name in FEATURE_NAMES}
    score = np.array([float(r["readiness_score"]) for r in rows])
    range_errors = [
        name
        for name, (lo, hi) in FEATURE_RANGES.items()
        if col[name].min() < lo - 1e-9 or col[name].max() > hi + 1e-9
    ]
    fat_cols = [f"fatigue_Mat_Muscle_{m}" for m in MUSCLE_KEYS]
    fat = np.array([[float(r[c]) for c in fat_cols] for r in rows])
    levels = [str(r["readiness_level"]) for r in rows]
    shares = {lv: round(levels.count(lv) / len(levels), 4) for lv in set(levels)}

    acwr = col["acute_chronic_workload_ratio"]
    corr_sleep = _corr(col["sleep_hours_last_night"], score)
    corr_fatigue = _corr(col["target_muscle_fatigue_raw"], score)
    mean_high_acwr = float(score[acwr > 1.5].mean()) if (acwr > 1.5).any() else float("nan")
    mean_low_acwr = float(score[acwr < 1.2].mean())
    mean_low_sleep = float(score[col["sleep_hours_last_night"] < 6.0].mean())
    mean_good_sleep = float(score[col["sleep_hours_last_night"] >= 7.5].mean())

    checks = {
        "feature_ranges_ok": not range_errors,
        "fatigue_in_0_1": bool(fat.min() >= 0.0 and fat.max() <= 1.0),
        "corr_sleep_readiness_positive": corr_sleep > 0.15,
        "corr_target_fatigue_readiness_negative": corr_fatigue < -0.25,
        "high_acwr_lowers_readiness": mean_high_acwr < mean_low_acwr,
        "low_sleep_lowers_readiness": mean_low_sleep < mean_good_sleep,
        "all_three_levels_present": len(shares) == 3 and min(shares.values()) >= 0.03,
    }
    return {
        "n_samples": len(rows),
        "feature_range_errors": range_errors,
        "readiness_mean": round(float(score.mean()), 2),
        "readiness_std": round(float(score.std()), 2),
        "readiness_level_share": shares,
        "corr_sleep_last_vs_readiness": round(corr_sleep, 3),
        "corr_target_fatigue_vs_readiness": round(corr_fatigue, 3),
        "mean_readiness_acwr_gt_1_5": round(mean_high_acwr, 2),
        "mean_readiness_acwr_lt_1_2": round(mean_low_acwr, 2),
        "mean_readiness_sleep_lt_6h": round(mean_low_sleep, 2),
        "mean_readiness_sleep_ge_7_5h": round(mean_good_sleep, 2),
        "checks": checks,
        "passed": all(checks.values()),
    }


def check_learnability(rows: list[dict[str, object]]) -> dict[str, object]:
    """Kiem tra nhanh du lieu hoc duoc (KHONG phai benchmark chinh thuc T-M4-05)."""
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.metrics import mean_absolute_error, r2_score
    except ImportError:
        return {"skipped": "scikit-learn chua duoc cai"}

    def xy(split: str) -> tuple[np.ndarray, np.ndarray]:
        sel = [r for r in rows if r["split"] == split]
        x = np.array([[float(r[f]) for f in FEATURE_NAMES] for r in sel])
        y = np.array([float(r["readiness_score"]) for r in sel])
        return x, y

    x_tr, y_tr = xy("train")
    x_te, y_te = xy("test")
    model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, random_state=0)
    model.fit(x_tr, y_tr)
    pred = model.predict(x_te)
    rmse = float(np.sqrt(np.mean((pred - y_te) ** 2)))
    return {
        "model": "HistGradientBoostingRegressor (sanity only)",
        "test_MAE": round(float(mean_absolute_error(y_te, pred)), 3),
        "test_RMSE": round(rmse, 3),
        "test_R2": round(float(r2_score(y_te, pred)), 4),
        "kpi_reference": {"MAE": 4.5, "RMSE": 6.2, "R2": 0.88},
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n-samples", type=int, default=15000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=here.parent / "datasets" / "model_c" / "banister_readiness_v1.csv",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=here.parent / "evaluation_reports" / "banister_data_report.json",
    )
    parser.add_argument("--check", action="store_true", help="chay sanity check sinh ly")
    args = parser.parse_args(argv)

    rows = generate_dataset(args.n_samples, args.seed)
    write_csv(rows, args.out)
    print(f"Da ghi {len(rows)} mau -> {args.out}")

    if not args.check:
        return 0

    report = {
        "version": "banister-v1",
        "seed": args.seed,
        "n_samples": args.n_samples,
        "recovery_direction": check_recovery_direction(),
        "dataset": check_dataset(rows),
        "learnability": check_learnability(rows),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = report["recovery_direction"]["passed"] and report["dataset"]["passed"]
    print("SANITY CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
