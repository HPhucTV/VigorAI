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

## Phiên 35 — 2026-11-24 15:30 | Thành viên: M1 | Task: Thiết kế & Cài đặt App Icon "Iron Volt V", Sửa lỗi 2 Icon khi Khởi động & Build Release APK
- **Mục tiêu phiên:**
  1. Thiết kế 3 mẫu App Icon (Favicon) cho VigorAI trên Figma (`VigorAI — 3 App Icon (Favicon) Concepts`); người dùng chốt **Mẫu 01 — Iron Volt V**.
  2. Thay thế icon chữ `"V"` nền xanh cũ bằng **Mẫu 01 — Iron Volt V** cho toàn bộ Android Adaptive Icon Vector (`ic_launcher_background.xml`, `ic_launcher_foreground.xml`, `mipmap-anydpi-v26/ic_launcher.xml`), xuất bộ PNG đa độ phân giải (`mdpi` 48px → `xxxhdpi` 192px) và icon Play Store `512×512` (`vigorai_playstore_512.png`).
  3. Khắc phục triệt để lỗi hiện **2 icon liên tiếp** khi mở app (Android 12+ system SplashScreen + `_VigorLaunchSplash` của Flutter) bằng cách đồng bộ nền `LaunchTheme` (`values/colors.xml` `#F4F6F9`, `values-night/colors.xml` `#090B0F`, `drawable-v21/launch_background.xml`) và bỏ icon/text trùng lặp khỏi `_VigorLaunchSplash`.
  4. Thay biểu tượng tạ chung trên `LoginScreen` bằng huy hiệu `CustomPaint` mini **Iron Volt V** và build Release APK kiểm thử máy thật.
- **Những file đã tạo / chỉnh sửa (`[OWNER: M1]`, `0` file `[LOCKED STUB]` bị chạm):**
  - Tạo mới (2 file): `mobile/android/app/src/main/res/drawable/ic_launcher_background.xml`, `mobile/android/app/src/main/res/values-night/colors.xml`.
  - Cập nhật Android resources: `mobile/android/app/src/main/res/drawable/ic_launcher_foreground.xml`, `mobile/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`, `mobile/android/app/src/main/res/values/colors.xml`, `mobile/android/app/src/main/res/drawable-v21/launch_background.xml`, `mobile/android/app/src/main/res/mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png`.
  - Cập nhật Flutter UI & Test: `mobile/lib/features/auth_privacy/presentation/app_launch_gate.dart`, `mobile/lib/features/auth_privacy/presentation/login_screen.dart`, `mobile/test/health/ui_layout_and_copy_test.dart`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0** errors, **0** warnings).
  - `flutter test test/health/ test/workout/`: **46 / 46 PASS**.
  - `flutter build apk --release --dart-define=MVP_CLOSED_TESTING=false`: Thành công, xuất `mobile/build/app/outputs/flutter-apk/app-release.apk` (`69,899,597` bytes / `66.7 MB`).
  - `git status -s`: Chỉ chạm các file thuộc `[OWNER: M1]` + `session_log.md`; `0` file `[LOCKED STUB]` bị sửa.
- **Việc cần làm ở phiên kế tiếp:**
  - Cài `app-release.apk` lên máy Android thật để kiểm tra icon **Iron Volt V** trên launcher, luồng mở app chỉ còn 1 splash duy nhất và logo mới trên `LoginScreen`.

---

## Phiên 34 — 2026-11-24 14:08 | Thành viên: M1 + M2 | Task: Thiết kế Figma 3 Mẫu UI + Triển khai Mẫu 01 Dual Theme, Sửa Nhảy Màn hình Khởi động & Giật Chuyển Tab
- **Mục tiêu phiên:**
  1. Kết nối Figma MCP tạo file `VigorAI — 3 Premium UI Design Concepts` gồm 3 mẫu UI cao cấp (9 màn hình + Variable Collection + Reusable Components) để người dùng chọn; người dùng chốt **Mẫu 01 — Obsidian Performance Lab** kèm hỗ trợ **Light Mode**.
  2. Triển khai Mẫu 01 Dual Theme (`Obsidian Performance Lab` Dark `#090B0F` / Volt `#CCFF00` / Cyan `#38BDF8` & `Alabaster Performance Lab` Light `#F4F6F9` / Porcelain `#FFFFFF` / Ink `#0F172A`), nới biên `20–24px`, giảm mật độ card bằng Dual Hero Card + Bento Grid 2×2 và sân khấu 3D tràn viền với Floating HUD.
  3. Khắc phục triệt để tình trạng nhảy màn hình lúc khởi động (`Onboarding -> Login -> Dashboard`) bằng `AppLaunchGate` + đọc song song `Future.wait` trong `AuthController.restoreSession()`.
  4. Khắc phục giật lag khi chuyển 5 tab trong `MainNavigationShell` bằng cách tách `select(...)` trên Riverpod providers, pre-warm provider sau 350ms, bọc `RepaintBoundary` + `_SmoothTabViewport` (`180ms`), và trì hoãn/ngủ đông `Muscle3DViewerWidget` khi Tab 4 không active.
- **Những file đã tạo / chỉnh sửa (`[OWNER: M1]` + `[OWNER: M2]`, `0` file `[LOCKED STUB]` bị chạm):**
  - Tạo mới (1 file `[OWNER: M1]`): `mobile/lib/features/auth_privacy/presentation/app_launch_gate.dart`.
  - `[OWNER: M1]`: `mobile/lib/core/theme/app_theme.dart`, `mobile/lib/core/router/health_routes.dart`, `mobile/lib/features/auth_privacy/presentation/auth_controller.dart`, `mobile/lib/features/auth_privacy/presentation/login_screen.dart`, `mobile/lib/features/auth_privacy/presentation/register_screen.dart`, `mobile/lib/features/health/presentation/health_dashboard_screen.dart`, `mobile/lib/features/health/{biometrics,food_scan,hydration,nutrition,progress_photos,sleep,supplements}/presentation/*.dart`, `mobile/test/health/ui_layout_and_copy_test.dart`.
  - `[OWNER: M2]`: `mobile/lib/features/ai_analytics/presentation/ai_coach_hub_screen.dart`, `mobile/lib/features/ai_analytics/readiness_3d/readiness_recovery_3d_view.dart`, `mobile/lib/features/ai_analytics/volume_analytics/volume_analytics_view.dart`, `mobile/lib/features/ai_analytics/muscle_balance/muscle_radar_view.dart`, `mobile/lib/features/gym3d/presentation/{gym3d_library_screen,exercise_3d_detail_screen}.dart`, `mobile/lib/features/workout/presentation/{routines_screen,live_workout_logger_screen}.dart`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0** errors, **0** warnings).
  - `flutter test test/health/ test/workout/`: **46 / 46 PASS** (bao gồm test `AppLaunchGate` không nháy Onboarding/Login khi đã đăng nhập hoặc đã chấp nhận miễn trừ, và test chuyển cả 5 tab ở `360dp + 1.3x` cả Light & Dark Mode).
- **Việc cần làm ở phiên kế tiếp:**
  - Cài thử lên máy Android thật / emulator để nghiệm thu trực quan Mẫu 01 Dual Theme, tốc độ chuyển tab và luồng khởi động mới.

---

## Phiên 33 — 2026-11-23 12:09 | Thành viên: M1 + M2 | Task: Nâng cấp UI/UX Dual Theme, Onboarding 3D 6 bước, Smart Routine Generator, 3D Coaching Guide & 5-Tab Shell
- **Mục tiêu phiên:** Triển khai trọn bộ 3 chặng nâng cấp trải nghiệm VigorAI:
  - Chặng 1 (`[OWNER: M1]`): Dual Theme Sáng (`Athletic Clean`) / Tối (`Dark Sporty Carbon`), `UserFitnessProfile` offline-first và Onboarding Wizard 3D 6 bước có tương tác trực tiếp với mô hình 3D + Medical Disclaimer.
  - Chặng 2 (`[OWNER: M2]`): Bộ sinh lịch tập thông minh `SmartRoutineGenerator` (thích ứng theo địa điểm/dụng cụ, tạng người, thời lượng, nhóm cơ ưu tiên), 5 Chương trình VĐV chuyên sâu, thư viện `ExerciseCoachingGuide` 4 phần tiếng Việt cho toàn bộ 39 bài tập gắn scrubber 3D `Chuẩn / Lỗi sai`, và `RoutinesScreen` 3 phân đoạn.
  - Chặng 3 (`[OWNER: M1]` + `[OWNER: M2]`): Khung điều hướng `MainNavigationShell` 5 tab tại `/health`, Avatar `36×36 dp` mở `/profile` (`ProfileSettingsScreen`) tái tính toán Realtime BMI/BMR/TDEE/Macros/Nước & đồng bộ gợi ý đổi lịch, cùng đồng bộ Dark Mode toàn bộ các màn hình.
- **Những file đã tạo / chỉnh sửa (`[OWNER: M1]` + `[OWNER: M2]`, `0` file `[LOCKED STUB]` bị chạm):**
  - Tạo mới (4 file): `mobile/lib/features/auth_privacy/data/user_fitness_profile.dart`, `mobile/lib/features/auth_privacy/presentation/profile_settings_screen.dart`, `mobile/lib/features/workout/domain/smart_routine_generator.dart`, `mobile/lib/features/gym3d/data/exercise_coaching_guide.dart`.
  - Chặng 1 & Core (`[OWNER: M1]`): `mobile/lib/core/network/dio_client.dart`, `mobile/lib/core/theme/app_theme.dart`, `mobile/lib/features/auth_privacy/data/auth_repository.dart`, `mobile/lib/features/auth_privacy/presentation/auth_controller.dart`, `mobile/lib/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart`, `mobile/lib/features/auth_privacy/presentation/register_screen.dart`, `mobile/lib/features/auth_privacy/presentation/login_screen.dart`, `mobile/lib/features/health/data/health_repository.dart`.
  - Chặng 2 (`[OWNER: M2]`): `mobile/lib/features/workout/data/workout_repository.dart`, `mobile/lib/features/workout/presentation/routines_screen.dart`, `mobile/lib/features/workout/presentation/live_workout_logger_screen.dart`, `mobile/lib/features/workout/presentation/widgets/plate_calculator_sheet.dart`, `mobile/lib/features/gym3d/presentation/exercise_3d_detail_screen.dart`, `mobile/lib/features/gym3d/presentation/gym3d_library_screen.dart`.
  - Chặng 3 Shell, Router & Dark Mode Sweep (`[OWNER: M1]` + `[OWNER: M2]`): `mobile/lib/core/router/{health_routes,gym3d_workout_routes,ai_analytics_routes}.dart`, `mobile/lib/features/health/presentation/health_dashboard_screen.dart`, `mobile/lib/features/health/{biometrics,food_scan,hydration,nutrition,progress_photos,sleep,supplements}/presentation/*.dart`, `mobile/lib/features/ai_analytics/{presentation/ai_coach_hub_screen,muscle_balance/muscle_radar_view,readiness_3d/readiness_recovery_3d_view,volume_analytics/volume_analytics_view}.dart`.
  - Kiểm thử (2 file): `mobile/test/health/ui_layout_and_copy_test.dart`, `mobile/test/workout/workout_sprint2_test.dart`.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Lưu `UserFitnessProfile` và `AppThemePreference` qua `FlutterSecureStorage` (`dio_client.dart`), tránh thêm gói ngoài nên `0` chạm `mobile/pubspec.yaml`; tự động xóa sạch khi chạy `deleteAccountAndLocalData()`.
  - Tạo `VigorAdaptiveTheme` trong `app_theme.dart` bọc các route/dialog/sheet để hỗ trợ chuyển 3 chế độ `Theo máy` / `Sáng` / `Tối` mượt `250ms` mà không đụng `mobile/lib/main.dart`.
  - Tạo `_SafeOnboarding3DStage` kiểm tra `FLUTTER_TEST` để giữ nguyên `Muscle3DViewerWidget` thật trên thiết bị Android và an toàn khi chạy `flutter test` headless không có `WebViewPlatform`.
  - Giữ 100% ràng buộc CH Play: không thêm quyền Android bị cấm, giữ nguyên văn `medicalDisclaimerText`, trích dẫn `Mifflin-St Jeor (1990)`, `Epley (1985) & Brzycki (1993)`, `WHO Asia-Pacific BMI`, và xóa tài khoản 2 kênh tại `/profile`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (`0` errors, `0` warnings).
  - `flutter test test/health/ test/workout/`: **45/45 PASS** (gồm test `360dp + 1.3x` Light & Dark Mode cho 5-Tab Shell, Profile Hub, Onboarding 6 bước + modal Đăng nhập nhanh; unit test `SmartRoutineGenerator`, 5 Pro Programs trên Drift SQLite và `ExerciseCoachingGuide` cho cả 39 bài tập).
  - `flutter build apk --release --dart-define=MVP_CLOSED_TESTING=false`: Thành công, xuất `mobile/build/app/outputs/flutter-apk/app-release.apk` (`69,689,361` bytes / `66.5 MB`).
- **Việc cần làm ở phiên kế tiếp:**
  - Kiểm thử trực quan trên thiết bị Android thật (`Sáng`/`Tối`, Onboarding 3D 6 bước, `/profile` tái tính toán Realtime, 5 chương trình VĐV và 3D Coaching Guide) rồi đóng gói/commit khi người dùng xác nhận.

---

## Phiên 32 — 2026-11-23 11:04 | Thành viên: M2 | Task: Sửa hình học 3D Mannequin (nắm tay, khớp vai/cổ tay), khử xoay 360° Quaternion & va chạm thiết bị/sàn
- **Mục tiêu phiên:** Khắc phục tình trạng bàn tay đơ/cổ tay lật ngược, sụp cấu trúc vùng vai trên (`Mesh_Muscle_Shoulders`, `Mesh_Muscle_Traps`), lỗi xoay 360° Quaternion khi nội suy giữa các keyframe, và các điểm va chạm/xuyên địa hình/chân trên bộ tài nguyên 3D (`hanging_leg_raise`, `barbell_deadlift`, `cable_crunch`, `cable_face_pull`, `push_up`, `plank`, v.v.), sau đó xuất lại `.blend`/`.glb` và đồng bộ SHA-256 theo cấu trúc slim-bundle (`T-M3-09`).
- **Những file đã tạo / chỉnh sửa (`[OWNER: M2]`, `0` file `[LOCKED STUB]` bị chạm):**
  - `assets_3d/scripts_blender_mcp/build_base_mannequin.py`: Thêm `_curl_fingers_into_grip_pose` (`grip_hands=True` cho 29 bài cầm nắm, giữ xòe phẳng `grip_hands=False` cho `push_up`, `plank`, `base_mannequin`, `base_mannequin_female`); mở rộng vùng tam giác `Mesh_Muscle_Shoulders` phần delta chữ V; thêm `_smooth_and_lock_skin_weights` khóa 100% trọng số ngón tay/lòng bàn tay vào `Hand_L`/`Hand_R` + làm mượt Laplacian 4 vòng vùng vai-đòn và cổ tay; bật `use_deform_preserve_volume = True` (Dual Quaternion Skinning).
  - `assets_3d/scripts_blender_mcp/build_mvp_exercises.py`: Cập nhật nhịp xương đòn `Clavicle`, kẹp cổ tay `<= 14°` trên sàn `> 0.12m`, đồng bộ dấu quaternion `_LAST_KEYED_QUAT` trong `_key_all_pose_bones` / `_begin_action`, loại bỏ điểm kỳ dị `atan2`/`swing_z` trong `_aim_bone_world`, và sửa `_pose_push_up` (IK 2 xương cho chân giữ mũi chân trên thảm `min_z = +0.004..+0.005 m` + lòng bàn tay úp phẳng `n_palm = (0, 0, -1)`).
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Đồng bộ nhịp xương đòn `Clavicle`, `_LAST_KEYED_QUAT`, khử kỳ dị `atan2`/`swing_z` trong `_aim_bone_world`, bổ sung `_get_posed_fist_center` & `_solve_arm_grip_ik`, sửa va chạm dây qua đầu/nệm ghế (`cable_crunch`, `dumbbell_shoulder_press`, `barbell_hip_thrust`), sửa roll/pole 6 bài (`cable_face_pull`, `cable_crunch`, `straight_arm_cable_pulldown`, `dumbbell_shoulder_press`, `skull_crusher`, `barbell_bicep_curl`), sửa hướng bàn chân theo trục cẳng chân trong `_pose_hanging_leg_raise`, chỉnh khoảng trống trước gối/ống đồng trong `_pose_barbell_deadlift`, và cập nhật `EXERCISE_SPECS` + `sync_manifest_and_mock_json` giữ đúng slim bundle 5 file lõi / 28 bài CDN Railway.
  - Tài nguyên đã xuất: `assets_3d/source_blend/*.blend` (32 file), `assets_3d/exported_glb/*.glb` (33 file; lượt chỉnh cuối xuất lại 2 bài `HANGING_LEG_RAISE` và `BARBELL_DEADLIFT` theo `--only`), `mobile/assets/3d_bundled/*.glb` (giữ đúng 5 file lõi: `base_mannequin.glb`, `base_mannequin_female.glb`, `barbell_squat.glb`, `push_up.glb`, `barbell_bench_press.glb`, tổng `6,867,500` bytes / ~`6.55 MiB` `< 40 MB`), và đồng bộ SHA-256 trong `assets_3d/exported_glb/assets_manifest.json` + `mobile/assets/mock_json/mock_m2_exercises.json`.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Giữ toàn bộ 33 `.glb` không bật nén Draco (`KHR_draco_mesh_compression = False`, max `12,796 triangles <= 25,000`) để `model_viewer_plus` dựng 100% offline không cần WASM CDN; 28 bài mở rộng tiếp tục phục vụ qua Railway CDN (`assets_3d/exported_glb/`) giữ gói APK/AAB nhẹ `< 40 MB`.
  - Chuẩn hóa dấu quaternion (`prev_q.dot(q) < 0.0 -> -q`) ngay trước `keyframe_insert` và căn trực tiếp trục `Z` của `Forearm_L/R` không qua `atan2` giúp triệt tiêu hoàn toàn hiện tượng nhảy xoay 360° khi nội suy frame.
- **Kiểm tra / Kết quả chạy thử:**
  - Kiểm định 100 frame (`f = 1..100`) toàn bộ **30/30** file `.blend`: mọi xương trên cả `Anim_GoodForm` & `Anim_BadForm` đều mượt `< 12 deg/frame` và `0` lần đảo dấu quaternion (`ZERO q_flips`).
  - Kiểm định riêng sau lượt sửa 2 bài (`abs_hanging_leg_raise.blend`, `back_barbell_deadlift.blend`):
    - `abs_hanging_leg_raise.blend`: `min_fwd = +0.552`, `min_zdot >= +0.995`, `max_step <= 3.9 deg/frame`, `q_flips = 0`.
    - `back_barbell_deadlift.blend` (World-space `BVHTree.overlap` thanh đòn với gối/ống đồng/bàn chân/cơ/đầu): `hits = []`, `min_z >= +0.003 m`, `max_grip <= 0.31 cm`, `max_step <= 3.3 deg/frame`, `q_flips = 0`.
  - `flutter test test/workout/` trong `mobile/`: **19/19 PASS** (`All tests passed!`).
- **Việc cần làm ở phiên kế tiếp:**
  - Người dùng kiểm tra trực quan cuối `abs_hanging_leg_raise.blend` và `back_barbell_deadlift.blend` trong ứng dụng/Blender và kiểm thử đồng bộ CDN các bài `.glb` vừa cập nhật SHA-256 trên môi trường thật.

---

## Phiên 31 — 2026-11-22 20:30 | Thành viên: M4 (Pure AI Engineer) | Task: `T-M4-02` (`[x]`), `T-M4-01` (`[~]`)
- **Mục tiêu phiên:** Khởi động phần AI của M4: sinh dữ liệu Banister cho Model C và chuẩn bị pipeline dataset cho Model B.
- **Những file đã tạo / chỉnh sửa (`0` file `[LOCKED STUB]` bị chạm):**
  - `ai_research/model_c_readiness_ml/generate_banister_data.py`: viết lại đầy đủ (mô phỏng lịch tập 35 ngày, 12 đặc trưng, nhãn `readiness_score` + 11 nhãn `fatigue_Mat_Muscle_*`, sanity check, CLI `--check`).
  - `ai_research/model_c_readiness_ml/README.md`, `ai_research/model_b_food_yolo/README.md`: hướng dẫn chạy.
  - `ai_research/model_b_food_yolo/food_classes.py`: 18 lớp cốt lõi v1.0 khớp `class_code` của `food_nutrition_catalog` + bảng alias.
  - `ai_research/model_b_food_yolo/prepare_dataset.py`: gộp nhãn, lọc bbox lỗi, khử ảnh trùng, chia 70/20/10 phân tầng, ghi `data.yaml`, kiểm tra hợp lệ.
  - `ai_research/evaluation_reports/banister_data_report.json`: báo cáo sanity check.
  - `docs/taskboard.md`, `session_log.md`: cập nhật tiến độ.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - **Spec mục 5.2.3 có công thức ngược chiều:** `exp(-Δt / (τ · RF))` với RF < 1 làm hồi phục NHANH hơn khi thiếu ngủ/đạm. Code dùng `exp(-Δt / (τ / RF))` đúng yêu cầu DoD "thiếu ngủ/thiếu đạm làm chậm hồi phục". Khi viết `ai_readiness_ml.py`/`feature_extractor.py` phải dùng cùng chiều này. Cần M3/nhóm sửa lại câu chữ spec.
  - `compute_recovery_factor` chặn `protein_compliance` ở `[0, 1]` (ăn dư đạm không làm phục hồi nhanh hơn).
  - Nhãn readiness là hàm quy tắc sinh lý + nhiễu Gauss (σ=1.5): R² rất cao trong kiểm tra nhanh chỉ chứng minh dữ liệu học được, chưa phản ánh sai số trên người thật. Cần tinh chỉnh bằng RPE thực ở `T-M4-11`.
  - CSV sinh ra nằm ở `ai_research/datasets/model_c/` (đã bị `.gitignore` chặn); chạy lại lệnh bên dưới để tái tạo.
  - Không tải được dataset Roboflow/Kaggle từ môi trường này (mạng bị chặn); `T-M4-01` giữ `[~]`.
- **Kiểm tra / Kết quả chạy thử:**
  - `python generate_banister_data.py --n-samples 15000 --seed 42 --check`: PASS; 0 vi phạm chiều phục hồi trên 2.760 ca; readiness trung bình ~75,5; tỉ lệ READY ~56% / MODERATE ~41% / REST_RECOMMENDED ~3%.
  - `prepare_dataset.py` đã chạy thử trên dataset giả có lỗi cố ý (bbox tràn biên, quá nhỏ, polygon, ảnh trùng, lớp lạ, thiếu nhãn): lọc đúng và validator bắt được nhãn bị phá.
- **Việc cần làm ở phiên kế tiếp:**
  - Tải dataset thật từ Roboflow Universe/Kaggle về `ai_research/datasets/raw/`, chạy `prepare_dataset.py`, bổ sung alias theo `unmapped_source_classes`, đạt `data.yaml` 15–20 lớp rồi đóng `T-M4-01`.
  - `T-M4-05`: viết `benchmark_models.py` (XGBoost vs LightGBM vs MLP) trên CSV Banister.
  - `T-M4-03`: rà lại stub `ai.py`/`ai_schema.py` rồi đóng task.

---

## Phiên 30 — 2026-11-22 18:40 | Thành viên: M1 + M2 | Task: Kiểm thử toàn diện & Bugfix theo `note.md` + Build Release APK
- **Mục tiêu phiên:** Thực hiện toàn bộ checklist trong `note.md` (Mục 0–5): kiểm tra tĩnh & unit/widget tests, khắc phục các lỗi UI copy/responsive `360dp + font_scale 1.3x` và self-healing SQLite Gym 3D phát hiện thêm, build & xác minh Release APK chuẩn CH Play, chạy E2E trên máy ảo Android 15 (`VigorAI_Pixel6_API35`) kết nối live Railway (`https://vigorai-production.up.railway.app`).
- **Những file đã tạo / chỉnh sửa (`0` file `[LOCKED STUB]` bị chạm):**
  - **Sửa lỗi M1 (`[OWNER: M1]`):**
    - `mobile/lib/features/auth_privacy/presentation/register_screen.dart`: Gỡ `(Bulk)`, `(Cut)`, `(Maintain)` khỏi 3 lựa chọn mục tiêu tập luyện, chuẩn hóa tiếng Việt (`Tăng cơ`, `Giảm mỡ`, `Giữ dáng`).
    - `mobile/lib/features/health/biometrics/presentation/biometrics_screen.dart`: Bọc `weightKg` trong `Flexible(flex: 5, child: FittedBox(...))` cạnh `Expanded(flex: 6)` badge BMI tránh tràn; đổi legend `Row` sang `Wrap`.
    - `mobile/lib/features/health/presentation/health_dashboard_screen.dart`: Bọc `Expanded` + `ellipsis` cho tiêu đề `Bước chân` và `Giấc ngủ`; đổi nhóm nút `+250 ml` / `+500 ml` / `Chi tiết` sang `Wrap`.
    - `mobile/lib/features/health/nutrition/presentation/nutrition_screen.dart`: Gỡ `Row` đơn thừa và bọc `Expanded`/`Flexible(FittedBox)` cho `_MacroBar`.
    - `mobile/lib/features/health/progress_photos/presentation/progress_photos_screen.dart`: Đưa 3 chip tư thế `Trước` / `Nghiêng` / `Sau` vào `Row` 3 cột `Expanded` (`FittedBox`) để luôn nằm trên 1 hàng ở `360dp + 1.3x`.
    - `mobile/lib/features/health/sleep/presentation/sleep_screen.dart`: Chuyển hàng đánh giá sao sang `Wrap` với nút `36x36`, tránh tràn ở `360dp + 1.3x`.
    - `mobile/lib/features/health/food_scan/presentation/food_scan_screen.dart`: Chuyển khung ảnh giữ chỗ sang `BoxConstraints(minHeight: 160)` tránh bóp/tràn ở cỡ chữ lớn.
    - `mobile/test/health/ui_layout_and_copy_test.dart` *(mới)*: 10 widget tests kiểm tra layout tại `360x780` + `TextScaler.linear(1.3)` và bảo toàn trích dẫn y tế/bỏ chuỗi CNTT cấm.
    - `mobile/test/health/health_sprint2_test.dart`: Bổ sung unit test hồi quy self-healing trùng `DailyHealthLogs` trên `addWaterMl` & `pullServerUpdates`.
  - **Sửa lỗi M2 (`[OWNER: M2]`):**
    - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Thêm tham số `useMockApi` tiêm qua constructor và nhận diện dòng `ex-*` trong `loadExercises()` để tự động làm mới từ `/api/v1/exercises` ngay khi có mạng.
    - `mobile/lib/features/gym3d/presentation/gym3d_library_screen.dart`: Bọc danh sách (và trạng thái rỗng) trong `RefreshIndicator` gọi `loadExercises(forceRefresh: true)`.
    - `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart`: Tăng `_loadTimeoutTimer` từ `8s` lên `15s` giúp máy yếu/khởi tạo WebView lạnh không báo nhầm lỗi timeout khi đang dựng WebGL (lỗi thật từ `<model-viewer>` vẫn bắt tức thì qua event `error`).
    - `mobile/test/workout/workout_sprint2_test.dart`: Bổ sung test SQLite trong bộ nhớ cho `deduplicateByCode` và quá trình chuyển `ex-*` offline -> UUID server online.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Tất cả 33 file `.glb` trong `assets_3d/exported_glb/` đều không dùng nén Draco (`KHR_draco_mesh_compression = False`) và `model_viewer_plus` phục vụ `model-viewer.min.js` + asset cục bộ hoàn toàn offline. Tuy nhiên ở kịch bản máy ảo chạy headless `-gpu swiftshader_indirect`, lần khởi tạo Chromium WebView đầu tiên ngay sau `pm clear` khi offline có thể vượt ngưỡng 15s do biên dịch shader WebGL bằng CPU; sau khi WebView ấm, cả bài Bundled lẫn Cloud đã cache trong `3d_assets/` đều dựng và chạy animation 100% offline.
  - Ghi nhận thẩm mỹ nhỏ ở tab `Radar Cơ` (`AiCoachHubScreen`): chữ `Ngực (0)` hơi sát dòng phụ đề ngay phía trên tại mật độ mặc định, chưa gây `RenderFlex overflowed`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0 errors · 0 warnings**; 26 info `deprecated_member_use` của `package:flutter/material.dart`).
  - `flutter test test/health/ test/workout/`: **41 / 41 PASS** (`12` test trong `health_sprint2_test.dart`, `10` test trong `ui_layout_and_copy_test.dart`, `19` test trong `workout_sprint2_test.dart`).
  - Quét tĩnh 34 file trong `mobile/lib/features/**/*.dart`: **0** chuỗi CNTT/mã nội bộ cấm; bảo toàn `Mifflin-St Jeor`, `Epley`, `Brzycki`, Miễn trừ Y tế Onboarding & AI disclaimer.
  - Build & Kiểm tra APK Release: `mobile/build/app/outputs/flutter-apk/app-release.apk` (`68,760,617` bytes / `65.58 MB`); ký `CN=VigorAI, OU=Mobile, O=VigorAI Team, L=Ho Chi Minh, ST=HCM, C=VN` (SHA-256 `0629aa11216b6bf38aa06475c4e0e9436d39eca21ddca143a94aef6a82eac321`); merged `AndroidManifest.xml` chứa **0** quyền CH Play bị cấm (chỉ giữ 10 quyền hợp lệ).
  - E2E Emulator Android 15 (`VigorAI_Pixel6_API35`) bản Release với live Railway: Onboarding, Login (`demo@vigorai.app` -> `Nguyễn Văn An`), Register, `360dp / 480dpi + font_scale 1.3` (Dashboard & Biometrics cân đối), toàn bộ màn hình chi tiết Health, `Gym3DLibraryScreen` + Bundled & Cloud 3D (`Deadlift đòn tạ` tải CDN, kiểm tra SHA-256 & dựng 3D), `AiCoachHubScreen` (`Phục hồi 3D` 79 điểm + `Volume & PR` + `Radar Cơ`), `LiveWorkoutLoggerScreen`, Đồng bộ live (`Đồng bộ hoàn tất (1 mục).`, badge về `0`), và kịch bản `pm clear` offline -> online (`ex-*` được thay sạch bằng UUID PostgreSQL khi kéo làm mới, mở tuần tự 5 bài tập). Logcat: **0** `Bad state: Too many elements`, **0** `RenderFlex overflowed`, **0** `FATAL EXCEPTION`.
- **Việc cần làm ở phiên kế tiếp:**
  - Cài `app-release.apk` lên máy Android thật có GPU phần cứng để kiểm tra thêm thao tác xoay/zoom 3D bằng tay, chụp/chọn ảnh thật (`FoodScan` / `ProgressPhotos`), rồi tách 2 PR sạch (`[OWNER: M1]`, `[OWNER: M2]`) và push sau khi người dùng xác nhận (không tự ý push Git trong phiên này).

---

## Phiên 29 — 2026-11-22 10:05 | Thành viên: M1 + M2 (Fix 3 lỗi UI Copy, Layout Biometrics & Gym 3D Duplicate SQLite) | Task: Bugfix Pre-Test Release
- **Mục tiêu phiên:** Xử lý triệt để 3 lỗi thực tế phát hiện khi test máy thật: (1) lược bỏ chữ kỹ thuật CNTT/mã nội bộ và tiếng Anh thừa gây bể layout trên toàn bộ màn hình Mobile trong khi vẫn giữ đầy đủ CH Play Guardrails, (2) sửa lỗi tràn viền thẻ BMI & lệch kích thước 3 khung chỉ số ở `BiometricsScreen`, (3) sửa triệt để lỗi `Bad state: Too many elements` khi mở chi tiết bài tập trong Phòng tập 3D, đồng thời tạo `note.md` (chặn qua `.gitignore`) lưu checklist test trên máy có Android Studio.
- **Những file đã tạo / chỉnh sửa:**
  - **Phòng tập 3D & Chống trùng SQLite (`[OWNER: M2]` + phòng ngừa `[OWNER: M1]`):**
    - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Bổ sung `pickPreferredByCode`, `deduplicateByCode`, `_cleanupDuplicateRows` tự chữa lành dòng trùng `code` (giữa ID `ex-*` mock và UUID server); bỏ `.getSingleOrNull()` ở `getExerciseByCode` thay bằng `.get()` + tự xóa dòng thừa; bọc `_upsertExercises` trong transaction dọn sạch ID cũ trùng `code` trước khi chèn.
    - `mobile/lib/features/gym3d/presentation/exercise_3d_detail_screen.dart`: Thay màn hình báo lỗi raw exception thành thông báo thân thiện kèm nút **Thử lại**; sửa thanh tua pha chống tràn ngang và bỏ `(30 FPS)`.
    - `mobile/lib/features/health/data/health_repository.dart`, `mobile/lib/core/sync/sync_queue_manager.dart`, `mobile/lib/features/workout/data/workout_repository.dart`: Gia cố phòng ngừa cùng lỗi `Bad state: Too many elements` cho các truy vấn `dailyHealthLogsTable` theo `logDateIso` (đổi sang `.get()` sắp theo `updatedAt desc` + tự dọn trùng).
    - `mobile/test/workout/workout_sprint2_test.dart`: Bổ sung unit test hồi quy kiểm chứng `ExerciseRepository.deduplicateByCode` ưu tiên UUID server + URL hợp lệ.
  - **Layout Hình 3 & Dashboard (`[OWNER: M1]`):**
    - `mobile/lib/features/health/biometrics/presentation/biometrics_screen.dart`: Đưa `weightKg` + badge `BMI` (`FittedBox` bên trong `Expanded`) lên hàng riêng, chuyển dòng `Cập nhật` xuống dưới để hết văng ra ngoài khung; bọc 3 `_MetricTile` (`Tỷ lệ mỡ`, `Khối cơ`, `TB 7 ngày`) bằng `IntrinsicHeight` + `CrossAxisAlignment.stretch` và bỏ `margin` lệch phải để 3 khung cân đối tuyệt đối.
    - `mobile/lib/features/health/presentation/health_dashboard_screen.dart`: Bọc `Expanded` cho tiêu đề thẻ Nước & Thực phẩm bổ sung tránh đè số; chuyển 2 thẻ `Quét món AI` / `Ảnh tiến độ` sang `IntrinsicHeight` + bố cục gọn để không bẻ 4 dòng.
  - **Lược bỏ chữ kỹ thuật CNTT & mã nội bộ (`[OWNER: M1]` & `[OWNER: M2]`):**
    - `[OWNER: M1]`: `health_dashboard_screen.dart` (gỡ unused import `api_endpoints.dart`), `biometrics_screen.dart`, `nutrition_screen.dart`, `food_scan_screen.dart`, `progress_photos_screen.dart`, `hydration_screen.dart`, `sleep_screen.dart`, `supplements_screen.dart`, `onboarding_disclaimer_screen.dart`, `login_screen.dart` (gỡ unused import `api_endpoints.dart`), `register_screen.dart`, `auth_controller.dart`, `health_repository.dart`.
    - `[OWNER: M2]`: `gym3d_library_screen.dart`, `exercise_3d_detail_screen.dart`, `live_workout_logger_screen.dart`, `routines_screen.dart`, `exercise_swapper_sheet.dart`, `plate_calculator_sheet.dart`, `ai_coach_hub_screen.dart`, `readiness_recovery_3d_view.dart`, `ai_analytics_repository.dart`.
  - **Ghi chú kiểm thử cục bộ & `.gitignore` (`[LOCKED STUB]` theo chỉ định trực tiếp của người dùng):**
    - Tạo `note.md` (checklist chạy `flutter analyze`, `flutter test`, test cài đè chữa lành dữ liệu 3D, test layout 360dp/font 1.3x, soát text UI) và thêm `note.md` vào `.gitignore` *(lưu ý tách commit `.gitignore` thành Micro-PR riêng khi push Git)*.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Bảo toàn 100% CH Play Policy Guardrails: giữ nguyên Miễn trừ Y tế ở Onboarding, trích dẫn `Mifflin-St Jeor (1990)` ở `NutritionScreen`, trích dẫn `Epley/Brzycki` ở `LiveWorkoutLoggerScreen`/`VolumeAnalyticsView` và thẻ `disclaimer` ở `FoodScanScreen` + `ReadinessRecovery3DView`.
  - Chỉ xóa chữ kỹ thuật CNTT/mã nội bộ (`F01`–`F26`, `M2`/`M4`, `Model B/C`, `SQLite`, `Offline-First`, `WorkManager`, `Photo Picker`, `Blender MCP`, `YOLOv8`, `MVP`, `Cloud 3D`, `3D Offline Ready`, `modelVersion`, `useMockApi`...) và chỉ rút gọn tiếng Anh ở những nơi làm bể layout.
- **Kiểm tra / Kết quả chạy thử:**
  - Đã chạy kiểm chứng trên **Flutter 3.50.1 / Dart 3.14.0**: `flutter pub get` & `dart run build_runner build` OK, `flutter analyze --no-fatal-infos` Exit `0` (**0 errors · 0 warnings**), `flutter test test/health/ test/workout/` **28 / 28 PASS** (gồm unit test hồi quy mới `deduplicates duplicate exercise codes and prefers server UUID with non-stale URL`).
  - Đã gỡ lại Android Studio/SDK/Flutter trên máy phụ do máy yếu; còn phần test UI trực quan & cài đè máy thật/emulator sẽ chạy trên máy chính theo `note.md`.
- **Việc cần làm ở phiên kế tiếp:**
  - Khi về máy có Android Studio & Flutter SDK, chạy toàn bộ checklist trong `note.md` (`flutter analyze`, `flutter test`, cài đè APK test self-healing Phòng tập 3D & layout `BiometricsScreen`).

---

## Phiên 28 — 2026-11-21 22:34 | Thành viên: M3 + M2 (CDN 3D Cloud Offload & Release APK Test) | Task: `T-M3-09` (`[x]` Hoàn tất) & Gỡ 28 `.glb` mở rộng khỏi Bundle Mobile
- **Mục tiêu phiên:** Hoàn tất `T-M3-09` (tách 28/31 bài tập `.glb` mở rộng lên Cloud/Railway S3 Bucket + FastAPI CDN endpoint), thu gọn `mobile/assets/3d_bundled/` từ `44.38 MB` xuống `6.53 MiB` (`6.85 MB`), deploy live lên Railway và build file `app-release.apk` trỏ thẳng Server Production để test máy thật.
- **Những thay đổi đã thực hiện:**
  - **Backend (`[OWNER: M3]`):**
    - `backend/app/core/config.py`: Bổ sung `API_PUBLIC_BASE_URL`, `LOCAL_GLB_ASSETS_DIR`, `S3_ADDRESSING_STYLE` và property `resolved_api_public_base_url`.
    - `backend/app/db/seed_catalog_and_exercises.py`: Nâng danh mục từ `30` lên đủ **`39` bài tập** (bổ sung 9 bài Sprint 2 còn thiếu từ `mock_m2_exercises.json`), cập nhật SHA-256 chuẩn từ `assets_manifest.json` cho 3 bài bundled + 28 bài CDN và fallback `base_mannequin.glb` cho 8 bài chưa có `.glb` riêng.
    - `backend/app/services/storage_service.py`: Nạp `assets_manifest.json`, bổ sung `sync_local_glb_assets_to_s3()` (upload idempotent toàn bộ `.glb` lên Railway Storage Bucket `gym3d-assets` dùng virtual-host addressing style), `get_presigned_glb_url()`, `get_local_glb_path()`.
    - `backend/app/routers/exercises.py`: Mở endpoint `GET /api/v1/exercises/{code}/glb` (trả `307` presigned S3 URL hoặc fallback `FileResponse` HTTPS kèm header `X-Asset-Sha256`) và trả full URL HTTPS thực tế theo `request` / `API_PUBLIC_BASE_URL`.
    - `backend/Dockerfile.railway`, `railway.json`, `backend/docker-compose.yml`, `backend/app/db/startup.py`, `backend/tests/test_core_api.py`: Đóng gói `assets_3d/exported_glb/` vào image Railway (`/app/assets_3d_glb`), đồng bộ `.glb` lên S3 lúc khởi động và cập nhật test contract `39` bài + tải `.glb`.
  - **Mobile (`[OWNER: M2]`):**
    - Giữ nguyên **33 file `.glb`** gốc tại `assets_3d/exported_glb/`; xóa **28 file `.glb` mở rộng** khỏi `mobile/assets/3d_bundled/` (chỉ giữ 5 file lõi: `base_mannequin.glb`, `base_mannequin_female.glb`, `barbell_squat.glb`, `push_up.glb`, `barbell_bench_press.glb` = `6,849,660 B` ≈ `6.53 MiB`).
    - Cập nhật `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json` đồng bộ `bundled: false` và URL HTTPS `/api/v1/exercises/{CODE}/glb` + SHA-256 thật cho 28 bài CDN.
    - `mobile/lib/features/gym3d/data/asset_cache_manager.dart`: Dùng `Dio` sạch độc lập cho `AssetCacheManager` (không gắn `AuthInterceptor` tránh lỗi `400` khi redirect presigned URL S3, tăng `receiveTimeout = 60s`).
    - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Thu gọn `_localBundledGlbs` về 3 bài MVP, tự làm mới URL cũ (`localhost:9000`/`cdn.vigorai.app`/`assets/3d_bundled/` cũ) khi sync offline/SQLite và phân biệt chính xác `isBundled` vs 8 bài fallback.
    - `mobile/lib/features/gym3d/presentation/gym3d_library_screen.dart`: Gắn nhãn chip `Cloud 3D` cho 28 bài tải lười từ Server CDN.
  - **Tiến độ:** `docs/taskboard.md` đóng `[x]` **`T-M3-09`** (`M3: 11/15 Done`, `Tổng: 30/63 Done`).
- **Kiểm tra & Triển khai:**
  - `python -m py_compile` 6 file Python sửa: Exit `0`.
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0 errors · 0 warnings**).
  - `flutter test test/workout/ test/health/`: **27 / 27 PASS**.
  - Railway Storage Bucket `gym3d-assets` (`8414403c`, `sjc`, virtual-host) & Deployment `f1a0afff-30cf-4370-a45f-de07c881b733` (`[SUCCESS]`): đồng bộ **33/33 file `.glb`** (`uploaded=33, skipped=0, failed=0`), `seed=39 exercises`; xác minh live `GET /healthz` (`200 OK`), `GET /api/v1/exercises` (`39` bài), và tải `GET /api/v1/exercises/LAT_PULLDOWN/glb` chuyển hướng `307` sang `https://gym3d-assets-hzz2h5xxtlks.t3.storageapi.dev/exercises/lat_pulldown.glb` (`1,432,108 B`, SHA-256 `5fe27fe31087...` khớp `100%` `assets_manifest.json`).
  - Release APK test máy thật: build sạch tại `mobile/build/app/outputs/flutter-apk/app-release.apk` (`68,645,929 B` / `65.47 MB` universal fat APK gồm 3 ABI `arm64-v8a` + `x86_64` + `armeabi-v7a`; `assets/flutter_assets/assets` chỉ còn `6.59 MB` sau tách CDN), xác minh chữ ký v2 `CN=VigorAI, O=VigorAI Team` qua `apksigner.bat` và `0` quyền cấm CH Play trong Merged Manifest.
- **Việc cần làm ở phiên kế tiếp:**
  - Cài `app-release.apk` lên máy Android thật test Full luồng 3D Cloud Lazy-Loading (`--dart-define=MVP_CLOSED_TESTING=false`), Health/Workout Offline-First và chuẩn bị đóng gói `.aab` `v1.1.0` (`T-M2-12`).

---

## Phiên 27 — 2026-11-21 22:18 | Thành viên: M2 (Rà soát & Nghiệm thu Sprint 2) | Task: `T-M2-08`, `T-M2-09`, `T-M2-10`, `T-M2-11` (`[x]` Đóng hoàn tất)
- **Mục tiêu phiên:** Sau khi merge PR #11 (`1458ab3`), chạy `flutter analyze` & `flutter test`, rà soát và sửa triệt để toàn bộ cảnh báo biên dịch và lỗi logic trên 4 tasks Sprint 2 của M2 (`T-M2-08`–`T-M2-11`), tuân thủ chặt `[OWNER: M2]` và không chạm `[LOCKED STUB]`.
- **Những file đã sửa (`[OWNER: M2]`):**
  - `mobile/lib/features/workout/domain/workout_calculators.dart`: Bổ sung hàm thuần Dart `calculateWorkoutHydrationBonusMl` mặc định `avgRpe = 0.0` khi không có set ghi RPE (tránh cộng nhầm `+750ml` cho buổi tập ngắn chưa nhập RPE).
  - `mobile/lib/features/workout/data/workout_repository.dart`: Sửa `_applyHydrationWorkoutBonus` dùng ngày **Local** (`localDateIso()`), ID `'daily-$todayIso'` đồng nhất với M1 và đọc cân nặng mới nhất từ `biometricLogsTable` (`35ml × kg`); cập nhật `syncStatus = 'SYNCED'` cho cả `workout_sets` sau khi `POST /workouts/sessions` thành công; bổ sung `_loadValidSessionIds()` lọc bỏ buổi `ABANDONED`/`CANCELLED` hoặc đã xóa mềm khỏi `getHistoricalBest1Rm` & `getLastPerformanceForExercise`.
  - `mobile/lib/features/workout/presentation/live_workout_logger_screen.dart`: Tách `ValueKey` ô Tạ/Reps sang `rowKey` + `inputVersion` cố định để hết lỗi mất focus/reset mỗi 1s do timer buổi tập; khóa sửa các hiệp đã tick hoàn thành; lưu `lockedExerciseCode`/`lockedExerciseNameVi` tránh `_swapExercise` ghi đè mã bài của hiệp cũ; sửa khôi phục Crash-safe `IN_PROGRESS` giữ nguyên phần còn lại của giáo án trong `routineId`; invalidate đủ `analyticsSummaryProvider(7, 30, 90, 365)` sau khi kết thúc buổi tập.
  - `mobile/lib/features/workout/presentation/routines_screen.dart`: Thay key theo `$index` bằng `_EditableRoutineItem(uid)` bền vững, chuẩn hóa `orderIndex` và dọn `supersetGroupId` mồ côi khi xóa/ghép bài, chuyển `onReorder` sang `onReorderItem`.
  - `mobile/lib/features/ai_analytics/data/ai_analytics_repository.dart`: Thêm `await` trước `_overlayLocal72hFatigue` ở `fetchReadinessAndOverload` (diệt warning `unawaited_return_in_try_block`), bật `unsyncedOnly: true` tránh cộng đôi mỏi cơ 72h từ các buổi đã sync với Server, đồng bộ ngày mock/local date cho cache offline, loại bỏ fallback sang `mock_m4_ai.json` trong build production offline; ở `aggregateAnalyticsFromData` lọc buổi `COMPLETED` hợp lệ trước khi tính PR/streak/volume/radar, dùng key tuần đủ năm `YYYY-MM-DD`, và sửa `pullPushRatio` (`0.0` khi rỗng, `pullSets.toDouble()` khi chưa có đẩy).
  - `mobile/lib/features/ai_analytics/muscle_balance/muscle_radar_view.dart` & `mobile/lib/features/ai_analytics/presentation/ai_coach_hub_screen.dart`: Cập nhật thông báo khi Radar trống hoặc chỉ có bài Kéo, và invalidate đủ 4 mốc (`7, 30, 90, 365`) khi làm mới.
  - `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart`, `exercise_3d_detail_screen.dart`, `gym3d_library_screen.dart`, `exercise_repository.dart`: Bổ sung `effectiveScaleFor` chống thu nhỏ 2 lần trên `base_mannequin_female.glb`, đồng bộ `_phaseTimer` chỉ chạy sau khi `onModelLoaded`, cập nhật text banner thư viện 3D (`đủ 10 nhóm cơ`), và làm mới cache metadata bài tập khi mock JSON cập nhật checksum/URL.
  - `mobile/test/workout/workout_sprint2_test.dart`, `docs/taskboard.md`: Bổ sung 3 unit test hồi quy mới và đóng `[x]` cho `T-M2-08`, `T-M2-09`, `T-M2-10`, `T-M2-11` (`M2: 10/17 Done`, `Tổng: 29/63 Done`).
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0 errors · 0 warnings**; hết warning `unawaited_return_in_try_block` và hết info `onReorder`).
  - `flutter test test/workout/ test/health/`: **27 / 27 PASS** (`asset_cache_manager_test.dart` `5/5`, `workout_sprint2_test.dart` `11/11` gồm benchmark 1.000 hiệp `< 300ms`, `health_sprint2_test.dart` `11/11`).
  - `git status -s`: Chỉ chạm các file thuộc `[OWNER: M2]` + `docs/taskboard.md` + `session_log.md`; `0` file `[LOCKED STUB]` bị sửa.
- **Việc cần làm ở phiên kế tiếp:**
  - Trước mốc đóng gói `T-M2-12` (`.aab` `v1.1.0 < 40 MB`), phối hợp `M3` (`T-M3-09`) upload 27–30 file `.glb` mở rộng lên MinIO/CDN để tách khỏi `mobile/assets/3d_bundled/` (hiện tại `34` file = `44.38 MB`), chỉ giữ gói lõi trong APK/AAB.

---

## Phiên 26 — 2026-11-21 21:42 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[x]` Hoàn tất 100% — Nhóm 10 Bụng & Lõi / Abs & Core — 3 bài, tổng **30/30** bài `gym.txt`)
- **Phạm vi thực hiện (Strict `[OWNER: M2]`):**
  - Hoàn thiện **3 bài Nhóm 10 Cơ Bụng & Lõi (`Abs & Core`)** trong `gym.txt` qua Blender 5.3 headless script (`build_sprint2_exercises.py`), nâng tổng tiến độ `T-M2-07` lên **30/30 bài (100%)** và tổng asset `.glb` đồng bộ lên **33/33 file** (gồm 2 Mannequin Nam/Nữ + `PUSH_UP` MVP + 30/30 bài `gym.txt`):
    1. `HANGING_LEG_RAISE` (*Treo người nâng chân*): `hanging_leg_raise.glb` (`1,412,008 B`, `12,176 tris`, SHA-256 `f55ba36ec0de...`) & `abs_hanging_leg_raise.blend` (`Anim_GoodForm` kiểm soát cuộn xương chậu nâng chân song song/cao không đung đưa vs `Anim_BadForm` đánh lăng hông kipping lấy đà; dùng giàn Pull-Up `Equip_PullUpRig`).
    2. `CABLE_CRUNCH` (*Quỳ gối gập bụng với dây cáp*): `cable_crunch.glb` (`1,462,356 B`, `12,292 tris`, SHA-256 `3fa1f8256071...`) & `abs_cable_crunch.blend` (`Anim_GoodForm` khóa hông quỳ trên thảm `Equip_KneelingMat` & cuộn tròn cột sống ngực `24° -> 96°`, giữ đầu dây thừng cạnh thái dương vs `Anim_BadForm` giữ lưng thẳng đơ & ngồi lùi hông về gót; tinh chỉnh độ cao gối để không xuyên đáy thảm).
    3. `PLANK` (*Chống khuỷu tay giữ thẳng người*): `plank.glb` (`1,395,112 B`, `11,860 tris`, SHA-256 `6001ec404432...`) & `abs_plank.blend` (`Anim_GoodForm` giữ đường thẳng vai–hông–cổ chân trên thảm `Equip_Mat` với nhịp thở siết core vs `Anim_BadForm` lỗi kép đẩy hông chữ V ở `f=1` rồi sụp võng thắt lưng ở `f=50`; tinh chỉnh góc cổ chân/bàn chân chống chuẩn trên mặt thảm `Z >= 0.018`).
- **Files đã tạo / cập nhật:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py` (cập nhật & tinh chỉnh pose `_pose_cable_crunch`, `_pose_plank`)
  - `assets_3d/exported_glb/{hanging_leg_raise,cable_crunch,plank}.glb` & `mobile/assets/3d_bundled/{hanging_leg_raise,cable_crunch,plank}.glb` (bit-for-bit giống nhau)
  - `assets_3d/source_blend/abs_{hanging_leg_raise,cable_crunch,plank}.blend`
  - `assets_3d/exported_glb/assets_manifest.json` (đồng bộ đủ `33` assets) & `mobile/assets/mock_json/mock_m2_exercises.json` (cập nhật `bundled: true`, SHA-256, `name_vi` cho `PLANK`)
  - `mobile/lib/features/gym3d/data/exercise_repository.dart` (thêm mapping `HANGING_LEG_RAISE`, `CABLE_CRUNCH`, `PLANK` vào `_localBundledGlbs`)
  - `docs/taskboard.md` (chuyển trạng thái `T-M2-07` sang `[x]`)
- **Kiểm chứng & Kết quả:**
  - Kiểm tra trực quan bằng Blender 5.3 EEVEE (`render_previews.py` đa góc & đa khung hình `f=1, 25, 50, 75, 100`), phát hiện & sửa dứt điểm lỗi mũi chân `PLANK` xuyên đáy thảm và lỗi gối `CABLE_CRUNCH` (`Anim_BadForm`) sát đáy thảm, sau đó render & kiểm tra lại sạch 100%.
  - Chạy script kiểm chứng headless `verify_sprint2_abs_all30.py` trên Blender 5.3 (`exit 0`): toàn bộ `33/33` file `.glb` đạt `GLB_OK` (`11,848 – 12,796 tris <= 25,000`, `1,315,064 – 1,462,356 B` trong ngưỡng `800KB–2.5MB`, đủ 11 `Mat_Muscle_*`, `clips=['Anim_GoodForm', 'Anim_BadForm']`), `REPO_AND_MOCK_ALL30_OK`, 3 file `abs_*.blend` đạt `BLEND_OK`, `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`.
  - `git status -s` xác nhận mọi thay đổi nằm đúng phạm vi `[OWNER: M2]` + `docs/taskboard.md` + `session_log.md`; không chạm file `[LOCKED STUB]` hay code M1/M3/M4. *(Lưu ý: máy Windows hiện tại chưa cài Flutter SDK nên chưa chạy `flutter analyze`/`flutter test` cục bộ.)*
- **Bước tiếp theo:**
  - Sẵn sàng để `M3` upload toàn bộ gói `.glb` lên MinIO/CDN (`T-M3-09`) và chạy CI `flutter analyze` / `flutter test` kiểm tra màn hình Gym 3D trên thiết bị/emulator.

---

## Phiên 25 — 2026-11-21 21:29 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 9 Cơ Mông / Glutes — 3 bài, tổng **27/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng, kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 9: Cơ Mông (Glutes)** theo `gym.txt` (`BARBELL_HIP_THRUST`, `WALKING_LUNGE`, `CABLE_GLUTE_KICKBACK`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung `Phase 9` với `_build_hip_thrust_bench_object`, `_build_cable_kickback_station`, cài đặt `_pose_barbell_hip_thrust`/`build_barbell_hip_thrust`, `_pose_walking_lunge`/`build_walking_lunge`, `_pose_cable_glute_kickback`/`build_cable_glute_kickback` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `barbell_hip_thrust.glb` (`1,427,712 B`, `12,368 tris`, SHA-256 `2f6ef45ead36...`) + `assets_3d/source_blend/glutes_barbell_hip_thrust.blend`
    - `walking_lunge.glb` (`1,404,556 B`, `12,256 tris`, SHA-256 `874373cedaf6...`) + `assets_3d/source_blend/glutes_walking_lunge.blend`
    - `cable_glute_kickback.glb` (`1,410,336 B`, `12,148 tris`, SHA-256 `6d689cbd62ad...`) + `assets_3d/source_blend/glutes_cable_glute_kickback.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`30` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 9 (`"Đẩy hông với tạ đòn"`, `"Bước chùng chân với tạ đơn"`, `"Đá chân ra sau với dây cáp"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `BARBELL_HIP_THRUST`, `WALKING_LUNGE`, `CABLE_GLUTE_KICKBACK` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **27/30** bài (**90%**).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Đẩy hông với tạ đòn (`BARBELL_HIP_THRUST`):* Bục ghế ngang (`Y=+0.39..+0.75, Z_top=0.405`) đỡ đúng vùng bả vai trong suốt cung `30° -> 2°`, hai cẳng chân vuông góc `90°` với sàn (`Y=-0.40`), thanh đòn đặt trên nếp gấp hông; `Anim_BadForm` đặt chân gần mông (`Y=-0.22`), ưỡn vồng thắt lưng quá mức (`Pelvis Z=0.54`) và ngửa cổ ra sau ghế.
  - *Bước chùng chân với tạ đơn (`WALKING_LUNGE`):* Bước tách rộng chuẩn (`L` `Y=-0.34`, `R` `Y=+0.34`), hạ thẳng hông xuống `Z=0.51` tạo hai góc gối `90°–90°` giữ hai tạ đơn dọc hai bên hông không chạm đùi; `Anim_BadForm` bước ngắn (`-0.22`), lao gối trước quá mũi chân + chụm gối (Knee Valgus), nhấc gót và đổ lưng `34°`.
  - *Đá chân ra sau với dây cáp (`CABLE_GLUTE_KICKBACK`):* Ròng rọc thấp lệch phải `X=-0.14` thẳng hàng chân đá `R`, tay vịn ngực `Z=1.18`, sửa hướng khoen đai cổ chân `+Y` và giữ đường chân đá thẳng hợp lý (`GoodForm` `Y=+0.52, Z=0.44`; `BadForm` `Y=+0.66, Z=0.50` kèm võng lưng dưới rõ rệt) giúp dây cáp luôn đi dưới gối không cắt chân hay khớp gối.
- **Kiểm tra / Kết quả chạy thử:**
  - Render EEVEE đa góc & các mốc khung hình (`f=1, 25, 50, 75, 100`) qua Blender 5.3 CLI (`render_previews.py`) và kiểm tra ảnh trực quan sau lần chỉnh cuối xác nhận sạch xuyên thấu cho cả 3 bài.
  - Headless Blender 5.3 (`verify_sprint2_glutes.py`, exit 0): **30/30** `.glb` khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, kích thước hợp lệ (`1,315,064 B – 1,446,388 B`), đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,796 tris` (`< 25,000`), đủ `['Anim_GoodForm', 'Anim_BadForm']`; **3/3** file `.blend` mới và `mock_m2_exercises.json` / `exercise_repository.dart` hợp lệ; `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`; `git status -s` giữ nguyên biên `[OWNER: M2]`.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Mông; tiếp theo dựng **Nhóm 10 (nhóm cuối): Cơ Bụng & Lõi (Abs & Core)** gồm 3 bài trong `gym.txt` (`Treo người nâng chân`, `Quỳ gối gập bụng với dây cáp`, `Chống khuỷu tay giữ thẳng người`).

---

## Phiên 24 — 2026-11-21 21:18 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 8 Cơ Đùi sau / Hamstrings — 3 bài, tổng **24/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng, kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 8: Cơ Đùi sau (Hamstrings)** theo `gym.txt` (`ROMANIAN_DEADLIFT`, `LEG_CURL_MACHINE`, `SEATED_LEG_CURL`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung `Phase 8` với `_build_lying_leg_curl_machine`, `_build_seated_leg_curl_machine`, cài đặt `_pose_romanian_deadlift`/`build_romanian_deadlift`, `_pose_leg_curl_machine`/`build_leg_curl_machine`, `_pose_seated_leg_curl`/`build_seated_leg_curl` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `romanian_deadlift.glb` (`1,417,600 B`, `12,284 tris`, SHA-256 `1792c1eca5d8...`) + `assets_3d/source_blend/hamstrings_romanian_deadlift.blend`
    - `leg_curl_machine.glb` (`1,417,128 B`, `12,520 tris`, SHA-256 `9b981f5936df...`) + `assets_3d/source_blend/hamstrings_leg_curl_machine.blend`
    - `seated_leg_curl.glb` (`1,428,052 B`, `12,796 tris`, SHA-256 `e6c35a0db5dc...`) + `assets_3d/source_blend/hamstrings_seated_leg_curl.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`27` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 8 (`"Kéo tạ đòn kiểu Romania"`, `"Nằm sấp móc đùi sau với máy"`, `"Ngồi móc đùi sau với máy"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `ROMANIAN_DEADLIFT`, `LEG_CURL_MACHINE`, `SEATED_LEG_CURL` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **24/30** bài (**80%**).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Kéo tạ đòn kiểu Romania (`ROMANIAN_DEADLIFT`):* Gối giữ độ chùng cố định `~15°`, đẩy mạnh hông ra sau (Hip Hinge `Pelvis Y = +0.30, Z = 0.77`), lưng phẳng nghiêng `~72°`, thanh đòn trượt sát đùi/ống đồng xuống giữa ống đồng (`Z = 0.42`, không chạm sàn); `Anim_BadForm` gập gối thành Squat (`Z = 0.57`), cuộn cong lưng chữ C (`95°`) và để thanh đòn trôi xa ống đồng.
  - *Nằm sấp móc đùi sau (`LEG_CURL_MACHINE`):* Đặt tháp tạ về phía trước-phải (`X = -0.46, Y = -0.78`) giữ thoáng hoàn toàn vùng hông/đùi sau khi nhìn ngang; con lăn đồng tâm khớp gối `(0, 0.47, 0.49)` cuốn đều qua cung `8° -> 102°` với hướng bàn chân giữ liên tục theo `calf_dir.cross((1,0,0))` không lật cổ chân; `Anim_BadForm` nhổm hông lên `+10.5 cm` tách khỏi mặt đệm.
  - *Ngồi móc đùi sau (`SEATED_LEG_CURL`):* Lùi khung chân ghế về `Y = +0.10` giữ thoáng gầm ghế khi cẳng chân cuốn tới `96°`, bổ sung đệm khóa trên đầu gối (`Thigh Lockdown Pad`) kèm tay cầm phía trên đệm đùi, đặt con lăn sau gót Achilles (`Z_local = +0.088`); `Anim_BadForm` nhổm lưng & vai lao về trước (`80° -> 114°`) rời khỏi đệm tựa lưng.
- **Kiểm tra / Kết quả chạy thử:**
  - Render EEVEE đa góc & các mốc khung hình (`f=1, 25, 50, 75, 100`) qua Blender 5.3 CLI (`render_previews.py`) và kiểm tra ảnh trực quan sau lần chỉnh cuối xác nhận sạch xuyên thấu cho cả 3 bài.
  - Headless Blender 5.3 (`verify_sprint2_hamstrings.py`, exit 0): **27/27** `.glb` khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, kích thước hợp lệ (`1,315,064 B – 1,446,388 B`), đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,796 tris` (`< 25,000`), đủ `['Anim_GoodForm', 'Anim_BadForm']`; **3/3** file `.blend` mới và `mock_m2_exercises.json` / `exercise_repository.dart` hợp lệ; `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`; `git status -s` giữ nguyên biên `[OWNER: M2]`.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Đùi sau; tiếp theo dựng **Nhóm 9: Cơ Mông (Glutes)** gồm 3 bài trong `gym.txt` (`Đẩy hông với tạ đòn`, `Bước chùng chân với tạ đơn`, `Đá chân ra sau với dây cáp`).

---

## Phiên 23 — 2026-11-21 21:05 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 7 Cơ Đùi trước / Quadriceps — 3 bài, tổng **21/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng, kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 7: Cơ Đùi trước (Quadriceps)** theo `gym.txt` (`BARBELL_SQUAT`, `LEG_PRESS`, `LEG_EXTENSION`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung `Phase 7` với `_build_squat_rack_object`, `_build_leg_press_machine`, `_build_leg_extension_machine`, cài đặt `_pose_barbell_squat`/`build_barbell_squat`, `_pose_leg_press`/`build_leg_press`, `_pose_leg_extension`/`build_leg_extension` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới / nâng cấp:**
    - `barbell_squat.glb` (`1,434,464 B`, `12,484 tris`, SHA-256 `6933137d1885...`) + `assets_3d/source_blend/quads_barbell_squat.blend`
    - `leg_press.glb` (`1,427,468 B`, `12,696 tris`, SHA-256 `d3c20380fe7c...`) + `assets_3d/source_blend/quads_leg_press.blend`
    - `leg_extension.glb` (`1,415,264 B`, `12,524 tris`, SHA-256 `15d09cc138d6...`) + `assets_3d/source_blend/quads_leg_extension.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`24` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, chuẩn hóa `phase_keyframes` `[0, 45]`/`[45, 55]`/`[55, 100]` cho `BARBELL_SQUAT` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 7 (`"Gánh tạ đòn"`, `"Đạp đùi trên máy"`, `"Ngồi đá đùi trước với máy"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `LEG_PRESS`, `LEG_EXTENSION` vào `_localBundledGlbs` (`BARBELL_SQUAT` đã có sẵn).
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **21/30** bài (**70%**).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Gánh tạ đòn (`BARBELL_SQUAT`):* Nâng cấp từ bản MVP 110 frames lên chuẩn Sprint 2 `100 frames` kèm `Equip_SquatRack` (`X = ±0.58`, J-cups & thanh bảo hiểm `Z = 0.68`) và gắn `Equip_Barbell` trực tiếp vào `Bone_Barbell` trên cầu vai `Spine_03`/`Neck`; `Anim_GoodForm` xuống song song/dưới song song (`Pelvis Z: 0.90 -> 0.46`) giữ bàn chân áp sàn và lòng bàn tay vòng qua thanh đòn, `Anim_BadForm` thể hiện rõ chụm gối (Knee Valgus), nhấc gót và gập lưng chu C.
  - *Đạp đùi trên máy (`LEG_PRESS`):* Dựng máy đạp đùi ray trượt đôi `40°` (`X = ±0.34` ngoài chân), lưng tựa ghế `35°`, bàn chân ép phẳng mặt bàn đạp (`track_dir`); đã tinh chỉnh `Anim_BadForm` để phần lưng trên vẫn tựa đệm trong khi vùng thắt lưng/xương cụt cuộn nhấc khỏi đệm ghế (Butt Wink), chụm gối, khóa cứng khớp gối ở đỉnh và buông tay đẩy gối.
  - *Ngồi đá đùi trước (`LEG_EXTENSION`):* Đặt tháp tạ lệch phía sau-phải (`X = -0.44, Y = 0.54`) giữ thoáng góc nhìn bên phải, trục cần đá `Bone_LegExtArm` đồng tâm khớp gối `(0, -0.37, 0.56)` giúp con lăn cổ chân tiếp xúc đều dọc cung `84° -> 4°`; đã tinh chỉnh `Anim_BadForm` trượt hông về trước khi nhấc mông `+10 cm` tránh xuyên tựa lưng và ghim cổ chân dưới con lăn không xuyên mesh.
- **Kiểm tra / Kết quả chạy thử:**
  - Render EEVEE đa góc & các mốc khung hình (`f=1, 25, 50, 75, 100`) qua Blender 5.3 CLI (`render_previews.py`) và kiểm tra trực quan xác nhận sạch xuyên thấu cho cả `GoodForm` và `BadForm`.
  - Headless Blender 5.3 (`verify_sprint2_quads.py`, exit 0): **24/24** `.glb` khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, kích thước hợp lệ (`1,315,064 B – 1,446,388 B`), đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,696 tris` (`< 25,000`), đủ `['Anim_GoodForm', 'Anim_BadForm']`; **3/3** file `.blend` mới và `mock_m2_exercises.json` / `exercise_repository.dart` hợp lệ; `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`; `git status -s` giữ nguyên biên `[OWNER: M2]`.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Đùi trước; tiếp theo dựng **Nhóm 8: Cơ Đùi sau (Hamstrings)** gồm 3 bài trong `gym.txt` (`Kéo tạ đòn kiểu Romania`, `Nằm sấp móc đùi sau với máy`, `Ngồi móc đùi sau với máy`).

---

## Phiên 22 — 2026-11-21 20:51 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 6 Cơ Tay sau / Triceps — 3 bài, tổng **18/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng, kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 6: Cơ Tay sau (Triceps)** theo `gym.txt` (`CABLE_TRICEP_PUSHDOWN`, `SKULL_CRUSHER`, `OVERHEAD_DUMBBELL_TRICEP_EXT`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Cài đặt `_pose_cable_tricep_pushdown`/`build_cable_tricep_pushdown`, `_pose_skull_crusher`/`build_skull_crusher`, `_pose_overhead_dumbbell_tricep_ext`/`build_overhead_dumbbell_tricep_ext` với đủ 2 clip `Anim_GoodForm` & `Anim_BadForm` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `cable_tricep_pushdown.glb` (`1,440,944 B`, `12,280 tris`, SHA-256 `ea04f1897288...`) + `assets_3d/source_blend/triceps_cable_tricep_pushdown.blend`
    - `skull_crusher.glb` (`1,389,472 B`, `12,356 tris`, SHA-256 `ebf84f929465...`) + `assets_3d/source_blend/triceps_skull_crusher.blend`
    - `overhead_dumbbell_tricep_ext.glb` (`1,391,508 B`, `12,052 tris`, SHA-256 `ded0225eec17...`) + `assets_3d/source_blend/triceps_overhead_dumbbell_tricep_ext.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`22` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 6 (`"Đẩy cáp dây thừng xuống"`, `"Nằm hạ tạ đòn qua trán"`, `"Duỗi tạ đơn qua đầu"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `CABLE_TRICEP_PUSHDOWN`, `SKULL_CRUSHER`, `OVERHEAD_DUMBBELL_TRICEP_EXT` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **18/30** bài (**60%**).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Blender MCP Fallback:* Kết nối MCP tới Blender GUI bị ngắt (`WinError 10053`), nên toàn bộ quy trình build, xuất `.glb`/`.blend` và kiểm tra trực quan được thực hiện bằng Blender 5.3 CLI (`--background --python-exit-code 1`) + script render EEVEE đa góc (`front`, `right`, `back`, `three_quarter`, `back_three_quarter`) và các mốc `f=1, 25, 50, 75, 100`.
  - *Đẩy cáp dây thừng xuống (`CABLE_TRICEP_PUSHDOWN`):* Dựng cụm ròng rọc cao (`CablePulleyHigh`) + dây thừng nylon chữ V hai nhánh có núm đầu dây (`RopeHandle`); `Anim_GoodForm` khóa hai khuỷu sát sườn và tách cổ tay nhẹ lúc duỗi hết tầm, `Anim_BadForm` ngả người lao vai về trước và xoè khuỷu sang hai bên.
  - *Nằm hạ tạ đòn qua trán (`SKULL_CRUSHER`):* Nằm ngửa trên ghế phẳng (`BenchFlat`), hạ thanh tạ đòn gọn phía trên trán (`"qua trán"`) mà không xuyên hộp sọ; `Anim_BadForm` mở góc khuỷu rộng sang hai bên và thả rơi thiếu kiểm soát.
  - *Duỗi tạ đơn qua đầu (`OVERHEAD_DUMBBELL_TRICEP_EXT`):* Phát hiện và sửa triệt để lỗi bánh tạ dưới chạm nhẹ chỏm sau hộp sọ ở `f=1`: chỉnh độ ngả core `GoodForm` (`torso_dir=(0, -0.15, 0.988)`), đưa tạ lùi về `Y=0.13..0.24, Z=1.90..1.48` (`GoodForm`) và `Y=0.20..0.28, Z=1.91..1.58` (`BadForm` kèm ngả lưng `16°` và xoè khuỷu `90°`), render kiểm chứng lại hoàn toàn sạch.
- **Kiểm tra / Kết quả chạy thử:**
  - Headless Blender 5.3 (`verify_sprint2_triceps.py`, exit 0): **22/22** `.glb` khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, kích thước hợp lệ (`1,315,064 B – 1,446,388 B`), đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,416 tris`, đủ `['Anim_GoodForm', 'Anim_BadForm']`; **3/3** file `.blend` mới và `mock_m2_exercises.json` / `exercise_repository.dart` hợp lệ; `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`; `git status -s` giữ nguyên biên `[OWNER: M2]`.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Tay sau; tiếp theo dựng **Nhóm 7: Cơ Đùi trước (Quadriceps)** gồm 3 bài trong `gym.txt` (`Gánh tạ đòn`, `Đạp đùi trên máy`, `Ngồi đá đùi trước với máy`).

---

## Phiên 21 — 2026-11-21 20:37 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 5 Cơ Tay trước / Biceps — 3 bài, tổng **15/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng qua **Blender 5.3 MCP** (`execute_blender_code` + `look`), kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 5: Cơ Tay trước (Biceps)** theo `gym.txt` (`BARBELL_BICEP_CURL`, `DUMBBELL_HAMMER_CURL`, `INCLINE_DUMBBELL_CURL`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Tái sử dụng `Equip_Barbell`, `Equip_Dumbbell_L/R` và ghế nghiêng `45°` (`Equip_Bench_Incline45`), cài đặt `build_barbell_bicep_curl`, `build_dumbbell_hammer_curl`, `build_incline_dumbbell_curl` với đủ 2 clip `Anim_GoodForm` & `Anim_BadForm` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `barbell_bicep_curl.glb` (`1,402,584 B`, `12,284 tris`, SHA-256 `b8f14393fb4b...`) + `assets_3d/source_blend/biceps_barbell_bicep_curl.blend`
    - `dumbbell_hammer_curl.glb` (`1,409,460 B`, `12,256 tris`, SHA-256 `01ff7c521e65...`) + `assets_3d/source_blend/biceps_dumbbell_hammer_curl.blend`
    - `incline_dumbbell_curl.glb` (`1,397,824 B`, `12,396 tris`, SHA-256 `520c80123b50...`) + `assets_3d/source_blend/biceps_incline_dumbbell_curl.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`19` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 5 (`"Đứng cuốn tạ đòn"`, `"Cuốn tạ đơn kiểu búa"`, `"Cuốn tạ đơn trên ghế nghiêng"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `BARBELL_BICEP_CURL`, `DUMBBELL_HAMMER_CURL`, `INCLINE_DUMBBELL_CURL` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **15/30** bài (mốc **50%**).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Đứng cuốn tạ đòn (`BARBELL_BICEP_CURL`):* Khóa khuỷu cố định hai bên sườn (`elbow_y = -0.03, elbow_z = 1.145`, cung `R = 0.295 m`) kết hợp tay nắm ngửa đối xứng (`thumb_dir = Vector((sx, 0, 0))`) không xoắn cổ tay/khuỷu; `Anim_BadForm` mô phỏng lỗi lắc lưng (`-22°` → `+16°`) và đẩy khuỷu lên cao lấy đà.
  - *Cuốn búa tạ đơn (`DUMBBELL_HAMMER_CURL`):* Căn tạ ở `X = ±0.245..0.265` tránh va chạm đùi và giữ thân tạ dựng đứng theo hướng `thumb_dir = hinge_inside`; `Anim_BadForm` dùng `depth ** 0.42` ở pha hạ (`f < 45`) để tạo chuyển động thả rơi tự do và vung tạ ra sau hông (`-18°`).
  - *Cuốn tạ đơn trên ghế nghiêng `45°` (`INCLINE_DUMBBELL_CURL`):* Lưng tựa khít mặt đệm `45°` (`Pelvis = (0.0, -0.06, 0.61)`), hai cánh tay trên thả thẳng đứng ngoài cạnh ghế (`X = ±0.265`, `elbow_y = +0.285`) kéo giãn tối đa đầu dài tay trước mà không chạm khung ghế; `Anim_BadForm` lao mạnh khuỷu về phía trước ngực khi cuốn lên.
- **Kiểm tra / Kết quả chạy thử:**
  - Kiểm tra trực quan bằng Blender MCP `look` (`angles`: `front`, `right`, `back`, `three_quarter` + `frames`: `[1, 25, 50, 75, 100]`, shading `material`) đạt yêu cầu ngay lần đầu cho cả `Anim_GoodForm` & `Anim_BadForm` của 3 bài; để sẵn `INCLINE_DUMBBELL_CURL` `Anim_GoodForm` tại `f=1` trong viewport Blender.
  - Headless Blender 5.3 kiểm tra toàn bộ **19/19** `.glb` (`verify_sprint2_biceps.py`, exit 0): khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,416 tris` (`< 25,000`), JSON hợp lệ, `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`, `git status -s` xác nhận không chạm `[LOCKED STUB]` hay file của M1/M3/M4.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Tay trước; tiếp theo dựng **Nhóm 6: Cơ Tay sau (Triceps)** gồm 3 bài trong `gym.txt` (`Đẩy cáp dây thừng xuống`, `Nằm hạ tạ đòn qua trán`, `Đứng đẩy tạ đơn qua đầu 1 hoặc 2 tay`).

---

## Phiên 20 — 2026-11-21 19:16 | Thành viên: M1 (Mobile Core, Health, Food/Photo UI & CH Play) | Task: `T-M1-08`, `T-M1-09`, `T-M1-11` (`[x]`), `T-M1-10`, `T-M1-12` (`[~]`)
- **Mục tiêu phiên:** Rà soát chéo toàn bộ code Phiên 15 trên Flutter SDK, sửa toàn bộ 4 lỗi biên dịch, 1 warning và các lỗi logic phát hiện được, giữ nguyên 100% `[LOCKED STUB]` và phạm vi `[OWNER: M1]`.
- **Những file đã tạo / chỉnh sửa:**
  - `mobile/lib/features/auth_privacy/data/auth_repository.dart`: Bổ sung `birthDateIso` (`birth_date`) + `calculateAgeYears()` (fallback `24`), đồng thời gọi `deleteAllPrivateMealPhotos()` khi xóa tài khoản (`F26`).
  - `mobile/lib/features/health/data/health_repository.dart`: Sửa lỗi thiếu import `AuthUserProfile` và 3 lỗi `unchecked_use_of_nullable_value` trong `_bootstrapInitialData`; giữ mức bù nước buổi tập (`workoutBonusWaterMl`) qua các lần `load()` và đánh dấu `PENDING_UPDATE` khi tự cộng bù nước; giữ `_fitnessGoalOverride`/`_activityLevelOverride` trong `HealthDashboardController` và truyền `_ageYears` thật vào `calculateBmrMifflinStJeor`.
  - `mobile/lib/features/health/nutrition/presentation/nutrition_screen.dart`: Xóa unused import `health_tables.drift.dart`.
  - `mobile/lib/core/sync/sync_queue_manager.dart`: Bổ sung Pull cho 3 bảng `workout_routines`, `workout_sessions`, `workout_sets` (đủ 7 bảng Drift), xử lý `legacyMockId` (`bio-{logged_date}`) tránh nhân đôi khi đổi sang UUID v5, và giữ `PENDING_UPDATE` khi `mergedSteps > serverSteps`.
  - `mobile/android/app/src/main/kotlin/com/vigorai/app/SupplementTakenReceiver.kt` & `mobile/lib/features/health/presentation/health_dashboard_screen.dart`: Đánh dấu `sync_status = 'PENDING_UPDATE'` khi bấm nút *"Đã uống"* trên notification và lắng nghe `AppLifecycleState.resumed` trên `HealthDashboardScreen` để tự refresh UI.
  - `mobile/lib/core/platform/photo_picker_service.dart` & `mobile/lib/features/health/food_scan/presentation/food_scan_screen.dart`: Lưu bền vững ảnh món ăn vào thư mục riêng tư `meal_photos/` khi lưu bữa, dùng `decodeImageFromList` + `AspectRatio` + `BoxFit.fill` để khớp 100% tọa độ `_FoodBboxPainter`.
  - `mobile/test/health/health_sprint2_test.dart`, `docs/taskboard.md` (`T-M1-08`, `T-M1-09`, `T-M1-11` đạt `[x]` $\rightarrow$ `M1: 9 / 17 Done`, `Tổng cộng: 24 / 63 Done (38.1%)`).
- **Lưu ý kỹ thuật còn mở (từ rà soát Phiên 15):**
  - `WorkManager` background isolate khi app tắt hẳn chưa có native handler riêng cho `com.vigorai.app/health_reminders` và `kBackgroundSyncTaskName` đang để stub `return true`; cần lưu ý hoặc hoàn thiện thêm nếu test notification chạy ngầm khi app killed.
  - Dữ liệu mock `meal-*` / `supp-*` nếu đẩy lên backend `M3` (chuyển sang UUID v5) vẫn cần chú ý ở giai đoạn tích hợp Sync thật (`T-M1-12`), trong khi `biometric_logs` đã có xử lý fallback `bio-{logged_date}`.
- **Kiểm tra / Kết quả chạy thử:**
  - `flutter analyze --no-fatal-infos`: Exit `0` (**0 errors, 0 warnings**; chỉ còn 18 info deprecation `package:flutter/material.dart` trên Flutter 3.50.0).
  - `flutter test test/health/health_sprint2_test.dart`: **Pass 11 / 11**.
  - `flutter test test/workout/`: **Pass 5 / 5**.
- **Việc cần làm ở phiên kế tiếp:**
  - Theo dõi `T-M4-06` (`M4` deploy Model B thật) để chốt `T-M1-10`, hoàn tất `T-M1-07` & tích hợp Sync Offline $\leftrightarrow$ Online với `M3` để chốt `T-M1-12`.

---

## Phiên 19 — 2026-11-21 11:00 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 4 Cơ Vai / Shoulders — 3 bài, tổng **12/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng qua **Blender 5.3 MCP** (`execute_blender_code` + `look`), kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 4: Cơ Vai (Shoulders)** theo `gym.txt` (`DUMBBELL_SHOULDER_PRESS`, `DUMBBELL_LATERAL_RAISE`, `CABLE_FACE_PULL`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung trạm cáp dây thừng `_build_cable_rope_station` (`Equip_CableTower_FacePull`, `Equip_RopeHub`, `Equip_Cable_FacePull`, 2 nhánh dây thừng co giãn `Equip_RopeBranch_L/R` & 2 nút chặn `Equip_RopeKnob_L/R`), tái sử dụng ghế nghiêng `80°` (`Equip_Bench_Upright80`) và tạ đơn (`Equip_Dumbbell_L/R`), cài đặt `build_dumbbell_shoulder_press`, `build_dumbbell_lateral_raise`, `build_cable_face_pull` với đủ 2 clip `Anim_GoodForm` & `Anim_BadForm` (`30 FPS`, `100 frames`) và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `dumbbell_shoulder_press.glb` (`1,411,936 B`, `12,396 tris`, SHA-256 `a70b92aadae5...`) + `assets_3d/source_blend/shoulders_dumbbell_shoulder_press.blend`
    - `dumbbell_lateral_raise.glb` (`1,412,476 B`, `12,256 tris`, SHA-256 `f52e2a0f7a81...`) + `assets_3d/source_blend/shoulders_dumbbell_lateral_raise.blend`
    - `cable_face_pull.glb` (`1,441,360 B`, `12,280 tris`, SHA-256 `958111166abf...`) + `assets_3d/source_blend/shoulders_cable_face_pull.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`16` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 4 (`"Ngồi đẩy vai qua đầu với tạ đơn"`, `"Dang tạ đơn sang ngang cho vai giữa"`, `"Kéo cáp hướng mặt cho vai sau"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `DUMBBELL_SHOULDER_PRESS`, `DUMBBELL_LATERAL_RAISE`, `CABLE_FACE_PULL` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **12/30** bài hoàn thành.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Ngồi đẩy vai (`DUMBBELL_SHOULDER_PRESS`):* Căn `Pelvis = (0.0, -0.165, 0.58)` khớp mặt đệm tựa `80°` để lưng áp sát ghế không xuyên mesh khi `GoodForm`, đối lập với `BadForm` ưỡn lưng dưới rời đệm và hạ tạ quá sâu dưới vai (`Z = 1.02 m`).
  - *Dang tạ ngang (`DUMBBELL_LATERAL_RAISE`):* Dùng hướng ngón cái tiến về trước `thumb_dir = Vector((0.0, -1.0, 0.0))` kết hợp mặt phẳng xương bả vai `20°` để hai lòng bàn tay xoay mượt từ áp đùi sang úp sàn ở đỉnh `85°`.
  - *Kéo cáp hướng mặt (`CABLE_FACE_PULL`):* Giải hình học bảo toàn chiều dài dây thừng cố định `L_rope = 0.42 m` từ nút chia `Equip_RopeHub` tới hai bàn tay; sau kiểm tra bằng Blender MCP `look`, đã kéo sâu điểm kết thúc ở `f=1` về ngang thái dương (`hand_y = +0.07`, `elbow_pole = (sx*0.92, 0.48, 0.12)`) giúp khuỷu tay rút gọn về ngang vai, đối lập rõ với `BadForm` tụt khuỷu dưới cổ tay.
- **Kiểm tra / Kết quả chạy thử:**
  - Kiểm tra trực quan bằng Blender MCP `look` (`angles`: `front`, `right`, `back`, `three_quarter` + `frames`: `[1, 25, 50, 75, 100]`, shading `material`) đạt yêu cầu cho cả `Anim_GoodForm` & `Anim_BadForm` của 3 bài; để sẵn `CABLE_FACE_PULL` `Anim_GoodForm` tại `f=1` trong viewport Blender.
  - Headless Blender 5.3 kiểm tra toàn bộ **16/16** `.glb` (`verify_sprint2_shoulders.py`, exit 0): khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,416 tris` (`< 25,000`), JSON hợp lệ, `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`, `git status -s` xác nhận không chạm `[LOCKED STUB]` hay file của M1/M3/M4.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Vai; tiếp theo dựng **Nhóm 5: Cơ Tay trước (Biceps)** gồm 3 bài trong `gym.txt` (`Đứng cuốn tạ đòn`, `Cuốn tạ đơn kiểu búa`, `Cuốn tạ đơn trên ghế nghiêng`).

---

## Phiên 18 — 2026-11-20 15:55 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 3 Cơ Lưng giữa & Lưng dưới — 3 bài, tổng **9/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng qua **Blender 5.3 MCP** (`execute_blender_code` + `look`), kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm 3: Lưng giữa & Lưng dưới (Mid & Lower Back)** theo `gym.txt` (`BARBELL_BENT_OVER_ROW`, `SEATED_CABLE_ROW`, `BARBELL_DEADLIFT`) trong phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung dụng cụ máy ngồi kéo cáp `_build_seated_row_machine` (`Equip_SeatedRowMachine`, `Equip_VHandle`, dây cáp co giãn `Equip_Cable_Row`), 3 hàm dựng/animation (`build_barbell_bent_over_row`, `build_seated_cable_row`, `build_barbell_deadlift`) với đủ 2 clip `Anim_GoodForm` & `Anim_BadForm` (`30 FPS`, `100 frames`, lỗi `giật thân + gù lưng trên` / `cong lưng dưới + ngả sau` / `hông cao + lưng cong chữ C + tạ trôi xa ống đồng`), và đăng ký vào `EXERCISE_SPECS` + `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `barbell_bent_over_row.glb` (`1,405,872 B`, `12,284 tris`, SHA-256 `1415727e5ae4...`) + `assets_3d/source_blend/back_barbell_bent_over_row.blend`
    - `seated_cable_row.glb` (`1,438,352 B`, `12,416 tris`, SHA-256 `c434576897e3...`) + `assets_3d/source_blend/back_seated_cable_row.blend`
    - `barbell_deadlift.glb` (`1,416,356 B`, `12,284 tris`, SHA-256 `b4fa80771a34...`) + `assets_3d/source_blend/back_barbell_deadlift.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256 (`13` assets trong manifest, `39` bài trong mock JSON), `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` khớp `gym.txt` Phần 3 (`"Gập người kéo tạ đòn"`, `"Ngồi kéo cáp hẹp tay"`, `"Kéo tạ đòn từ sàn"`).
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `BARBELL_BENT_OVER_ROW`, `SEATED_CABLE_ROW`, `BARBELL_DEADLIFT` vào `_localBundledGlbs`.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **9/30** bài hoàn thành.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Kết nối trực tiếp Blender MCP:* Khi kiểm tra `SEATED_CABLE_ROW` qua `look`, phát hiện mũi/lòng bàn chân chạm nhẹ vào mặt thép bàn đạp nghiêng `22°`; đã tịnh tiến bàn đạp về trước `6 cm` (`Y = -0.84, Z = 0.47`) và xác minh lại qua `look` cho thấy hai lòng bàn chân áp khít lên bàn đạp không xuyên mesh.
  - *Conventional Deadlift (`BARBELL_DEADLIFT`):* Đồng bộ bánh tạ ngoài `R = 0.215 m` với `bar_z = 0.215 m` tại đáy (`f=45..55`) để bánh tạ chạm chuẩn mặt sàn `Z = 0.000 m`, `Pelvis` hạ xuống `Z = 0.53 m` giữ lưng phẳng `62°` và hai bàn tay nắm sấp đối xứng (`X = ±0.27`) khóa chặt thanh đòn bên ngoài ống đồng.
- **Kiểm tra / Kết quả chạy thử:**
  - Kiểm tra trực quan bằng Blender MCP `look` (`angles`: `front`, `right`, `back`, `three_quarter` + `frames`: `[1, 25, 50, 75, 100]`, shading `material`) đạt yêu cầu cho cả `Anim_GoodForm` & `Anim_BadForm` của 3 bài.
  - Headless Blender 5.3 kiểm tra toàn bộ **13/13** `.glb` (`verify_sprint2_back.py`, exit 0): khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,416 tris` (`< 25,000`), JSON hợp lệ, `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`, `git status -s` không chạm `[LOCKED STUB]` hay file của M1/M3/M4.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Lưng giữa & Lưng dưới; tiếp theo dựng **Nhóm 4: Cơ Vai (Shoulders)** gồm 3 bài trong `gym.txt` (`Ngồi đẩy vai qua đầu với tạ đơn`, `Dang tạ đơn sang ngang cho vai giữa`, `Kéo cáp hướng mặt cho vai sau`).

---

## Phiên 17 — 2026-11-20 15:30 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Nhóm 2 Cơ Xô / Lats — 3 bài, tổng **6/30** bài `gym.txt`)
- **Mục tiêu phiên:** Tiếp tục dựng, kiểm tra trực quan đa góc/đa khung hình và đồng bộ SHA-256 cho **3 bài Nhóm cơ Xô (Lats)** trong `gym.txt` (`WIDE_GRIP_PULLUP`, `LAT_PULLDOWN`, `STRAIGHT_ARM_CABLE_PULLDOWN`) theo phạm vi `[OWNER: M2]`.
- **Những file đã tạo / chỉnh sửa:**
  - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Bổ sung 3 bộ dụng cụ rời (`_build_pullup_rack_object`, `_build_lat_pulldown_machine`, `_build_single_cable_tower`), 3 hàm dựng/animation (`build_wide_grip_pullup`, `build_lat_pulldown`, `build_straight_arm_cable_pulldown`) với đủ 2 clip `Anim_GoodForm` & `Anim_BadForm` (`30 FPS`, `100 frames`, chuyển động chuẩn cơ Xô vs lỗi `Kipping swing` / `ngả lưng >44°` / `gập khuỷu >95° thành Tricep Pushdown`), cùng cập nhật `EXERCISE_SPECS` & `ordered_specs`.
  - **File 3D & `.blend` mới:**
    - `wide_grip_pullup.glb` (`1,406,808 B`, `12,176 tris`, SHA-256 `c6de82378213...`) + `assets_3d/source_blend/lats_wide_grip_pullup.blend`
    - `lat_pulldown.glb` (`1,432,108 B`, `12,380 tris`, SHA-256 `5fe27fe31087...`) + `assets_3d/source_blend/lats_lat_pulldown.blend`
    - `straight_arm_cable_pulldown.glb` (`1,408,692 B`, `12,120 tris`, SHA-256 `5d536bbfccde...`) + `assets_3d/source_blend/lats_straight_arm_cable_pulldown.blend`
    - Sao chép đồng nhất từng byte giữa `assets_3d/exported_glb/` và `mobile/assets/3d_bundled/`.
  - `assets_3d/exported_glb/assets_manifest.json` & `mobile/assets/mock_json/mock_m2_exercises.json`: Đồng bộ SHA-256, `bundled: true`, `clips: ["Anim_GoodForm", "Anim_BadForm"]` và chuẩn hóa `name_vi` của `LAT_PULLDOWN` thành `"Kéo xô trước ngực với máy cáp"`.
  - `mobile/lib/features/gym3d/data/exercise_repository.dart`: Đăng ký thêm `WIDE_GRIP_PULLUP`, `LAT_PULLDOWN`, `STRAIGHT_ARM_CABLE_PULLDOWN` vào `_localBundledGlbs` để load offline ngay trên Android WebView.
  - `docs/taskboard.md`: Cập nhật tiến độ `T-M2-07` lên **6/30** bài hoàn thành (Nhóm 1 Ngực + Nhóm 2 Xô).
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - *Kết nối Blender:* Blender GUI đang đóng khi bắt đầu phiên nên Blender MCP báo `Not connected to Blender`; đã dựng & render kiểm tra trực quan đa góc (`front`, `right`, `back`, `three_quarter`, `back_three_quarter`) và đa khung hình (`1, 25, 50, 75, 100`) qua **Blender 5.3 CLI EEVEE** (`--background --python-exit-code 1`).
  - *Chuẩn hóa tay nắm sấp đối xứng (Symmetric Pronated Grip):* Xác định trục cục bộ của `Hand_L` / `Hand_R` trong `Armature_GymHuman` (`+Z` = ngón cái, `+X` là lòng bàn tay trái, `-X` là lòng bàn tay phải), truyền `thumb_dir = Vector((-sx, 0, 0))` cho `_aim_bone_world` để loại bỏ hoàn toàn lỗi xoắn một bên tay ngửa / một bên sấp và triệt tiêu xoắn khớp khuỷu trên bài hít xà.
  - *Tinh chỉnh biomechanics qua kiểm tra ảnh render:* Hạ tầm với `LatBar` (`1.18–1.60 m` dọc trục `Y = 0.08`) và nâng đệm đùi/mặt sàn đứng (`ankle Z = 0.140`) để tay luôn khóa chặt vào thanh kéo ở `f=50`, bàn chân đặt chuẩn trên sàn thép; mở bán kính cung vung thẳng tay `arm_arc = 0.565` cho `STRAIGHT_ARM_CABLE_PULLDOWN` giữ tay duỗi thẳng tự nhiên (~20° mềm khuỷu) đối lập rõ với lỗi gập khuỷu ở `Anim_BadForm`.
- **Kiểm tra / Kết quả chạy thử:**
  - Headless Blender 5.3 kiểm tra đồng bộ cả 10 `.glb` (`base_mannequin`, `base_mannequin_female`, 2 bài MVP, 3 bài Ngực, 3 bài Xô): 100% khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, đủ 11 `Mat_Muscle_*`, `extensionsUsed=[]`, `<= 12,396 tris` (`< 25,000`), JSON hợp lệ (`39` bài), `ALL_DART_RELATIVE_IMPORTS_OK (checked=70)`, `git status -s` xác nhận không chạm file `[LOCKED STUB]` hay của M1/M3/M4.
  - *Lưu ý:* Máy chưa cài Flutter SDK nên chưa chạy trực tiếp `flutter analyze` / `flutter test`.
- **Việc cần làm ở phiên kế tiếp:**
  - Chờ người dùng kiểm thử 3 bài Nhóm cơ Xô; nếu đạt yêu cầu, tiếp tục dựng **Nhóm 3: Cơ Tay trước (Biceps)** gồm 3 bài trong `gym.txt`.

---

## Phiên 16 — 2026-11-20 15:05 | Thành viên: M2 (3D Blender MCP, Workout, Recovery 3D & Charts) | Task: `T-M2-07` (`[~]` Pilot Ngực 3 bài), `T-M2-08`..`T-M2-11` (`[~]`)
- **Mục tiêu phiên:** Triển khai hạ tầng Sprint 2 của Thành viên M2 theo `[OWNER: M2]`, trong đó phần 3D Blender MCP ưu tiên làm trước **3 bài Nhóm cơ Ngực (Chest)** từ `gym.txt` (`BARBELL_BENCH_PRESS`, `INCLINE_DUMBBELL_PRESS`, `CABLE_CHEST_FLY`) sử dụng bộ mesh `D:\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend` để người dùng kiểm thử trước khi mở rộng 27 bài còn lại.
- **Những file đã tạo / chỉnh sửa:**
  - **3D Blender MCP (`T-M2-07` Pilot 3 bài Ngực + Mannequin Nam/Nữ):**
    - `assets_3d/scripts_blender_mcp/build_base_mannequin.py`: Cập nhật `resolve_bundle_path()` hỗ trợ `D:\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend`, tìm Principled BSDF theo node type, hỗ trợ xuất cả `base_mannequin.glb` (`GEO-body_male_realistic`, `1.78 m`, `1,315,064 B`) và `base_mannequin_female.glb` (`GEO-body_female_realistic`, `1.66 m`, `1,320,320 B`, `11,848 tris`).
    - `assets_3d/scripts_blender_mcp/build_sprint2_exercises.py`: Dựng dụng cụ rời (`Equip_Barbell`, `Equip_Bench`, `Equip_Bench_Incline` `30°`, `Equip_Dumbbell_L/R`, `Equip_CableMachine` kèm `Equip_Handle_L/R` & dây cáp co giãn động `Equip_Cable_L/R`) và xuất đủ 2 clip `Anim_GoodForm` + `Anim_BadForm` (`30 FPS`, `100 frames`) cho 3 bài Ngực: `barbell_bench_press.glb` (`1,404,416 B`), `incline_dumbbell_press.glb` (`1,411,316 B`), `cable_chest_fly.glb` (`1,446,388 B`), kèm `.blend` kiểm tra tại `assets_3d/source_blend/chest_*.blend`. Đồng bộ SHA-256 sang `assets_3d/exported_glb/assets_manifest.json` và `mobile/assets/mock_json/mock_m2_exercises.json` (bổ sung đủ 39 bài gồm 30 bài `gym.txt` + 9 bài `EXERCISES_SEED`).
  - **Phòng tập 3D Nâng cao (`T-M2-08`):** `muscle_3d_viewer_widget.dart` (`normalizedProgress`, `BodyAvatarPreset` Nam/Nữ/Cơ bắp), `exercise_repository.dart`, `gym3d_library_screen.dart` (bộ lọc 10 nhóm cơ + dụng cụ + tìm kiếm + chọn Avatar), `exercise_3d_detail_screen.dart` (Overlay nhịp thở 3 pha + cảnh báo `Anim_BadForm` + Timeline Scrubber + 3 nút nhảy pha + Avatar selector).
  - **Giáo án & Live Workout Logger (`T-M2-09`):** `workout_calculators.dart` (1RM Epley/Brzycki, Progressive Overload, Greedy Plate Calculator, Streak), `workout_repository.dart` (4 mẫu giáo án, khôi phục phiên `IN_PROGRESS` crash-safe, pre-fill, PR, bù nước `+500/+750 ml`, Exercise Swapper top 5), `routines_screen.dart` (kéo thả & Superset), `plate_calculator_sheet.dart`, `exercise_swapper_sheet.dart`, `live_workout_logger_screen.dart`, `gym3d_workout_routes.dart`.
  - **AI Readiness 3D & Biểu đồ (`T-M2-10`, `T-M2-11`):** `ai_analytics_repository.dart` (tổng hợp thuần Dart `< 300ms`, Banister decay cục bộ 72h, fallback user mới `85.0`), `readiness_recovery_3d_view.dart`, `volume_analytics_view.dart` (`fl_chart` `BarChart` + PR Wall), `muscle_radar_view.dart` (`fl_chart` 6-axis `RadarChart`), `ai_coach_hub_screen.dart`.
  - **Unit Tests (`T-M2-12` prep):** `mobile/test/workout/workout_sprint2_test.dart`.
- **Quyết định kỹ thuật / Lưu ý quan trọng:**
  - Giữ nguyên 100% các file `[LOCKED STUB]` và chỉ chạm file `[OWNER: M2]`.
  - Máy hiện tại (`ĐĂNG KHOA`) chưa cài Flutter SDK nên các file Dart mới kiểm tra cấu trúc import tương đối & logic; cần chạy `flutter pub get`, `dart run build_runner build --delete-conflicting-outputs`, `flutter analyze --no-fatal-infos` và `flutter test test/workout/` trên máy có Flutter SDK.
- **Kiểm tra / Kết quả chạy thử:**
  - Blender MCP `look` (`angles` & `frames` cho cả `Anim_GoodForm` và `Anim_BadForm`): Đã tinh chỉnh vị trí cổ tay/lòng bàn tay ôm sát thanh đòn, tạ đơn và tay cầm cáp, kiểm tra lưng tựa ghế `30°` và dây cáp căng mượt không clipping.
  - Blender 5.3 Headless Verification (`--python-exit-code 1`): Pass 100% (7 `.glb` khớp SHA-256 bit-for-bit giữa `exported_glb/` và `3d_bundled/`, đủ 11 `Mat_Muscle_*`, đủ `Anim_GoodForm`/`Anim_BadForm`, `MOCK_EXERCISES = 39`, `ALL_DART_RELATIVE_IMPORTS_OK`).
- **Việc cần làm ở phiên kế tiếp:**
  - Người dùng kiểm thử 3 bài Nhóm cơ Ngực (`chest_*.blend` & app 3D); sau khi duyệt, chạy mở rộng `build_sprint2_exercises.py` cho 9 nhóm cơ còn lại (`27+` bài) để chốt `T-M2-07`, chạy `flutter analyze` + `flutter test test/workout/` để chốt `T-M2-08`..`T-M2-11`, và build `.aab` `v1.1.0+2` (`T-M2-12`).

---

## Phiên 15 — 2026-11-20 14:38 | Thành viên: M1 (Mobile Core, Health, Food/Photo UI & CH Play) | Task: `T-M1-08`, `T-M1-09`, `T-M1-10`, `T-M1-11`, `T-M1-12` (`[~]`)
- **Mục tiêu phiên:** Triển khai đầy đủ 5 tasks Sprint 2 của Thành viên M1 (`T-M1-08` đến `T-M1-12`) theo đúng `[OWNER: M1]`, giữ nguyên 100% file `[LOCKED STUB]` (`pubspec.yaml`, `main.dart`, `app_database.dart`, `app_router.dart`) và chuẩn tuân thủ Google Play Store.
- **Những file đã tạo / chỉnh sửa:**
  - **Core Network, DB Models & WorkManager (`T-M1-08`, `T-M1-09`, `T-M1-12`):**
    - `mobile/lib/core/network/{api_endpoints,dio_client}.dart`: Bổ sung endpoint `/api/v1/health/catalog`, `DELETE /supplements/{id}`, mở rộng `MockApiInterceptor` cho `/api/v1/sync/*`, `/api/v1/ai/food-analyze` và CRUD Health.
    - `mobile/lib/core/database/health_tables.drift.dart`: Giữ nguyên 4 Drift `Table` (tương thích `schemaVersion = 1`), bổ sung `calculateMovingAverage7Day`, `calculateMacroTargets`, `classifySleepStatus`, `MealLogModel.extractTitleFromDetectedItems` và `toJson`/`copyWith`.
    - `mobile/lib/core/platform/workmanager_reminder_service.dart`: Nhắc uống nước (`07:00–21:30`, chu kỳ 2h) & Supplement bằng `WorkManager` (`ExistingPeriodicWorkPolicy.update`), `SupplementIntakeStore` lưu trạng thái `"Đã uống"` và tính % tuân thủ 7 ngày.
    - `mobile/android/app/src/main/kotlin/com/vigorai/app/{MainActivity,SupplementTakenReceiver}.kt` & `AndroidManifest.xml`: Kênh thông báo Android API 26+ với nút hành động **"Đã uống"** xử lý ngầm qua `BroadcastReceiver` (0 quyền cấm CH Play, giữ nguyên khối `[RE-ENABLE IN v1.2.0]`).
    - `mobile/lib/core/sync/sync_queue_manager.dart`: Push/Pull hai chiều với `M3` (7 bảng Drift, `SyncConflictResolver` LWW theo `updated_at` UTC & `max(steps_count)`, auto-sync khi `connectivity_plus` báo có mạng).
    - `mobile/lib/features/auth_privacy/data/auth_repository.dart`: Dọn sạch `SupplementIntakeStore` khi xóa tài khoản (`F26`).
  - **Health Offline-First & 7 Màn hình Sprint 2 (`T-M1-08`..`11`):**
    - `mobile/lib/features/health/data/health_repository.dart`: Đọc/ghi trực tiếp Drift SQLite cho Cân nặng, Nước bù tập (`+500/+750ml`), Calo/Macro, Giấc ngủ, Supplement & Sync.
    - `mobile/lib/features/health/biometrics/presentation/biometrics_screen.dart` (`F01`: `fl_chart` Moving Average 7 ngày + 5 vòng đo + WHO Châu Á BMI).
    - `mobile/lib/features/health/hydration/presentation/hydration_screen.dart` (`F03`: nước nền + bù buổi tập + `WorkManager`).
    - `mobile/lib/features/health/nutrition/{data/offline_food_catalog,presentation/nutrition_screen}.dart` (`F04`: Mifflin-St Jeor, 4 bữa, từ điển 27+ món offline).
    - `mobile/lib/features/health/sleep/presentation/sleep_screen.dart` (`F05`: `fl_chart` 7 ngày + nhập tay 2 chạm).
    - `mobile/lib/features/health/supplements/presentation/supplements_screen.dart` (`F06`: lịch nhắc + `"Đã uống"` + % tuân thủ).
    - `mobile/lib/features/health/food_scan/{data/food_scan_repository,presentation/food_scan_screen}.dart` (`F19`: Photo Picker + vẽ BBox `CustomPainter` + thanh kéo gram + disclaimer + lưu thẳng vào `MealLogsTable`).
    - `mobile/lib/features/health/progress_photos/{data/progress_photos_repository,presentation/progress_photos_screen}.dart` (`F24`: lưu 100% cục bộ `progress_photos/`, Slider so sánh Before/After).
    - `mobile/lib/core/router/health_routes.dart` & `mobile/lib/features/health/presentation/health_dashboard_screen.dart`: Kết nối toàn bộ 7 route mới & nút Sync thật.
  - **CH Play Checklist, Tests & Tiến độ:**
    - `docs/chplay_submission_checklist.md`, `mobile/test/health/health_sprint2_test.dart`, `docs/taskboard.md` (`T-M1-08`..`12` đánh dấu `[~]` chờ nghiệm thu trên Flutter SDK & phụ thuộc `M4` / Closed Testing 14 ngày).
- **Kiểm tra / Kết quả chạy thử:**
  - Máy hiện tại chưa cài `flutter`/`dart` SDK trong `PATH` nên chưa chạy `flutter analyze` & `flutter test`; đã kiểm tra tĩnh toàn bộ import nội bộ, API gói (`workmanager ^0.10.10`, `connectivity_plus ^6.1.0`, `fl_chart ^0.69.2`) và `AndroidManifest.xml` sạch 0 quyền cấm.
- **Việc cần làm ở phiên kế tiếp:**
  - Trên máy có cài Flutter SDK: chạy `cd mobile && dart run build_runner build --delete-conflicting-outputs && flutter analyze --no-fatal-infos && flutter test test/health/` để nghiệm thu đóng `[x]` cho `T-M1-08`, `T-M1-09`, `T-M1-11`.
  - Theo dõi `T-M4-06` (`M4` deploy Model B thật) để chốt `T-M1-10`, và đủ 14 ngày Closed Testing (`T-M1-07` / `T-M2-06`) để chốt `T-M1-12`.

---

## Phiên 14 — 2026-11-20 09:09 | Thành viên: M1 + M2 + M3 (Hotfix Điện thoại thật: 3D Load < 0.8s & Lỗi Auth Thân thiện) | Task: `T-M2-02`, `T-M2-03`, `T-M1-04`, `T-M2-06`, `T-M3-06`
- **Mục tiêu phiên:** Xử lý 2 lỗi phát hiện khi test `app-release.apk` trên điện thoại thật: (1) Màn hình 3D treo mãi *"Đang dựng mô hình 3D..."* do Android Release chặn HTTP local proxy `127.0.0.1` của `model_viewer_plus` (`net::ERR_CLEARTEXT_NOT_PERMITTED`) và tránh tải Draco WASM từ `gstatic.com`; (2) Màn hình Đăng nhập hiển thị cả chuỗi `DioException` kỹ thuật dài dòng thay vì thông báo ngắn gọn tiếng Việt + thiếu tài khoản `demo@vigorai.app` trên Railway.
- **Những file đã tạo / chỉnh sửa:**
  - **Fix 3D (`ERR_CLEARTEXT_NOT_PERMITTED` + Fast-Load Binary glTF):**
    - `mobile/android/app/src/main/res/xml/network_security_config.xml` & `mobile/android/app/src/main/AndroidManifest.xml`: Cấu hình `android:networkSecurityConfig` & `android:usesCleartextTraffic="true"` (kèm `domain-config` cho `127.0.0.1`, `localhost`, `10.0.2.2`) để WebView cho phép nạp trang/model từ local HTTP proxy `http://127.0.0.1:<port>/`.
    - `assets_3d/scripts_blender_mcp/build_base_mannequin.py` & `build_mvp_exercises.py`: Chuyển xuất 4 file bundled (`base_mannequin.glb`, `barbell_squat.glb`, `push_up.glb`, `barbell_bench_press.glb`) sang chuẩn **Binary glTF 2.0 (`export_draco_mesh_compression_enable=False`)** để mở tức thì cả khi offline mà không cần fetch Draco decoder WASM từ `gstatic.com`; đồng bộ SHA-256 sang `assets_3d/exported_glb/assets_manifest.json` và `mobile/assets/mock_json/mock_m2_exercises.json` (`extensionsUsed = []`, tổng 4 `.glb` trước nén Zip `5,513,360 B`, sau nén vào APK gần như không tăng `+0.1 MB`).
    - `mobile/lib/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart`: Bật `loading: Loading.eager`, gửi tín hiệu `'loaded'` trước khi tô màu, thêm bắt sự kiện `error` + watchdog timeout 8 giây hiển thị nút **"Thử tải lại"** trên nền đặc `0xFF12161F`.
  - **Fix Auth UI & Seed tài khoản Demo trên Railway:**
    - `mobile/lib/features/auth_privacy/presentation/auth_controller.dart`: Bổ sung `AuthController.mapAuthErrorMessage(...)` biến lỗi `DioException` (`400`/`401`/`404`) khi đăng nhập thành `"Tài khoản hoặc mật khẩu không chính xác."`, `409` khi đăng ký thành thông báo trùng email rõ ràng, và lỗi kết nối thành hướng dẫn kiểm tra mạng.
    - `backend/app/db/startup.py`: Gọi thêm `await seed_demo_history(db)` (idempotent) khi container khởi động để tự tạo tài khoản `demo@vigorai.app` (`VigorAI@2026`) cùng 30 ngày lịch sử mẫu. Đã seed và kiểm tra trực tiếp login/sai mật khẩu trên `https://vigorai-production.up.railway.app`.
- **Kiểm tra / Kết quả chạy thử:**
  - Headless Blender 5.3 (`--python-exit-code 1`): Xuất sạch 4 `.glb` chuẩn Binary glTF 2.0, kiểm tra binary header xác nhận `extensionsUsed = []`.
  - Live Railway `https://vigorai-production.up.railway.app`: `demo@vigorai.app` / `VigorAI@2026` login `200 OK`; sai mật khẩu trả `401` (`RAILWAY_DEMO_USER_OK`).
  - `flutter analyze --no-fatal-infos`: Exit `0`.
  - `flutter test test/workout/`: Pass `5 / 5`.
  - `flutter build apk --release --target-platform android-arm64` (`USE_MOCK_API=false`, `API_BASE_URL=https://vigorai-production.up.railway.app`): Exit `0`, `26,430,584 B` (`25.2 MB`).
  - `flutter build appbundle --release` + `jarsigner -verify`: Exit `0`, `44,850,488 B` (`42.8 MB`), `jar verified.` (`CN=VigorAI`).
  - Merged Release `AndroidManifest.xml`: Xác nhận có `networkSecurityConfig` + `usesCleartextTraffic="true"`, **0 quyền cấm CH Play**.
- **Việc cần làm ở phiên kế tiếp:**
  - Cài lại `app-release.apk` mới lên điện thoại thật để test lại tốc độ mở 3D và thông báo đăng nhập sai; xong thực hiện `T-M1-07` nộp `app-release.aab` lên Google Play Console Closed Testing.

---

## Phiên 13 — 2026-11-20 01:10 | Thành viên: M3 (Backend & DB) | Task: `T-M3-07`, `T-M3-08`, `T-M3-10`, `T-M3-11` (`[x]`), `T-M3-09` (`[~]`)
- **Mục tiêu phiên:** Triển khai và nghiệm thu toàn bộ 5 tasks Sprint 2 của Thành viên M3 (`T-M3-07` đến `T-M3-11`) theo đúng `[OWNER: M3]`, bảo đảm 100% tương thích với app Mobile `M1`/`M2` và không đụng `feature_extractor.py` (`M4`) hay `[LOCKED STUB]`.
- **Những file đã tạo / chỉnh sửa:**
  - Schemas & Sync (`T-M3-07`): `backend/app/schemas/core_schemas.py`, `backend/app/services/sync_service.py`, `backend/app/routers/sync.py` (`POST /api/v1/sync/push` LWW theo `updated_at` UTC + `max(steps_count)` + tính `total_volume_kg`/`is_pr`, `GET /api/v1/sync/pull?since=`).
  - Health (`T-M3-08`): `backend/app/routers/health.py` (`/biometrics` kèm BMI Châu Á & 7-Day Moving Average, `/daily/{date}` trả `200 OK` mặc định nếu user mới + Smart Hydration, `/catalog`, `/meals`, `/supplements`).
  - 3D Exercises & Storage (`T-M3-09`): `backend/app/db/seed_catalog_and_exercises.py`, `backend/app/services/storage_service.py`, `backend/app/routers/exercises.py` (3 bài MVP giữ đường dẫn `assets/3d_bundled/*.glb` + SHA-256 khớp `assets_manifest.json` của `M2`; `/exercises/{code}/alternatives` trả top 5 bài cùng nhóm cơ chính).
  - Routines & Workouts (`T-M3-10`): `backend/app/routers/routines.py`, `backend/app/routers/workouts.py` (trả kèm `exercise_code` cho `M2`, tính `total_volume_kg`, `estimated_1rm` Epley/Brzycki, cờ `is_pr` & tự cộng bù nước ngày tập).
  - Analytics (`T-M3-11`): `backend/app/services/analytics_service.py`, `backend/app/routers/analytics.py` (`GET /api/v1/analytics/summary` trả Weekly Volume Load, 6-Axis Muscle Radar & PR Wall + Streak).
  - Test & Tiến độ: `backend/tests/test_core_api.py` (bổ sung test E2E Sprint 2), `docs/taskboard.md` (`T-M3-07`, `08`, `10`, `11` `[x]`; `T-M3-09` `[~]` chờ 27 `.glb` của `M2`).
- **Kiểm tra / Kết quả chạy thử:**
  - `docker compose exec api python -m app.db.seed_catalog_and_exercises`: Thành công (`total_foods: 36`, `total_exercises: 30`).
  - `docker compose exec api pytest tests/test_core_api.py -v`: **`8 passed in 3.56s`** (Pass 100% cả Sprint 1 + Sprint 2 E2E trên PostgreSQL 16 thật).
- **Việc cần làm ở phiên kế tiếp:**
  - Commit & tạo Pull Request từ nhánh `role/backend-architect` vào `main`; khi `M2` hoàn thành `T-M2-07` thì upload 27 file `.glb` mở rộng lên MinIO/CDN để chốt `[x]` cho `T-M3-09`.

---

## Phiên 12 — 2026-11-20 00:11 | Thành viên: M3 + M2 (Hoàn tất Cloud Deploy & Final Signed AAB Sprint 1) | Task: `T-M3-06` (`[x]`), `T-M2-06` (`[~]`)
- **Mục tiêu phiên:** Sử dụng **Railway MCP** để triển khai live Backend FastAPI + PostgreSQL lên `unique-grace / production`, xác minh HTTPS E2E cho **`T-M3-06`**, và build lại file `.aab` Release đã ký (`USE_MOCK_API=false`) trỏ thẳng server thật cho **`T-M2-06`**.
- **Hạ tầng Railway & Thao tác đã thực hiện:**
  - Gỡ bỏ service nháp trùng lặp `secure-kindness` (`10d57bff-4b16-438d-910c-fb466343e6ba`) khỏi staged changes.
  - Khởi tạo template chính thức **`Postgres`** (`01352b25-a306-4e8a-872d-0cf73db91991`, `ghcr.io/railwayapp-templates/postgres-ssl:18`, deployment `7ae25a4f-1b1c-4ce8-b83b-903b19adc691` `[SUCCESS]`).
  - Cấu hình service **`VigorAI`** (`3d16d190-58a9-4ada-b451-1b407b5dcc7f`): `builder=DOCKERFILE`, `dockerfilePath=backend/Dockerfile.railway`, `healthcheckPath=/healthz`, `healthcheckTimeout=120`, `watchPatterns=["backend/**", "railway.json"]`, gán biến `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `JWT_SECRET_KEY`, `S3_ENDPOINT_URL=""`, tạo domain HTTPS **`https://vigorai-production.up.railway.app`**.
  - Sửa lỗi `ImportError: cannot import name 'NoDecode' from 'pydantic_settings'` trên `pydantic-settings==2.6.1` trong `backend/app/core/config.py` (commit `bef0d9c`, merge PR #5 `323ab90`), gắn lại nguồn `HPhucTV/VigorAI@main` và theo dõi deployment **`51958d75-17b1-44a1-accb-b5d611faaa77`** đạt **`[SUCCESS]`**.
- **File cập nhật phiên này:**
  - `docs/taskboard.md` (`T-M3-06` `[x]` $\rightarrow$ `M3: 6 / 15 Done (40.0%)`, `Tổng cộng: 17 / 63 Done (27.0%)`; cập nhật trạng thái `.aab` trỏ server thật ở `T-M2-06`).
  - `session_log.md` (Phiên 12).
- **Kiểm tra / Kết quả chạy thử:**
  - **Railway Deploy Logs (`51958d75`):** `alembic upgrade head` chạy `0001_initial_schema` thành công, seed hoàn tất `36` món ăn / `30` bài tập / `4` giáo án mẫu, Uvicorn chạy trên `:8080`, healthcheck `/healthz` trả `200 OK`.
  - **10/10 Live HTTPS E2E Smoke Checks (`https://vigorai-production.up.railway.app`):** `GET /healthz` (`200`), `GET /delete-account` (`200`), `GET /docs` (`200`), `POST /api/v1/auth/register` thiếu disclaimer (`400`), Register hợp lệ (`201`), `POST /api/v1/auth/refresh` (`200`), `GET /api/v1/users/me/export` (`200`), `DELETE /api/v1/users/me` (`200`), token cũ gọi lại sau xóa (`401`), và kênh Web `POST /api/v1/users/delete-via-web` (`200`) + login lại (`401`). Không để lại user test trong DB production.
  - **Final Signed Release `.aab` (`USE_MOCK_API=false`, `API_BASE_URL=https://vigorai-production.up.railway.app`):** Exit `0`, xuất `mobile/build/app/outputs/bundle/release/app-release.aab` (`44,689,240 B`), xác minh bởi `jarsigner -verify -verbose -certs` (`jar verified.`, `CN=VigorAI`).
- **Việc cần làm ở phiên kế tiếp:**
  - Bạn thực hiện **`T-M1-07`** (đăng ký Google Play Console \$25, xác minh danh tính, gom 20–25 email testers) và tải `mobile/build/app/outputs/bundle/release/app-release.aab` lên **Closed Testing** cùng URL chính sách xóa tài khoản `https://vigorai-production.up.railway.app/delete-account` để chốt **`T-M2-06`** và kích hoạt đồng hồ 14 ngày.

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
