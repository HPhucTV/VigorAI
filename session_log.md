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

## Phiên 12 — 2026-11-20 01:10 | Thành viên: M3 (Backend & DB) | Task: `T-M3-07`, `T-M3-08`, `T-M3-10`, `T-M3-11` (`[x]`), `T-M3-09` (`[~]`)
- **Mục tiêu phiên:** Triển khai và nghiệm thu toàn bộ 5 tasks Sprint 2 của Thành viên M3 (`T-M3-07` đến `T-M3-11`) theo đúng `[OWNER: M3]`, bảo đảm 100% tương thích với app Mobile `M1`/`M2` và không đụng `feature_extractor.py` (`M4`) hay `[LOCKED STUB]`.
- **Những file đã tạo / chỉnh sửa:**
  - Schemas & Sync (`T-M3-07`): `backend/app/schemas/core_schemas.py`, `backend/app/services/sync_service.py`, `backend/app/routers/sync.py` (`POST /api/v1/sync/push` LWW theo `updated_at` UTC + `max(steps_count)` + tính `total_volume_kg`/`is_pr`, `GET /api/v1/sync/pull?since=`).
  - Health (`T-M3-08`): `backend/app/routers/health.py` (`/biometrics` kèm BMI Châu Á & 7-Day Moving Average, `/daily/{date}` trả `200 OK` mặc định nếu user mới + Smart Hydration, `/catalog`, `/meals`, `/supplements`).
  - 3D Exercises & Storage (`T-M3-09`): `backend/app/db/seed_catalog_and_exercises.py`, `backend/app/services/storage_service.py`, `backend/app/routers/exercises.py` (3 bài MVP giữ đường dẫn `assets/3d_bundled/*.glb` + SHA-256 thật khớp `assets_manifest.json` của `M2`; `/exercises/{code}/alternatives` trả top 5 bài cùng nhóm cơ chính).
  - Routines & Workouts (`T-M3-10`): `backend/app/routers/routines.py`, `backend/app/routers/workouts.py` (trả kèm `exercise_code` cho `M2`, tính `total_volume_kg`, `estimated_1rm` Epley/Brzycki, cờ `is_pr` & tự cộng bù nước ngày tập).
  - Analytics (`T-M3-11`): `backend/app/services/analytics_service.py`, `backend/app/routers/analytics.py` (`GET /api/v1/analytics/summary` trả Weekly Volume Load, 6-Axis Muscle Radar & PR Wall + Streak).
  - Test & Tiến độ: `backend/tests/test_core_api.py` (bổ sung test E2E Sprint 2), `docs/taskboard.md` (`T-M3-07`, `08`, `10`, `11` `[x]`; `T-M3-09` `[~]` chờ 27 `.glb` của `M2`).
- **Kiểm tra / Kết quả chạy thử:**
  - `docker compose exec api python -m app.db.seed_catalog_and_exercises`: Thành công (`total_foods: 36`, `total_exercises: 30`).
  - `docker compose exec api pytest tests/test_core_api.py -v`: **`8 passed in 3.56s`** (Pass 100% cả Sprint 1 + Sprint 2 E2E trên PostgreSQL 16 thật).
- **Việc cần làm ở phiên kế tiếp:**
  - Commit & tạo Pull Request từ nhánh `role/backend-architect` vào `main`; khi `M2` hoàn thành `T-M2-07` thì upload 27 file `.glb` mở rộng lên MinIO/CDN để chốt `[x]` cho `T-M3-09`.

---

## Phiên 11 — 2026-11-19 23:52 | Thành viên: M3 + M2 (Chốt Sprint 1) | Task: `T-M3-06` (`[~]`), `T-M2-06` (`[~]`)
- **Mục tiêu phiên:** Xử lý lỗi build Railpack trên Railway (`T-M3-06`), hoàn thiện cấu hình ký Release `.aab` với Upload Keystore thật (`T-M2-06`), trừ `T-M1-07` làm cuối cùng theo yêu cầu người dùng; chuẩn bị commit sạch sẽ theo phạm vi và push/mở PR lên GitHub.
- **Những file đã tạo / chỉnh sửa:**
  - **Backend & Railway Cloud Deploy (`T-M3-06`):**
    - `railway.json` & `.dockerignore`: Khai báo builder `DOCKERFILE` trỏ thẳng `backend/Dockerfile.railway`, healthcheck `/healthz` (`120s`), loại bỏ `mobile/`, `assets_3d/`, `ai_research/`, `docs/` khỏi Docker build context khi Railway build từ root `/`.
    - `backend/railway.json`, `backend/Dockerfile.railway`, `backend/Dockerfile`, `backend/.dockerignore`: Hỗ trợ build từ cả root `/` lẫn `backend/`; thêm `ARG INSTALL_AI_DEPS=false` bỏ qua wheel AI nặng (`ultralytics`/`torch`/`xgboost`...) ở Sprint 1 khi `app/routers/ai.py` chạy stub (không đụng `[LOCKED STUB]` `backend/requirements.txt`), bind động `${PORT:-8000}` với `--proxy-headers`, chạy `python -m app.db.startup` trước `uvicorn`.
    - `backend/app/core/config.py`: Chuẩn hóa `DATABASE_URL` (`postgres://`, `postgresql://`, `postgresql+psycopg2://` $\rightarrow$ `postgresql+asyncpg://`, quy đổi `sslmode=` sang `ssl=` hoặc bỏ khi `disable`), parse linh hoạt `CORS_ORIGINS` (`NoDecode` hỗ trợ CSV hoặc JSON), thêm cờ `RUN_MIGRATIONS_ON_STARTUP` & `RUN_SEED_ON_STARTUP`.
    - `backend/app/db/session.py`: Bật `pool_pre_ping=True` cho kết nối PostgreSQL managed trên cloud.
    - `backend/app/db/startup.py`: Startup runner bằng Python (tránh lỗi CRLF trên Windows) chạy `alembic upgrade head` tối đa 5 lần retry khi DB cold-start, rồi chạy idempotent `seed_catalog_and_exercises`.
    - `backend/app/services/storage_service.py`: Xử lý an toàn khi `S3_ENDPOINT_URL` rỗng hoặc chưa triển khai MinIO/S3 trên Railway (`retries={"max_attempts": 1}`) để `DELETE /api/v1/users/me` hoạt động tức thì.
    - `backend/tests/test_core_api.py`: Bổ sung unit test cho `Settings.normalize_database_url` và `Settings.parse_cors_origins`.
  - **Upload Keystore & Signed `.aab` (`T-M2-06`):**
    - Sinh cặp khóa RSA 2048-bit (`vigorai-upload`, hiệu lực `10,000` ngày) lưu tại `mobile/android/app/vigorai-upload-keystore.jks` và cấu hình `mobile/android/key.properties` (cả hai đều bị `.gitignore` chặn tuyệt đối, không commit lên Git).
  - **Tài liệu tiến độ:** `docs/taskboard.md` (`T-M3-06` `[~]`, cập nhật ghi chú `T-M2-06` `[~]`).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Dùng `INSTALL_AI_DEPS=false` mặc định cho bản Sprint 1 giúp image Docker gọn (~vài trăm MB thay vì vài GB CUDA/PyTorch) và build nhanh trên Railway mà vẫn giữ nguyên `backend/requirements.txt` (`[LOCKED STUB]`). Sang Sprint 2 (`M4`) chỉ cần đặt Build Arg `INSTALL_AI_DEPS=true`.
  - Toàn bộ `[LOCKED STUB]` (`mobile/pubspec.yaml`, `mobile/lib/main.dart`, `mobile/lib/core/database/app_database.dart`, `mobile/lib/core/router/app_router.dart`, `backend/requirements.txt`, `backend/app/main.py`, `.gitignore`) được giữ nguyên 100%.
- **Kiểm tra / Kết quả chạy thử:**
  - `python -m py_compile` (5 file Python backend chỉnh sửa/mới): Exit `0`.
  - Kiểm tra cú pháp `railway.json` & `backend/railway.json` + unit logic `Settings.normalize_database_url` & `Settings.parse_cors_origins`: Pass (`UNIT_LOGIC_OK`, `JSON_OK`).
  - `git check-ignore -v mobile/android/key.properties mobile/android/app/vigorai-upload-keystore.jks`: Xác nhận match rule `.gitignore`.
  - `flutter analyze --no-fatal-infos`: Exit `0` (0 lỗi, 0 cảnh báo).
  - `flutter test test/workout/`: Pass `5 / 5`.
  - `flutter build appbundle --release --target-platform android-arm64,android-x64 --dart-define=USE_MOCK_API=true --dart-define=MVP_CLOSED_TESTING=true --dart-define=ENABLE_HEALTH_CONNECT=false`: Exit `0` (`44,703,677 B` $\approx 42.63\text{ MB}$ gồm debug symbols).
  - `jarsigner -verify -verbose -certs mobile/build/app/outputs/bundle/release/app-release.aab`: Exit `0` (`jar verified.`, `Signed by "CN=VigorAI, OU=Mobile, O=VigorAI Team, L=Ho Chi Minh, ST=HCM, C=VN"`).
- **Việc cần làm ở phiên kế tiếp:**
  - Trên Railway UI: thêm **PostgreSQL** service vào project `unique-grace`, cấu hình `DATABASE_URL=${{Postgres.DATABASE_URL}}` & `JWT_SECRET_KEY`, bật **Generate Domain** ở Settings > Networking, rồi merge PR trên GitHub vào `main` để Railway build & deploy tự động.
  - Kiểm tra `https://<domain>/healthz` và `https://<domain>/delete-account` trả `200 OK`, sau đó build lại `.aab` trỏ `--dart-define=API_BASE_URL=https://<domain> --dart-define=USE_MOCK_API=false` và thực hiện `T-M1-07` để nộp Closed Testing.

---

## Phiên 10 — 2026-11-19 23:28 | Thành viên: M2 (phối hợp M1 Sprint 1) | Task: `T-M2-01`, `T-M2-02`, `T-M2-03`, `T-M2-04`, `T-M2-05` (`[x]`), `T-M2-06` (`[~]`)
- **Mục tiêu phiên:** Hoàn thiện toàn bộ phần việc Sprint 1 của Thành viên M2 (Blender MCP 3D pipeline `base_mannequin.glb` + 3 bài mẫu MVP, Drift tables/routes/30-exercise Mock JSON, `AssetCacheManager` SHA-256 + LRU 250 MB, `Muscle3DViewerWidget` + màn hình Phòng tập 3D MVP, thẻ mở 3D trên Dashboard và kiểm thử build `.aab` Release `v1.0.0+1`) rồi dừng đúng phạm vi Sprint 1 (không đụng `[LOCKED STUB]`, chưa commit/push).
- **Những file đã tạo / chỉnh sửa:**
  - **3D Blender MCP (`T-M2-01`, `T-M2-02`):**
    - `assets_3d/scripts_blender_mcp/build_base_mannequin.py`: Dựng Mannequin **Low-Poly Anatomical Faceted** từ bộ **Blender Studio Human Base Meshes v1.4.1 (CC0)** (`GEO-body_male_realistic`), chuẩn hóa chiều cao `1.78 m`, Decimate đối xứng `11,848 triangles`, gắn xương `Armature_GymHuman` bằng `ARMATURE_AUTO` trước khi tách thành đúng **11 Mesh/Material cơ bắp** (`Mesh_Muscle_*` / `Mat_Muscle_*`) + `Body_Head_Neck` + `Body_Joints_Hands_Feet` (`Mat_Body_Neutral`) + 4 Empty Sockets (`Socket_Hand_L/R`, `Socket_Back_Barbell`, `Floor_Origin`), lưu `assets_3d/source_blend/base_mannequin.blend` và xuất Draco `.glb` (`322,160 B`).
    - `assets_3d/scripts_blender_mcp/build_mvp_exercises.py`: Dựng dụng cụ rời (`Equip_Barbell`, `Equip_Bench`, `Equip_Mat`) + 2 clip `Anim_GoodForm` & `Anim_BadForm` (NLA Tracks, 30 FPS) cho 3 bài mẫu MVP (`barbell_squat.glb` `408,360 B` / `12,284 tris`; `push_up.glb` `381,872 B` / `11,860 tris`; `barbell_bench_press.glb` `391,312 B` / `12,356 tris`), xuất đồng thời sang `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/` (tổng 4 file = `1,503,704 B` $\approx 1.43\text{ MB}$), cập nhật SHA-256 thật vào `assets_3d/exported_glb/assets_manifest.json`.
  - **Drift, Routes & Mock JSON (`T-M2-04`):**
    - `mobile/lib/core/database/workout_tables.drift.dart` (thêm `nameEn`, `setupGuideJson`, `exercisesJson` và Domain Models chuẩn hóa cả 2 định dạng `phase_keyframes`), `mobile/lib/core/database/ai_cache_tables.drift.dart` (cập nhật header `[OWNER: M2]`, giữ nguyên `LocalProgressPhotosTable` cho M1, thêm Domain Models Readiness), `mobile/assets/mock_json/mock_m2_exercises.json` (đủ 30 bài tập khớp `seed_catalog_and_exercises.py` của M3 + SHA-256 thật cho 3 bài MVP), `mobile/lib/core/router/gym3d_workout_routes.dart` (`/gym3d`, `/gym3d/exercise/:code`, `/workout/live`), `mobile/lib/core/router/ai_analytics_routes.dart`, `mobile/lib/features/ai_analytics/presentation/ai_coach_hub_screen.dart` và `mobile/lib/core/database/app_database.g.dart` (sinh lại qua `build_runner`, giữ nguyên `app_database.dart`).
  - **Cache 3D & Pure-Dart SHA-256 (`T-M2-05`):**
    - `mobile/lib/features/gym3d/data/sha256_util.dart` (FIPS 180-4 thuần Dart không mở khóa `pubspec.yaml`), `mobile/lib/features/gym3d/data/asset_cache_manager.dart` (lazy download qua `.tmp`, verify SHA-256, LRU `250 MB` với `cache_index.json`, `clearAllCachedAssets()`), `mobile/test/workout/asset_cache_manager_test.dart`.
  - **3D Viewer, Màn hình MVP & Dashboard (`T-M2-03`):**
    - `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart` (`StatefulWidget` bọc `ModelViewer` giữ key duy nhất `glbAssetOrUrl`, JS Bridge qua `relatedJs` + `onWebViewCreated` + `didUpdateWidget` đổi màu 11 `Mat_Muscle_*`, 4 góc nhìn `front/side/back/top`, chuyển clip Đúng/Sai, tốc độ `0.25x–1.0x`, `VigorMuscleChannel` cho `onMuscleTap`), `mobile/lib/features/gym3d/data/exercise_repository.dart`, `mobile/lib/features/gym3d/presentation/gym3d_library_screen.dart` (hiển thị đúng 3 bài mẫu MVP khi `isMvpClosedTesting = true`), `mobile/lib/features/gym3d/presentation/exercise_3d_detail_screen.dart`, `mobile/lib/features/health/presentation/health_dashboard_screen.dart` (gắn thẻ **"Phòng tập 3D Tương tác (3 bài mẫu MVP)"** ngay dưới thẻ Dinh dưỡng).
  - **Build `.aab` Release Prep (`T-M2-06`):**
    - `mobile/android/app/build.gradle.kts` (thêm hook đọc tùy chọn `mobile/android/key.properties` cho `signingConfigs.release`, fallback `debug` nếu chưa tạo keystore), `mobile/android/app/proguard-rules.pro` (thêm `-dontwarn com.google.android.play.core.**` cho R8 Release).
  - **Tiến độ:** `docs/taskboard.md` (`T-M2-01`..`T-M2-05` `[x]`, `T-M2-06` `[~]` $\rightarrow$ `M2: 5 / 17 Done (29.4%)`, `Tổng cộng: 16 / 63 Done (25.4%)`).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Dùng `clear_scene_safely()` (xóa qua `bpy.data.*`) trong toàn bộ script Blender MCP thay cho `bpy.ops.wm.read_factory_settings` để không làm reset add-on/socket Blender MCP.
  - Vì `model_viewer_plus 1.10.0` chỉ dựng HTML ở `initState` (và có lỗi typo ở attribute `shadowIntensity`/`shadowSoftness`), `Muscle3DViewerWidget` bỏ qua 2 prop đó và điều khiển toàn bộ cập nhật màu/camera/animation qua `runJavaScript(...)` trong `didUpdateWidget`.
  - Toàn bộ `[LOCKED STUB]` (`pubspec.yaml`, `main.dart`, `app_database.dart`, `app_router.dart`, `.gitignore`) được giữ nguyên 100%.
- **Kiểm tra / Kết quả chạy thử:**
  - Blender MCP `look` xác nhận ranh giới 11 bó cơ giải phẫu và chuỗi khung hình `barbell_squat`, `push_up`, `barbell_bench_press` không clipping; kiểm tra header nhị phân glTF cả 4 `.glb` đạt Draco level 6, đủ 11 `Mat_Muscle_*`, đủ `Anim_GoodForm` + `Anim_BadForm`.
  - `dart run build_runner build --delete-conflicting-outputs`: Exit `0` (57 outputs).
  - `flutter analyze --no-fatal-infos`: Exit `0` (0 lỗi, 0 cảnh báo; chỉ còn 11 info deprecation `package:flutter/material.dart` trên Flutter 3.50.0).
  - `flutter test test/workout/`: Pass `5 / 5` tests (`Sha256Util` NIST vectors, bundled passthrough, cache hit, SHA-256 mismatch rejection, LRU eviction & `clearAllCachedAssets`).
  - `flutter build appbundle --release --target-platform android-arm64,android-x64 --dart-define=USE_MOCK_API=true --dart-define=MVP_CLOSED_TESTING=true --dart-define=ENABLE_HEALTH_CONNECT=false`: Exit `0` (`app-release.aab` thô `42.63 MB` gồm `21.63 MB` `BUNDLE-METADATA/debugsymbols`; không tính debug symbols = `21.00 MB`, tải cài đặt ước tính trên máy `arm64-v8a` $\approx 11.28\text{ MB} < 40\text{ MB}$). Merged Release `AndroidManifest.xml` đạt `minSdkVersion="26"`, `targetSdkVersion="35"`, `extractNativeLibs="false"`, **0 quyền cấm CH Play**, **0 quyền Health Connect / `FOREGROUND_SERVICE_HEALTH`**.
- **Việc cần làm ở phiên kế tiếp:**
  - Hoàn tất `T-M1-07` (Play Console \$25 + 20–25 Gmail testers) và `T-M3-06` (URL HTTPS Server thật của M3).
  - Sinh Upload Keystore (`keytool`) + tạo `mobile/android/key.properties` (ngoài Git), chạy app trên emulator `VigorAI_Pixel6_API35` kiểm tra hiển thị WebGL `<model-viewer>` cho cả 3 bài 3D (lưu ý kiểm tra tải Draco decoder ở chế độ offline), build `.aab` ký thật truyền `--dart-define=API_BASE_URL=https://<domain-m3> --dart-define=USE_MOCK_API=false` để chốt `T-M2-06` lên Closed Testing.

---

## Phiên 09 — 2026-11-19 15:26 | Thành viên: M1 | Task: `T-M1-01`, `T-M1-02`, `T-M1-03`, `T-M1-04`, `T-M1-05`, `T-M1-06`
- **Mục tiêu phiên:** Hoàn thiện 3 nhóm việc còn lại của M1 trong Sprint 1 (`FeatureFlags` + Xóa tài khoản + Manifest MVP `T-M1-06`, Android native scaffolding `T-M1-01`/`02`, Drift `app_database.g.dart` & JWT Auto-Refresh `401` `T-M1-03`/`04`/`05`), kết nối Android Studio/SDK và chạy kiểm thử E2E trên máy ảo Android 15 (chưa commit/push theo yêu cầu).
- **Những file đã tạo / chỉnh sửa:**
  - MVP & FeatureFlags (`T-M1-06`): `mobile/lib/core/config/feature_flags.dart` (`isMvpClosedTesting = true`, `enableHealthConnect = false`), `mobile/android/app/src/main/AndroidManifest.xml` (tạm comment quyền `health.READ_*`, `FOREGROUND_SERVICE_HEALTH`, `<queries>`, `<activity-alias>` với ghi chú `[RE-ENABLE IN v1.2.0]` và bổ sung `tools:node="remove"` đủ 7 quyền cấm gồm `QUERY_ALL_PACKAGES`), `mobile/lib/features/health/presentation/health_dashboard_screen.dart` (ẩn nút stub M2/M4 khi MVP, thêm thẻ & hộp thoại Xóa tài khoản `F26`).
  - Android Native Scaffolding (`T-M1-01`, `T-M1-02`): `mobile/android/build.gradle.kts`, `mobile/android/settings.gradle.kts` (`AGP 9.3.1`, `KGP 2.4.20`), `mobile/android/app/build.gradle.kts` (`compileSdk 36`, `ndkVersion 28.2.13676358`, `minSdk 26`, `targetSdk 35`, `arm64-v8a`/`x86_64`, cờ ELF 16 KB page size, R8 minify), `mobile/android/gradle.properties` (gỡ cờ deprecated `android.bundle.enableUncompressedNativeLibs`), `mobile/android/app/proguard-rules.pro`, `mobile/android/gradle/wrapper/gradle-wrapper.properties` (`gradle-9.5.0-all.zip`), `mobile/android/app/src/main/kotlin/com/vigorai/app/MainActivity.kt`, bộ `res/` (`styles.xml`, `colors.xml`, `launch_background.xml`, `ic_launcher*`, mipmap PNG), `src/{debug,profile}/AndroidManifest.xml`, cùng Gradle wrapper binaries (`.gitignored`).
  - Drift & JWT (`T-M1-03`..`05`): Mở khóa `[LOCKED STUB]` `mobile/lib/core/database/app_database.dart` (đã được user duyệt) & sinh `mobile/lib/core/database/app_database.g.dart`, cập nhật `mobile/lib/core/network/dio_client.dart` (tự refresh JWT khi gặp `401` + retry 1 lần), `mobile/lib/features/auth_privacy/data/auth_repository.dart` (`refreshToken()`, `deleteAccountAndLocalData()`), `mobile/lib/features/auth_privacy/presentation/auth_controller.dart` (`deleteAccount()`, sửa `logout()` xóa sạch `state.user` qua `clearUser: true`).
  - Nâng cấp dependency (Micro-PR cần tách riêng khi commit): Mở khóa `[LOCKED STUB]` `mobile/pubspec.yaml` theo xác nhận của user để nâng `workmanager: ^0.5.2` $\rightarrow$ `^0.10.10` (`workmanager_android 0.10.9`) vì bản `0.5.2` gọi Flutter Android v1 embedding đã bị gỡ khỏi Flutter `3.50.0`.
  - Tiến độ: `docs/taskboard.md` (đánh dấu `[x]` `T-M1-01`, `T-M1-03`, `T-M1-04`, `T-M1-05`, `T-M1-06` $\rightarrow$ `M1: 6 / 17 Done`, `Tổng cộng: 11 / 63 Done`).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Khi commit lên nhánh `HPhucTV`, **tách riêng 1 Micro-PR** cho `[LOCKED STUB]` (`mobile/pubspec.yaml` & `mobile/lib/core/database/app_database.dart`) đúng luật [AGENTS.md](./AGENTS.md).
  - Cài đặt Android SDK (`platforms;android-35/36`, `build-tools;35.0.0`, `ndk;28.2.13676358`, `cmake;3.22.1`, `system-images;android-35;google_apis_playstore;x86_64`) + AVD **`VigorAI_Pixel6_API35`** (`pixel_6`, 3 GB RAM, 4 cores, WHPX) chạy mượt trên i7-13700H / 16 GB RAM.
- **Kiểm tra / Kết quả chạy thử:**
  - `dart run build_runner build` & `flutter pub get`: Thành công (`app_database.g.dart` sinh sạch, `workmanager 0.10.10` khớp hoàn toàn).
  - `flutter analyze --no-fatal-infos`: Exit `0` (0 lỗi, 0 cảnh báo).
  - `flutter build apk --debug --dart-define=USE_MOCK_API=true`: Thành công (`build/app/outputs/flutter-apk/app-debug.apk`).
  - Kiểm tra `Merged AndroidManifest.xml` (`processDebugMainManifest`): Đạt `minSdkVersion="26"`, `targetSdkVersion="35"`, `extractNativeLibs="false"`, **0 quyền cấm CH Play** và **0 quyền Health Connect/FGS Health** đang kích hoạt ở bản MVP.
  - Chạy thực tế trên `VigorAI_Pixel6_API35` (`emulator-5554`): Khởi chạy `COLD` không crash; Onboarding chặn nút tiếp tục cho tới khi tick Medical Disclaimer; Đăng nhập tài khoản demo mở Health Dashboard (`BMI 23.7`, `Bước chân`, `Giấc ngủ`, `+250 ml` cập nhật `2000 / 2950 ml` & hiện nút `Sync (1)`, `Mifflin-St Jeor`, `F06 Supplements`); xác nhận nút stub M2/M4 bị ẩn; chạy trọn luồng **Xóa tài khoản** gọi `DELETE /api/v1/users/me` + `clearAllLocalData()` quay về `/onboarding` kèm SnackBar xác nhận; `adb logcat` sạch lỗi.
- **Việc cần làm ở phiên kế tiếp:**
  - M1 commit/push thay đổi (tách riêng Micro-PR cho `[LOCKED STUB]`) khi sẵn sàng, đồng thời thực hiện `T-M1-07` (đăng ký Google Play Console \$25 & gom 20–25 Gmail testers) và bắt đầu Sprint 2 (`T-M1-08`..`12`).

---

## Phiên 08 — 2026-11-19 14:04 | Thành viên: Toàn nhóm (Điều chỉnh Lộ trình) | Task: Tách `M4` Pure AI & Áp dụng Lộ trình CH Play 2 Nhịp
- **Mục tiêu phiên:** Tách toàn bộ công việc Flutter ra khỏi Dev AI (`M4`) để tập trung thu thập dữ liệu & train model, đồng thời tích hợp chiến lược phát hành CH Play 2 nhịp ("Vừa code vừa chạy đồng hồ Closed Testing 14 ngày").
- **Những file đã cập nhật:**
  - `AGENTS.md`: Cập nhật bảng `[OWNER]` mới (`M4` chỉ làm Python AI; `M1` nhận UI `F19` + Ảnh `F24`; `M2` nhận UI `F20`–`F23` + Radar `F24`), bổ sung quy tắc CH Play 2 nhịp.
  - `docs/roadmap.md`: Vẽ lại lộ trình 3 Mốc CH Play (`v1.0.0+1` Closed Testing cuối Sprint 1 $\rightarrow$ `v1.1.0` Production & Chiến dịch 1.000 lượt tải cuối Sprint 2 $\rightarrow$ `v1.2.0` Full 26 chức năng gồm Health Connect & AI `v1.2` ở Sprint 3).
  - `docs/taskboard.md`: Tái cấu trúc thành **63 tasks** (`M1`: 17, `M2`: 17, `M3`: 15, `M4`: 14), giữ nguyên tiến độ đã đạt của M1 (`1/17 Done`, `4/17 Code Ready`) và M3 (`5/15 Done` — hoàn tất `T-M3-01`..`05`), kéo sớm `T-M1-06`/`07`, `T-M2-06`, `T-M3-06` lên Sprint 1 và chia Model B thành 2 đợt (`v1.0` 15–20 món từ Roboflow/Kaggle $\rightarrow$ `v1.2` 35–50 món).
  - `docs/system-design-spec.md` & `README.md`: Đồng bộ phân công 4 thành viên và lộ trình Sprint 1–4.
- **Lưu ý cho phiên tiếp theo:**
  - `M1` ưu tiên hoàn thiện `T-M1-06` (nút Xóa tài khoản + `FeatureFlags` ẩn stub cho bản MVP `v1.0.0+1`) và `T-M1-07` (Play Console \$25 + gom 20–25 Gmail).
  - `M3` thực hiện `T-M3-06` (deploy Backend vừa hoàn thành ở Phiên 07 lên host HTTPS công khai với `/delete-account`).
  - Nhắc `M2` khi mở các file stub cũ trong `mobile/lib/features/ai_analytics/`, `ai_cache_tables.drift.dart`, `ai_analytics_routes.dart` lưu ý quyền sở hữu đã chuyển từ `M4` sang `M2`.

---

## Phiên 07 — 2026-11-18 19:25 | Thành viên: M3 (Backend & DB) | Task: `T-M3-01`, `T-M3-02`, `T-M3-03`, `T-M3-04`, `T-M3-05`
- **Mục tiêu phiên:** Triển khai và nghiệm thu hoàn tất toàn bộ 5 tasks Sprint 1 của Thành viên M3 (`T-M3-01` đến `T-M3-05`), giữ nguyên các file `[LOCKED STUB]` (`requirements.txt`, `app/main.py`, `.gitignore`).
- **Những file đã tạo / chỉnh sửa:**
  - Hạ tầng & Auth (`T-M3-01`, `T-M3-03`): `backend/docker-compose.yml` (cập nhật image MinIO sang `cgr.dev/chainguard/minio:latest`), `backend/app/core/config.py`, `backend/app/core/security.py`, `backend/app/core/dependencies.py`, `backend/app/schemas/core_schemas.py` (dùng `StringConstraints` kiểm tra email không phụ thuộc `email-validator`), `backend/app/services/auth_service.py`, `backend/app/routers/auth.py`.
  - Migration & Seed (`T-M3-02`, `T-M3-05`): `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/0001_initial_schema.py`, `backend/app/db/seed_catalog_and_exercises.py` (36 món VNFood/USDA + 30 bài tập 3D chuẩn 11 `Mat_Muscle_*` + 4 giáo án mẫu), `backend/app/db/seed_demo_history.py` (30 ngày lịch sử cho M4).
  - Privacy & CH Play (`T-M3-04`): `backend/app/services/storage_service.py`, `backend/app/routers/users.py` (`GET /me`, `GET /me/export`, `DELETE /me`, `POST /delete-via-web`).
  - Kiểm thử & Tiến độ: `backend/tests/test_core_api.py`, `docs/taskboard.md` (đánh dấu `[x]` toàn bộ 5 tasks Sprint 1 của M3 sau khi người dùng xác nhận nghiệm thu).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Chuyển image MinIO sang `cgr.dev/chainguard/minio:latest` do `minio/minio` và `quay.io/minio/minio` đã khóa anonymous pull.
  - Dùng `StringConstraints` của Pydantic v2 cho kiểu `EmailAddress` để không phải sửa file `[LOCKED STUB]` `requirements.txt`.
  - `TokenResponse` trả kèm object `user` (`UserProfileResponse`) khớp 100% với `AuthRepository` của M1.
  - `get_current_user` truy vấn lại `User` trong DB trên mỗi request để bảo đảm sau khi `DELETE /api/v1/users/me`, token cũ lập tức trả về `401 Unauthorized`.
- **Kiểm tra / Kết quả chạy thử:**
  - `docker compose up -d --build`: Thành công (PostgreSQL 16 + Chainguard MinIO + FastAPI).
  - `docker compose exec api alembic upgrade head`: Thành công (tạo đủ 12 bảng + Indexes).
  - `docker compose exec api python -m app.db.seed_demo_history`: Thành công (seed 36 món ăn, 30 bài tập 3D, 4 giáo án mẫu và 30 ngày lịch sử cho `demo@vigorai.app`).
  - `docker compose exec api pytest tests/test_core_api.py -v`: Pass toàn bộ test cases.
- **Việc cần làm ở phiên kế tiếp:**
  - M3 chuyển sang triển khai Sprint 2 (`T-M3-06` đến `T-M3-10`: Sync Engine Push/Pull LWW, API Health, API Exercises CDN, API Routines/Workouts và Analytics Summary).

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
