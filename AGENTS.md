# AGENTS.md — Quy chuẩn Vận hành & Phối hợp Team 4 Người

> **Dự án:** VigorAI (`VigorAI: 3D Gym & Health Log` — Ứng dụng Quản lý Sức khỏe & Luyện tập Gym 3D kết hợp Trí tuệ Nhân tạo)
> **Tài liệu nguồn (Single Source of Truth):**
> - Đặc tả thiết kế hệ thống (26 chức năng, ERD, AI, 3D, CH Play): [docs/system-design-spec.md](./docs/system-design-spec.md)
> - Lộ trình 10 tuần & Phân quyền Monorepo: [docs/roadmap.md](./docs/roadmap.md)
> - Bảng phân công & Tiến độ 64 tasks: [docs/taskboard.md](./docs/taskboard.md)
> - Nhật ký bàn giao các phiên làm việc: [session_log.md](./session_log.md)

Mọi AI Coding Agent và thành viên trong nhóm **BẮT BUỘC** đọc và tuân thủ các quy tắc dưới đây trước khi chỉnh sửa bất kỳ dòng code nào.

---

## 1. Quy trình Đầu & Cuối mỗi Phiên làm việc (Session Protocol)

1. **Đầu phiên:**
   - Đọc 20–40 dòng gần nhất của [session_log.md](./session_log.md) để nắm bối cảnh dự án.
   - Kiểm tra [docs/taskboard.md](./docs/taskboard.md) xem thành viên đang làm việc (`M1`, `M2`, `M3`, hay `M4`) sở hữu mã Task nào (`T-Mx-xx`).
2. **Trong phiên:**
   - Chỉ tạo/sửa file nằm trong phạm vi `[OWNER]` của thành viên đó (xem Mục 2).
   - Nếu cần thêm package hoặc sửa file `[LOCKED STUB]`, phải báo trước cho người dùng và thực hiện dưới dạng Micro-PR riêng, không gộp lẫn vào task tính năng.
3. **Cuối phiên:**
   - Cập nhật trạng thái `[x]` trong [docs/taskboard.md](./docs/taskboard.md) nếu Task đã đạt Definition of Done.
   - Ghi nối tiếp một mục mới vào cuối [session_log.md](./session_log.md) gồm: Ngày giờ, Thành viên, Mã Task, Danh sách file đã chạm, Quyết định kỹ thuật và Bước tiếp theo.

---

## 2. Luật Phân vùng Sở hữu Chống Xung đột Git (Strict Ownership Rules)

| Thành viên | Vai trò | Thư mục / File được phép sửa (`[OWNER]`) |
| :--- | :--- | :--- |
| **M1** | Mobile Core & Health (Flutter) | `mobile/android/app/src/main/AndroidManifest.xml`, `mobile/lib/core/theme/`, `mobile/lib/core/network/`, `mobile/lib/core/platform/`, `mobile/lib/core/sync/`, `mobile/lib/core/database/health_tables.drift.dart`, `mobile/lib/core/router/health_routes.dart`, `mobile/lib/features/auth_privacy/`, `mobile/lib/features/health/`, `mobile/assets/mock_json/mock_m1_health.json`, `mobile/test/health/` |
| **M2** | 3D Blender MCP & Gym Execution | `assets_3d/`, `mobile/assets/3d_bundled/`, `mobile/lib/core/database/workout_tables.drift.dart`, `mobile/lib/core/router/gym3d_workout_routes.dart`, `mobile/lib/features/gym3d/`, `mobile/lib/features/workout/`, `mobile/assets/mock_json/mock_m2_exercises.json`, `mobile/test/workout/` |
| **M3** | Backend FastAPI & PostgreSQL | `backend/docker-compose.yml`, `backend/alembic/`, `backend/app/core/`, `backend/app/db/`, `backend/app/models/`, `backend/app/templates/`, `backend/app/schemas/core_schemas.py`, `backend/app/services/{auth_service,sync_service,storage_service,analytics_service}.py`, `backend/app/routers/{auth,users,sync,health,exercises,routines,workouts,analytics}.py`, `backend/tests/test_core_api.py` |
| **M4** | AI Engineer & Data Analytics | `ai_research/`, `backend/ai_models/`, `backend/app/schemas/ai_schema.py`, `backend/app/services/{feature_extractor,ai_food_yolo,ai_readiness_ml}.py`, `backend/app/routers/ai.py`, `backend/tests/test_ai_api.py`, `mobile/lib/core/database/ai_cache_tables.drift.dart`, `mobile/lib/core/router/ai_analytics_routes.dart`, `mobile/lib/features/ai_analytics/`, `mobile/assets/mock_json/mock_m4_ai.json` |

### Các File Khóa Giao diện (`[LOCKED STUB]`) — Không tự ý sửa đổi
- `mobile/pubspec.yaml`, `mobile/lib/main.dart`, `mobile/lib/core/database/app_database.dart`, `mobile/lib/core/router/app_router.dart`
- `backend/requirements.txt`, `backend/app/main.py`
- `.gitignore`

**Giao ước dùng chung giữa các thành viên (Không sửa code của nhau):**
- `M4` dùng `Muscle3DViewerWidget` tại `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart` của `M2` qua import cho màn hình `F23`.
- `M4` dùng `PhotoPickerService` tại `mobile/lib/core/platform/photo_picker_service.dart` của `M1` qua import cho `F19` và `F24`.

---

## 3. Luật Sắt Tuân thủ Google Play Store (CH Play Policy Guardrails)

Mọi Agent **TUYỆT ĐỐI KHÔNG** vi phạm các ràng buộc dưới đây:
1. **Quyền Android Cấm dùng:** Không thêm `READ_MEDIA_IMAGES`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `SCHEDULE_EXACT_ALARM`, `USE_EXACT_ALARM`, `ACCESS_BACKGROUND_LOCATION`, `QUERY_ALL_PACKAGES` vào `AndroidManifest.xml` hoặc thư viện kéo quyền này ngầm.
2. **Lấy ảnh & Sức khỏe:**
   - Chọn/chụp ảnh món ăn (`F19`) và ảnh tiến độ cơ thể (`F24`) chỉ dùng **Android Photo Picker API** (`image_picker` / `PhotoPickerService`).
   - Ảnh Before/After (`F24`) mặc định lưu **100% cục bộ** trong `getApplicationDocumentsDirectory()/progress_photos/`, không lưu vào Gallery công cộng.
   - Đếm bước chân/giấc ngủ dùng **Android Health Connect** (`READ_STEPS`, `READ_SLEEP`, `READ_ACTIVE_CALORIES_BURNED`) và `ACTIVITY_RECOGNITION` xin đúng lúc bật tính năng.
   - Nhắc uống nước (`F03`) và Supplement (`F06`) dùng `WorkManager` / Inexact Alarms.
   - Đồng hồ nghỉ giữa hiệp (`F16`) chạy `FOREGROUND_SERVICE_HEALTH`.
3. **Miễn trừ Y tế (Medical Disclaimer):** Bắt buộc giữ xác nhận ở Onboarding (`F26`), hiển thị trích dẫn công thức (`Mifflin-St Jeor` cho BMR/TDEE, `Epley/Brzycki` cho 1RM) và dòng disclaimer dưới kết quả AI Model B & C.
4. **Xóa Tài khoản 2 kênh:** Phải duy trì cả API `DELETE /api/v1/users/me` (xóa Cascade DB + Object Storage + dữ liệu cục bộ) và trang HTML công khai `GET /delete-account`.
5. **Đóng gói `.aab`:** `minSdk = 26`, `targetSdk = 35` (Android 15), 64-bit (`arm64-v8a`, `x86_64`), hỗ trợ **16 KB page size alignment**, kích thước cài gốc **`< 40 MB`** (tách file 3D `.glb` mở rộng lên CDN).

---

## 4. Chuẩn hóa Kỹ thuật 3D (Blender MCP) & AI Contracts

### 4.1. Tên 11 Mesh & Material Cơ bắp Bắt buộc (`base_mannequin.glb`)
Mọi script Blender MCP, JSON của Backend (`exercises`), đầu ra của AI Model C (`muscle_fatigue_map`) và JS Bridge của Flutter **bắt buộc dùng chính xác** 11 định danh sau:
- `Mesh_Muscle_Chest` / `Mat_Muscle_Chest`
- `Mesh_Muscle_Shoulders` / `Mat_Muscle_Shoulders`
- `Mesh_Muscle_Biceps` / `Mat_Muscle_Biceps`
- `Mesh_Muscle_Triceps` / `Mat_Muscle_Triceps`
- `Mesh_Muscle_Back_Lats` / `Mat_Muscle_Back_Lats`
- `Mesh_Muscle_Traps` / `Mat_Muscle_Traps`
- `Mesh_Muscle_Abs_Core` / `Mat_Muscle_Abs_Core`
- `Mesh_Muscle_Glutes` / `Mat_Muscle_Glutes`
- `Mesh_Muscle_Quads` / `Mat_Muscle_Quads`
- `Mesh_Muscle_Hamstrings` / `Mat_Muscle_Hamstrings`
- `Mesh_Muscle_Calves` / `Mat_Muscle_Calves`

**Chuẩn Animation & Export:** Bộ xương `Armature_GymHuman`; Sockets `Socket_Hand_L`, `Socket_Hand_R`, `Socket_Back_Barbell`, `Floor_Origin`; Clips `Anim_GoodForm`, `Anim_BadForm`; Polycount `<= 25,000 triangles`; bật nén Draco (`800 KB – 2.5 MB`/bài tập).

### 4.2. Chuẩn Hợp đồng AI (Model B & Model C)
- **Model B (`POST /api/v1/ai/food-analyze`):** Nhận ảnh `< 300 KB`, chạy YOLOv8s/m, trả về `detected_items` (`class_code`, `bbox_norm`, `estimated_grams`, `calories`, `protein_g`, `carbs_g`, `fat_g`), `total_nutrition` và `disclaimer`.
- **Model C (`GET /api/v1/ai/readiness-and-overload`):** Dùng 12 đặc trưng (Banister + 72h/28d logs), trả về `readiness_score` (`0–100`), `readiness_level`, `muscle_fatigue_map` (11 khóa `Mat_Muscle_*` giá trị `0.0–1.0`), `weight_recommendations` và `disclaimer` (kèm Fallback cho user mới `< 3 ngày`).
