# Hồ sơ Chuẩn bị & Kiểm soát Phát hành Google Play Console (CH Play)

> **Phạm vi sở hữu:** `[OWNER: M1]` — Tuân thủ `AGENTS.md` (Mục 3) & `docs/roadmap.md` (Mốc 1 $\rightarrow$ Mốc 2 $\rightarrow$ Mốc 3).
> **Ứng dụng:** `VigorAI: Tập Gym 3D & Calo` (`com.vigorai.app`)
> **Trang web Chính sách Quyền riêng tư công khai (`Privacy Policy URL`):** `https://vigorai-production.up.railway.app/api/v1/users/privacy-policy`
> **Trang web Xóa tài khoản công khai (`Data Safety Delete URL`):** `https://vigorai-production.up.railway.app/delete-account`

---

## 1. Theo dõi Nhịp 1 — Closed Testing (`v1.0.0+1`) & Chuẩn bị Apply Production (`v1.1.0`) (`T-M1-07`, `T-M1-12`)

| Hạng mục kiểm soát | Trạng thái | Ghi chú kỹ thuật |
| :--- | :---: | :--- |
| **Tài khoản Google Play Console (\$25) & Xác minh danh tính** | `[x]` | Đã tạo & xác minh xong; đã hoàn tất toàn bộ Store Listing & tờ khai App Content |
| **Danh sách 20–25 Gmail Testers (Closed Testing 14 ngày liên tục)** | `[~]` | Đã tạo danh sách `Virgo` (16) + `tester-A1` (15) & đã nộp phát hành Closed Testing (`Đang xem xét`), chờ Google duyệt 24–72h để chạy 14 ngày |
| **Upload Keystore RSA 2048-bit & Signed `.aab` (`v1.0.0+2`, `targetSdk 36`)** | `[x]` | Đã ký `CN=VigorAI`, trỏ `https://vigorai-production.up.railway.app` |
| **URL Privacy Policy & Xóa tài khoản (`/api/v1/users/privacy-policy`, `/delete-account`)** | `[x]` | Đã live `200 OK` + test xóa qua Web (`POST /api/v1/users/delete-via-web`) |
| **Điều kiện Apply Production (`v1.1.0`) cuối Tuần 5** | `[~]` | Đủ 14 ngày Closed Testing + tích hợp Sprint 2 (`F01`, `F03`–`F06`, `F19` UI, `F24` ảnh, Sync) |

---

## 2. Rà soát Quyền Android (`AndroidManifest.xml`) & Đóng gói `.aab`

| Kiểm tra Policy Google Play | Nhịp 1 & 2 (`v1.0.0+1` / `v1.1.0`) | Nhịp 3 (`v1.2.0` — Sprint 3) |
| :--- | :---: | :---: |
| **`minSdk = 26`, `targetSdk = 36` (Android 16)** | Đạt | Đạt |
| **64-bit (`arm64-v8a`, `x86_64`) & 16 KB Page Size Alignment** | Đạt | Đạt |
| **Dung lượng cài đặt `.aab` gốc `< 40 MB`** | Đạt (`~11–25 MB`) | Đạt |
| **0 Quyền cấm** (`READ_MEDIA_IMAGES`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `SCHEDULE_EXACT_ALARM`, `USE_EXACT_ALARM`, `ACCESS_BACKGROUND_LOCATION`, `QUERY_ALL_PACKAGES`) | Chặn cứng bằng `tools:node="remove"` | Chặn cứng bằng `tools:node="remove"` |
| **Chọn ảnh món ăn (`F19`) & Before/After (`F24`)** | Android Photo Picker API (`image_picker`) | Android Photo Picker API (`image_picker`) |
| **Nhắc uống nước (`F03`) & Supplement (`F06`)** | `WorkManager` inexact + Native Notification Action `"Đã uống"` | `WorkManager` inexact + Native Notification Action |
| **Health Connect (`READ_STEPS`, `READ_SLEEP`, `READ_ACTIVE_CALORIES_BURNED`) & `FOREGROUND_SERVICE_HEALTH`** | Tạm comment (`[RE-ENABLE IN v1.2.0]`) để mở Production nhanh | Bật lại kèm Video minh họa nộp Health Apps Declaration |

---

## 3. Ma trận Khai báo **Data Safety** (Google Play Console)

| Loại dữ liệu thu thập | Mục đích thu thập | Chia sẻ bên thứ 3? | Mã hóa truyền tải & Lưu trữ | Cho phép người dùng xóa? |
| :--- | :--- | :---: | :---: | :--- |
| **Email & Tên hiển thị** | Tạo tài khoản, xác thực JWT (`F26`) | Không | HTTPS TLS + Argon2 hash | Có (`DELETE /api/v1/users/me` & `/delete-account`) |
| **Sinh trắc học & Sức khỏe** *(Cân nặng, 5 vòng đo, nước, bữa ăn, giấc ngủ)* | Tính BMI, BMR/TDEE, đồng bộ Offline-Online & AI Readiness | Không | HTTPS TLS + SQLite nội bộ + PostgreSQL | Có (Cascade Delete toàn phần) |
| **Ảnh món ăn (`F19`)** | Gửi tạm tới API AI Model B ước tính Calo/Macro | Không | HTTPS TLS (`< 300 KB`) | Có (Cascade Delete DB + Object Storage) |
| **Ảnh tiến độ cơ thể Before/After (`F24`)** | Lưu **100% cục bộ** tại `app_flutter/progress_photos/` để người dùng tự so sánh | Không | Không rời khỏi thiết bị; không vào Gallery công cộng | Có (`deleteAllPrivateProgressPhotos()` khi xóa tài khoản) |

---

## 4. Checklist Miễn trừ Y tế (Medical Disclaimer)
- [x] Bắt buộc xác nhận tại Onboarding (`OnboardingDisclaimerScreen`) kèm timestamp lưu PostgreSQL (`disclaimer_accepted_at`).
- [x] Trích dẫn nguồn công thức **Mifflin-St Jeor (1990)** tại màn hình Dinh dưỡng (`NutritionScreen`).
- [x] Hiển thị dòng miễn trừ trách nhiệm dưới kết quả nhận diện **AI Model B** (`FoodScanScreen`).
