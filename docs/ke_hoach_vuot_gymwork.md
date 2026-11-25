# Kế hoạch Nâng cấp VigorAI Vượt mặt Gymwork (`짐워크`)

> **Tài liệu thảo luận & đặc tả sản phẩm**
> **Ngày lập:** 2026-11-23
> **Mục tiêu:** Biến VigorAI từ một ứng dụng nhật ký sức khỏe + 3D thuần tiện ích thành một **hệ sinh thái cá nhân hóa tập luyện & dinh dưỡng AI 3D đẳng cấp cao**, khắc phục toàn bộ điểm yếu giao diện/onboarding so với Gymwork (`짐워크` — 4.9★, 90 MB) và phát huy tối đa những vũ khí độc quyền mà VigorAI đã có sẵn.

---

## 1. Giải phẫu Đối thủ: Gymwork Mạnh ở đâu & VigorAI Thắng Tuyệt đối ở đâu?

| Tiêu chí | Gymwork (`짐워크`) | VigorAI (Hiện tại -> Sau nâng cấp) | Lợi thế Vượt trội của VigorAI |
| :--- | :--- | :--- | :--- |
| **Lần đầu vào app (First Impression)** | Chuỗi câu hỏi cá nhân hóa đa bước (tuổi, chiều cao, cân nặng, `%` mỡ, vóc dáng, kinh nghiệm, nơi tập, thời gian, giáo án VĐV) kèm animation mượt, tạo cảm giác "được thiết kế riêng". | Hiện mới có màn hình văn bản Miễn trừ Y tế ([onboarding_disclaimer_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart)) + form đăng ký 1 trang ([register_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/auth_privacy/presentation/register_screen.dart)). | **Nâng cấp trọng tâm:** Thay thế màn mở đầu khô khan bằng **Wizard 6 bước có Avatar 3D tương tác trực tiếp** theo từng lựa chọn cơ thể & nhóm cơ. |
| **Trực quan hóa Cơ bắp & Kỹ thuật tập** | Hình vẽ 2D xám + tô đỏ vùng cơ tĩnh trên mặt phẳng; không xoay được, không thấy lỗi sai động tác. | **Mô hình giải phẫu 3D `.glb` thời gian thực** (33 bài tập): xoay 360°, 4 góc nhìn (`Trước / Ngang / Sau / Trên`), so sánh **Chuẩn vs. Lỗi sai (`Anim_GoodForm` / `Anim_BadForm`)**, tua 3 pha hít thở & 3 Avatar (`Nam Chuẩn`, `Nữ Fitness`, `Nam Cơ bắp`). | **Vũ khí độc quyền:** Người tập nhìn thấy góc khớp & chuyển động 3D đa chiều, nhận biết lỗi võng lưng/khóa khớp thay vì nhìn ảnh 2D tĩnh. |
| **Hệ sinh thái Sức khỏe & AI** | Thuần sổ ghi chép lịch tập, bài tập và đồng hồ đếm ngược. | **All-in-One:** Tập Gym 3D + **Quét ảnh món ăn AI (`YOLOv8`)** + **Nước thông minh (tự cộng `+500`/`+750 ml` sau buổi tập)** + **Giấc ngủ** + **Bản đồ Phục hồi 3D 11 bó cơ**. | Người dùng chỉ cần **1 app duy nhất** thay vì phải cài tách rời app lịch tập + app tính calo + app nhắc uống nước. |
| **Điều hướng (Navigation)** | Thanh Tab đáy (Bottom Nav) tách bạch rõ ràng, vào Lịch tập / Biểu đồ / Hồ sơ trong 1 chạm. | Đang dồn toàn bộ vào 1 trang cuộn dài ở [health_dashboard_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/health/presentation/health_dashboard_screen.dart) (phải cuộn xuống đáy mới thấy `Tập Gym 3D` và `AI Coach`). | **Nâng cấp trọng tâm:** Chuyển sang **Bottom Navigation 5 Tab** rõ ràng, đưa **Phòng tập 3D** và **Lịch & Giáo án** lên vị trí 1 chạm. |
| **Dung lượng & Hoạt động Offline** | **90 MB** trên CH Play. | **65.58 MB** (APK đa kiến trúc) / **< 40 MB** (`.aab` chuẩn CH Play nhờ tách CDN), kiến trúc 100% Offline-First (Drift SQLite + cache `.glb` kiểm tra SHA-256). | Nhẹ hơn ~30%, mở ở phòng tập tầng hầm mất sóng vẫn xem 3D & ghi log hiệp tập mượt mà. |

---

## 2. Trụ cột 1: Interactive 3D Onboarding Wizard 6 Bước

Thay vì bắt người dùng đọc nhiều chữ hoặc gõ bàn phím dài, luồng vào app lần đầu sẽ được thiết kế thành **6 bước chạm-chọn mượt mà** có thanh tiến độ liên tục, phản hồi rung nhẹ (`HapticFeedback.selectionClick()`) và mô hình 3D phản ứng theo lựa chọn.

### Thanh đầu trang gọn nhẹ & Chống bể layout (`360dp + 1.3x`)
- Bố cục hàng trên cùng chỉ gồm **3 thành phần tinh gọn** nằm trong `Row` với `Expanded` / `FittedBox(fit: BoxFit.scaleDown)`:
  `[Bước X/6]   ...   [☀️/🌙]  [Đăng nhập]`
- **Nút `Đăng nhập` nhỏ gọn ở góc phải:** Dành cho người dùng đã có tài khoản hoặc khi test nhanh tài khoản demo — bấm vào mở hộp thoại xác nhận nhanh **Miễn trừ Y tế** (giữ 100% chuẩn CH Play) rồi chuyển thẳng tới `/login` mà không cần đi lại 6 bước, đồng thời tuyệt đối không rớt dòng hay tràn viền trên màn hình `360dp` phóng chữ `1.3x`.

### Luồng trải nghiệm chi tiết từng bước

1. **Bước 1 — Hồ sơ Cơ thể & Avatar 3D Tương tác (`Giới tính · Tuổi · Chiều cao · Cân nặng`)**
   - **Chọn Giới tính (`Nam` / `Nữ`):** Avatar 3D trên màn hình chuyển ngay lập tức giữa `Nam Chuẩn` và `Nữ Fitness`.
   - **Tuổi (`16–75`):** Bánh xe cuộn mượt hoặc thanh trượt nhanh -> dùng để tính BMR chính xác theo tuổi (`Mifflin-St Jeor`).
   - **Chiều cao (`140–210 cm`), Cân nặng hiện tại (`35–180 kg`) & Cân nặng mục tiêu:** Thanh trượt thước đo (Ruler Slider) có hiệu ứng số nhảy mượt và hiển thị ngay phân loại BMI Châu Á theo thời gian thực.

2. **Bước 2 — Vóc dáng (`Somatotype`) & Ước lượng Tỷ lệ mỡ (`% Body Fat`) Trực quan**
   - *Giải quyết rào cản tâm lý:* Đa số người tập không đo InBody nên không biết `% Body Fat` của mình. Thay vì bắt nhập số khô khan, hiển thị **4 thẻ trực quan** để chọn 1 chạm:
     - **Săn chắc / Rõ nét cơ:** ước lượng `10%` (Nam `8–12%`) · `17%` (Nữ `15–19%`).
     - **Cân đối / Thể thao:** ước lượng `15%` (Nam `13–17%`) · `22%` (Nữ `20–24%`) *(chuyển Avatar 3D sang `Nam Cơ bắp` nếu mục tiêu là Tăng cơ nâng cao)*.
     - **Trung bình / Hơi đầy:** ước lượng `21%` (Nam `18–24%`) · `28%` (Nữ `25–30%`).
     - **Dễ tích mỡ / Cần giảm mỡ ưu tiên:** ước lượng `28%` (Nam `25%+`) · `34%` (Nữ `31%+`).
   - **Chọn Tạng người (`Somatotype`):**
     - `Ectomorph` (Người gầy, khung xương nhỏ, chuyển hóa nhanh, khó tăng cân).
     - `Mesomorph` (Khung xương cân đối, vai rộng, dễ tăng cơ & phục hồi nhanh).
     - `Endomorph` (Khung xương to, dễ tăng sức mạnh nhưng dễ tích mỡ).

3. **Bước 3 — Kinh nghiệm Tập luyện & Địa điểm Tập (`Thiết bị sẵn có`)**
   - **Kinh nghiệm tập:**
     - `Người mới (< 6 tháng)`: Ưu tiên bài cơ bản dễ kiểm soát kỹ thuật, `3 hiệp`, `RPE mục tiêu 6.5–7.5`, nhấn mạnh xem 3D `Chuẩn / Lỗi sai`.
     - `Trung cấp (6–24 tháng)`: Split đa dạng (`PPL` / `Upper-Lower`), tăng volume trung bình, `RPE 7.5–8.5`.
     - `Nâng cao (> 2 năm)`: Volume cao hơn, hỗ trợ `Superset` / biến thể tạ nặng, `RPE 8.0–9.0`.
   - **Địa điểm tập luyện (Trực tiếp lọc thư viện 33 bài tập 3D):**
     - `Phòng Gym đầy đủ máy`: Mở khóa toàn bộ `BARBELL`, `DUMBBELL`, `CABLE`, `MACHINE`, `BODYWEIGHT`.
     - `Tại nhà với Tạ đơn`: Ưu tiên `DUMBBELL` + `BODYWEIGHT` (tự động thay thế bài máy/đòn tạ).
     - `Tại nhà Không dụng cụ / Calisthenics`: Chỉ chọn `BODYWEIGHT` (`PUSH_UP`, `PLANK`, `HANGING_LEG_RAISE`, `WALKING_LUNGE`...).

4. **Bước 4 — Quỹ Thời gian & Nhóm cơ Ưu tiên**
   - **Tần suất tập:** Chọn `3`, `4`, `5`, hoặc `6 buổi/tuần` và chọn trực tiếp các ngày rảnh trong tuần (`T2 -> CN`).
   - **Thời lượng mỗi buổi:**
     - `30 phút` (Nhanh gọn / Giờ nghỉ trưa)
     - `45–60 phút` (Tiêu chuẩn cân bằng)
     - `75–90 phút` (Chuyên sâu / Thể hình)
   - **Nhóm cơ muốn ưu tiên phát triển (`Chọn nhiều`):** `Ngực`, `Lưng Xô`, `Vai`, `Tay (Trước/Sau)`, `Mông & Chân`, `Bụng & Lõi`.
   - **Điểm nhấn 3D:** Khi người dùng chạm chọn nhóm cơ nào (ví dụ `Ngực` và `Vai`), **bó cơ `Mat_Muscle_Chest` và `Mat_Muscle_Shoulders` trên mô hình 3D sẽ phát sáng màu nhấn ngay lập tức** thông qua JS Bridge có sẵn.

5. **Bước 5 — Chọn Chương trình Riêng hay Chương trình của VĐV**
   - **Lựa chọn A — AI Thiết kế Riêng theo Vóc dáng của bạn:** Hệ thống tự động lắp ghép giáo án từ toàn bộ câu trả lời Bước 1–4.
   - **Lựa chọn B — Tập theo Chương trình VĐV & Giáo án Kinh điển (`Pro Athlete Programs`):**
     1. **CBum Classic Physique PPL (6 buổi/tuần):** Tập trung vai rộng, ngực trên dày và lưng xô hình chữ V (*V-Taper*).
     2. **Jeff Nippard Science-Based Upper/Lower (4 buổi/tuần):** Tối ưu hóa hypertrophy dựa trên khoa học thể thao, cân bằng Đẩy/Kéo.
     3. **Arnold Golden Era Volume (5–6 buổi/tuần):** Phối hợp Ngực–Lưng đối kháng, chú trọng thẩm mỹ tay & vai.
     4. **Glute & Core Sculpt — Nữ Fitness (4 buổi/tuần):** Trọng tâm Mông (`BARBELL_HIP_THRUST`, `CABLE_GLUTE_KICKBACK`), Đùi sau, Lõi & Lưng thon.
     5. **Home Dumbbell & Bodyweight Shred (3–4 buổi/tuần):** Đốt mỡ giữ cơ trong `30–45 phút` tại nhà chỉ với tạ đơn & trọng lượng cơ thể.

6. **Bước 6 — Tổng kết "Phác đồ Của Riêng Bạn Đã Sẵn Sàng!" & Miễn trừ Y tế CH Play**
   - Hiệu ứng đếm số mượt (`TweenAnimationBuilder`) hiển thị thành quả ngay sau khảo sát:
     - **Chỉ số Calo & Macro mục tiêu/ngày** (tính chuẩn từ công thức `Mifflin-St Jeor (1990)` dựa trên giới tính, tuổi, chiều cao, cân nặng, mức vận động và mục tiêu tăng cơ/giảm mỡ/giữ dáng).
     - **Mục tiêu nước uống hàng ngày** (`35 ml × cân nặng + bù +500/+750 ml buổi tập`).
     - **Lịch tập tuần đã được nạp sẵn vào SQLite** (từ thứ `T2` đến `CN`, vào app là tập được ngay).
   - Đặt Checkbox **Miễn trừ Trách nhiệm Y tế** ngay dưới bản phác đồ tổng kết để vừa đạt 100% tiêu chuẩn Google Play Store vừa mang lại trải nghiệm tự nhiên, không bị cảm giác "màn hình cảnh báo khô cứng" như bản cũ.

*(Lưu ý cho người dùng đã đăng nhập sẵn: Trong phần Hồ sơ / Cài đặt vẫn có nút **"Chỉnh sửa lại Hồ sơ & Tạo lại Lịch tập"** để gọi lại Wizard bất cứ lúc nào.)*

---

## 3. Trụ cột 2: Bộ máy Sinh Giáo án Thông minh (`Smart Routine Generator Engine`)

Tránh tình trạng "hỏi cho có nhưng vào trong ai cũng giống ai", bộ máy sẽ tận dụng **33 bài tập 3D** và thuật toán **`findSwapCandidates` (`overlapRatio`)** hiện có trong [workout_repository.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/workout/data/workout_repository.dart) để biến hóa lịch tập thật sự:

| Biến số đầu vào | Cách Bộ máy xử lý vào Giáo án thực tế |
| :--- | :--- |
| **Địa điểm tập = Gym đầy đủ** | Dùng tối ưu các bài đòn tạ, cáp, máy & tạ đơn (`BARBELL_BENCH_PRESS`, `LAT_PULLDOWN`, `LEG_PRESS`, `CABLE_FACE_PULL`...). |
| **Địa điểm tập = Tại nhà (Tạ đơn)** | Giữ `DUMBBELL` & `BODYWEIGHT`; tự động gọi thuật toán trùng nhóm cơ (`overlapRatio`) thay `BARBELL_BENCH_PRESS` -> `INCLINE_DUMBBELL_PRESS` / `PUSH_UP`, `BARBELL_BENT_OVER_ROW` -> biến thể tạ đơn... |
| **Địa điểm tập = Không dụng cụ** | Lọc nghiêm ngặt về `BODYWEIGHT` (`PUSH_UP`, `PLANK`, `HANGING_LEG_RAISE`, `WALKING_LUNGE`), tự động tăng rep mục tiêu (`12–20 reps`) để đủ kích thích cơ. |
| **Thời lượng = `30 phút`** | `3–4 bài/buổi` · `3 hiệp/bài` · nghỉ `60–75s` (ưu tiên bài Compound đa khớp để tối ưu thời gian). |
| **Thời lượng = `45–60 phút`** | `5 bài/buổi` · `3–4 hiệp/bài` · nghỉ `90–120s`. |
| **Thời lượng = `75–90 phút`** | `6–7 bài/buổi` · `4 hiệp` cho bài Compound chính + `3 hiệp` bài cô lập · nghỉ `120–150s`. |
| **Tạng Ectomorph (Gầy)** | Rep `6–10`, thời gian nghỉ dài hơn (`120–150s`), Calo mục tiêu cộng thặng dư (`+350 đến +450 kcal`). |
| **Tạng Mesomorph (Cân đối)** | Rep `8–12`, nghỉ `90–120s`, cân bằng Macro (`Protein 2.0 g/kg`). |
| **Tạng Endomorph (Dễ tích mỡ)** | Rep `10–15`, nghỉ ngắn hơn (`60–90s`) giữ nhịp tim cao, Calo thâm hụt an toàn (`-350 đến -450 kcal`), giữ Protein cao (`2.0–2.2 g/kg`) tránh mất cơ. |
| **Nhóm cơ ưu tiên** | Cộng thêm `+1 bài cô lập` hoặc `+1 hiệp` vào đúng các buổi có nhóm cơ ưu tiên của người dùng (ví dụ ưu tiên `Vai` -> chèn `DUMBBELL_LATERAL_RAISE` vào ngày Đẩy/Thân trên). |

---

## 4. Trụ cột 3: Tái cấu trúc Bố cục 5 Tab (`Bottom Navigation Bar`)

Thay vì nhồi mọi thứ vào 1 trang cuộn dài ở `/health`, thiết kế một **`MainNavigationShell`** sử dụng Material 3 `NavigationBar` ngay tại route `/health`. **Ưu điểm kỹ thuật:** Không phải đụng vào file khóa `[LOCKED STUB]` [app_router.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/core/router/app_router.dart), vẫn giữ tương thích toàn bộ deep-link con hiện tại.

```text
+-------------------------------------------------------------------------+
| AppBar: [VigorAI · Xin chào...]                  [Sync]  (Avatar Tron)  |
|-------------------------------------------------------------------------|
|                       MainNavigationShell (/health)                     |
+-------------+---------------+--------------+-------------+--------------+
| Tab 1       | Tab 2         | Tab 3        | Tab 4       | Tab 5        |
| Hôm nay     | Lịch tập      | Phòng tập 3D | Dinh dưỡng  | AI & Cơ thể  |
|             |               |  (Nổi bật)  |             |              |
+-------------+---------------+--------------+-------------+--------------+
```

### 4.1. Chi tiết từng Tab
1. **Tab 1 — `Hôm nay` (Tổng quan Hành động):**
   - **Trên cùng: Hero Card "Buổi tập Hôm nay"** hiển thị tên giáo án khớp với thứ hiện tại (ví dụ: *Thứ 2 · CBum Classic Push — Ngực & Vai · ~55 phút*), danh sách tóm tắt nhóm cơ và nút nổi bật **"Bắt đầu tập ngay"** (1 chạm vào [live_workout_logger_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/workout/presentation/live_workout_logger_screen.dart)).
   - **Cụm 3 thẻ thông minh ngay dưới:**
     - **Sẵn sàng AI (`79 điểm`)** + thanh trạng thái phục hồi tổng quan.
     - **Calo & Nước thông minh (`+250 ml / +500 ml`)** tương tác nhanh.
     - **Cân nặng · Bước chân · Giấc ngủ** dạng lưới 2–3 thẻ gọn.
2. **Tab 2 — `Lịch tập` (`Routines & Pro Programs`):**
   - Bộ chọn lịch tuần `T2 -> CN` có chấm chỉ báo ngày có lịch.
   - Tab con hoặc bộ lọc nhanh: **Giáo án Của tôi (AI tạo)** · **Chương trình VĐV** · **Tự thiết kế** (gọi thẳng `RoutineBuilderSheet` từ [routines_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/workout/presentation/routines_screen.dart)).
3. **Tab 3 — `Phòng tập 3D` (Điểm nhấn Trung tâm Thanh Điều hướng):**
   - Mở thẳng thư viện 33 bài tập 3D ([gym3d_library_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/gym3d/presentation/gym3d_library_screen.dart)) với chip lọc theo 11 bó cơ & dụng cụ, badge chỉ báo tư thế `Đúng / Sai 3D`, bấm vào là xoay 360°.
4. **Tab 4 — `Dinh dưỡng` (Calo, Quét ảnh AI & Supplement):**
   - Vòng tròn Calo + 3 thanh Macro (`Đạm / Carb / Fat`).
   - Thẻ hành động lớn **"Quét món ăn bằng AI"** (`YOLOv8`).
   - Theo dõi nước thông minh & checklist Thực phẩm bổ sung hôm nay (`Creatine`, `Whey`, `Omega-3`).
5. **Tab 5 — `AI & Cơ thể` (Phân tích Chuyên sâu):**
   - Lối vào trực tiếp 3 tab **AI Coach** (`Phục hồi 3D 11 bó cơ`, `Volume & Kỷ lục 1RM`, `Radar Cân bằng 6 nhóm cơ`), Biểu đồ Cân nặng/BMI Châu Á và Ảnh tiến độ `Before/After` (lưu cục bộ).

### 4.2. Khung Avatar Tròn Góc Trên Bên Phải & Màn hình Hồ sơ Cá nhân (`Profile Hub`)
Thay vì tốn thêm 1 Tab thứ 6 dưới đáy (làm chật thanh Bottom Nav trên màn hình `360dp`), **góc cập nhật thông tin cá nhân được thiết kế theo mô hình chuẩn các app Fitness cao cấp**:

- **Điểm chạm cố định trên AppBar (Góc trên bên phải):**
  - Một **khung Avatar tròn nhỏ (`36×36 dp`)** nằm ở góc trên bên phải luôn xuất hiện ở các Tab chính, hiển thị chữ cái đầu tên người dùng (hoặc icon Avatar 3D tương ứng giới tính/vóc dáng) kèm chấm trạng thái nhỏ (xanh lá = đã đồng bộ, cam = có dữ liệu chờ đồng bộ).
  - Chạm vào khung Avatar tròn mở màn hình **`/profile` (`ProfileSettingsScreen`)** với hiệu ứng chuyển cảnh `Hero` / `Slide` mượt mà.
- **4 Nhóm chức năng bên trong Màn hình Hồ sơ & Cập nhật Thông tin (`/profile`):**
  1. **Chỉ số Cơ thể & Vóc dáng:** Sửa nhanh Họ tên, Giới tính (`Nam / Nữ`), Tuổi/Năm sinh, Chiều cao (`cm`), Cân nặng hiện tại & mục tiêu (`kg`), `% Body Fat`, Tạng người (`Ectomorph / Mesomorph / Endomorph`), và chọn Avatar 3D mặc định (`Nam Chuẩn / Nữ Fitness / Nam Cơ bắp`).
  2. **Cấu hình Tập luyện & Mục tiêu:** Sửa Kinh nghiệm tập (`Mới / Trung cấp / Nâng cao`), Nơi tập (`Phòng Gym / Tạ đơn tại nhà / Tay không`), Thời lượng buổi tập (`30 / 45–60 / 75–90 phút`), Các ngày tập trong tuần (`T2–CN`), Nhóm cơ ưu tiên, Chương trình VĐV đang theo — kèm nút **"Làm lại Khảo sát 6 Bước"** nếu user muốn chọn lại từ đầu theo giao diện Wizard.
  3. **Tự động Tính lại Phác đồ Thời gian thực (`Realtime Recalculation`):** Ngay khi bấm **Lưu thay đổi**, hệ thống tự động ghi thêm bản ghi `BiometricLogs` mới, tính lại **BMI Châu Á**, **BMR/TDEE & Macro (`Mifflin-St Jeor`)**, **Lượng nước mục tiêu (`35 ml/kg`)**, đồng thời hiện công tắc/hộp thoại hỏi *"Bạn có muốn tạo lại Lịch tập tuần theo thông số mới không?"* để đồng bộ tức thì sang Tab `Lịch tập`.
  4. **Tài khoản, Đồng bộ & Chính sách CH Play:** Dời nút **Đồng bộ ngay**, **Xem lại Miễn trừ Trách nhiệm Y tế**, **Đăng xuất**, và thẻ **Xóa tài khoản vĩnh viễn** từ trang chủ Dashboard vào cuối màn hình Hồ sơ này — giúp trang `Hôm nay` cực kỳ gọn gàng mà vẫn đảm bảo 100% quy định xóa tài khoản của Google Play.

### 4.3. Nâng cấp Phần Mô tả & Hướng dẫn Kỹ thuật Chi tiết trong Phòng tập 3D (Tab Trung tâm)
Giữ **`Phòng tập 3D`** làm **Tab trung tâm (Tab 3/5)** để người dùng dễ bấm xem hướng dẫn bài tập mọi lúc (còn nút *"Bắt đầu tập ngay"* đã đặt nổi bật ở Hero Card đầu Tab `Hôm nay` và Tab `Lịch tập`).

Bên trong màn hình chi tiết bài tập ([exercise_3d_detail_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/gym3d/presentation/exercise_3d_detail_screen.dart)) & dữ liệu bài tập ([exercise_repository.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/gym3d/data/exercise_repository.dart)), phần mô tả ngắn hiện tại sẽ được nâng cấp thành **Cẩm nang Kỹ thuật 4 Phần trực quan**, liên kết trực tiếp với mô hình 3D:

1. **Bước Chuẩn bị Tư thế (`Setup & Điểm tựa`):**
   - Hướng dẫn từng điểm chốt cơ thể trước khi nhấc tạ: vị trí bàn chân trụ sàn, độ rộng tay cầm (`rộng hơn vai` / `ngang vai`), góc nghiêng ghế (`0°`, `30°`, `45°`), cách ép & hạ bả vai xuống ghế và hít gồng chặt bụng (`Bracing`).
2. **Chuyển động 3 Pha & Nhịp Thở Chi tiết (`Đồng bộ với Thanh tua 3D`):**
   - **Pha 1 — Hạ tạ / Giãn cơ (`Eccentric · 2–3 giây · Hít sâu bằng mũi`):** Nói rõ quỹ đạo thanh đòn/tạ đi xuống tới điểm nào (ví dụ: chạm nhẹ giữa ngực, góc khuỷu tay mở `45°` tránh xòe `90°`).
   - **Pha 2 — Giữ đáy / Điểm căng nhất (`Isometric · 0.5–1 giây · Giữ áp lực lõi`):** Hướng dẫn dừng chủ động để cắt quán tính, không để tạ nảy hoặc mất lực gồng.
   - **Pha 3 — Phát lực / Đẩy lên (`Concentric · 1–1.5 giây · Thở ra dứt khoát`):** Hướng đẩy đúng quỹ đạo và điểm dừng cuối (dừng trước khi khóa cứng khớp khuỷu/gối để giữ an toàn & áp lực vào cơ).
3. **Cảm nhận Cơ bắp Đúng (`Mind-Muscle Connection`):**
   - Giải thích rõ bó cơ nào phải mỏi/căng chủ đạo và khớp nào cần giữ cố định, khớp màu với chú thích **Đỏ (Cơ chính)** · **Cam (Cơ phụ)** · **Vàng (Cơ ổn định)** khi người dùng chạm trực tiếp vào bó cơ trên mô hình 3D.
4. **Phân tích Lỗi sai & Cách Sửa (`Liên kết trực tiếp với chế độ "Lỗi sai" 3D`):**
   - Khi người dùng gạt nút **`Lỗi sai`** trên sân khấu 3D, phần hướng dẫn làm nổi bật thẻ cảnh báo theo cấu trúc 3 dòng dễ đọc:
     - **❌ Lỗi đang mô phỏng trên 3D:** *(ví dụ: Xòe khuỷu tay 90° hoặc cong lưng dưới)*
     - **⚠️ Tác hại:** *(tăng áp lực dây chằng khớp vai trước / chèn ép đĩa đệm L4–L5)*
     - **✅ Cách sửa ngay:** *(khép nhẹ khuỷu tay về góc ~45° và giữ gót chân bám chặt mặt sàn)*

---

## 5. Trụ cột 4: Chuẩn Thiết kế UI, Dual Theme (Light/Dark Mode) & Animation Mượt Cao cấp

Để tạo cảm giác cao cấp ngang (hoặc vượt) các app Hàn Quốc như Gymwork trên Android tầm trung lẫn flagship, VigorAI hỗ trợ **cả 2 chế độ Light Mode & Dark Mode** một cách đồng bộ từ Onboarding tới mọi màn hình tập luyện:

### 5.1. Hệ thống Giao diện Kép: Light Mode (`Athletic Clean`) & Dark Mode (`Dark Sporty Carbon`)

1. **Bảng màu chuẩn hóa trong [app_theme.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/core/theme/app_theme.dart) (`[OWNER: M1]`):**
   | Thành phần UI | Light Mode (`Sáng Thể thao`) | Dark Mode (`Tối Phòng tập OLED`) |
   | :--- | :--- | :--- |
   | **Nền chính (`Scaffold`)** | `#F6F8FC` (Trắng xám dịu mắt) | `#0B0F17` (Đen Carbon sâu) |
   | **Thẻ nội dung (`Card`)** | `#FFFFFF`, viền `#E2E8F0` mỏng | `#151C28`, viền `#263042` (hòa quyện liền mạch với sân khấu 3D `#12161F`) |
   | **Màu nhấn chính (`Primary`)** | `#1565C0` (Athletic Blue) | `#3B82F6` (Electric Blue sáng rõ trên nền tối) |
   | **Màu phụ (`Accent`)** | `#00BFA5` (Teal Mint) | `#14B8A6` (Neon Teal) |
   | **Thanh Nav đáy (`NavigationBar`)** | Trắng mờ, icon Active xanh đậm | `#111827`, pill Active ánh xanh phát sáng nhẹ |
2. **Thẻ màu Ngữ nghĩa Tự thích ứng (`Adaptive Semantic Surfaces`):**
   - Trong code hiện tại vẫn còn một số hộp thông báo dùng màu sáng cứng (`Colors.red.shade50`, `Colors.blue.shade50`, `Color(0xFFE3F2FD)`, `Colors.black87`), nếu bật Dark Mode dễ bị chói trắng hoặc chữ tối trùng nền tối.
   - Bổ sung helper dùng chung `AppColors.tintedSurface(context, baseColor)` tự động chọn alpha nhẹ (`0.08` ở Light Mode và `0.18` ở Dark Mode) và đọc toàn bộ màu chữ từ `Theme.of(context).colorScheme` (`onSurface`, `onSurfaceVariant`).
3. **Cách chuyển đổi 3 chế độ (`Theo hệ thống` · `Light` · `Dark`) mà không chạm `[LOCKED STUB]` [main.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/main.dart):**
   - [main.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/main.dart) hiện đã khai báo sẵn `theme: AppTheme.lightTheme`, `darkTheme: AppTheme.darkTheme`, `themeMode: ThemeMode.system` -> khi máy Android bật/tắt Dark Mode, app tự đổi tức thì.
   - Để người dùng **chủ động gạt Light / Dark ngay trong app** (bất kể máy đang ở chế độ nào) mà vẫn giữ nguyên `main.dart` khóa:
     - Thêm nút gạt nhanh **`☀️ / 🌙`** ở góc trên của **Onboarding Wizard 6 bước** và mục **"Giao diện (`Theo máy` / `Sáng` / `Tối`)"** trong trang **Hồ sơ Cá nhân (`/profile`)**, lưu vào `SharedPreferences`.
     - Dùng wrapper `VigorAdaptiveTheme` (`AnimatedTheme` thời lượng `250ms`) đọc `themePreferenceProvider` cho toàn bộ Wizard, `MainNavigationShell` 5 Tab, `/profile` và các màn hình con.

### 5.2. Chuẩn Animation & Hiệu năng Chuyển động Mượt (60/120 FPS)

1. **Chuyển bước Onboarding (`PageTransitionSwitcher` tự viết bằng Flutter core):**
   - Kết hợp `AnimatedSwitcher` + `FadeTransition` + `SlideTransition` (`Offset(0.08, 0) -> Offset.zero`), đường cong `Curves.easeOutCubic`, thời lượng `280ms`.
   - Thanh tiến độ trên đầu dùng `TweenAnimationBuilder<double>` nối liền mạch `Bước 1/6 -> 6/6`.
2. **Vi tương tác (`Micro-interactions`) trên Thẻ Chọn:**
   - Khi chạm thẻ Vóc dáng, Nơi tập hoặc Chương trình VĐV: phóng nhẹ `AnimatedScale(scale: selected ? 1.02 : 1.0, duration: 180ms)`, viền nổi màu `colorScheme.primary`, nền tint tự thích ứng Sáng/Tối, kèm `HapticFeedback.selectionClick()`.
3. **Animation Số liệu Phác đồ (Bước 6):**
   - Các con số `Calo mục tiêu`, `Protein (g)`, `Lượng nước (ml)` đếm tăng mượt trong `600ms` bằng `TweenAnimationBuilder<int>`.
4. **Hiệu năng WebGL 3D & Tương thích màn hẹp:**
   - Giữ đúng chuẩn responsive **`360dp` + `font_scale 1.3x`** (đã chứng minh không tràn/lỗi ở Phiên 30): mọi nút/chip/nhãn trong Wizard và 5 Tab đều bọc `Expanded` / `Flexible(FittedBox)` / `Wrap`.
   - Khi rời tab `Phòng tập 3D` sang tab khác, giữ state scroll danh sách (`IndexedStack` hoặc `PageStorage`) nhưng chỉ khởi tạo `ModelViewer` WebView khi người dùng vào chi tiết hoặc tab `Phục hồi 3D` để tiết kiệm RAM & pin.
5. **Lưu trữ Offline-First & Đồng bộ Server:**
   - Lưu hồ sơ khảo sát (`age`, `somatotype`, `estimatedBodyFatPct`, `experienceLevel`, `trainingLocation`, `sessionDurationMin`, `weeklyDays`, `priorityMuscles`, `selectedProgramType`, `themeMode`) vào `SharedPreferences` + JSON cục bộ để dùng ngay khi offline.
   - Đồng bộ thẳng bản ghi `BiometricLogs` đầu tiên + `WorkoutRoutines` mới tạo vào Drift SQLite và hàng đợi đồng bộ (`SyncQueueManager`) sẵn có.

---

## 6. Lộ trình Triển khai Kỹ thuật (Tuân thủ 100% `AGENTS.md`, `0` File `[LOCKED STUB]`)

Toàn bộ nâng cấp được chia làm **3 Giai đoạn**, chỉ chạm các thư mục thuộc quyền `[OWNER: M1]` và `[OWNER: M2]`:

| Giai đoạn | Phạm vi (`[OWNER]`) | File Tạo mới / Chỉnh sửa | Đầu ra & Nghiệm thu |
| :--- | :--- | :--- | :--- |
| **Giai đoạn 1: Dual Theme Light/Dark + Onboarding Wizard 6 Bước** | **`[OWNER: M1]`** | • [app_theme.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/core/theme/app_theme.dart) *(chuẩn hóa bảng màu Sáng/Tối + helper tint + `themePreferenceProvider`)*<br>• `mobile/lib/features/auth_privacy/data/user_fitness_profile.dart` *(mới)*<br>• [onboarding_disclaimer_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart)<br>• [register_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/auth_privacy/presentation/register_screen.dart)<br>• [auth_controller.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/auth_privacy/presentation/auth_controller.dart) | Hỗ trợ mượt 2 chế độ **Light / Dark Mode**, luồng Wizard 6 bước có Avatar 3D tương tác, ước lượng `% Body Fat`, tính ngay Calo/Macro/Nước & ghi `BiometricLogs` đầu tiên. |
| **Giai đoạn 2: Bộ máy Sinh Giáo án, 5 Chương trình VĐV & Hướng dẫn 3D Kỹ** | **`[OWNER: M2]`** | • `mobile/lib/features/workout/domain/smart_routine_generator.dart` *(mới)*<br>• [workout_repository.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/workout/data/workout_repository.dart)<br>• [routines_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/workout/presentation/routines_screen.dart)<br>• [exercise_repository.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/gym3d/data/exercise_repository.dart)<br>• [exercise_3d_detail_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/gym3d/presentation/exercise_3d_detail_screen.dart) | Tự sinh lịch tập theo Nơi tập (`Gym / Tạ đơn / Tay không`), Thời lượng (`30/45/60/90p`), Tạng người & 5 Giáo án VĐV vào SQLite Drift; nâng cấp phần mô tả bài tập thành **Cẩm nang Kỹ thuật 4 Phần** liên kết chế độ `Chuẩn / Lỗi sai` 3D; chuẩn hóa màu Dark Mode. |
| **Giai đoạn 3: Main Navigation 5 Tab, Avatar Hồ sơ (`/profile`) & Test** | **`[OWNER: M1]` + `[OWNER: M2]`** | • [health_dashboard_screen.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/features/health/presentation/health_dashboard_screen.dart) *(Shell 5 Tab + Avatar tròn góc phải + Hero Card)*<br>• `mobile/lib/features/auth_privacy/presentation/profile_settings_screen.dart` *(mới — Màn hình Hồ sơ `/profile` + gạt Sáng/Tối)*<br>• [health_routes.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/lib/core/router/health_routes.dart) *(thêm route `/profile`, không chạm `app_router.dart`)*<br>• Các màn hình Health/FoodScan/Biometrics/Workout *(thay màu nền cứng sang `tintedSurface` tương thích Dark Mode)*<br>• [ui_layout_and_copy_test.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/test/health/ui_layout_and_copy_test.dart) & [workout_sprint2_test.dart](file:///c:/Users/tranh/Documents/Duy/Gym/mobile/test/workout/workout_sprint2_test.dart) | Thanh Bottom Nav 5 Tab + Khung Avatar tròn mở Hồ sơ cá nhân (`/profile`), test đủ Light + Dark Mode và `360dp + 1.3x`, build & verify APK Release mới. |

> **Cam kết An toàn Kiến trúc:** Không chỉnh sửa `app_router.dart`, `app_database.dart`, `main.dart`, `pubspec.yaml`, `.gitignore` (`[LOCKED STUB]`) và giữ nguyên toàn bộ 10 quyền Android hợp lệ chuẩn CH Play (0 quyền nhạy cảm bị cấm).

---

## 7. Trạng thái Chốt Thiết kế & Bàn luận Tiếp

### Đã chốt 5/5 quyết định cốt lõi
- ✅ **Góc cập nhật Hồ sơ (`/profile`):** Khung Avatar tròn nhỏ (`36×36 dp`) cố định ở góc trên bên phải AppBar.
- ✅ **Giao diện Kép Light Mode & Dark Mode:** Đầy đủ cả 2 chế độ + `Theo hệ thống` và nút gạt nhanh `☀️/🌙`.
- ✅ **Nút Đăng nhập nhanh trên Onboarding:** Nút `Đăng nhập` gọn trên thanh đầu (an toàn ở `360dp + 1.3x`), xác nhận nhanh Miễn trừ Y tế rồi vào `/login`.
- ✅ **5 Chương trình VĐV mẫu (Bước 5):** Tạm giữ 5 bộ (*CBum PPL*, *Jeff Nippard Upper/Lower*, *Arnold Volume*, *Glute & Core Nữ Fitness*, *Home Shred*).
- ✅ **Bố cục 5 Tab & Phòng tập 3D:** Giữ **`Phòng tập 3D`** ở vị trí **Tab trung tâm (Tab 3/5)** để user xem hướng dẫn kỹ thuật bất cứ lúc nào, kết hợp nâng cấp mô tả bài tập thành **Cẩm nang Kỹ thuật 4 Phần chi tiết** (Setup -> 3 Pha & Nhịp thở -> Cảm nhận cơ -> Lỗi sai & Cách sửa).

> **Sẵn sàng bàn tiếp:** Bạn muốn góp ý thêm về chi tiết nào nữa (ví dụ: nội dung hướng dẫn chi tiết cho 33 bài tập 3D, hiệu ứng đồng hồ nghỉ giữa hiệp, hay cách hiển thị điểm nhấn ở trang `Hôm nay`) trước khi bắt tay vào code?
