# Bảng Phân công & Kiểm soát Tiến độ (Team Taskboard)

> **Dự án:** VigorAI (`VigorAI: 3D Gym & Health Log` — Ứng dụng Quản lý Sức khỏe & Luyện tập Gym 3D kết hợp Trí tuệ Nhân tạo)
> **Tài liệu liên quan:** [system-design-spec.md](./system-design-spec.md) | [roadmap.md](./roadmap.md)
> **Hướng dẫn sử dụng:** Trưởng nhóm và các thành viên cập nhật dấu `[x]` vào cột **Trạng thái** sau khi Pull Request tương ứng đã vượt qua **Definition of Done (DoD)** và được merge sạch vào nhánh `develop`.

---

## 1. Bảng Tổng hợp Tiến độ (Dashboard Overview)

### 1.1. Phân bổ Số lượng Task theo Sprint & Thành viên

| Thành viên | Vai trò | Sprint 1 (T1–T2) | Sprint 2 (T3–T5) | Sprint 3 (T6–T8) | Sprint 4 (T9–T10) | Tổng số Task | Tiến độ hiện tại |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1** | Mobile Core & Health (Flutter) | 5 | 6 | 3 | 3 | **17** | `0 / 17 (0%)` |
| **M2** | 3D Blender MCP & Gym Execution | 5 | 6 | 3 | 3 | **17** | `0 / 17 (0%)` |
| **M3** | Backend FastAPI & PostgreSQL | 5 | 5 | 3 | 2 | **15** | `0 / 15 (0%)` |
| **M4** | AI Engineer & Data Analytics | 5 | 4 | 4 | 2 | **15** | `0 / 15 (0%)` |
| **Tổng cộng** | **Toàn đội (4 thành viên)** | **20** | **21** | **13** | **10** | **64** | **`0 / 64 (0%)`** |

### 1.2. Bảng Ánh xạ 26 Chức năng (`F01`–`F26`) sang Mã Task

| Phân hệ | Mã Chức năng | Tên Chức năng | Các Task Liên quan |
| :--- | :---: | :--- | :--- |
| **1. Sức khỏe & Sinh trắc** | `F01` | Cân nặng, BMI & Thành phần cơ thể | `T-M1-06`, `T-M3-07` |
| | `F02` | Đếm bước chân & Vận động (Health Connect) | `T-M1-07`, `T-M3-07` |
| | `F03` | Theo dõi lượng nước thông minh | `T-M1-08`, `T-M3-07` |
| | `F04` | Nhật ký Calo & Macro (Mifflin-St Jeor) | `T-M1-09`, `T-M1-13`, `T-M3-07` |
| | `F05` | Theo dõi Giấc ngủ & Phục hồi nền | `T-M1-10`, `T-M3-07` |
| | `F06` | Nhắc lịch Thực phẩm bổ sung | `T-M1-10`, `T-M3-07` |
| **2. Phòng Tập 3D (Blender MCP)** | `F07` | Thư viện Bài tập 3D Tương tác | `T-M2-03`, `T-M2-06`, `T-M2-14`, `T-M3-08` |
| | `F08` | Camera 3D 360° & Đa góc nhìn cố định | `T-M2-03`, `T-M2-14`, `T-M3-08` |
| | `F09` | Bản đồ Giải phẫu Cơ bắp 3D (Heatmap) | `T-M2-07`, `T-M2-14`, `T-M3-08` |
| | `F10` | Mô phỏng Tư thế Đúng vs. Lỗi Sai 3D | `T-M2-08`, `T-M2-14`, `T-M3-08` |
| | `F11` | Điều khiển Tốc độ & Phân tách 3 Pha | `T-M2-08`, `T-M2-14`, `T-M3-08` |
| | `F12` | Bộ Dụng cụ Gym 3D Rời (Sockets) | `T-M2-06`, `T-M2-14`, `T-M3-08` |
| | `F13` | Tùy biến Tỷ lệ Mô hình 3D (Body Avatar) | `T-M2-08`, `T-M2-14` |
| **3. Kế hoạch & Thực thi Gym** | `F14` | Lịch tập luyện & Thiết kế Giáo án | `T-M2-09`, `T-M3-09` |
| | `F15` | Ghi chép Buổi tập Trực tiếp (Offline-first) | `T-M2-10`, `T-M3-09` |
| | `F16` | Đồng hồ Nghỉ giữa Hiệp (Foreground Service) | `T-M2-11`, `T-M3-09` |
| | `F17` | Ước tính 1RM (Epley/Brzycki) & Overload | `T-M2-10`, `T-M2-15`, `T-M3-09` |
| | `F18` | Công cụ Tính Bánh Tạ Trực quan | `T-M2-10`, `T-M2-15`, `T-M3-09` |
| **4. Trí tuệ Nhân tạo (AI)** | `F19` | AI Nhận diện Món ăn qua Ảnh (Model B) | `T-M4-01`, `T-M4-04`, `T-M4-06`, `T-M4-10`, `T-M4-13`, `T-M4-14`, `T-M1-13`, `T-M3-11` |
| | `F20` | AI Dự báo Readiness & Mỏi cơ (Model C) | `T-M4-02`, `T-M4-05`, `T-M4-07`, `T-M4-11`, `T-M4-12`, `T-M4-13`, `T-M4-14`, `T-M3-11` |
| | `F21` | AI Khuyến nghị Mức tạ & Cảnh báo Quá tải | `T-M4-11`, `T-M2-12` |
| **5. Phân tích & CH Play** | `F22` | Thống kê Tiến độ & Volume Load | `T-M4-08`, `T-M3-10` |
| | `F23` | Bản đồ Phục hồi Cơ bắp 3D | `T-M2-13`, `T-M4-12` |
| | `F24` | Radar Cân bằng cơ & Ảnh Before/After cục bộ | `T-M4-09`, `T-M3-10` |
| | `F25` | Đổi Bài tập Tức thì & Kỷ lục PR / Streak | `T-M2-09`, `T-M2-11`, `T-M3-08`, `T-M3-10` |
| | `F26` | Quyền riêng tư, Miễn trừ Y tế & Xóa Tài khoản | `T-M1-04`, `T-M1-12`, `T-M1-16`, `T-M1-17`, `T-M3-03`, `T-M3-04`, `T-M3-12`, `T-M3-15` |

---

## 2. Sprint 1 (Tuần 1 – 2): Nền tảng, Hợp đồng API, DB & 3D Base (20 Tasks)

### Thành viên 1 (`M1` – Mobile Core & Health)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-01:** Khởi tạo Flutter project, chốt `pubspec.yaml`, `main.dart`, `app_theme.dart`, `app_router.dart` stub (import 3 file route con), `dio_client.dart`. | `INFRA` | `mobile/pubspec.yaml`, `mobile/lib/main.dart`, `mobile/lib/core/theme/`, `mobile/lib/core/network/`, `mobile/lib/core/router/` | Tạo sẵn file rỗng `gym3d_workout_routes.dart` & `ai_analytics_routes.dart` để M2, M4 điền sau. | `flutter run` build thành công trên Android; cả 3 thành viên Mobile chạy chung khung router không lỗi. |
| `[ ]` | **T-M1-02:** Cấu hình `AndroidManifest.xml` & `build.gradle` chuẩn CH Play (`minSdk 26`, `targetSdk 35`, Health Connect queries, `ACTIVITY_RECOGNITION`, `CAMERA`, `FOREGROUND_SERVICE_HEALTH`). | `INFRA` | `mobile/android/app/src/main/AndroidManifest.xml`, `mobile/android/app/build.gradle.kts` | Khóa cấu hình ngay Ngày 2 để M2, M4 dùng chung. | Kiểm tra không chứa bất kỳ quyền cấm nào (`READ_MEDIA_IMAGES`, `SCHEDULE_EXACT_ALARM`, `READ_EXTERNAL_STORAGE`). |
| `[ ]` | **T-M1-03:** Tạo `app_database.dart` stub, bảng `health_tables.drift.dart` (có `sync_status`, `updated_at`, `deleted_at`) & viết `photo_picker_service.dart` (nén ảnh `< 300KB`). | `INFRA` | `mobile/lib/core/database/`, `mobile/lib/core/platform/photo_picker_service.dart` | Chừa sẵn slot import `workout_tables.drift.dart` (M2) và `ai_cache_tables.drift.dart` (M4). | Code generator `build_runner` sinh file `.g.dart` sạch lỗi; `PhotoPickerService` trả về JPEG `< 300KB`. |
| `[ ]` | **T-M1-04:** Xây dựng màn hình Onboarding, Login/Register & Màn hình Bắt buộc chấp thuận **Medical Disclaimer** (Mifflin-St Jeor, Epley/Brzycki). | `F26` | `mobile/lib/features/auth_privacy/`, `mobile/lib/core/router/health_routes.dart` | Dùng `MockAuthInterceptor` khi M3 chưa dựng xong server. | Không thể vào Dashboard nếu chưa tick đồng ý Miễn trừ y tế; Token lưu vào `flutter_secure_storage`. |
| `[ ]` | **T-M1-05:** Viết bộ Mock JSON cho Auth & Health (`mock_m1.json`) + tầng `auth_repository` & `health_repository`. | `INFRA` | `mobile/assets/mock_json/mock_m1.json`, `mobile/lib/features/health/data/` | Bật cờ `useMockApi = true` chạy full luồng UI trước khi ghép Backend. | Chuyển đổi qua lại giữa Mock và HTTP thật chỉ qua 1 biến cấu hình môi trường. |

### Thành viên 2 (`M2` – 3D Blender MCP & Gym Execution)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-01:** Thiết lập kịch bản Python **Blender MCP** dựng `base_mannequin.glb` (11 Mesh `Mesh_Muscle_*`, 11 Material `Mat_Muscle_*`, `Armature_GymHuman`). | `INFRA` | `assets_3d/scripts_blender_mcp/`, `assets_3d/source_blend/`, `mobile/assets/3d_bundled/base_mannequin.glb` | Làm độc lập hoàn toàn trên Blender MCP. | File `base_mannequin.glb` đạt `<= 25,000 triangles`, nén Draco, dung lượng `<= 2.0 MB`, đủ 11 tên Material chuẩn. |
| `[ ]` | **T-M2-02:** Dựng 3 bài tập 3D mẫu đóng gói sẵn (Barbell Squat, Push-up, Bench Press) kèm clip `Anim_GoodForm` & `Anim_BadForm`, `Socket_Hand_L/R`, `Socket_Back_Barbell`. | `INFRA` | `assets_3d/exported_glb/`, `mobile/assets/3d_bundled/` | Chưa cần server CDN của M3, đọc thẳng từ `assets/3d_bundled/` để test. | 3 file `.glb` chạy chuẩn `30 FPS`, dụng cụ gắn Socket không bị xuyên thấu (clipping) qua tay/vai. |
| `[ ]` | **T-M2-03:** Xây dựng widget tái sử dụng **`Muscle3DViewerWidget`** (`model_viewer_plus` + JS Bridge xoay 360°, Pinch-to-Zoom, 4 nút góc nhìn Front/Side/Back/Top). | `F07`, `F08` | `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart` | Xuất interface sạch nhận `glbPath` & `muscleColorsMap` để M4 dùng sau cho `F23`. | Xoay 360° mượt trên máy Android thật; 4 nút chuyển góc nhìn hoạt động trong `< 300ms`. |
| `[ ]` | **T-M2-04:** Viết `workout_tables.drift.dart`, `gym3d_workout_routes.dart` & file `mock_m2_exercises.json` cho 5 bài tập đầu. | `INFRA` | `mobile/lib/core/database/workout_tables.drift.dart`, `mobile/lib/core/router/gym3d_workout_routes.dart`, `mobile/assets/mock_json/mock_m2_exercises.json` | Dùng dữ liệu JSON tĩnh không cần đợi API `/api/v1/exercises` từ M3. | Drift sinh bảng `exercises`, `workout_routines`, `workout_sessions`, `workout_sets` sạch lỗi. |
| `[ ]` | **T-M2-05:** Xây dựng `AssetCacheManager` tải lười `.glb` từ URL, kiểm tra mã băm SHA-256 và giới hạn LRU Cache tối đa `250 MB`. | `INFRA` | `mobile/lib/features/gym3d/data/asset_cache_manager.dart` | Test với localhost HTTP server hoặc file mock URL. | Tải 1 lần, lần mở thứ 2 đọc từ ổ đĩa cục bộ (`< 1.2s`); tự động xóa file cũ khi vượt `250 MB`. |

### Thành viên 3 (`M3` – Backend FastAPI & PostgreSQL)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-01:** Khởi tạo FastAPI (`main.py` mount sẵn `ai.router` stub), `requirements.txt`, `docker-compose.yml` (PostgreSQL 16 + MinIO S3 local + FastAPI). | `INFRA` | `backend/requirements.txt`, `backend/docker-compose.yml`, `backend/app/main.py`, `backend/app/core/` | Chừa sẵn file stub `routers/ai.py` cho M4 toàn quyền chỉnh sửa. | `docker compose up` chạy ngay FastAPI (`/docs`) và PostgreSQL 16 trên local. |
| `[ ]` | **T-M3-02:** Viết SQLAlchemy Models & Alembic Migration cho toàn bộ 11 bảng nghiệp vụ + bảng `food_nutrition_catalog` + script seed dữ liệu mẫu VNFood/USDA & 30 bài tập. | `INFRA` | `backend/app/models/`, `backend/alembic/`, `backend/app/db/` | Tạo seed dữ liệu ngay để M1, M2, M4 có dữ liệu kiểm thử. | `alembic upgrade head` chạy sạch trên DB mới; truy vấn thử thấy đủ 12 bảng và Indexes. |
| `[ ]` | **T-M3-03:** Xây dựng luồng Auth JWT (`register`, `login`, `refresh`) băm mật khẩu Argon2/bcrypt, lưu `medical_disclaimer_accepted` & timestamp. | `F26` | `backend/app/routers/auth.py`, `backend/app/services/auth_service.py`, `backend/app/schemas/core_schemas.py` | Xuất Postman/OpenAPI JSON sớm để M1 ghép nối ở cuối Tuần 2. | Đăng ký bắt buộc `medical_disclaimer_accepted = true`; Token Access 15p / Refresh 30 ngày hoạt động đúng. |
| `[ ]` | **T-M3-04:** Xây dựng `GET /api/v1/users/me/export`, `DELETE /api/v1/users/me` (Cascade Delete) & trang Web HTML công khai `GET /delete-account`. | `F26` | `backend/app/routers/users.py`, `backend/app/templates/delete_account.html` | Không phụ thuộc thành viên nào khác. | Mở `/delete-account` trên trình duyệt hiển thị form chuẩn Google Play; xóa user xong trả về `401` cho token cũ. |
| `[ ]` | **T-M3-05:** Dựng Swagger OpenAPI `/docs` hoàn chỉnh & viết script `seed_demo_history.py` tạo 30 ngày lịch sử tập/ăn uống giả lập cho M4 train/test AI. | `INFRA` | `backend/app/db/seed_demo_history.py` | Gửi link Swagger cho M1, M2, M4 chốt lại toàn bộ tên trường JSON. | Script chạy sinh đủ dữ liệu 30 ngày sạch sẽ không vi phạm ràng buộc khóa ngoại. |

### Thành viên 4 (`M4` – AI Engineer & Data Analytics)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-01:** Thu thập, làm sạch Dataset 35–50 món ăn VN & đồ ăn Gym (~5,000–8,000 ảnh), chia 70/20/10, gán nhãn chuẩn YOLO + cấu hình Augmentation. | `F19` | `ai_research/model_b_food_yolo/` | Làm việc độc lập trong `ai_research/`, không đụng vào Backend/Mobile. | File `data.yaml` hợp lệ; kiểm tra phân bố nhãn cân đối, không bị lỗi bounding box rỗng. |
| `[ ]` | **T-M4-02:** Viết bộ sinh dữ liệu tổng hợp theo mô hình Banister Fitness-Fatigue (~15,000 mẫu chuỗi 7 ngày) với 12 biến đầu vào & nhãn Readiness/Fatigue. | `F20` | `ai_research/model_c_readiness_ml/generate_banister_data.py` | Không cần chờ dữ liệu thật từ App để bắt đầu nghiên cứu/train. | Tập dữ liệu sinh ra phản ánh đúng quy luật sinh lý (thiếu ngủ/thiếu đạm làm giảm tốc độ hồi phục). |
| `[ ]` | **T-M4-03:** Tạo `routers/ai.py` stub (trả JSON Mock chuẩn hợp đồng Mục 5 `system-design-spec.md`), `ai_schema.py`, `ai_analytics_routes.dart`, `ai_cache_tables.drift.dart`. | `INFRA` | `backend/app/routers/ai.py`, `backend/app/schemas/ai_schema.py`, `mobile/lib/core/router/ai_analytics_routes.dart`, `mobile/lib/core/database/ai_cache_tables.drift.dart` | Cho phép M1, M2 thấy được cấu trúc trả về của AI ngay từ Tuần 2. | Gọi thử 2 endpoint AI stub trên Swagger trả về đúng JSON mẫu `200 OK`. |
| `[ ]` | **T-M4-04:** Xây dựng công thức quy đổi `BBoxAreaRatio` sang gram khẩu phần (`clamp(0.4, 2.5)`) và hàm tra cứu `food_nutrition_catalog`. | `F19` | `ai_research/model_b_food_yolo/portion_estimator.py`, `backend/app/services/ai_food_yolo.py` | Dùng danh mục JSON từ điển của M3 (`T-M3-02`) để kiểm thử logic quy đổi. | Unit test tính đúng Calo/Protein/Carb/Fat từ danh sách bounding box giả lập. |
| `[ ]` | **T-M4-05:** Chạy thử nghiệm so sánh baseline 3 thuật toán **XGBoost vs LightGBM vs MLP** trên dữ liệu Banister & viết script đo `MAE`, `RMSE`, `R2`. | `F20` | `ai_research/model_c_readiness_ml/benchmark_models.py` | Độc lập hoàn toàn trong `ai_research/`. | Có bảng so sánh 3 thuật toán và biểu đồ phân phối sai số ban đầu cho báo cáo. |

---

## 3. Sprint 2 (Tuần 3 – 5): Core Sức khỏe, 3D Blender & Gym Logger Offline-First (21 Tasks)

### Thành viên 1 (`M1` – Mobile Core & Health)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-06:** Xây dựng module Cân nặng & Thành phần cơ thể (BMI WHO Châu Á, Body Fat %, Muscle Mass, 5 số đo vòng, biểu đồ đường 7-Day Moving Average). | `F01` | `mobile/lib/features/health/biometrics/` | Lưu trực tiếp SQLite Drift; test offline trước. | Nhập/xem biểu đồ `< 200ms`; BMI làm tròn 1 chữ số thập phân chuẩn xác. |
| `[ ]` | **T-M1-07:** Tích hợp **Android Health Connect** (`READ_STEPS`, `READ_ACTIVE_CALORIES_BURNED`) + cảm biến Pedometer dự phòng + màn hình giải thích quyền Runtime. | `F02` | `mobile/lib/core/platform/health_connect_bridge.dart`, `mobile/lib/features/health/steps/` | Dùng `HealthConnect` thật trên máy Android 14+ hoặc giả lập Health Connect Toolbox. | Khử trùng lặp bước chân; hiển thị đúng số km & kcal NEAT; xin quyền đúng lúc bật tính năng. |
| `[ ]` | **T-M1-08:** Xây dựng module Lượng nước thông minh (`35ml x weight_kg` + tự cộng `+500/+750ml` khi có buổi tập Gym) & WorkManager nhắc uống nước (`07:00–21:30`). | `F03` | `mobile/lib/features/health/hydration/` | Đọc trạng thái buổi tập trong ngày từ bảng cục bộ `workout_sessions` (hoặc mock nếu M2 chưa xong). | Hoàn thành buổi tập 60p RPE 8 $\rightarrow$ mục tiêu nước tự tăng thêm `750 ml`; không dùng `SCHEDULE_EXACT_ALARM`. |
| `[ ]` | **T-M1-09:** Xây dựng Nhật ký Calo & Macro (BMR **Mifflin-St Jeor**, TDEE, Bulk/Cut/Maintain, P/C/F, chia 4 bữa & tra cứu từ điển dinh dưỡng cục bộ). | `F04` | `mobile/lib/features/health/nutrition/` | Chưa cần AI Camera của M4; cho phép chọn món từ từ điển tĩnh và nhập tay. | Tính đúng BMR/TDEE/Macro; hiển thị trích dẫn nguồn công thức Mifflin-St Jeor. |
| `[ ]` | **T-M1-10:** Xây dựng module Giấc ngủ (nhập tay + Health Connect `READ_SLEEP`) & Nhắc lịch Supplement (Whey/Creatine) qua WorkManager + nút **"Đã uống"** trên thông báo. | `F05`, `F06` | `mobile/lib/features/health/sleep/`, `mobile/lib/features/health/supplements/` | Test trên Android Emulator API 34/35 với quyền `POST_NOTIFICATIONS`. | Bấm "Đã uống" ngay trên notification cập nhật SQLite mà không cần mở app. |
| `[ ]` | **T-M1-11:** Hoàn thiện `SyncQueueManager` (tự động Push/Pull khi có mạng hoặc mỗi 6h) & ghép nối API Health thật từ M3 (`useMockApi = false`). | `INFRA` | `mobile/lib/core/sync/sync_queue_manager.dart` | Phối hợp M3 khi `T-M3-06` & `T-M3-07` hoàn tất ở Tuần 4–5. | Tắt Wi-Fi nhập cân nặng/nước/bữa ăn -> bật mạng -> dữ liệu tự đồng bộ lên PostgreSQL không trùng lặp. |

### Thành viên 2 (`M2` – 3D Blender MCP & Gym Execution)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-06:** Dùng Blender MCP dựng hoàn chỉnh **20–30 bài tập 3D** + Bộ dụng cụ rời (`Barbell`, `Dumbbell`, `Bench`, `Cable`, `Rack`, `Kettlebell`), xuất `.glb` nén Draco + `assets_manifest.json`. | `F07`, `F12` | `assets_3d/scripts_blender_mcp/`, `assets_3d/exported_glb/` | Upload lên MinIO/CDN do M3 cung cấp ở `T-M3-08`. | Tất cả file `.glb` đều đạt `800KB – 2.5MB`, `<= 25,000 tris`, đủ metadata SHA-256 & Setup máy. |
| `[ ]` | **T-M2-07:** Hoàn thiện **Bản đồ Giải phẫu Cơ bắp 3D** trên `Muscle3DViewerWidget` (JS Bridge đổi `Mat_Muscle_*`: Đỏ `#E53935`, Cam `#FB8C00`, Vàng `#FDD835`, Xám `#9E9E9E`). | `F09` | `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart` | Chạy trực tiếp trên `base_mannequin.glb` ở local. | Đổi màu chính xác từng bó cơ theo từng bài tập mà không cần tải lại file `.glb`. |
| `[ ]` | **T-M2-08:** Tích hợp chuyển đổi `Anim_GoodForm` vs `Anim_BadForm` (ít nhất 15 bài Compound), điều khiển tốc độ `0.25x/0.5x/1.0x`, thanh phân tách 3 pha & chọn Avatar Nam/Nữ. | `F10`, `F11`, `F13` | `mobile/lib/features/gym3d/presentation/screens/exercise_3d_detail_screen.dart` | Dùng metadata `phase_keyframes` từ `mock_m2_exercises.json` rồi ghép API M3. | Tua thanh timeline ở `0.25x` hiển thị khớp nhịp "Hít vào / Thở ra" theo pha Eccentric/Isometric/Concentric. |
| `[ ]` | **T-M2-09:** Xây dựng Màn hình Thiết kế Giáo án tuần (`Push-Pull-Legs`, `Upper-Lower`, `Full Body`, kéo thả thứ tự, Superset) & Smart Exercise Swapper (`>= 80%` trùng cơ chính). | `F14`, `F25` | `mobile/lib/features/workout/routines/` | Đọc/ghi trực tiếp bảng `workout_routines` & `routine_exercises` dưới SQLite. | Tạo/kéo thả/sửa giáo án mượt khi offline; đổi bài tập giữ nguyên được ngữ cảnh giáo án. |
| `[ ]` | **T-M2-10:** Xây dựng **Live Workout Logger** (Offline-first SQLite, Pre-fill buổi trước, Set Types, RPE), công thức **1RM (Epley/Brzycki)** & **Visual Barbell Plate Calculator**. | `F15`, `F17`, `F18` | `mobile/lib/features/workout/logger/`, `mobile/lib/features/workout/tools/` | Test hoàn toàn trên SQLite cục bộ. | Đóng đột ngột app giữa buổi tập mở lại vẫn khôi phục đủ hiệp đã tick; Plate Calculator vẽ đúng từng bánh tạ. |
| `[ ]` | **T-M2-11:** Xây dựng **Smart Rest Timer** dùng **Android Foreground Service (`FOREGROUND_SERVICE_HEALTH`)** + Notification đếm ngược (`+15s/-15s/Skip`) & Logic lưu Kỷ lục cá nhân (PR) / Streak. | `F16`, `F25` | `mobile/lib/features/workout/timer/`, `mobile/android/app/src/main/kotlin/` | Dùng Channel Kotlin/Flutter hoặc plugin foreground service hợp lệ chuẩn Android 14+. | Khóa màn hình 3 phút đồng hồ nghỉ vẫn đếm chính xác và rung/chuông báo hết giờ; lưu PR khi vượt 1RM lịch sử. |

### Thành viên 3 (`M3` – Backend FastAPI & PostgreSQL)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-06:** Xây dựng Engine Đồng bộ hai chiều `POST /api/v1/sync/push` & `GET /api/v1/sync/pull` (Batch Transaction, LWW theo `updated_at` UTC, ưu tiên `max(steps_count)`). | `INFRA` | `backend/app/routers/sync.py`, `backend/app/services/sync_service.py` | Test bằng Pytest giả lập 2 thiết bị sync cùng lúc. | Xử lý an toàn khi client gửi lại cùng 1 lô dữ liệu nhiều lần (Idempotent); không mất bước chân. |
| `[ ]` | **T-M3-07:** Hoàn thiện API Sức khỏe (`/api/v1/health/biometrics`, `/daily/{date}`, `/meals`, `/supplements`, tra cứu `food_nutrition_catalog`). | `F01`–`F06` | `backend/app/routers/health.py` | Độc lập hoàn toàn; ưu tiên xong ở Tuần 4 để M1 ghép. | Tất cả CRUD + Filter theo khoảng ngày hoạt động đúng trên Swagger & Pytest. |
| `[ ]` | **T-M3-08:** Hoàn thiện API Kho bài tập 3D (`/api/v1/exercises`, `/exercises/{code}/alternatives`) & dịch vụ CDN/MinIO lưu `.glb` kèm SHA-256 checksum. | `F07`–`F12`, `F25` | `backend/app/routers/exercises.py`, `backend/app/services/storage_service.py` | Nhận các file `.glb` đã export của M2 đưa lên bucket công khai. | API trả về URL tải `.glb`, mảng `primary_muscles` và top 5 bài thay thế cùng nhóm cơ. |
| `[ ]` | **T-M3-09:** Hoàn thiện API Giáo án & Buổi tập (`/api/v1/routines`, `/api/v1/workouts/sessions`) kèm logic tính lại `total_volume_kg` và cập nhật cờ `is_pr`. | `F14`–`F18` | `backend/app/routers/routines.py`, `backend/app/routers/workouts.py` | Dùng seed data để test trước khi M2 gọi API. | Lưu phiên tập 20 hiệp trong `< 100ms`; tự động tính đúng tổng Volume và đánh dấu PR. |
| `[ ]` | **T-M3-10:** Xây dựng API Tổng hợp Tiến độ `/api/v1/analytics/summary` (Volume Load tuần/tháng, 6 trục Radar cân bằng nhóm cơ, Bảng kỷ lục PR). | `F22`, `F24`, `F25` | `backend/app/routers/analytics.py`, `backend/app/services/analytics_service.py` | Phối hợp với M4 để khớp định dạng trục biểu đồ. | Truy vấn tổng hợp 90 ngày dữ liệu chạy `< 150ms` nhờ Index PostgreSQL. |

### Thành viên 4 (`M4` – AI Engineer & Data Analytics)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-06:** Huấn luyện **AI Model B (YOLOv8s/m)** trên GPU/Colab, tối ưu Hyperparameters, đánh giá đạt KPI (`mAP@0.5 >= 0.80`, `Precision >= 0.82`, `Recall >= 0.78`). | `F19` | `ai_research/model_b_food_yolo/train_yolo.py`, `backend/ai_models/model_b_manifest.json` | Train độc lập trên GPU/Colab; lưu trọng số `.pt`/`.onnx` lên Object Storage/Git Release. | Đạt KPI trên tập Test; thời gian suy luận `< 150ms/ảnh`. |
| `[ ]` | **T-M4-07:** Huấn luyện & chọn mô hình tốt nhất cho **AI Model C (XGBoost / LightGBM / MLP)** đạt KPI (`MAE <= 4.5`, `RMSE <= 6.2`, `R2 >= 0.88`). | `F20` | `ai_research/model_c_readiness_ml/train_readiness.py`, `backend/ai_models/model_c_manifest.json` | Train trên dữ liệu Banister + fine-tune trên dữ liệu seed 30 ngày của M3. | Lưu model tốt nhất (`.joblib`/`.json`), xuất biểu đồ Feature Importance cho báo cáo. |
| `[ ]` | **T-M4-08:** Xây dựng màn hình **Thống kê Tiến độ & Tổng Khối lượng Tập** (`Volume Load` theo tuần/tháng đối chiếu biểu đồ cân nặng & Calo ròng). | `F22` | `mobile/lib/features/ai_analytics/volume_analytics/` | Đọc dữ liệu từ bảng SQLite (`workout_sessions`, `biometric_logs`, `meal_logs`) qua `Mock`/`Seed`. | Tổng hợp biểu đồ 1.000 hiệp tập trong `< 300ms` ngay cả khi offline. |
| `[ ]` | **T-M4-09:** Xây dựng **Biểu đồ Radar Cân bằng 6 Nhóm cơ** & **Nhật ký Ảnh Before/After** (Slider so sánh 2 mốc ảnh, lưu 100% cục bộ trong `getApplicationDocumentsDirectory()/progress_photos/`). | `F24` | `mobile/lib/features/ai_analytics/muscle_balance/`, `mobile/lib/features/ai_analytics/progress_photos/` | Gọi `PhotoPickerService` của M1 để chụp/chọn ảnh không vi phạm quyền CH Play. | Ảnh Progress không xuất hiện trong Gallery hệ thống; Slider kéo so sánh mượt mà. |

---

## 4. Sprint 3 (Tuần 6 – 8): Tích hợp AI Production, Bản đồ Mỏi cơ 3D & Ghép nối E2E (13 Tasks)

### Thành viên 1 (`M1` – Mobile Core & Health)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-12:** Hoàn thiện **Trung tâm Quyền riêng tư** (`F26`): nút Xuất dữ liệu JSON, bật/tắt Health Connect, nút **"Xóa tài khoản & toàn bộ dữ liệu vĩnh viễn"** (xác thực lại + dọn sạch SQLite, cache 3D, Progress Photos). | `F26` | `mobile/lib/features/auth_privacy/privacy_center/` | Gọi `DELETE /api/v1/users/me` và `GET /api/v1/users/me/export` của M3. | Xóa xong tài khoản đăng xuất về Onboarding; kiểm tra ổ đĩa không còn ảnh progress hay bản ghi SQLite. |
| `[ ]` | **T-M1-13:** Nối luồng kết quả bữa ăn từ màn hình Quét AI (M4) vào Nhật ký Calo & Macro (`F04`) và cập nhật tự động Dashboard Sức khỏe hàng ngày. | `F04`, `F19` | `mobile/lib/features/health/nutrition/` | Sử dụng hợp đồng `MealLog` chung trong `health_tables.drift.dart`. | Quét đĩa cơm xong bấm Lưu $\rightarrow$ tổng Calo & Protein trong ngày trên Dashboard tăng ngay lập tức. |
| `[ ]` | **T-M1-14:** Kiểm thử toàn trình Offline-Online Sync giữa các màn hình Health (`M1`), Workout (`M2`) và AI (`M4`). | `INFRA` | `mobile/lib/core/sync/` | Thực hiện chung sau buổi ghép nối cuối Sprint 2. | Không xảy ra crash, mất dữ liệu hay trùng bản ghi khi chuyển mạng 4G $\leftrightarrow$ Airplane Mode. |

### Thành viên 2 (`M2` – 3D Blender MCP & Gym Execution)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-12:** Tích hợp thẻ **AI Khuyến nghị Mức tạ & Cảnh báo Quá tải (Deload)** từ API Model C của M4 vào ngay cạnh ô nhập hiệp tập trong Live Logger (`F15`). | `F21` | `mobile/lib/features/workout/logger/` | Đọc JSON từ `ai_readiness_logs` (cache từ M4), hỗ trợ nút 1 chạm áp dụng mức tạ gợi ý. | Hiển thị rõ lý do tăng/giữ/giảm tạ kèm dòng miễn trừ y tế; người dùng vẫn sửa tay tự do. |
| `[ ]` | **T-M2-13:** Mở rộng `Muscle3DViewerWidget` hỗ trợ **Gradient Color Mapping Phục hồi** (Xanh `#43A047`, Cam `#FB8C00`, Đỏ `#E53935`) và callback `onMuscleTap` khi chạm vào từng bó cơ. | `F23` | `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart` | Giữ nguyên tham số cũ để không ảnh hưởng tới màn hình tập (`F09`). | M4 nhúng widget vào màn hình Phục hồi 3D và chạm bó cơ mở pop-up chính xác 100%. |
| `[ ]` | **T-M2-14:** Tối ưu hiệu năng WebGL/3D Viewer (giải phóng texture/context khi rời trang, pre-warm `base_mannequin.glb`, kiểm tra RAM trên máy Android 4GB). | `F07`–`F13` | `mobile/lib/features/gym3d/` | Đo thực tế bằng Flutter DevTools Memory & Frame Chart. | Tốc độ khung hình duy trì `>= 45 FPS`; mở/đóng màn hình 3D 20 lần liên tiếp không bị tràn bộ nhớ (OOM). |

### Thành viên 3 (`M3` – Backend FastAPI & PostgreSQL)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-11:** Phối hợp cùng M4 hoàn thiện `feature_extractor.py` truy vấn nhanh 12 đặc trưng từ PostgreSQL (72h–28 ngày) & lưu lịch sử vào bảng `ai_readiness_logs`. | `F19`, `F20` | `backend/app/services/feature_extractor.py` | Truy vấn đọc chung các bảng Health, Meals, Workouts của M3. | Thời gian trích xuất đủ 12 biến cho 1 user `< 60ms`. |
| `[ ]` | **T-M3-12:** Gia cố bảo mật Production (HTTPS TLS 1.2+, Rate Limiting cho endpoint AI upload ảnh, Cascade Delete xóa sạch ảnh món ăn trên Object Storage khi gọi `DELETE /users/me`). | `F26` | `backend/app/core/security.py`, `backend/app/services/storage_service.py` | Độc lập trên Backend. | Gửi liên tiếp quá ngưỡng request AI trả về `429 Too Many Requests`; xóa user xóa sạch ảnh trên bucket S3/MinIO. |
| `[ ]` | **T-M3-13:** Triển khai Staging Server công khai (Cloud VPS / Railway / Render) với tên miền HTTPS và cấu hình trang Web `https://<domain>/delete-account`. | `INFRA` | `backend/docker-compose.yml`, cấu hình triển khai | Cả 4 thành viên trỏ App sang Staging Server để test thực tế qua 4G. | Trang `/delete-account` và `/docs` truy cập công khai qua HTTPS bình thường. |

### Thành viên 4 (`M4` – AI Engineer & Data Analytics)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-10:** Đóng gói **AI Model B** vào `ai_food_yolo.py` (`POST /api/v1/ai/food-analyze`) & hoàn thiện UI **Quét Món ăn AI** trên Flutter (Photo Picker + khung bbox + thanh kéo chỉnh gram + disclaimer). | `F19` | `backend/app/services/ai_food_yolo.py`, `backend/app/routers/ai.py`, `mobile/lib/features/ai_analytics/food_scan/` | Gọi `PhotoPickerService` của M1; lưu kết quả vào `meal_logs` để M1 cộng tổng ngày. | Chụp đĩa cơm $\rightarrow$ trả kết quả `< 3.0s` trên 4G; chỉnh thanh trượt gram tự tính lại Macro chính xác. |
| `[ ]` | **T-M4-11:** Đóng gói **AI Model C** vào `ai_readiness_ml.py` (`GET /api/v1/ai/readiness-and-overload`) kèm logic Fallback cho user mới (`< 3 ngày` dữ liệu) & cảnh báo Overtraining. | `F20`, `F21` | `backend/app/services/ai_readiness_ml.py`, `backend/app/routers/ai.py` | Gọi `feature_extractor.py` phối hợp với M3 (`T-M3-11`). | API phản hồi `< 500ms`; user mới chưa có dữ liệu không bị lỗi 500 mà trả về Readiness = 85 kèm giải thích. |
| `[ ]` | **T-M4-12:** Xây dựng màn hình **AI Readiness Dashboard & Bản đồ Phục hồi Cơ bắp 3D** (nhúng `Muscle3DViewerWidget` của M2, truyền `muscle_fatigue_map` và pop-up % hồi phục). | `F20`, `F23` | `mobile/lib/features/ai_analytics/readiness_3d/` | Import trực tiếp widget của M2 (`T-M2-13`), không sửa code trong `features/gym3d/`. | Điểm Readiness + giải thích hiển thị rõ; chạm vào bất kỳ bó cơ nào trên Mannequin 3D hiện đúng % hồi phục. |
| `[ ]` | **T-M4-13:** Chạy kiểm thử chéo AI thực tế (Human-in-the-loop trên ảnh chụp thật của 4 thành viên), xuất Confusion Matrix, biểu đồ Loss/mAP & MAE/R2 phục vụ báo cáo đồ án. | `F19`, `F20` | `ai_research/evaluation_reports/` | Độc lập trong thư mục `ai_research/`. | Hoàn chỉnh bộ số liệu đánh giá định lượng và định tính cho quyển báo cáo đồ án. |

---

## 5. Sprint 4 (Tuần 9 – 10): Kiểm thử Toàn diện, Tối ưu Đóng gói & Duyệt CH Play (10 Tasks)

### Thành viên 1 (`M1` – Mobile Core & Health)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-15:** Viết **Unit Test** cho toàn bộ công thức Sức khỏe (`BMI`, `BMR Mifflin-St Jeor`, `TDEE`, `Smart Hydration`) & **Integration Test** luồng Đăng ký $\rightarrow$ Xóa tài khoản. | `INFRA` | `mobile/test/health/` | Chạy tự động trên máy cục bộ/CI. | `flutter test test/health/` đạt 100% Pass, độ phủ logic công thức đạt `>= 90%`. |
| `[ ]` | **T-M1-16:** Kiểm tra **Merged AndroidManifest.xml** bằng APK Analyzer (bảo đảm 0 quyền cấm `READ_MEDIA_IMAGES`, `SCHEDULE_EXACT_ALARM`, `ACCESS_BACKGROUND_LOCATION`). | `F26` | `mobile/android/app/src/main/AndroidManifest.xml` | Rà soát kể cả quyền do các thư viện bên thứ 3 tự kéo vào (dùng `tools:node="remove"` nếu cần). | Bản build Release không chứa bất kỳ quyền cấm nào trong file Manifest hợp nhất cuối cùng. |
| `[ ]` | **T-M1-17:** Hoàn thiện hồ sơ khai báo **Data Safety**, **Health Apps Declaration** & **Privacy Policy** chuẩn bị nộp Google Play Console. | `F26` | `docs/chplay_submission_checklist.md` (tùy chọn bổ sung trong `docs/`) | Đối chiếu 1-1 với các chức năng đã cài đặt thực tế trong App. | Khai báo khớp 100% với hành vi thực tế của App (không khai báo thiếu hoặc sai mục). |

### Thành viên 2 (`M2` – 3D Blender MCP & Gym Execution)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-15:** Viết **Unit Test** cho thuật toán tính **1RM (Epley/Brzycki)**, tính **Total Volume** & **Barbell Plate Calculator**. | `F17`, `F18` | `mobile/test/workout/` | Chạy độc lập không cần Server. | `flutter test test/workout/` đạt 100% Pass cho mọi trường hợp biên (1 rep, 15 reps, tạ lẻ không chia chẵn `1.25kg`). |
| `[ ]` | **T-M2-16:** Build bản Release **Android App Bundle (`.aab`)** chuẩn 64-bit (`arm64-v8a`, `x86_64`), kiểm tra kích thước **`< 40 MB`** & xác minh **16 KB Page Size Alignment** (Android 15+). | `INFRA` | `mobile/android/`, cấu hình NDK/Gradle Release | Dùng `bundletool` / script kiểm tra ELF 16KB alignment trên thư viện `.so`. | File `.aab` tải xuống `< 40 MB`; tất cả file `.so` căn lề `16KB` đạt chuẩn Google Play Android 15+. |
| `[ ]` | **T-M2-17:** Thực hiện **Test thực địa tại phòng Gym** (chế độ Airplane Mode suốt buổi tập), quay video demo 3D Gym Studio & chụp bộ Screenshot chuẩn kích thước CH Play. | `INFRA` | Tài liệu trình diễn & Store Assets | Chạy trên bản Release build cài từ `.aab` qua `bundletool`. | Ghi chép đủ buổi tập, đếm ngược Rest Timer khi khóa màn hình mượt, đồng bộ lại sau khi bật mạng thành công. |

### Thành viên 3 (`M3` – Backend FastAPI & PostgreSQL)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-14:** Viết **Pytest** toàn diện cho API Core (`Auth`, `Sync LWW`, `Health`, `Workouts`, `Delete Account trả 401`) & Load Test API với Locust/k6. | `INFRA` | `backend/tests/test_core_api.py` | Chạy trên Docker Test Database riêng biệt. | `pytest` Pass 100%; chịu tải tối thiểu 50 người dùng đồng thời không lỗi `5xx`. |
| `[ ]` | **T-M3-15:** Cấu hình Backup tự động PostgreSQL, giám sát log lỗi Staging và kiểm tra trang Web công khai `GET /delete-account` hoạt động ổn định 24/7 trước khi duyệt CH Play. | `F26` | Cấu hình vận hành Server | Xác nhận Google Reviewer truy cập được URL xóa tài khoản từ mạng ngoài. | URL `/delete-account` trả HTTP `200 OK` qua HTTPS; quy trình xóa hoạt động đầy đủ. |

### Thành viên 4 (`M4` – AI Engineer & Data Analytics)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-14:** Viết **Pytest** cho 2 API AI (`food-analyze` với ảnh hợp lệ / ảnh không có đồ ăn / file lỗi; `readiness-and-overload` với user mới và user đủ dữ liệu) + kiểm tra dòng Medical Disclaimer. | `F19`, `F20` | `backend/tests/test_ai_api.py` | Chạy độc lập không đụng `test_core_api.py` của M3. | `pytest backend/tests/test_ai_api.py` Pass 100%; mọi phản hồi AI đều có trường `disclaimer`. |
| `[ ]` | **T-M4-15:** Hoàn thiện bộ số liệu/biểu đồ AI trong báo cáo đồ án & điều phối toàn nhóm tham gia **Closed Testing (12 testers)** trên Google Play Console để mở khóa Production. | `INFRA` | `ai_research/evaluation_reports/` | Cài đặt bản test từ Google Play Console cho nhóm và người thử nghiệm. | Hoàn tất đủ điều kiện Closed Testing trên Google Play Console không gặp lỗi crash (ANR = 0%). |

---

## 6. Checklist Kiểm tra Trước khi Nộp CH Play & Bảo vệ Đồ án (Pre-Release Verification Board)

Trưởng nhóm kiểm tra toàn bộ các chốt chặn sau trước khi chuyển nhánh `develop` sang `main` ở cuối Sprint 4:

- [ ] **Zero-Conflict Git Check:** Toàn bộ 4 nhánh `feat/m1-*`, `feat/m2-*`, `feat/m3-*`, `feat/m4-*` đã merge sạch vào `develop` và `main`; không còn file `.blend1`, `.pt` nặng, hay `build/` nằm trong lịch sử commit mới nhất.
- [ ] **Đủ 26 Chức năng (`F01`–`F26`):** Kiểm tra chạy thử trên máy thật đủ 5 phân hệ (Sức khỏe, 3D Gym Studio Blender MCP, Thực thi buổi tập, 2 AI Models B & C, Phân tích & Quyền riêng tư).
- [ ] **Quyền Android (`AndroidManifest.xml`):** Merged Manifest **không chứa** `READ_MEDIA_IMAGES`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `SCHEDULE_EXACT_ALARM`, `USE_EXACT_ALARM`, `ACCESS_BACKGROUND_LOCATION`.
- [ ] **Xóa Tài khoản & Dữ liệu (`F26`):** Nút xóa trong App hoạt động sạch sẽ (kèm xóa SQLite/ảnh cục bộ) VÀ đường dẫn web công khai `/delete-account` hoạt động bình thường trên trình duyệt.
- [ ] **Miễn trừ Y tế & Nguồn Khoa học:** Màn hình Onboarding, mục Dinh dưỡng (`Mifflin-St Jeor`), mục 1RM (`Epley/Brzycki`) và các kết quả AI đều hiển thị rõ thông báo miễn trừ trách nhiệm y khoa.
- [ ] **Đóng gói `.aab` & Android 15:** `targetSdkVersion = 35`, `minSdkVersion = 26`, kích thước tải xuống ban đầu của `.aab < 40 MB`, hỗ trợ đầy đủ 64-bit và **16 KB page size alignment**.
