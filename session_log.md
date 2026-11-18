# Nhật ký Phiên làm việc (Session Log)

> File này ghi lại lịch sử các phiên làm việc để chống trôi ngữ cảnh khi chuyển ngày hoặc đổi người/AI Agent hỗ trợ.
> **Quy ước:** Mỗi khi kết thúc một phiên làm việc, thêm mục mới lên **trên cùng** (mới nhất ở trên) hoặc theo thứ tự thời gian rõ ràng kèm Mã Task (`T-Mx-xx`) đã thực hiện.

---

### Mẫu ghi chép cho Phiên tiếp theo (Copy mẫu này khi bắt đầu ghi)
```markdown
## Phiên XX — YYYY-MM-DD HH:mm | Thành viên: M? | Task: T-M?-??
- **Mục tiêu phiên:** ...
- **Những file đã tạo / chỉnh sửa:** ...
- **Quyết định kỹ thuật / Lưu ý quan trọng:** ...
- **Kiểm tra / Kết quả chạy thử:** ...
- **Việc cần làm ở phiên kế tiếp:** ...
```

---

## Phiên 06 — 2026-11-18 16:04 | Thành viên: M1 | Task: Cài đặt Flutter SDK & Kiểm tra `flutter pub get` / `flutter analyze`
- **Mục tiêu phiên:** Cài đặt Flutter SDK (`stable`) vào máy và chạy kiểm chứng mã nguồn `mobile/`.
- **Những thay đổi đã thực hiện:**
  - Cài đặt **Flutter 3.50.0 (channel stable)** & **Dart 3.14.0** tại `C:\Users\tranh\flutter` và thêm `C:\Users\tranh\flutter\bin` vào User `PATH`.
  - Sửa lỗi cú pháp `_ = source;` trong `mobile/lib/core/platform/photo_picker_service.dart` và cập nhật `value:` $\rightarrow$ `initialValue:` trong `mobile/lib/features/auth_privacy/presentation/register_screen.dart` do `flutter analyze` phát hiện.
  - Cập nhật trạng thái kiểm chứng trong `docs/taskboard.md`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter pub get`: Thành công (tải 152 packages).
  - `dart run build_runner build --delete-conflicting-outputs`: Chạy xong trong 64s (49 outputs); ghi nhận cảnh báo cần bỏ comment `part 'app_database.g.dart';` trong `[LOCKED STUB]` `app_database.dart` khi nhóm kích hoạt Drift generated class.
  - `flutter analyze --no-fatal-infos`: Exit code `0` (0 error, 0 warning; chỉ còn 9 info deprecation của `package:flutter/material.dart` trên Flutter 3.50.0).
  - `flutter doctor`: Flutter & Chrome OK; máy chưa cài Android Studio / Android SDK (`Unable to locate Android SDK`).
- **Việc cần làm ở phiên kế tiếp:**
  - Cài đặt **Android Studio + Android SDK (API 35 & NDK 27)** để chạy `flutter run --dart-define=USE_MOCK_API=true` trên máy ảo Android.

---

## Phiên 05 — 2026-11-18 15:52 | Thành viên: M1 (Mobile Core & Health) | Task: `T-M1-01`, `T-M1-02`, `T-M1-03`, `T-M1-04`, `T-M1-05`
- **Mục tiêu phiên:** Triển khai toàn bộ 5 tasks của Thành viên M1 trong Sprint 1 (`T-M1-01` đến `T-M1-05`) tuân thủ ranh giới `[OWNER: M1]` và không chỉnh sửa `[LOCKED STUB]`.
- **Những file đã tạo / chỉnh sửa:**
  - Core (`T-M1-01`): `mobile/lib/core/theme/app_theme.dart`, `mobile/lib/core/network/dio_client.dart` (tích hợp `AuthInterceptor` + `MockApiInterceptor` + `FlutterSecureStorage`), `mobile/lib/core/router/health_routes.dart` (`/onboarding`, `/login`, `/register`, `/health`).
  - Android & CH Play (`T-M1-02`): `mobile/android/app/src/main/AndroidManifest.xml` (bổ sung `ViewPermissionUsageActivity`), `mobile/android/app/build.gradle.kts` (`com.vigorai.app`, `minSdk = 26`, `targetSdk = 35`, NDK `27.0.12077973`, `arm64-v8a` & `x86_64`, `max-page-size=16384`, `useLegacyPackaging = false`, R8 minify), `mobile/android/settings.gradle.kts`, `mobile/android/gradle.properties`.
  - DB & Platform (`T-M1-03`): `mobile/lib/core/database/health_tables.drift.dart` (bổ sung Domain Models, công thức BMI WHO Châu Á, nước thông minh, Mifflin-St Jeor), `mobile/lib/core/platform/photo_picker_service.dart` (kiểm tra `< 300 KB`, lưu riêng tư tại `getApplicationDocumentsDirectory()/progress_photos/`, hàm xóa sạch).
  - Auth & Medical Disclaimer (`T-M1-04` / `F26`): `mobile/lib/features/auth_privacy/data/auth_repository.dart`, `mobile/lib/features/auth_privacy/presentation/auth_controller.dart`, `onboarding_disclaimer_screen.dart`, `login_screen.dart`, `register_screen.dart`.
  - Mock Data & Health Dashboard (`T-M1-05`): `mobile/assets/mock_json/mock_m1_health.json`, `mobile/assets/mock_json/mock_m1.json`, `mobile/lib/features/health/data/health_repository.dart`, `mobile/lib/features/health/presentation/health_dashboard_screen.dart`.
  - Quản lý tiến độ: `docs/taskboard.md` (`T-M1-02` đạt `[x]`, `T-M1-01`/`03`/`04`/`05` ở trạng thái `[~]` code xong chờ Flutter SDK chạy build/run).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Giữ nguyên `[LOCKED STUB]` (`pubspec.yaml`, `main.dart`, `app_database.dart`, `app_router.dart`) để tránh conflict với `M2`/`M3`/`M4`.
  - Sửa tên kiểu cột `FloatColumn` thành `RealColumn` (kiểu chuẩn của Drift) trong `health_tables.drift.dart`.
- **Kiểm tra / Kết quả chạy thử:**
  - Đã kiểm tra JSON hợp lệ (`mock_m1_health.json`, `mock_m1.json`), kiểm tra XML `AndroidManifest.xml` (đủ Health Connect & chặn 6 quyền cấm bằng `tools:node="remove"`), và kiểm tra `build.gradle.kts` (`minSdk=26`, `targetSdk=35`, 16KB page size, 64-bit).
  - Máy hiện tại chưa có `flutter`/`dart` trong `PATH` nên chưa chạy `flutter pub get`, `build_runner`, `flutter analyze` và `flutter run`.
- **Việc cần làm ở phiên kế tiếp:**
  - Trên máy có cài Flutter SDK: chạy `cd mobile && flutter pub get && dart run build_runner build && flutter analyze && flutter run --dart-define=USE_MOCK_API=true` để nghiệm thu đóng `[x]` cho `T-M1-01`, `T-M1-03`, `T-M1-04`, `T-M1-05`.
  - Sau khi xong Sprint 1, M1 chuyển sang Sprint 2 (`T-M1-06` – `T-M1-11`).

---

## Phiên 04 — 2026-11-18 15:16 | Thành viên: Toàn nhóm (Tài liệu gốc) | Task: Tạo `README.md` dự án VigorAI
- **Mục tiêu phiên:** Thiết kế file `README.md` tại thư mục gốc cho dự án **VigorAI** chuẩn GitHub Showcase.
- **Những file đã tạo / chỉnh sửa:**
  - `README.md`: Header badges, 3 trụ cột công nghệ, sơ đồ kiến trúc Mermaid & vòng lặp AI khép kín, bảng 26 chức năng, cấu trúc Monorepo Team 4 người, Quick Start và bảng tuân thủ CH Play.
  - `session_log.md`: Ghi nhận Phiên 04.
- **Việc cần làm ở phiên kế tiếp:**
  - Chạy `git init`, tạo nhánh `develop` và bắt đầu triển khai các task Sprint 1 trong `docs/taskboard.md`.

---

## Phiên 03 — 2026-11-18 15:12 | Thành viên: Toàn nhóm (Đồng bộ thương hiệu) | Task: Chốt tên dự án chính thức `VigorAI`
- **Mục tiêu phiên:** Chốt tên dự án chính thức thành **VigorAI** (`VigorAI: 3D Gym & Health Log`) và đồng bộ toàn bộ tài liệu + file khai báo ứng dụng.
- **Những file đã chỉnh sửa:**
  - Tài liệu & Điều phối: `docs/system-design-spec.md`, `docs/roadmap.md`, `docs/taskboard.md`, `AGENTS.md`, `session_log.md`
  - Khai báo Mobile & Backend: `mobile/pubspec.yaml`, `mobile/android/app/src/main/AndroidManifest.xml`, `mobile/lib/main.dart`, `mobile/lib/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart`, `backend/app/core/config.py`, `backend/app/main.py`, `backend/app/templates/delete_account.html`, `backend/app/__init__.py`
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Giữ nguyên tên các thư mục phân quyền (`features/gym3d/`, `gym3d_workout_routes.dart`) và cấu hình Docker/DB local (`gym3d_user`, `gym3d_db`, `gym3d-assets`) để không phá vỡ cấu trúc Monorepo đã chốt ở `roadmap.md`.
- **Việc cần làm ở phiên kế tiếp:**
  - Khởi tạo Git repository (`git init`), tạo nhánh `develop`, và bắt đầu triển khai Sprint 1 theo từng vai trò (`M1`–`M4`).

---

## Phiên 02 — 2026-11-18 15:05 | Thành viên: Toàn nhóm (Khởi tạo) | Task: `T-M1-01`, `T-M1-02`, `T-M1-03`, `T-M2-01` (stub), `T-M3-01` (stub), `T-M4-03` (stub)
- **Mục tiêu phiên:** Khởi tạo toàn bộ khung thư mục Monorepo (Project Scaffolding) chống xung đột Git và 2 file điều phối gốc (`AGENTS.md`, `session_log.md`).
- **Những file đã tạo / chỉnh sửa:**
  - Thư mục gốc: `AGENTS.md`, `session_log.md`, `.gitignore`
  - Khung Flutter (`mobile/`): `pubspec.yaml`, `AndroidManifest.xml`, `lib/main.dart`, các file `[LOCKED STUB]` (`app_router.dart`, `app_database.dart`), 3 file route/drift tách riêng (`health_*`, `gym3d_workout_*`, `ai_analytics_*`), core services (`app_theme.dart`, `api_endpoints.dart`, `dio_client.dart`, `photo_picker_service.dart`, `health_connect_bridge.dart`, `sync_queue_manager.dart`), giao diện widget dùng chung `Muscle3DViewerWidget`, các stub màn hình theo từng feature và 3 file Mock JSON (`mock_m1_health.json`, `mock_m2_exercises.json`, `mock_m4_ai.json`).
  - Khung Backend (`backend/`): `requirements.txt`, `docker-compose.yml`, `app/main.py`, `app/core/{config,security}.py`, `app/db/{base,session}.py`, `app/models/entities.py`, `app/schemas/{core_schemas,ai_schema}.py`, đầy đủ các stub routers của M3 & M4 (`routers/ai.py` trả Mock JSON đúng chuẩn), các stub services và trang HTML công khai `app/templates/delete_account.html`, `ai_models/README.md`.
  - Khung AI Research (`ai_research/`): `model_b_food_yolo/{README.md,portion_estimator.py}`, `model_c_readiness_ml/{README.md,generate_banister_data.py}`.
  - Khung 3D Blender MCP (`assets_3d/`): `scripts_blender_mcp/build_base_mannequin.py`, `exported_glb/assets_manifest.json`.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Đặt `AGENTS.md` và `session_log.md` ngay tại thư mục gốc để mọi công cụ AI tự động nhận diện.
  - Khóa danh sách package và quyền Android chuẩn CH Play trong `pubspec.yaml`, `requirements.txt`, `AndroidManifest.xml`.
  - Chưa đánh dấu `[x]` hoàn thành hẳn các task Sprint 1 trong `docs/taskboard.md` vì đây mới là khung stub khởi tạo; từng thành viên sẽ hoàn thiện logic, chạy build/test thật và đánh dấu `[x]` khi nghiệm thu xong.
- **Việc cần làm ở phiên kế tiếp:**
  - Chạy `git init` & đẩy khung dự án lên repository chung của nhóm, tạo nhánh `develop` và 4 nhánh `feat/m1-*`, `feat/m2-*`, `feat/m3-*`, `feat/m4-*`.
  - M3 chạy `docker compose up` kiểm tra PostgreSQL + FastAPI `/docs`; M2 chạy script `build_base_mannequin.py` qua **Blender MCP** để sinh file `base_mannequin.glb` thật; M1 khởi tạo Flutter Android Gradle wrapper & Drift `build_runner`; M4 bắt đầu chuẩn bị dataset Model B & sinh dữ liệu Banister Model C.

---

## Phiên 01 — 2026-11-18 14:20 – 14:50 | Thành viên: Toàn nhóm (Thiết kế) | Task: Brainstorming & Tài liệu Đặc tả
- **Mục tiêu phiên:** Brainstorming ý tưởng app Sức khỏe + Gym 3D Blender MCP + AI cho team 4 người, đáp ứng tiêu chuẩn phát hành Google Play (CH Play), lên Roadmap & Taskboard chống xung đột Git.
- **Những file đã tạo:**
  - `docs/system-design-spec.md`: Đặc tả 26 chức năng (`F01`–`F26`), Kiến trúc Hybrid Offline-First + Cloud AI & Dynamic 3D, ERD 11 bảng nghiệp vụ + `food_nutrition_catalog`, Đặc tả AI Model B (YOLOv8) & Model C (XGBoost/LightGBM/MLP), Chuẩn 3D Blender MCP (11 Mesh/Material cơ bắp, Draco compression), Danh mục FastAPI Endpoints, Hồ sơ Tuân thủ CH Play (`targetSdk 35`, 16KB page size, Photo Picker, Health Connect, `/delete-account`, Medical Disclaimer).
  - `docs/roadmap.md`: Cây thư mục phân quyền `[OWNER: M1/M2/M3/M4]`, 5 Quy tắc vàng chống conflict, lộ trình 10 tuần (4 Sprints).
  - `docs/taskboard.md`: Phân chia 64 tasks cụ thể qua 4 Sprints, ánh xạ đầy đủ `F01`–`F26`, chiến lược Mock/Unblock và Pre-Release Checklist.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Chốt Stack: **Flutter + Drift (SQLite) + Blender MCP (.glb) + Python FastAPI + PostgreSQL 16 + YOLOv8 (Model B) + XGBoost/LightGBM/MLP (Model C)**.
  - Toàn bộ tài liệu đặt trực tiếp trong `docs/`, không tạo `superpowers/specs`.
