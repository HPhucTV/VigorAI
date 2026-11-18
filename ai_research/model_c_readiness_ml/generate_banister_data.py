# [OWNER: M4] Khung sinh du lieu tong hop theo mo hinh Banister Fitness-Fatigue (T-M4-02)
import math


def compute_recovery_factor(sleep_hours: float, protein_compliance: float) -> float:
    raw = 0.6 + 0.25 * (sleep_hours / 8.0) + 0.15 * protein_compliance
    return max(0.65, min(1.15, raw))


def compute_muscle_fatigue(
    intensities: list[float],
    hours_elapsed: list[float],
    tau_hours: float,
    recovery_factor: float,
) -> float:
    total = 0.0
    denom = tau_hours * recovery_factor
    for intensity, dt in zip(intensities, hours_elapsed):
        total += intensity * math.exp(-dt / max(denom, 1e-6))
    return max(0.0, min(1.0, total))
