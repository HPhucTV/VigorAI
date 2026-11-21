# Bảng Phân công & Kiểm soát Tiến độ (Team Taskboard)

> **Dự án:** VigorAI (`VigorAI: 3D Gym & Health Log` — Ứng dụng Quản lý Sức khỏe & Luyện tập Gym 3D kết hợp Trí tuệ Nhân tạo)
> **Tài liệu liên quan:** [system-design-spec.md](./system-design-spec.md) | [roadmap.md](./roadmap.md)
> **Hướng dẫn sử dụng:** Trưởng nhóm và các thành viên cập nhật dấu `[x]` vào cột **Trạng thái** sau khi Pull Request tương ứng đã vượt qua **Definition of Done (DoD)** và được merge sạch vào nhánh `develop`.
> *(Chiến lược mới: Đã tách `M4` thành **100% Pure AI Engineer (Python Only)** và áp dụng **Lộ trình CH Play 2 Nhịp** kích hoạt đồng hồ 14 ngày ngay cuối Sprint 1.)*

---

## 1. Bảng Tổng hợp Tiến độ (Dashboard Overview)

### 1.1. Phân bổ Số lượng Task theo Sprint & Thành viên

| Thành viên | Vai trò | Sprint 1 (T1–T2) | Sprint 2 (T3–T5) | Sprint 3 (T6–T8) | Sprint 4 (T9–T10) | Tổng số Task | Tiến độ hiện tại |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1** | Mobile Core, Health, Food/Photo UI & CH Play | 7 | 5 | 3 | 2 | **17** | `9 / 17 Done (52.9%) · 2 / 17 [~] (Chờ M4 & Play Console 14d)` |
| **M2** | 3D Blender MCP, Workout, Recovery 3D & Charts | 6 | 6 | 3 | 2 | **17** | `5 / 17 Done (29.4%)` |
| **M3** | Backend FastAPI, PostgreSQL & Cloud Deploy | 6 | 5 | 2 | 2 | **15** | `10 / 15 Done (66.7%) · 1 [~]` |
| **M4** | **100% Pure AI Engineer (Python Only)** | 5 | 4 | 3 | 2 | **14** | `0 / 14 (0%)` |
| **Tổng cộng** | **Toàn đội (4 thành viên)** | **24** | **20** | **11** | **8** | **63** | **`24 / 63 Done (38.1%)`** |

### 1.2. Bảng Ánh xạ 26 Chức năng (`F01`–`F26`) sang Mã Task

| Phân hệ | Mã Chức năng | Tên Chức năng | Các Task Liên quan |
| :--- | :---: | :--- | :--- |
| **1. Sức khỏe & Sinh trắc** | `F01` | Cân nặng, BMI & Thành phần cơ thể | `T-M1-08`, `T-M3-08` |
| | `F02` | Đếm bước chân & Vận động (Health Connect) | `T-M1-13`, `T-M3-08` |
| | `F03` | Theo dõi lượng nước thông minh | `T-M1-08`, `T-M3-08` |
| | `F04` | Nhật ký Calo & Macro (Mifflin-St Jeor) | `T-M1-09`, `T-M1-10`, `T-M3-08` |
| | `F05` | Theo dõi Giấc ngủ & Phục hồi nền | `T-M1-09`, `T-M1-13`, `T-M3-08` |
| | `F06` | Nhắc lịch Thực phẩm bổ sung | `T-M1-09`, `T-M3-08` |
| **2. Phòng Tập 3D (Blender MCP)** | `F07` | Thư viện Bài tập 3D Tương tác | `T-M2-03`, `T-M2-07`, `T-M2-14`, `T-M3-09` |
| | `F08` | Camera 3D 360° & Đa góc nhìn cố định | `T-M2-03`, `T-M2-14`, `T-M3-09` |
| | `F09` | Bản đồ Giải phẫu Cơ bắp 3D (Heatmap) | `T-M2-08`, `T-M2-14`, `T-M3-09` |
| | `F10` | Mô phỏng Tư thế Đúng vs. Lỗi Sai 3D | `T-M2-08`, `T-M2-14`, `T-M3-09` |
| | `F11` | Điều khiển Tốc độ & Phân tách 3 Pha | `T-M2-08`, `T-M2-14`, `T-M3-09` |
| | `F12` | Bộ Dụng cụ Gym 3D Rời (Sockets) | `T-M2-07`, `T-M2-14`, `T-M3-09` |
| | `F13` | Tùy biến Tỷ lệ Mô hình 3D (Body Avatar) | `T-M2-08`, `T-M2-14` |
| **3. Kế hoạch & Thực thi Gym** | `F14` | Lịch tập luyện & Thiết kế Giáo án | `T-M2-09`, `T-M3-10` |
| | `F15` | Ghi chép Buổi tập Trực tiếp (Offline-first) | `T-M2-09`, `T-M3-10` |
| | `F16` | Đồng hồ Nghỉ giữa Hiệp (Foreground Service) | `T-M2-13`, `T-M3-10` |
| | `F17` | Ước tính 1RM (Epley/Brzycki) & Overload | `T-M2-09`, `T-M2-16`, `T-M3-10` |
| | `F18` | Công cụ Tính Bánh Tạ Trực quan | `T-M2-09`, `T-M2-16`, `T-M3-10` |
| **4. Trí tuệ Nhân tạo (AI)** | `F19` | AI Nhận diện Món ăn qua Ảnh (Model B) | `T-M4-01`, `T-M4-04`, `T-M4-06`, `T-M4-09`, `T-M4-10`, `T-M4-11`, `T-M4-12`, `T-M4-13`, `T-M1-10` |
| | `F20` | AI Dự báo Readiness & Mỏi cơ (Model C) | `T-M4-02`, `T-M4-05`, `T-M4-07`, `T-M4-08`, `T-M4-11`, `T-M4-12`, `T-M4-13`, `T-M2-10` |
| | `F21` | AI Khuyến nghị Mức tạ & Cảnh báo Quá tải | `T-M4-07`, `T-M4-08`, `T-M2-10` |
| **5. Phân tích & CH Play** | `F22` | Thống kê Tiến độ & Volume Load | `T-M2-11`, `T-M3-11` |
| | `F23` | Bản đồ Phục hồi Cơ bắp 3D | `T-M2-10`, `T-M2-14` |
| | `F24` | Radar Cân bằng cơ & Ảnh Before/After cục bộ | `T-M1-11`, `T-M2-11`, `T-M3-11` |
| | `F25` | Đổi Bài tập Tức thì & Kỷ lục PR / Streak | `T-M2-09`, `T-M3-09`, `T-M3-11` |
| | `F26` | Quyền riêng tư, Miễn trừ Y tế & Xóa Tài khoản | `T-M1-04`, `T-M1-06`, `T-M1-13`, `T-M1-14`, `T-M1-17`, `T-M3-03`, `T-M3-04`, `T-M3-06`, `T-M3-12`, `T-M3-15` |

---

## 2. Sprint 1 (Tuần 1 – 2): Nền tảng, MVP Closed Testing (`v1.0.0+1`) & Dataset AI Đợt 1 (24 Tasks)

### Thành viên 1 (`M1` – Mobile Core, Health, Food/Photo UI & CH Play)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[x]` | **T-M1-01:** Khởi tạo Flutter project, chốt `pubspec.yaml`, `main.dart`, `app_theme.dart`, `app_router.dart` stub (import 3 file route con), `dio_client.dart` (tích hợp Auto-Refresh JWT `401`). *(Đã build APK & chạy test sạch trên Android 15 `VigorAI_Pixel6_API35`)* | `INFRA` | `mobile/pubspec.yaml`, `mobile/lib/main.dart`, `mobile/lib/core/theme/`, `mobile/lib/core/network/`, `mobile/lib/core/router/`, `mobile/android/` | Đã khóa sẵn khung cho `M2` ghép màn hình. | `flutter run` build thành công trên Android; khung router chạy sạch lỗi. |
| `[x]` | **T-M1-02:** Cấu hình `AndroidManifest.xml` & `build.gradle.kts` chuẩn CH Play (`minSdk 26`, `targetSdk 35`, 16KB page size, chặn 7 quyền cấm). | `INFRA` | `mobile/android/app/src/main/AndroidManifest.xml`, `mobile/android/app/build.gradle.kts`, `mobile/android/{settings.gradle.kts,gradle.properties}` | Khóa cấu hình ngay Sprint 1 cho `M2` build `.aab`. | Kiểm tra XML & Gradle đạt 0 quyền cấm (`READ_MEDIA_IMAGES`, `SCHEDULE_EXACT_ALARM`, ...). |
| `[x]` | **T-M1-03:** Mở khóa `app_database.dart` sinh `app_database.g.dart` (Drift SQLite), `health_tables.drift.dart` (Domain Models + BMI/BMR/Water + `sync_status`) & `photo_picker_service.dart` (`< 300KB`, `progress_photos/`). | `INFRA` | `mobile/lib/core/database/`, `mobile/lib/core/platform/photo_picker_service.dart` | Tách sẵn bảng để không đụng `M2`. | `build_runner` sinh `.g.dart` sạch lỗi; `PhotoPickerService` trả JPEG `< 300KB`. |
| `[x]` | **T-M1-04:** Xây dựng Onboarding, Login/Register & Màn hình Bắt buộc chấp thuận **Medical Disclaimer** (Mifflin-St Jeor, Epley/Brzycki). *(Đã test E2E trên máy ảo Android 15)* | `F26` | `mobile/lib/features/auth_privacy/`, `mobile/lib/core/router/health_routes.dart` | Dùng `MockApiInterceptor` khi `M3` chưa deploy. | Không thể vào Dashboard nếu chưa tick đồng ý Miễn trừ y tế; Token lưu vào `FlutterSecureStorage`. |
| `[x]` | **T-M1-05:** Viết bộ Mock JSON cho Auth & Health (`mock_m1_health.json`, `mock_m1.json`) + `auth_repository`, `health_repository` & Dashboard cơ bản. *(Đã test E2E +250ml & Sync trên máy ảo Android 15)* | `INFRA` | `mobile/assets/mock_json/mock_m1*.json`, `mobile/lib/features/health/` | Chạy mượt ở chế độ `USE_MOCK_API=true`. | Chuyển đổi qua lại giữa Mock và HTTP thật chỉ qua `--dart-define=USE_MOCK_API`. |
| `[x]` | **T-M1-06** *(Kéo sớm cho MVP)*: Thêm nút **"Xóa tài khoản & Dữ liệu"** ngay trên Dashboard/Profile gọi `DELETE /api/v1/users/me` + dọn sạch dữ liệu cục bộ; thêm `FeatureFlags.isMvpClosedTesting` ẩn toàn bộ nút stub và tạm tách quyền `health.READ_*` / `FOREGROUND_SERVICE_HEALTH` khỏi nhánh build MVP `v1.0.0+1`. *(Đã test E2E trên `VigorAI_Pixel6_API35`)* | `F26` | `mobile/lib/core/config/feature_flags.dart`, `mobile/lib/features/auth_privacy/`, `mobile/lib/features/health/presentation/health_dashboard_screen.dart`, `mobile/android/app/src/main/AndroidManifest.xml` | Cần gấp để bản `v1.0.0+1` không bị Google đánh lỗi *Broken Functionality* hay bắt quay video Health Connect sớm. | App MVP `v1.0.0+1` không còn nút bấm vào màn hình stub; nút Xóa tài khoản hoạt động thật với API `M3`. |
| `[ ]` | **T-M1-07** *(Kéo sớm cho MVP)*: Đăng ký tài khoản **Google Play Console (\$25)**, xác minh danh tính Developer & gom danh sách **20–25 email Gmail bạn bè** cho đợt Closed Testing 14 ngày. | `INFRA` | Google Play Console & `docs/chplay_submission_checklist.md` | Làm song song ngay Tuần 1 để kịp xác minh giấy tờ (2–3 ngày). | Tài khoản Play Console được xác minh xanh; sẵn sàng danh sách 20–25 Gmail testers. |

### Thành viên 2 (`M2` – 3D Blender MCP, Workout, Recovery 3D & Charts)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[x]` | **T-M2-01:** Thiết lập script Python **Blender MCP** dựng `base_mannequin.glb` (11 Mesh `Mesh_Muscle_*`, 11 Material `Mat_Muscle_*`, `Armature_GymHuman`). *(Dựng từ CC0 `GEO-body_male_realistic`, Low-Poly Faceted `11,848 tris`, Draco `322 KB`, đủ 4 sockets)* | `INFRA` | `assets_3d/scripts_blender_mcp/`, `assets_3d/source_blend/`, `mobile/assets/3d_bundled/base_mannequin.glb` | Làm độc lập hoàn toàn trên Blender MCP. | File `base_mannequin.glb` đạt `<= 25,000 triangles`, nén Draco, dung lượng `<= 2.0 MB`, đủ 11 Material chuẩn. |
| `[x]` | **T-M2-02:** Dựng 3 bài tập 3D mẫu đóng gói sẵn (Barbell Squat, Push-up, Bench Press) kèm `Anim_GoodForm` & `Anim_BadForm`, `Socket_Hand_L/R`, `Socket_Back_Barbell`. *(Đã verify khung hình via Blender MCP `look`, đủ 2 clip Đúng/Sai, tổng 4 `.glb` bundled = `1.43 MB`)* | `INFRA` | `assets_3d/exported_glb/`, `mobile/assets/3d_bundled/` | Đọc thẳng từ `assets/3d_bundled/` để test trong bản MVP. | 3 file `.glb` chạy chuẩn `30 FPS`, dụng cụ gắn Socket không bị clipping. |
| `[x]` | **T-M2-03:** Xây dựng widget **`Muscle3DViewerWidget`** (`model_viewer_plus` + JS Bridge xoay 360°, Pinch-to-Zoom, 4 góc nhìn Front/Side/Back/Top) + màn hình xem 3 bài tập 3D mẫu cho MVP. *(Đã gắn thẻ mở `/gym3d` ngay dưới Dinh dưỡng trên Dashboard)* | `F07`, `F08` | `mobile/lib/features/gym3d/` | Mở trực tiếp từ Dashboard `M1` qua route `gym3d` để bản MVP có tính năng 3D thật. | Xoay 360° mượt trên máy Android thật; 4 nút chuyển góc nhìn trong `< 300ms`. |
| `[x]` | **T-M2-04:** Hoàn thiện `workout_tables.drift.dart`, `ai_cache_tables.drift.dart`, `gym3d_workout_routes.dart`, `ai_analytics_routes.dart` & `mock_m2_exercises.json`. *(Đủ 30 bài tập chuẩn M3 + SHA-256 thật cho 3 bài MVP; `build_runner` & `flutter analyze` exit `0`)* | `INFRA` | `mobile/lib/core/database/{workout_tables,ai_cache_tables}.drift.dart`, `mobile/lib/core/router/{gym3d_workout_routes,ai_analytics_routes}.dart`, `mobile/assets/mock_json/mock_m2_exercises.json` | Đọc JSON tĩnh không cần đợi `M3`/`M4`. | Drift sinh bảng sạch lỗi; các route sẵn sàng kích hoạt qua `FeatureFlags`. |
| `[x]` | **T-M2-05:** Xây dựng `AssetCacheManager` tải lười `.glb` từ URL, kiểm tra SHA-256 checksum & LRU Cache tối đa `250 MB`. *(Kèm `sha256_util.dart` thuần Dart & 5/5 Unit Test Pass)* | `INFRA` | `mobile/lib/features/gym3d/data/asset_cache_manager.dart` | Test với MinIO/localhost hoặc mock URL. | Tải 1 lần, lần mở sau đọc từ cache `< 1.2s`; tự dọn khi vượt `250 MB`. |
| `[~]` | **T-M2-06** *(Kéo sớm - Mốc 1 CH Play)*: Tạo Upload Keystore, cấu hình ký Release và build file **`.aab` MVP (`v1.0.0+1`)** (Auth + Disclaimer + Xóa tài khoản + Health Dashboard + 3 bài 3D, 0 stub) đẩy lên **Closed Testing** cuối Tuần 2. *(Đã tạo Upload Keystore `vigorai-upload` + `mobile/android/key.properties` ngoài Git, build & xác minh chữ ký `CN=VigorAI` bằng `jarsigner` trên bản `app-release.aab` `44,689,240 B` trỏ thẳng `https://vigorai-production.up.railway.app` với `USE_MOCK_API=false`, 0 quyền cấm; chỉ còn chờ bạn làm `T-M1-07` cuối cùng để upload lên Play Console)* | `INFRA` | `mobile/android/app/`, file ký Keystore (không commit lên Git) | Kích hoạt ngay bộ đếm **14 ngày** song song trong lúc cả nhóm code Sprint 2. | Google duyệt bản Closed Testing `v1.0.0+1` và 20–25 testers cài đặt thành công. |

### Thành viên 3 (`M3` – Backend FastAPI, PostgreSQL & Cloud Deploy)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[x]` | **T-M3-01:** Hoàn thiện FastAPI (`main.py`), `docker-compose.yml` (PostgreSQL 16 + MinIO + FastAPI), `core/` & `db/`. | `INFRA` | `backend/docker-compose.yml`, `backend/Dockerfile`, `backend/app/{main.py,core/,db/}` | Giữ nguyên mount `ai.router` cho `M4`. | `docker compose up` chạy sạch FastAPI `/docs` và PostgreSQL 16. |
| `[x]` | **T-M3-02:** Viết Alembic Migration đầu tiên cho 11 bảng nghiệp vụ + `food_nutrition_catalog` + seed data VNFood/USDA & 30 bài tập. | `INFRA` | `backend/app/models/`, `backend/alembic/`, `backend/app/db/` | Tạo seed data ngay để `M1`, `M2`, `M4` dùng chung. | `alembic upgrade head` chạy sạch; đủ 12 bảng và Indexes. |
| `[x]` | **T-M3-03:** Xây dựng luồng Auth JWT thật (`register`, `login`, `refresh` Argon2/bcrypt) & lưu `medical_disclaimer_accepted` + timestamp. | `F26` | `backend/app/routers/auth.py`, `backend/app/services/auth_service.py`, `backend/app/schemas/core_schemas.py` | Phối hợp `M1` kiểm thử bản MVP `v1.0.0+1`. | Đăng ký bắt buộc `medical_disclaimer_accepted = true`; JWT Access/Refresh chạy đúng. |
| `[x]` | **T-M3-04:** Xây dựng `GET /api/v1/users/me/export`, `DELETE /api/v1/users/me` (Cascade Delete) & trang Web HTML công khai `GET /delete-account`. | `F26` | `backend/app/routers/users.py`, `backend/app/templates/delete_account.html` | Không phụ thuộc thành viên khác. | Trang `/delete-account` hiển thị sạch đẹp; xóa user xong trả `401` cho token cũ. |
| `[x]` | **T-M3-05:** Dựng Swagger OpenAPI `/docs` & script `seed_demo_history.py` tạo 30 ngày lịch sử tập/ăn uống giả lập cho `M4` test AI. | `INFRA` | `backend/app/db/seed_demo_history.py` | Chốt JSON chuẩn cho cả 4 người. | Script sinh đủ dữ liệu 30 ngày sạch sẽ không lỗi khóa ngoại. |
| `[x]` | **T-M3-06** *(Kéo sớm - Mốc 1 CH Play)*: Deploy Backend FastAPI + PostgreSQL lên host HTTPS công khai (Render / Railway / Cloud VPS) để trang `https://<domain>/delete-account` và API Auth/Delete hoạt động thật cho bản MVP `v1.0.0+1`. *(Đã triển khai live qua Railway MCP trên `https://vigorai-production.up.railway.app` + PostgreSQL 18 `Postgres`; deployment `51958d75` `[SUCCESS]`, Alembic migration `0001_initial_schema` & seed `36` món / `30` bài tập / `4` giáo án hoàn tất, Pass 10/10 bài kiểm thử HTTPS E2E)* | `INFRA`, `F26` | `backend/docker-compose.yml`, cấu hình triển khai | Dùng biến môi trường bảo mật; cung cấp URL HTTPS cho `M1`/`M2` đưa vào bản build `.aab`. | Truy cập `https://<domain>/delete-account` và `/healthz` trả `200 OK` qua 4G; Google Reviewer test xóa tài khoản thành công. |

### Thành viên 4 (`M4` – 100% Pure AI Engineer, Python Only)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-01** *(Model B Đợt 1 — Fast Dataset)*: Tải và lọc tập dữ liệu có sẵn từ **Roboflow Universe / Kaggle** cho **15–20 món ăn phổ biến nhất** (cơm trắng, ức gà, trứng, thịt bò, cá hồi, khoai lang, bông cải, chuối, phở, cơm tấm...), chia 70/20/10. | `F19` | `ai_research/model_b_food_yolo/` | Tái sử dụng nhãn có sẵn để rút ngắn thời gian tìm dữ liệu cho bản Production `v1.1.0`. | File `data.yaml` hợp lệ với 15–20 lớp; không có bounding box rỗng/lệch chuẩn YOLO. |
| `[ ]` | **T-M4-02:** Xây dựng bộ sinh dữ liệu tổng hợp Banister Fitness-Fatigue (`~15,000` mẫu chuỗi 7 ngày) với 12 biến đầu vào & nhãn Readiness/Fatigue. | `F20` | `ai_research/model_c_readiness_ml/generate_banister_data.py` | Làm độc lập hoàn toàn bằng Python, không cần đợi dữ liệu thật. | Tập dữ liệu sinh ra phản ánh đúng quy luật sinh lý (thiếu ngủ/thiếu đạm làm chậm hồi phục). |
| `[ ]` | **T-M4-03:** Hoàn thiện `routers/ai.py` stub & `ai_schema.py` (trả JSON Mock chuẩn cho `M1` làm UI Quét món ăn & `M2` làm UI Readiness/Recovery). | `INFRA` | `backend/app/routers/ai.py`, `backend/app/schemas/ai_schema.py` | `M1` và `M2` không phải chờ `M4` train xong mới làm UI. | Gọi 2 endpoint AI trên Swagger `/docs` trả về `200 OK` đúng schema. |
| `[ ]` | **T-M4-04:** Xây dựng logic quy đổi `BBoxAreaRatio` sang gram (`clamp(0.4, 2.5)`) & tra cứu `food_nutrition_catalog` trong `portion_estimator.py` và `ai_food_yolo.py`. | `F19` | `ai_research/model_b_food_yolo/portion_estimator.py`, `backend/app/services/ai_food_yolo.py` | Kiểm thử bằng danh mục JSON dinh dưỡng từ `M3`. | Unit test tính đúng Calo/Protein/Carb/Fat từ danh sách bbox mẫu. |
| `[ ]` | **T-M4-05:** Chạy benchmark baseline 3 thuật toán **XGBoost vs LightGBM vs MLP** trên dữ liệu Banister & viết script đo `MAE`, `RMSE`, `R2`. | `F20` | `ai_research/model_c_readiness_ml/benchmark_models.py` | Độc lập 100% trong `ai_research/`. | Có bảng so sánh 3 thuật toán và biểu đồ sai số ban đầu cho báo cáo. |

---

## 3. Sprint 2 (Tuần 3 – 5): Hoàn thiện App Core, 3D/Logger, AI `v1.0` & Production `v1.1.0` (20 Tasks)

> *(Toàn bộ công việc Sprint 2 diễn ra song song trong lúc bộ đếm **14 ngày Closed Testing** đang chạy trên Google Play Console.)*

### Thành viên 1 (`M1` – Mobile Core, Health, Food/Photo UI & CH Play)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[x]` | **T-M1-08:** Hoàn thiện module **Cân nặng/BMI/5 vòng đo** (Moving Average 7 ngày) & **Lượng nước thông minh** (`35ml × kg` + tự cộng `+500/+750ml` khi có buổi tập Gym, nhắc bằng `WorkManager`). *(Đã fix lỗi compile & bảo toàn mức bù nước buổi tập qua các lần `load()`; `flutter analyze` 0 error/0 warning, Pass 11/11 `health_sprint2_test.dart`)* | `F01`, `F03` | `mobile/lib/features/health/biometrics/`, `mobile/lib/features/health/hydration/` | Lưu cục bộ SQLite Drift, tự đồng bộ ngầm. | Hoàn thành buổi tập 60p RPE 8 $\rightarrow$ mục tiêu nước tự tăng thêm `750 ml`; không dùng `SCHEDULE_EXACT_ALARM`. |
| `[x]` | **T-M1-09:** Hoàn thiện **Nhật ký Calo & Macro** (*Mifflin-St Jeor*, chia 4 bữa, tra từ điển offline), **Giấc ngủ** (nhập tay, sẵn sàng mở rộng Health Connect ở `v1.2.0`) & **Nhắc Supplement** qua `WorkManager` + nút *"Đã uống"*. *(Đã nối tuổi thật từ `birth_date`, giữ goal khi thêm bữa, tự refresh UI khi `resumed` sau khi bấm "Đã uống" & gắn `PENDING_UPDATE` trên `SupplementTakenReceiver`; `flutter analyze` & `health_sprint2_test.dart` Pass 11/11)* | `F04`, `F05`, `F06` | `mobile/lib/features/health/nutrition/`, `mobile/lib/features/health/sleep/`, `mobile/lib/features/health/supplements/` | Chạy Offline-First hoàn toàn. | Công thức BMR/TDEE/Macro chuẩn xác; bấm *"Đã uống"* trên notification cập nhật ngay SQLite. |
| `[~]` | **T-M1-10** *(Nhận từ M4)*: Xây dựng UI **Quét Món ăn AI** (`F19`) gọi `PhotoPickerService` (ảnh `< 300KB`) $\rightarrow$ `POST /api/v1/ai/food-analyze` $\rightarrow$ hiển thị bbox, thanh kéo chỉnh gram, thẻ disclaimer và lưu thẳng vào Nhật ký Calo (`F04`). *(Đã sửa tỷ lệ `AspectRatio` khớp 100% ảnh gốc cho `_FoodBboxPainter` & lưu bền vững ảnh vào `meal_photos/`; giữ `[~]` phụ thuộc `M4` hoàn thiện `T-M4-06` model YOLOv8 thật trên Server)* | `F19`, `F04` | `mobile/lib/features/health/food_scan/` | Test trước với stub `/api/v1/ai/food-analyze` hoặc `mock_m4_ai.json`, nối ngay model thật `v1.0` của `M4` khi xong. | Chụp đĩa cơm $\rightarrow$ chỉnh gram tự tính lại Macro và cộng thẳng vào tổng Calo trong ngày. |
| `[x]` | **T-M1-11** *(Nhận từ M4)*: Xây dựng UI **Nhật ký Ảnh Thể hình Before/After** (`F24` phần ảnh) với Slider kéo so sánh 2 mốc ảnh, dùng `PhotoPickerService.savePrivateProgressPhoto` lưu 100% cục bộ. *(Đã kiểm chứng `flutter analyze` 0 error/0 warning & `flutter test` sạch lỗi trên Flutter SDK)* | `F24` | `mobile/lib/features/health/progress_photos/` | Độc lập hoàn toàn, không dùng quyền đọc Gallery hệ thống. | Ảnh Progress không lộ ra Gallery công cộng; Slider so sánh hoạt động mượt. |
| `[~]` | **T-M1-12:** Hoàn thiện `SyncQueueManager` Push/Pull hai chiều với `M3`, theo dõi đủ **14 ngày Closed Testing (20–25 testers)** & chuẩn bị hồ sơ bấm **Apply for Production (`v1.1.0`)** cuối Tuần 5. *(Đã bổ sung Pull đủ 7 bảng gồm `workout_routines`/`sessions`/`sets`, chống trùng mock ID `bio-*` & giữ `PENDING_UPDATE` khi `localSteps > serverSteps`; giữ `[~]` chờ kiểm thử Offline $\leftrightarrow$ Online với `M3` và đủ 14 ngày Closed Testing `T-M1-07`/`T-M2-06`)* | `INFRA` | `mobile/lib/core/sync/sync_queue_manager.dart`, Google Play Console | Phối hợp `M3` (`T-M3-07`) kiểm thử Offline $\leftrightarrow$ Online. | Dữ liệu tạo khi tắt mạng tự sync sạch khi bật mạng; đủ điều kiện mở khóa Production trên Play Console. |

### Thành viên 2 (`M2` – 3D Blender MCP, Workout, Recovery 3D & Charts)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-07:** Dùng Blender MCP dựng đủ **20–30 bài tập 3D** + Bộ dụng cụ rời (`Barbell`, `Dumbbell`, `Bench`, `Cable`, `Rack`, `Kettlebell`), xuất `.glb` nén Draco lên CDN của `M3`. | `F07`, `F12` | `assets_3d/scripts_blender_mcp/`, `assets_3d/exported_glb/` | Upload lên MinIO/CDN của `M3` (`T-M3-09`). | Toàn bộ file `.glb` đạt `800KB – 2.5MB`, `<= 25,000 tris`, đủ SHA-256 & setup guide. |
| `[ ]` | **T-M2-08:** Hoàn thiện **Bản đồ Giải phẫu Cơ 3D** (`Mat_Muscle_*`: Đỏ/Cam/Vàng/Xám), chuyển đổi `Anim_GoodForm` / `Anim_BadForm` (15+ bài Compound), tốc độ `0.25x–1.0x` + 3 pha & chọn Body Avatar Nam/Nữ. | `F09`, `F10`, `F11`, `F13` | `mobile/lib/features/gym3d/` | Chạy trực tiếp trên `Muscle3DViewerWidget`. | Đổi màu cơ & đổi clip Đúng/Sai mượt mà; tua `0.25x` khớp nhãn hít/thở 3 pha. |
| `[ ]` | **T-M2-09:** Xây dựng **Giáo án tuần** (`PPL`, `Upper-Lower`, `Full Body`, Superset), **Exercise Swapper**, **Live Workout Logger Offline-first**, **1RM (Epley/Brzycki)**, **Visual Plate Calculator** & Kỷ lục **PR / Streak** (tạm dùng timer cục bộ trước khi bật Foreground Service ở `v1.2.0`). | `F14`, `F15`, `F17`, `F18`, `F25` | `mobile/lib/features/workout/` | Lưu SQLite Drift cục bộ 100%. | Tắt app đột ngột giữa buổi tập mở lại khôi phục đủ các hiệp đã tick; Plate Calculator vẽ đúng từng bánh tạ. |
| `[ ]` | **T-M2-10** *(Nhận từ M4)*: Xây dựng màn hình **AI Readiness Dashboard & Bản đồ Phục hồi Cơ bắp 3D** (`F20`, `F23`) nhúng trực tiếp `Muscle3DViewerWidget` (Gradient Xanh `#43A047` / Cam `#FB8C00` / Đỏ `#E53935` + `onMuscleTap` pop-up % hồi phục) và gắn thẻ gợi ý mức tạ/cảnh báo Deload (`F21`) ngay trong Live Logger. | `F20`, `F21`, `F23` | `mobile/lib/features/ai_analytics/readiness_3d/`, `mobile/lib/features/workout/logger/` | Test bằng `mock_m4_ai.json` hoặc AI stub `M4`, tự nhận data thật từ `/api/v1/ai/readiness-and-overload`. | Chạm từng bó cơ trên Mannequin 3D hiện đúng % hồi phục; thẻ gợi ý tạ hiển thị kèm disclaimer y tế. |
| `[ ]` | **T-M2-11** *(Nhận từ M4)*: Xây dựng màn hình **Thống kê Tiến độ Volume Load** (`F22`) & **Biểu đồ Radar Cân bằng 6 Nhóm cơ** (`F24` phần Radar) đọc từ SQLite/Analytics API. | `F22`, `F24` | `mobile/lib/features/ai_analytics/{volume_analytics,muscle_balance}/` | Đọc trực tiếp từ bảng `workout_sessions` & `workout_sets`. | Tổng hợp biểu đồ 1.000 hiệp tập `< 300ms` ngay cả khi offline. |
| `[ ]` | **T-M2-12** *(Mốc 2 CH Play)*: Bật tính năng thật qua `FeatureFlags`, tối ưu ASO tiêu đề/mô tả (*"VigorAI: Tập Gym 3D & Tính Calo"*), build **`.aab` bản `v1.1.0`** (chưa bật Health Connect để duyệt Production nhanh) đẩy lên Closed Testing ngày 10–12 và xin duyệt **Production**. | `INFRA` | `mobile/android/`, Play Console Release | Tách Health Connect sang `v1.2.0` giúp Production mở khóa nhanh để chạy 1.000 downloads ngay Tuần 6. | Bản `v1.1.0` vượt kiểm duyệt và lên kệ Production CH Play. |

### Thành viên 3 (`M3` – Backend FastAPI, PostgreSQL & Cloud Deploy)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[x]` | **T-M3-07:** Xây dựng Engine Đồng bộ hai chiều `POST /api/v1/sync/push` & `GET /api/v1/sync/pull` (Batch Transaction, LWW theo `updated_at` UTC, `max(steps_count)`). | `INFRA` | `backend/app/routers/sync.py`, `backend/app/services/sync_service.py` | Test giả lập 2 thiết bị sync cùng lúc. | Xử lý Idempotent an toàn khi gửi trùng lô sync; không mất bước chân. |
| `[x]` | **T-M3-08:** Hoàn thiện nhóm API Sức khỏe (`/api/v1/health/biometrics`, `/daily/{date}`, `/meals`, `/supplements`, tra cứu `food_nutrition_catalog`). | `F01`–`F06` | `backend/app/routers/health.py` | Ưu tiên xong Tuần 3–4 để `M1` ghép nối. | Tất cả CRUD + Filter ngày hoạt động đúng trên Swagger & Pytest. |
| `[~]` | **T-M3-09:** Hoàn thiện API Kho bài tập 3D (`/api/v1/exercises`, `/exercises/{code}/alternatives`) & dịch vụ MinIO/CDN lưu `.glb` kèm SHA-256. *(API & 3 bài MVP `assets/3d_bundled/*.glb` đã hoàn thiện và Pass Pytest; giữ `[~]` chờ `M2` hoàn thành `T-M2-07` để upload 27 file `.glb` mở rộng lên MinIO/CDN)* | `F07`–`F12`, `F25` | `backend/app/routers/exercises.py`, `backend/app/services/storage_service.py` | Nhận `.glb` của `M2` đưa lên bucket công khai. | API trả URL `.glb`, mảng `primary_muscles` và top 5 bài thay thế cùng nhóm cơ. |
| `[x]` | **T-M3-10:** Hoàn thiện API Giáo án & Buổi tập (`/api/v1/routines`, `/api/v1/workouts/sessions`), tự tính `total_volume_kg` & cập nhật `is_pr`. | `F14`–`F18` | `backend/app/routers/routines.py`, `backend/app/routers/workouts.py` | Dùng seed data test trước khi `M2` ghép. | Lưu phiên 20 hiệp `< 100ms`; tự động đánh dấu kỷ lục PR chính xác. |
| `[x]` | **T-M3-11:** Xây dựng API Tổng hợp Tiến độ `/api/v1/analytics/summary` (Volume tuần/tháng, Radar 6 nhóm cơ, Bảng PR). | `F22`, `F24`, `F25` | `backend/app/routers/analytics.py`, `backend/app/services/analytics_service.py` | Phối hợp `M2` để khớp định dạng dữ liệu vẽ biểu đồ. | Truy vấn tổng hợp 90 ngày chạy `< 150ms` nhờ Index PostgreSQL. |

### Thành viên 4 (`M4` – 100% Pure AI Engineer, Python Only)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-06** *(Model B Đợt 1 — Lên kệ v1.1.0)*: Huấn luyện **AI Model B `v1.0` (YOLOv8s)** trên tập 15–20 món cốt lõi & triển khai ngay vào `ai_food_yolo.py` (`POST /api/v1/ai/food-analyze`) trên Server. | `F19` | `ai_research/model_b_food_yolo/train_yolo.py`, `backend/app/services/ai_food_yolo.py`, `backend/app/routers/ai.py`, `backend/ai_models/` | Đẩy weight `v1.0` lên FastAPI để bản Production `v1.1.0` có AI quét món ăn chạy thật ngay. | Thời gian suy luận `< 150ms/ảnh`, API end-to-end `< 3.0s`, nhận diện chuẩn 15–20 món cốt lõi. |
| `[ ]` | **T-M4-07:** Huấn luyện & chọn mô hình tốt nhất cho **AI Model C (XGBoost / LightGBM / MLP)** đạt KPI (`MAE <= 4.5`, `RMSE <= 6.2`, `R2 >= 0.88`) kèm logic Overtraining/Deload & Fallback user mới (`< 3 ngày`). | `F20`, `F21` | `ai_research/model_c_readiness_ml/train_readiness.py`, `backend/app/services/ai_readiness_ml.py`, `backend/ai_models/` | Train trên dữ liệu Banister + seed 30 ngày của `M3`. | Đạt KPI trên tập Test; user mới không bị lỗi 500 mà trả Readiness mặc định `85.0`. |
| `[ ]` | **T-M4-08:** Phối hợp cùng `M3` hoàn thiện `feature_extractor.py` trích xuất 12 đặc trưng từ PostgreSQL 72h–28 ngày, lưu `ai_readiness_logs` & nối vào `GET /api/v1/ai/readiness-and-overload`. | `F20`, `F21` | `backend/app/services/feature_extractor.py`, `backend/app/routers/ai.py` | Chạy test trực tiếp trên PostgreSQL Staging. | Thời gian trích xuất 12 đặc trưng `< 60ms`; API phản hồi `< 500ms`. |
| `[ ]` | **T-M4-09** *(Model B Đợt 2 — Mở rộng Dataset)*: Thu thập thêm ảnh tự chụp thực tế & gán nhãn mở rộng tập dữ liệu từ 15–20 món lên **35–50 món ăn Việt & đồ Gym**. | `F19` | `ai_research/model_b_food_yolo/` | Trong khi bản `v1.1.0` chạy Production với `v1.0`, `M4` thong thả hoàn thiện dataset chuẩn cho đồ án. | Dataset mở rộng đạt `~5,000–8,000 ảnh` sạch nhãn, phân bố đều 35–50 món. |

---

## 4. Sprint 3 (Tuần 6 – 8): Bật Health Connect (`v1.2.0`), AI `v1.2` & Chiến dịch 1.000 Downloads (11 Tasks)

### Thành viên 1 (`M1` – Mobile Core, Health, Food/Photo UI & CH Play)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-13:** Bật lại quyền **Android Health Connect** (`READ_STEPS`, `READ_SLEEP`, `READ_ACTIVE_CALORIES_BURNED`) trong `AndroidManifest.xml`, hoàn thiện `health_connect_bridge.dart` + Pedometer dự phòng + quay video chứng minh nộp Form Health Connect cho bản `v1.2.0`. | `F02`, `F05`, `F26` | `mobile/android/app/src/main/AndroidManifest.xml`, `mobile/lib/core/platform/health_connect_bridge.dart`, `mobile/lib/features/health/{steps,sleep}/` | Không làm gián đoạn link Production `v1.1.0` đang chạy chiến dịch tải. | Đọc chuẩn bước chân/giấc ngủ từ Health Connect với độ lệch `< 2%`; nộp đủ video xét duyệt. |
| `[ ]` | **T-M1-14:** Hoàn thiện **Trung tâm Quyền riêng tư** đầy đủ (`F26`): nút Xuất dữ liệu JSON (`/users/me/export`), công tắc ngắt kết nối Health Connect & kiểm tra dọn sạch SQLite + `progress_photos/` + 3D cache khi Xóa tài khoản. | `F26` | `mobile/lib/features/auth_privacy/privacy_center/` | Phối hợp `M3` xác nhận xóa sạch Object Storage. | Xóa tài khoản xong ổ đĩa không còn ảnh progress hay dữ liệu SQLite. |
| `[ ]` | **T-M1-15:** Điều phối **Chiến dịch 1.000 lượt tải** trên bản Production `v1.1.0` (Cộng đồng Trường/Khoa + TikTok/Reels 15–30s + dự phòng Google App Campaign nếu cần). | `INFRA` | Truyền thông & Play Console Analytics | Chạy song song từ Tuần 6 ngay khi `v1.1.0` lên Production. | Cán mốc `>= 1.000` lượt tải thật hiển thị trên Play Console trước Tuần 10. |

### Thành viên 2 (`M2` – 3D Blender MCP, Workout, Recovery 3D & Charts)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-13:** Bật `FOREGROUND_SERVICE_HEALTH` và hoàn thiện **Smart Rest Timer** chạy Android Foreground Service + Notification đếm ngược (`+15s/-15s/Skip`) ổn định khi tắt màn hình 3 phút. | `F16` | `mobile/lib/features/workout/timer/`, `mobile/android/app/src/main/kotlin/` | Tích hợp vào bản cập nhật `v1.2.0` cùng Health Connect của `M1`. | Khóa màn hình 3 phút đồng hồ nghỉ vẫn đếm chuẩn và rung/chuông báo hết giờ. |
| `[ ]` | **T-M2-14:** Tối ưu hiệu năng WebGL/3D Viewer (`>= 45 FPS`, giải phóng context/texture khi rời màn hình, kiểm tra rò rỉ bộ nhớ trên máy 4GB RAM). | `F07`–`F13`, `F23` | `mobile/lib/features/gym3d/` | Đo bằng Flutter DevTools Memory & Frame Chart. | Mở/đóng màn hình 3D 20 lần liên tiếp không tràn RAM (OOM). |
| `[ ]` | **T-M2-15** *(Mốc 3 CH Play)*: Build và phát hành bản cập nhật **`.aab` `v1.2.0`** (Full 26 chức năng gồm Health Connect + Foreground Rest Timer) lên Production Play Console. | `INFRA` | `mobile/android/`, Play Console Release | Cập nhật đè lên app đang có sẵn 1.000 lượt tải. | Bản `v1.2.0` được duyệt cập nhật trên Google Play Store thành công. |

### Thành viên 3 (`M3` – Backend FastAPI, PostgreSQL & Cloud Deploy)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-12:** Gia cố bảo mật Production (Rate Limiting cho endpoint upload ảnh AI, Cascade Delete xóa sạch ảnh món ăn trên Object Storage khi gọi `DELETE /users/me`, tối ưu index truy vấn). | `F26` | `backend/app/core/security.py`, `backend/app/services/storage_service.py` | Độc lập trên Backend. | Gửi dồn request AI vượt ngưỡng trả `429`; xóa user xóa sạch ảnh trên bucket S3/MinIO. |
| `[ ]` | **T-M3-13:** Cấu hình Backup tự động PostgreSQL & giám sát log/hiệu năng Server trong đợt tăng trưởng 1.000 users tải app. | `INFRA` | Hạ tầng Server & Database | Theo dõi tài nguyên CPU/RAM khi `M4` cập nhật model `v1.2`. | Server hoạt động ổn định, không rớt kết nối trong thời gian chiến dịch. |

### Thành viên 4 (`M4` – 100% Pure AI Engineer, Python Only)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-10** *(Model B Đợt 2 — Nâng cấp Server)*: Fine-tune **AI Model B `v1.2` (YOLOv8s/m)** trên 35–50 món đạt KPI (`mAP@0.5 >= 0.80`, `Precision >= 0.82`, `Recall >= 0.78`) và cập nhật thẳng weight lên FastAPI Server. | `F19` | `ai_research/model_b_food_yolo/train_yolo.py`, `backend/ai_models/model_b_manifest.json` | Cập nhật nóng trên Server, Mobile app đang trên CH Play tự động thông minh hơn mà không cần build lại `.aab`. | Đạt KPI trên tập Test; thời gian suy luận giữ `< 150ms/ảnh`. |
| `[ ]` | **T-M4-11:** Chạy kiểm thử chéo thực tế (Human-in-the-loop trên ảnh bữa ăn thật & nhật ký tập luyện của 4 thành viên), hiệu chỉnh tham số `clamp` khẩu phần và độ phân rã Banister. | `F19`, `F20` | `ai_research/` | Thu thập phản hồi trực tiếp từ bản Production của nhóm. | Sai số ước tính khẩu phần và điểm sẵn sàng khớp sát cảm nhận RPE thực tế. |
| `[ ]` | **T-M4-12:** Xuất đầy đủ **Confusion Matrix**, biểu đồ **Loss/mAP**, **Feature Importance**, **MAE/RMSE/R2** vào `ai_research/evaluation_reports/` phục vụ quyển báo cáo đồ án. | `F19`, `F20` | `ai_research/evaluation_reports/` | Độc lập hoàn toàn trong `ai_research/`. | Đủ số liệu so sánh trước/sau (Đợt 1 vs Đợt 2 và XGBoost vs LightGBM vs MLP). |

---

## 5. Sprint 4 (Tuần 9 – 10): Kiểm thử Tự động, Tối ưu Đóng gói Cuối & Bảo vệ Đồ án (8 Tasks)

### Thành viên 1 (`M1` – Mobile Core, Health, Food/Photo UI & CH Play)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M1-16:** Viết **Unit Test** công thức (`BMI`, `BMR Mifflin-St Jeor`, `TDEE`, `Smart Hydration`) & **Integration Test** luồng Đăng ký $\rightarrow$ Sync $\rightarrow$ Xóa tài khoản. | `INFRA` | `mobile/test/health/` | Chạy tự động qua `flutter test test/health/`. | Pass 100%, độ phủ logic công thức đạt `>= 90%`. |
| `[ ]` | **T-M1-17:** Rà soát lần cuối **Merged AndroidManifest.xml** của bản `v1.2.0` (0 quyền cấm) & đồng bộ hồ sơ **Data Safety** + **Health Apps Declaration** trên Play Console. | `F26` | `mobile/android/app/src/main/AndroidManifest.xml`, `docs/chplay_submission_checklist.md` | Đối chiếu 1-1 giữa khai báo Play Console và code thực tế. | Không chứa quyền cấm; hồ sơ Play Console khớp 100% hành vi App. |

### Thành viên 2 (`M2` – 3D Blender MCP, Workout, Recovery 3D & Charts)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M2-16:** Viết **Unit Test** cho thuật toán tính **1RM (Epley/Brzycki)**, tính **Total Volume** & **Barbell Plate Calculator**. | `F17`, `F18` | `mobile/test/workout/` | Chạy độc lập qua `flutter test test/workout/`. | Pass 100% cho mọi trường hợp biên (1 rep, 15 reps, tạ lẻ không chia chẵn `1.25kg`). |
| `[ ]` | **T-M2-17:** Xác minh file `.aab` bản cuối (`< 40 MB`, 64-bit `arm64-v8a`/`x86_64`, **16 KB page size ELF alignment**), test thực địa Airplane Mode tại phòng Gym & hoàn thiện Video/Screenshot bảo vệ. | `INFRA` | `mobile/android/`, Store & Demo Assets | Kiểm tra từ bản Release cài qua `bundletool` / Play Store. | Đạt đủ tiêu chuẩn Android 15+, quay trọn vẹn video demo 26 chức năng. |

### Thành viên 3 (`M3` – Backend FastAPI, PostgreSQL & Cloud Deploy)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M3-14:** Viết **Pytest** toàn diện cho API Core (`Auth`, `Sync LWW`, `Health`, `Workouts`, `Delete Account trả 401`) & Load Test API với Locust/k6. | `INFRA` | `backend/tests/test_core_api.py` | Chạy trên Docker Test Database riêng biệt. | `pytest` Pass 100%; chịu tải tối thiểu 50 người dùng đồng thời không lỗi `5xx`. |
| `[ ]` | **T-M3-15:** Kiểm tra bảo mật Production cuối kỳ & xác nhận URL công khai `GET /delete-account` ổn định 24/7. | `F26` | Cấu hình vận hành Server | Xác nhận truy cập công khai từ mạng ngoài. | URL `/delete-account` trả HTTP `200 OK` qua HTTPS ổn định. |

### Thành viên 4 (`M4` – 100% Pure AI Engineer, Python Only)

| Trạng thái | Mã Task & Công việc | Mã `Fxx` | Phạm vi File (File Scope) | Chiến lược Song song (Mock / Unblock) | Tiêu chí Nghiệm thu (Definition of Done) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `[ ]` | **T-M4-13:** Viết **Pytest** cho 2 API AI (`food-analyze` ảnh hợp lệ / không có đồ ăn / file lỗi; `readiness-and-overload` user mới `< 3 ngày` & đủ dữ liệu; kiểm tra trường `disclaimer`). | `F19`, `F20` | `backend/tests/test_ai_api.py` | Chạy độc lập không chạm `test_core_api.py` của `M3`. | `pytest backend/tests/test_ai_api.py` Pass 100%; mọi phản hồi AI có `disclaimer`. |
| `[ ]` | **T-M4-14:** Hoàn thiện chương **Nghiên cứu & Đánh giá Mô hình AI** trong tài liệu báo cáo đồ án + chuẩn bị kịch bản demo live AI Inference trước hội đồng. | `INFRA` | `ai_research/evaluation_reports/` | Không phụ thuộc Mobile UI. | Hoàn chỉnh số liệu khoa học Model B (`v1.0` vs `v1.2`) & Model C (XGBoost/LightGBM/MLP). |

---

## 6. Checklist Kiểm tra Trước khi Bảo vệ Đồ án & Chốt CH Play (Pre-Release Verification Board)

- [ ] **Zero-Conflict Git Check:** Toàn bộ nhánh cá nhân (`M1`–`M4`) đã merge sạch vào `develop` và `main`; `M4` hoàn toàn độc lập ở Backend/AI Python không xung đột Flutter.
- [ ] **Đủ 26 Chức năng (`F01`–`F26`):** Chạy ổn định trên bản Production `v1.2.0` (tải trực tiếp từ Google Play Store).
- [ ] **Quyền Android (`AndroidManifest.xml`):** Merged Manifest **không chứa** `READ_MEDIA_IMAGES`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `SCHEDULE_EXACT_ALARM`, `USE_EXACT_ALARM`, `ACCESS_BACKGROUND_LOCATION`.
- [ ] **Xóa Tài khoản 2 kênh (`F26`):** Nút xóa trong App hoạt động sạch sẽ (kèm xóa SQLite/ảnh cục bộ) VÀ đường dẫn web công khai `/delete-account` hoạt động bình thường.
- [ ] **Miễn trừ Y tế & Nguồn Khoa học:** Onboarding, Dinh dưỡng (*Mifflin-St Jeor*), 1RM (*Epley/Brzycki*) và kết quả AI đều hiển thị rõ thông báo miễn trừ y khoa.
- [ ] **Đóng gói `.aab` & Lượt tải:** `targetSdkVersion = 35`, `minSdkVersion = 26`, `.aab < 40 MB`, chuẩn 64-bit + **16 KB page size alignment**, hoàn thành mục tiêu lượt tải trên Google Play Console.
