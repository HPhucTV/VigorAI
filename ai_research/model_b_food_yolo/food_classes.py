# [OWNER: M4] 40 lop mon an Viet, do Gym, nuoc uong & snack cho AI Model B v1.3 (T-M4-01, T-M4-09)
"""Danh sach 40 lop v1.3 + bang alias de gop nhan tu Roboflow / HuggingFace / COCO ve `class_code`.

18 lop dau (0..17) giu nguyen thu tu v1.0/v1.1 khop `food_nutrition_catalog` (seed boi M3).
12 lop mo rong v1.2 (18..29) bo sung nhom Nuoc uong & Banh snack / Do an nhanh.
10 lop mo rong v1.3 (30..39) bat them nhom Mon Viet pho bien da co san du lieu tho.
"""
from __future__ import annotations

import re
import unicodedata

# (class_code, alias...) - alias co the co dau tieng Viet, se duoc chuan hoa khi so khop.
CORE_CLASSES_V1: list[tuple[str, tuple[str, ...]]] = [
    (
        "WHITE_RICE",
        (
            "rice",
            "white rice",
            "steamed rice",
            "cooked rice",
            "plain rice",
            "nasi putih",
            "cơm",
            "cơm trắng",
        ),
    ),
    ("BROWN_RICE", ("brown rice", "gạo lứt", "cơm gạo lứt")),
    (
        "GRILLED_CHICKEN_BREAST",
        ("chicken breast", "grilled chicken", "grilled chicken breast", "ức gà"),
    ),
    ("BOILED_EGG", ("boiled egg", "hard boiled egg", "boiled eggs", "trứng luộc", "trứng gà luộc")),
    ("FRIED_EGG", ("fried egg", "fried eggs", "sunny side up", "telur-dadar", "omelette", "trứng ốp la", "trứng chiên", "trứng tráng")),
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
    (
        "BANH_MI_THIT",
        (
            "banh mi",
            "banh mi thit",
            "vietnamese sandwich",
            "grilled pork banh mi",
            "bánh mì",
            "bánh mì thịt",
        ),
    ),
    ("BUN_CHA", ("bun cha", "bún chả", "grilled pork with vermicelli", "grilled pork vermicelli", "bun thit nuong", "bún thịt nướng")),
    # Nuoc uong & Giai khat (18..20)
    (
        "BOTTLED_DRINK",
        (
            "bottle",
            "bottled drink",
            "soda-bottles",
            "coca-cola",
            "fanta",
            "sprite",
            "soda",
            "soft drink",
            "water bottle",
            "sports drink",
            "nuoc dong chai",
            "nuoc ngot",
            "nước đóng chai",
            "nước ngọt",
        ),
    ),
    (
        "COFFEE_MILK_TEA",
        (
            "coffee",
            "kopi-hitam",
            "milkshake",
            "milk",
            "tea",
            "cup",
            "latte",
            "milk tea",
            "boba",
            "ca phe",
            "tra sua",
            "cà phê",
            "trà sữa",
        ),
    ),
    (
        "FRUIT_JUICE_SMOOTHIE",
        ("juice", "fruit juice", "smoothie", "nuoc ep", "sinh to", "nước ép", "sinh tố"),
    ),
    # Banh snack, banh ngot & do an nhanh (21..29)
    (
        "COOKIE_BISCUIT",
        ("cookie", "biscuit", "chocolate-chip-cookie", "banh quy", "bánh quy"),
    ),
    (
        "CAKE_MUFFIN_PASTRY",
        (
            "cake",
            "muffin",
            "blueberry-muffin",
            "red-velvet",
            "egg tart",
            "pie",
            "banh kem",
            "banh ngot",
            "bánh kem",
            "bánh ngọt",
        ),
    ),
    (
        "DONUT_WAFFLE_PANCAKE",
        ("donut", "doughnut", "waffle", "pancake", "banh donut", "banh kep", "bánh donut"),
    ),
    (
        "CROISSANT_SWEET_BREAD",
        (
            "croissant",
            "roti-slice",
            "bread",
            "pretzel",
            "banh sung bo",
            "banh mi ngot",
            "bánh sừng bò",
            "bánh mì ngọt",
        ),
    ),
    (
        "CHIPS_POPCORN_SNACK",
        (
            "popcorn",
            "chips",
            "potato chips",
            "kacang-mete",
            "almond",
            "cashew",
            "peanut",
            "snack",
            "bong ngo",
            "bỏng ngô",
        ),
    ),
    (
        "CHOCOLATE_CANDY",
        ("chocolate", "candy", "keo", "so co la", "kẹo", "sô cô la"),
    ),
    (
        "ICE_CREAM_DESSERT",
        ("ice cream", "pudding", "kem"),
    ),
    (
        "FRENCH_FRIES",
        ("french fries", "french-fries", "khoai tay chien", "khoai tây chiên"),
    ),
    (
        "BURGER_PIZZA_FASTFOOD",
        ("burger", "hamburg", "pizza", "hot dog", "fastfood", "hamburger"),
    ),
    # Mon Viet pho bien bo sung cho v1.3 (30..39)
    (
        "RAU_MUONG_XAO",
        ("rau muong", "rau muong xao", "rau muống", "rau muống xào", "rau muống xào tỏi", "morning glory", "water spinach", "kangkung"),
    ),
    (
        "BUN_BO_HUE",
        ("bun bo hue", "bún bò huế", "bún bò", "hue style spicy beef noodle soup", "hue-style spicy beef noodle soup"),
    ),
    (
        "COM_CHIEN",
        ("com chien", "com rang", "cơm chiên", "cơm rang", "fried rice", "nasi goreng", "nasi-goreng"),
    ),
    (
        "XOI_MAN",
        ("xoi", "xoi man", "xôi", "xôi mặn", "sticky rice"),
    ),
    (
        "GOI_CUON_NEM",
        ("goi cuon", "cha gio", "nem ran", "gỏi cuốn", "chả giò", "nem rán", "spring rolls", "spring roll"),
    ),
    (
        "BUN_DAU",
        ("bun dau", "bun dau mam tom", "bún đậu", "bún đậu mắm tôm", "vermicelli with tofu"),
    ),
    (
        "CHAO_THIT",
        ("chao", "chao long", "chao thit", "cháo", "cháo lòng", "cháo thịt", "porridge", "pork offal porridge", "bubur"),
    ),
    (
        "BANH_CUON",
        ("banh cuon", "bánh cuốn", "steamed rice rolls"),
    ),
    (
        "BANH_GIO",
        ("banh gio", "bánh giò", "vietnamese pyramid rice dumpling"),
    ),
    (
        "COM_XANH",
        ("com xanh", "banh com", "cốm", "bánh cốm", "flattened green rice"),
    ),
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
