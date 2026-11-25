# AI Model B — YOLOv8 Food & Macro Detection (`[OWNER: M4]`)

- **Nhiệm vụ:** `T-M4-01`, `T-M4-03`, `T-M4-04`, `T-M4-06`, `T-M4-09`, `T-M4-10`, `T-M4-12`, `T-M4-13`
- **Kiến trúc:** `YOLOv8s` (suy luận Production bằng **ONNX Runtime thuần** trên CPU: `onnxruntime + numpy + pillow`, không cần PyTorch/Ultralytics trên server)
- **KPI bắt buộc:** `mAP@0.5 >= 0.80`, `mAP@0.5:0.95 >= 0.58`, `Precision >= 0.82`, `Recall >= 0.78`, `F1 >= 0.80`, tốc độ `< 150 ms/ảnh`, API end-to-end `< 3.0s`.
- **Lưu ý Git:** Không commit ảnh gốc (`ai_research/datasets/`) và file weights nặng (`*.pt`, `*.onnx`) vào Git.

---

## 1. Chuẩn bị Dataset 16/18 món cốt lõi (`T-M4-01`)

18 lớp cốt lõi v1.0 nằm trong `food_classes.py`, khớp 100% `class_code` của bảng `food_nutrition_catalog` (seed bởi `M3`).

### Bước 1 — Tải tự động các dataset mở (HuggingFace, không cần đăng nhập)
```bash
cd ai_research/model_b_food_yolo
python fetch_open_datasets.py --max-per-class 350
```
Script tự tải và chuẩn hóa về `ai_research/datasets/raw/`:
- `vn-streetfood` (`HoagMin/Vietnamese_StreetFood_Dataset`, CC BY 4.0): Phở bò (`BEEF_PHO`), Cơm tấm (`COM_TAM_SUON`), Bánh mì (`BANH_MI_THIT`), Bún chả (`BUN_CHA`).
- `foodseg103` (`EduardoPacheco/FoodSeg103`, Apache 2.0): chuyển pixel segmentation masks thành bounding box YOLO sạch cho `WHITE_RICE`, `GRILLED_CHICKEN_BREAST`, `BEEF_STEAK`, `STEAMED_SHRIMP`, `TOFU`, `BROCCOLI`, `GREEN_SALAD`, `BANANA`, `APPLE`.

Kết hợp cùng các nguồn Roboflow cục bộ trong `ai_research/datasets/raw/` (`pork-rice`, `food-detection`, `chicken` — chi tiết nguồn/giấy phép xem `ai_research/SOURCES.md`).

### Bước 2 — Gộp nhãn, lọc bbox lỗi, chống rò rỉ augment & chia 70/20/10
```bash
python prepare_dataset.py \
    --src ../datasets/raw/pork-rice \
    --src ../datasets/raw/food-detection \
    --src ../datasets/raw/chicken \
    --src ../datasets/raw/vn-streetfood \
    --src ../datasets/raw/foodseg103 \
    --map "pork-rice:egg=BOILED_EGG" \
    --map "food-detection:telur-mata-sapi=FRIED_EGG" \
    --map "chicken:cookedchicken=GRILLED_CHICKEN_BREAST" \
    --map "foodseg103:chicken_duck=GRILLED_CHICKEN_BREAST" \
    --max-images-per-class 350 \
    --out ../datasets/model_b_v3
```
Kiểm tra lại bất kỳ lúc nào:
```bash
python prepare_dataset.py --validate-only --out ../datasets/model_b_v3
```

---

## 2. Huấn luyện YOLOv8s trên Google Colab T4 (`T-M4-06` / `T-M4-10`)

Mở notebook 1-click [`train_model_b_colab.ipynb`](./train_model_b_colab.ipynb) trên Google Colab (chọn **T4 GPU**):
1. Upload file nén `model_b_v3.zip` (nén thư mục `ai_research/datasets/model_b_v3`, không nén `raw/`) lên Google Drive `MyDrive/model_b_v3.zip`.
2. Chạy toàn bộ các cell trong `train_model_b_colab.ipynb`.
3. Tải `food_yolo_v1.onnx`, `model_b_manifest.json`, `results.png`, `confusion_matrix.png` từ `MyDrive/VigorAI_ModelB_Output/`.
4. Đặt `food_yolo_v1.onnx` vào `backend/ai_models/weights/food_yolo_v1.onnx` và cập nhật `backend/ai_models/model_b_manifest.json`.

---

## 3. Đánh giá & Benchmark tốc độ CPU ONNX Runtime (`T-M4-06`, `T-M4-12`)

Chạy đánh giá trực tiếp trên file `.onnx` bằng đúng `FoodYoloService` của FastAPI (không cần PyTorch):
```bash
python evaluate_model.py \
    --model ../../backend/ai_models/weights/food_yolo_v1.onnx \
    --data ../datasets/model_b_v2/data.yaml \
    --split test \
    --conf 0.30 \
    --out ../evaluation_reports/model_b_v1/model_b_v1_onnx_eval.json
```

---

## 4. Test nhanh bằng ảnh thật & chạy FastAPI local

```bash
# 1. Test trực tiếp bằng file ảnh & xuất ảnh vẽ bounding box
python test_camera_local.py --image path/to/meal.jpg --save-preview preview.jpg

# 2. Chạy Pytest toàn diện (unit + ONNX + API /api/v1/ai/food-analyze)
cd ../../
python -m pytest backend/tests/test_ai_api.py -v

# 3. Chạy FastAPI local cho Mobile/Swagger test (/docs)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **Kiểm tra trạng thái model:** `GET http://localhost:8000/api/v1/ai/food-model/info`
- **Quét món ăn:** `POST http://localhost:8000/api/v1/ai/food-analyze` (`multipart/form-data`: `image`, `meal_type`)
