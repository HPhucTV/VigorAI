# AI Model C — Readiness, Muscle Fatigue & Overload Predictor (`[OWNER: M4]`)

- **Nhiệm vụ:** `T-M4-02`, `T-M4-05`, `T-M4-07`
- **Kiến trúc so sánh:** `XGBoost Regressor` vs `LightGBM Regressor` vs `MLP`
- **Dữ liệu:** Sinh ~15,000 mẫu chuỗi 7 ngày theo **Mô hình Thể lực – Mệt mỏi Banister** + fine-tune bằng log RPE thực tế.
- **KPI bắt buộc:** `MAE <= 4.5` (thang 0–100), `RMSE <= 6.2`, `R2-Score >= 0.88`.
