# AI Model B — YOLOv8 Food & Macro Detection (`[OWNER: M4]`)

- **Nhiệm vụ:** `T-M4-01`, `T-M4-04`, `T-M4-06`
- **Kiến trúc:** `YOLOv8s` / `YOLOv8m` (35–50 lớp món ăn Việt Nam & thực phẩm Gym)
- **KPI bắt buộc:** `mAP@0.5 >= 0.80`, `Precision >= 0.82`, `Recall >= 0.78`, tốc độ `< 150 ms/ảnh`.
- **Lưu ý Git:** Không commit ảnh gốc (`ai_research/datasets/`) và file weights nặng (`*.pt`, `*.onnx`) vào Git.

## Đợt 1 — Dataset 18 món cốt lõi (`T-M4-01`)

18 lớp v1.0 nằm trong `food_classes.py`, dùng đúng `class_code` của bảng `food_nutrition_catalog`.

1. Tải các dataset định dạng **YOLOv8** từ Roboflow Universe / Kaggle về `ai_research/datasets/raw/<tên>/` (cần tài khoản; kiểm tra giấy phép từng dataset). **Giải nén vào đúng thư mục này**, không giải nén ở gốc repo vì sẽ bị `git add .` đưa nhầm hàng trăm ảnh lên GitHub.
   - Bộ chưa có phiên bản (Dataset versions = 0): **Fork Dataset** → Create New Version, **bỏ trống Preprocessing và Augmentation** → Download YOLOv8.
   - Ghi nguồn, tác giả, giấy phép từng bộ vào `ai_research/SOURCES.md`.
2. Chạy (đứng ở `ai_research/model_b_food_yolo`):
   ```bash
   python prepare_dataset.py \
       --src ../datasets/raw/pork-rice --src ../datasets/raw/<dataset-2> \
       --map "pork-rice:egg=BOILED_EGG" \
       --out ../datasets/model_b_v1
   ```
   - `--map "<tên thư mục nguồn>:<nhãn nguồn>=<CLASS_CODE>"` gán nhãn riêng cho đúng một bộ (lặp lại nhiều lần; dùng `*` thay tên thư mục để áp cho mọi bộ). `--map` ưu tiên hơn bảng alias chung, nên nhãn chung chung như `egg` chỉ gán khi bạn đã xem ảnh và biết đó là trứng luộc hay ốp la.
3. Đọc `dataset_report.json` (và phần in ra màn hình):
   - `source_class_mapping`: mỗi nhãn nguồn được gán vào lớp nào, bao nhiêu khung (`class_code: null` = bị bỏ).
   - `unmapped_source_classes`: nhãn nguồn chưa gán được, thêm alias vào `food_classes.py` hoặc dùng `--map`, rồi chạy lại vào thư mục `--out` mới.
   - `warnings`: lớp thiếu ảnh (khuyến nghị >= 100 ảnh/lớp).
4. Kiểm tra lại bất kỳ lúc nào: `python prepare_dataset.py --validate-only --out ../datasets/model_b_v1`.

Script loại bbox rỗng/lệch chuẩn/tràn biên, ảnh trùng nội dung, chuyển nhãn polygon sang bbox, chia 70/20/10 phân tầng theo lớp và ghi `data.yaml`. Chỉ dùng thư viện chuẩn của Python.

**Tên file đầu ra ngắn:** ảnh trong `--out` có dạng `<nguồn>__<hash12>__<mã-nhóm>.jpg` để không vượt giới hạn 260 ký tự của Windows (tên file Roboflow gốc rất dài, làm OpenCV/YOLO không mở được). Bảng tra tên gốc nằm ở `manifest.csv` trong thư mục `--out`. Script đọc được cả file nguồn có đường dẫn dài.

**Bản augment của Roboflow:** các file `<tên>_jpg.rf.<mã>.jpg` cùng `<tên>` là bản biến đổi của một ảnh gốc. Script gom chúng thành một nhóm, cả nhóm vào cùng một tập (không rò rỉ giữa train và val/test), và ở val/test chỉ giữ một ảnh mỗi nhóm. Validator báo lỗi nếu một ảnh gốc xuất hiện ở hai tập. Vẫn nên ưu tiên bộ không augment, vì bbox của ảnh xoay bị nới rộng.
