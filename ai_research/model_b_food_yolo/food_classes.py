# [OWNER: M4] 18 lop mon an cot loi cho AI Model B v1.0 (T-M4-01)
"""Danh sach lop v1.0 + bang alias de gop nhan tu Roboflow / Kaggle ve `class_code`.

`class_code` KHOP 100% voi bang `food_nutrition_catalog` (seed boi M3), de
`ai_food_yolo.py` tra Calo/Macro truc tiep khong can anh xa them.

Alias chi la goi y. Sau khi chay `prepare_dataset.py`, xem muc `unmapped_source_classes`
trong `dataset_report.json` de bo sung alias con thieu.
"""
from __future__ import annotations

import re
import unicodedata

# (class_code, alias...) - alias co the co dau tieng Viet, se duoc chuan hoa khi so khop.
CORE_CLASSES_V1: list[tuple[str, tuple[str, ...]]] = [
    ("WHITE_RICE", ("rice", "white rice", "steamed rice", "cooked rice", "cơm", "cơm trắng")),
    ("BROWN_RICE", ("brown rice", "gạo lứt", "cơm gạo lứt")),
    (
        "GRILLED_CHICKEN_BREAST",
        ("chicken breast", "grilled chicken", "grilled chicken breast", "ức gà"),
    ),
    ("BOILED_EGG", ("boiled egg", "hard boiled egg", "boiled eggs", "trứng luộc", "trứng gà luộc")),
    ("FRIED_EGG", ("fried egg", "fried eggs", "sunny side up", "trứng ốp la")),
    ("BEEF_STEAK", ("beef steak", "steak", "beef", "bò bít tết", "bít tết")),
    ("SALMON_FILLET", ("salmon", "salmon fillet", "grilled salmon", "cá hồi")),
    ("STEAMED_SHRIMP", ("shrimp", "steamed shrimp", "boiled shrimp", "prawn", "tôm", "tôm hấp")),
    ("TOFU", ("tofu", "bean curd", "đậu hũ", "đậu phụ")),
    ("SWEET_POTATO", ("sweet potato", "boiled sweet potato", "khoai lang")),
    ("BROCCOLI", ("broccoli", "bông cải xanh", "súp lơ xanh")),
    ("GREEN_SALAD", ("salad", "green salad", "lettuce", "xà lách")),
    ("BANANA", ("banana", "chuối")),
    ("APPLE", ("apple", "táo")),
    ("BEEF_PHO", ("pho", "pho bo", "beef pho", "phở", "phở bò")),
    (
        "COM_TAM_SUON",
        ("com tam", "com tam suon", "broken rice", "broken rice with grilled pork", "cơm tấm", "cơm tấm sườn"),
    ),
    ("BANH_MI_THIT", ("banh mi", "banh mi thit", "vietnamese sandwich", "bánh mì", "bánh mì thịt")),
    ("BUN_CHA", ("bun cha", "bún chả")),
]

CLASS_CODES: list[str] = [code for code, _ in CORE_CLASSES_V1]


def normalize_name(name: str) -> str:
    """Chu thuong, bo dau tieng Viet, doi ky tu la thanh khoang trang."""
    text = name.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return text.strip()


def _build_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for code, aliases in CORE_CLASSES_V1:
        for alias in (code, *aliases):
            index[normalize_name(alias)] = code
    return index


ALIAS_TO_CODE: dict[str, str] = _build_alias_index()


def resolve_class(source_name: str) -> str | None:
    """Tra ve class_code chuan hoac None neu nhan nguon khong thuoc 18 lop cot loi."""
    return ALIAS_TO_CODE.get(normalize_name(source_name))
