# AI Model Weights Directory (`[OWNER: M4]`)

- **Không commit file trọng số nặng** (`*.pt`, `*.onnx`, `*.joblib`) lên Git (đã chặn trong `.gitignore`).
- **Chạy local:** đặt file trọng số vào `backend/ai_models/weights/`:
  - `food_yolo_v1.onnx` *(khuyên dùng — chạy trực tiếp qua `onnxruntime` + `numpy` + `pillow`, không cần PyTorch/Ultralytics, nhẹ RAM và nhanh trên CPU `< 150 ms/ảnh`)*
  - hoặc `food_yolo_v1.pt` *(chạy qua `ultralytics` nếu đã cài)*
- **Triển khai Production (Railway / Docker):**
  1. Upload `food_yolo_v1.onnx` lên Railway Storage Bucket (ví dụ key `ai_models/food_yolo_v1.onnx`) / S3 / GitHub Release.
  2. Điền `download_url` + `sha256` trong `model_b_manifest.json` hoặc đặt biến môi trường:
     - `VIGOR_FOOD_MODEL_URL=s3://gym3d-assets/ai_models/food_yolo_v1.onnx` *(Railway Storage Bucket private, dùng `S3_*` hoặc `AWS_*`)* hoặc `https://.../food_yolo_v1.onnx`
     - `VIGOR_FOOD_MODEL_SHA256=<sha256>` *(tùy chọn, khuyến nghị)*
     - `VIGOR_FOOD_ALLOW_STUB=0` *(mặc định tự động tắt trên Railway Production để không bao giờ trả kết quả Ức gà + Cơm trắng giả)*
     - `VIGOR_AI_UPSTREAM_URL=https://vigorai-api-production.up.railway.app` *(mặc định bật tự động trên Railway khi service chính `vigorai-production` chưa gắn bucket trọng số `.onnx` riêng, giúp bản `.aab` trên CH Play luôn chạy model ONNX mới nhất của `M4`)*
     - `VIGOR_FOOD_CONF=0.30` *(tùy chọn)*
     - `VIGOR_FOOD_IOU=0.45` *(tùy chọn)*
  3. Server cần tối thiểu `onnxruntime`, `numpy`, `pillow` (đã có trong `backend/requirements.txt`; với `backend/Dockerfile.railway` của `M3`, bật `INSTALL_AI_DEPS=true` hoặc cài 3 gói nhẹ này cho nhánh ONNX).
  4. Kiểm tra trạng thái nạp model qua `GET /api/v1/ai/food-model/info`.
