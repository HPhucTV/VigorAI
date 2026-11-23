# AI Model B — YOLOv8 Food & Macro Detection (`[OWNER: M4]`)

- **Nhiệm vụ:** `T-M4-01`, `T-M4-04`, `T-M4-06`
- **Kiến trúc:** `YOLOv8s` / `YOLOv8m` (35–50 lớp món ăn Việt Nam & thực phẩm Gym)
- **KPI bắt buộc:** `mAP@0.5 >= 0.80`, `Precision >= 0.82`, `Recall >= 0.78`, tốc độ `< 150 ms/ảnh`.
- **Lưu ý Git:** Không commit ảnh gốc (`ai_research/datasets/`) và file weights nặng (`*.pt`, `*.onnx`) vào Git.

## Đợt 1 — Dataset 18 món cốt lõi (`T-M4-01`)

18 lớp v1.0 nằm trong `food_classes.py`, dùng đúng `class_code` của bảng `food_nutrition_catalog`.

1. Tải các dataset định dạng **YOLOv8** từ Roboflow Universe / Kaggle về `ai_research/datasets/raw/<tên>/` (cần tài khoản; kiểm tra giấy phép từng dataset).
2. Chạy:
   ```bash
   cd ai_research/model_b_food_yolo
   python prepare_dataset.py \
       --src ../datasets/raw/<dataset-1> --src ../datasets/raw/<dataset-2> \
       --out ../datasets/model_b_v1
   ```
3. Đọc `dataset_report.json`:
   - `unmapped_source_classes`: nhãn nguồn chưa gán được, thêm alias vào `food_classes.py` rồi chạy lại vào thư mục `--out` mới.
   - `warnings`: lớp thiếu ảnh (khuyến nghị >= 100 ảnh/lớp).
4. Kiểm tra lại bất kỳ lúc nào: `python prepare_dataset.py --validate-only --out ../datasets/model_b_v1`.

Script loại bbox rỗng/lệch chuẩn/tràn biên, ảnh trùng nội dung, chuyển nhãn polygon sang bbox, chia 70/20/10 phân tầng theo lớp và ghi `data.yaml`. Chỉ dùng thư viện chuẩn của Python.
