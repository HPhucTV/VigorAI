# AI Model C — Readiness, Muscle Fatigue & Overload Predictor (`[OWNER: M4]`)

- **Nhiệm vụ:** `T-M4-02`, `T-M4-05`, `T-M4-07`
- **Kiến trúc so sánh:** `XGBoost Regressor` vs `LightGBM Regressor` vs `MLP`
- **Dữ liệu:** Sinh ~15,000 mẫu chuỗi 7 ngày theo **Mô hình Thể lực – Mệt mỏi Banister** + fine-tune bằng log RPE thực tế.
- **KPI bắt buộc:** `MAE <= 4.5` (thang 0–100), `RMSE <= 6.2`, `R2-Score >= 0.88`.

## Sinh dữ liệu (`T-M4-02`)

```bash
cd ai_research/model_c_readiness_ml
python generate_banister_data.py --n-samples 15000 --seed 42 --check
```

- Đầu ra CSV: `ai_research/datasets/model_c/banister_readiness_v1.csv` (không commit, đã bị `.gitignore` chặn).
- Báo cáo sanity check: `ai_research/evaluation_reports/banister_data_report.json`.
- Cột CSV: `sample_id`, `split` (train 70% / val 15% / test 15%), 12 đặc trưng (tên khớp `ReadinessFeatures12`), `readiness_score`, `readiness_level`, `target_muscle`, 11 cột `fatigue_Mat_Muscle_*`.

## Lưu ý công thức

Spec viết `exp(-Δt / (τ · RecoveryFactor))`, nhưng với `RecoveryFactor < 1` công thức đó làm cơ hồi phục **nhanh hơn** khi thiếu ngủ/thiếu đạm. Code dùng `exp(-Δt / (τ / RecoveryFactor))` để thiếu ngủ/đạm làm hồi phục **chậm hơn**. `--check` kiểm tra chiều này tự động. Nhãn là hàm quy tắc + nhiễu nên R² cao chỉ chứng minh dữ liệu học được; cần tinh chỉnh bằng RPE thực (`T-M4-11`).
