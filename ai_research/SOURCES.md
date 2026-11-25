# Nguồn dữ liệu huấn luyện AI Model B (`[OWNER: M4]`)

Ghi mọi dataset ngoài được dùng, để báo cáo đồ án có nguồn rõ ràng và tuân thủ giấy phép.
Ảnh gốc nằm trong `ai_research/datasets/raw/` (không commit lên Git). File này thì commit.

| Bộ dữ liệu | Tác giả | Link | Giấy phép | Số ảnh | Lớp dùng | Gán vào |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Pork rice Computer Vision Dataset | thitipat Kamolsakkamjorn | https://universe.roboflow.com/ (tìm "Pork rice Computer Vision Dataset") | CC BY 4.0 | 181 | `egg` (161 khung) | `BOILED_EGG` |
| Food Detection Computer Vision Dataset (v1 original-version) | workeveryday | https://universe.roboflow.com/workeveryday/food-detection-qgw0f/dataset/1 | Public Domain | 5.571 | `nasi-putih` (199 khung), `salad` (132), `salmon` (137), `steak` (146), `telur-mata-sapi` (156) | `WHITE_RICE`, `GREEN_SALAD`, `SALMON_FILLET`, `BEEF_STEAK`, `FRIED_EGG` |

Ghi chú theo bộ:

- **Pork rice:** nhãn `egg` là trứng hầm kiểu Thái (cắt đôi, cạnh thịt hầm), khác trứng luộc thường; chỉ nên dùng làm nguồn bổ sung cho `BOILED_EGG`. Hai lớp `Pork rice` và `leg pork` không thuộc 18 món v1.0 nên bị bỏ. Bản tải về là phiên bản tự tạo (không augmentation, không resize). Lệnh gán: `--map "pork-rice:egg=BOILED_EGG"`.

- **Food Detection (workeveryday):** 40 lớp, phần lớn món Indonesia và món Âu nên bị bỏ (34 lớp). Chỉ `nasi-putih`, `salad`, `salmon`, `steak` tự khớp alias; `telur-mata-sapi` (trứng ốp la) gán bằng `--map "food-detection:telur-mata-sapi=FRIED_EGG"`. Cố ý không gán `telur-dadar` (trứng chiên dạng omelet), `telur-balado` (trứng sốt sambal), `ayam` và `seafood` vì không chắc đúng món. Bản tải về là v1 `original-version`, không augment. Chạy gộp với Pork rice ra 718 ảnh (592/84/42), 6 lớp có dữ liệu.

Cách thêm một bộ mới: điền một dòng vào bảng trên (ghi rõ giấy phép; nếu trang không ghi, viết "chưa rõ"), rồi ghi lệnh `--map` đã dùng.
