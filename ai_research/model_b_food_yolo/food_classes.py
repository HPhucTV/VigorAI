# [OWNER: M4] 69 lop mon an Viet, do Gym, nuoc uong nhan hieu & snack cho AI Model B v1.6 (T-M4-01, T-M4-09, T-M4-10)
"""Danh sach 69 lop v1.6 + bang alias de gop nhan tu Roboflow / HuggingFace / COCO / OpenFoodFacts / Wikimedia ve `class_code`.

11 lop mo rong v1.6 (58..68): AVOCADO, CUCUMBER, CHERRY_TOMATO, LEAN_PORK, ALMONDS, OATMEAL, GREEK_YOGURT,
WHEY_SHAKE (co san dinh duong trong FOOD_CATALOG_SEED cua M3) + DRINK_COCONUT_WATER, DRINK_YOGURT_PROBIOTIC, DRINK_BEER.

18 lop dau (0..17) giu nguyen thu tu v1.0/v1.1 khop `food_nutrition_catalog` (seed boi M3).
12 lop mo rong v1.2 (18..29) bo sung nhom Nuoc uong & Banh snack / Do an nhanh.
10 lop mo rong v1.3 (30..39) bat nhom Mon Viet tu `vn-streetfood` + `food-detection`.
10 lop mo rong v1.4 (40..49) bo sung Mon an & Dac san Viet Nam pho bien tu `vn-food-combined`.
8 lop mo rong v1.5 (50..57) tach chi tiet cac nhom Nuoc uong nhan hieu & bao bi (Coca/Pepsi, 7Up/Sprite, Sting/RedBull, Revive/Pocari, Tra dong chai, Ca phe chai/lon, Sua hop, Nuoc suoi).
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
    ("FRIED_EGG", ("fried egg", "fried eggs", "sunny side up", "telur-dadar", "telur-mata-sapi", "omelette", "trứng ốp la", "trứng chiên", "trứng tráng")),
    ("BEEF_STEAK", ("beef steak", "steak", "beef", "bò bít tết", "bít tết")),
    ("SALMON_FILLET", ("salmon", "salmon fillet", "grilled salmon", "cá hồi")),
    ("STEAMED_SHRIMP", ("shrimp", "steamed shrimp", "boiled shrimp", "prawn", "tôm", "tôm hấp")),
    ("TOFU", ("tofu", "bean curd", "tau-hu-non", "tau-hu-nhoi-thit", "đậu hũ", "đậu phụ")),
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
            "soda",
            "soft drink",
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
        ("com chien", "com rang", "com-rang-dua-bo", "cơm chiên", "cơm rang", "fried rice", "nasi goreng", "nasi-goreng"),
    ),
    (
        "XOI_MAN",
        ("xoi", "xoi man", "xoi-xeo", "xoi xeo", "xoi-gac", "xoi-nep-than", "xôi", "xôi mặn", "xôi xéo", "xôi gấc", "sticky rice"),
    ),
    (
        "GOI_CUON_NEM",
        ("goi cuon", "cha gio", "nem ran", "gỏi cuốn", "chả giò", "nem rán", "spring rolls", "spring roll"),
    ),
    (
        "BUN_DAU",
        ("bun dau", "bun-dau-mam-tom", "bun dau mam tom", "bún đậu", "bún đậu mắm tôm", "vermicelli with tofu"),
    ),
    (
        "CHAO_THIT",
        ("chao", "chao-long", "chao long", "chao thit", "chao-vit", "cháo", "cháo lòng", "cháo thịt", "porridge", "pork offal porridge", "bubur"),
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
        ("com xanh", "banh com", "cha-com", "cốm", "bánh cốm", "flattened green rice"),
    ),
    # 10 mon an & dac san Viet Nam bo sung cho v1.4 (40..49)
    (
        "CANH_CHUA_CA",
        ("canh chua", "canh-chua", "canh chua ca", "canh chua cá lóc", "sour fish soup"),
    ),
    (
        "BANH_XEO",
        ("banh xeo", "banh-xeo", "bánh xèo", "banh khot", "banh-khot", "bánh khọt"),
    ),
    (
        "BUN_RIEU",
        ("bun rieu", "bun-rieu", "bún riêu", "bún riêu cua"),
    ),
    (
        "HU_TIEU",
        ("hu tieu", "hu-tieu", "hủ tiếu", "banh canh", "banh-canh", "bánh canh"),
    ),
    (
        "BANH_BAO",
        ("banh bao", "banh-bao", "bánh bao"),
    ),
    (
        "BANH_CHUNG_TET",
        ("banh chung", "banh-chung", "bánh chưng", "banh tet", "banh-tet", "bánh tét"),
    ),
    (
        "THIT_KHO_TRUNG",
        ("thit kho", "thit kho tau", "thit-kho-tau", "thịt kho tàu", "thịt kho trứng"),
    ),
    (
        "CA_KHO_TO",
        ("ca kho", "ca kho to", "ca-kho-to", "cá kho tộ", "cá kho"),
    ),
    (
        "MI_QUANG_XAO",
        ("mi quang", "mi-quang", "mì quảng", "cao lau", "cao-lau", "cao lầu", "mi xao", "mi-xao-gion", "mì xào"),
    ),
    (
        "COM_GA_XOI_MO",
        ("com ga", "com ga xoi mo", "com-ga-xoi-mo", "cơm gà", "cơm gà xối mỡ", "ga-chien-nuoc-mam"),
    ),
    # 8 nhom Nuoc uong nhan hieu & bao bi bo sung cho v1.5 (50..57)
    (
        "DRINK_COLA",
        ("drink-cola", "coca-cola", "coca cola", "pepsi", "cola", "coke", "nuoc ngot cola"),
    ),
    (
        "DRINK_CITRUS_SODA",
        ("drink-citrus-soda", "7up", "seven up", "sprite", "fanta", "mirinda", "mountain dew", "moutaindew", "nuoc ngot co gas"),
    ),
    (
        "DRINK_ENERGY",
        ("drink-energy", "sting", "red bull", "redbull", "monster", "monsters", "energy drink", "wake up 247", "number 1", "nuoc tang luc"),
    ),
    (
        "DRINK_SPORTS_ISOTONIC",
        ("drink-sports-isotonic", "revive", "pocari", "pocari sweat", "aquarius", "gatorade", "powerade", "sports drink", "isotonic", "nuoc dien giai"),
    ),
    (
        "DRINK_BOTTLED_TEA",
        ("drink-bottled-tea", "c2", "c2 tea", "tra xanh 0 do", "tea plus", "olong tea", "fuzetea", "liptonbrisk", "pureleaf", "nestea", "arizonateas", "tra dong chai"),
    ),
    (
        "DRINK_BOTTLED_COFFEE",
        ("drink-bottled-coffee", "kirin latte", "starbucks_bottled_frappuccino", "starbucks_doubleshot", "nescafe can", "bottled coffee", "canned coffee", "ca phe dong chai", "ca phe lon"),
    ),
    (
        "DRINK_MILK_CARTON",
        ("drink-milk-carton", "vinamilk", "th true milk", "milo", "milk carton", "milk box", "sua hop", "sua tuoi hop", "sua lua mach"),
    ),
    (
        "DRINK_MINERAL_WATER",
        ("drink-mineral-water", "aquafina", "lavie", "evian", "nestle_pure_life", "perrier", "san_pellegrino", "water bottle", "mineral water", "nuoc suoi", "nuoc khoang"),
    ),
    # 11 lop bo sung cho v1.6 (58..68): mon Gym/healthy co san trong catalog M3 + 3 nhom do uong pho bien
    ("AVOCADO", ("avocado", "quả bơ", "trái bơ", "sliced avocado")),
    ("CUCUMBER", ("cucumber", "dưa leo", "dưa chuột")),
    ("CHERRY_TOMATO", ("tomato", "cherry tomato", "cà chua", "cà chua bi")),
    ("LEAN_PORK", ("pork", "lean pork", "thịt heo", "thịt lợn", "thịt heo luộc", "thịt heo nạc")),
    ("ALMONDS", ("almond", "almonds", "hạnh nhân", "hạnh nhân rang")),
    ("OATMEAL", ("oatmeal", "oats", "rolled oats", "porridge oats", "overnight oats", "yến mạch", "cháo yến mạch")),
    ("GREEK_YOGURT", ("greek-yogurt", "greek yogurt", "yogurt", "yoghurt", "sữa chua", "sữa chua hy lạp")),
    ("WHEY_SHAKE", ("whey-shake", "whey", "whey protein", "protein shake", "sữa whey")),
    (
        "DRINK_COCONUT_WATER",
        ("drink-coconut-water", "coconut water", "young coconut", "nước dừa", "nước dừa tươi"),
    ),
    (
        "DRINK_YOGURT_PROBIOTIC",
        ("drink-yogurt-probiotic", "yakult", "probi", "betagen", "actimel", "calpis", "drinking yogurt", "sữa chua uống"),
    ),
    (
        "DRINK_BEER",
        ("drink-beer", "beer", "bia", "lager", "heineken", "tiger beer", "bia sài gòn", "bia lon"),
    ),
    # 31 lop bo sung cho v1.7 (69..99): mon Viet dac san, mon Gym con thieu, trai cay/rau cu & 3 nhom do uong moi
    ("STIR_FRIED_BEEF", ("stir-fried-beef", "stir fried beef", "bo-luc-lac", "bo luc lac", "bo-ne", "bo ne", "thịt bò xào", "bò lúc lắc")),
    ("BOILED_CHICKEN_BREAST", ("boiled-chicken-breast", "boiled chicken", "ga-hap-la-chanh", "ga hap la chanh", "ga luoc", "ức gà luộc", "gà luộc")),
    ("TUNA_CANNED", ("tuna-canned", "canned tuna", "tuna in water", "cá ngừ ngâm nước", "cá ngừ đóng hộp")),
    ("PEANUT_BUTTER", ("peanut-butter", "peanut butter", "bơ đậu phộng")),
    ("WHOLE_WHEAT_BREAD", ("whole-wheat-bread", "whole wheat bread", "wholemeal bread", "bánh mì nguyên cám")),
    ("BANH_BEO_BOT_LOC", ("banh-beo-bot-loc", "banh-beo", "banh beo", "banh-bot-loc", "banh bot loc", "banh-duc", "banh duc", "bánh bèo", "bánh bột lọc")),
    ("BANH_TRANG_NUONG", ("banh-trang-nuong", "banh trang nuong", "bánh tráng nướng")),
    ("BO_KHO", ("bo-kho", "bo kho", "ca-ri-ga", "ca ri ga", "bò kho", "cà ri gà")),
    ("BUN_MAM", ("bun-mam", "bun mam", "bun-cha-ca", "banh-da-cua", "bún mắm", "bún chả cá", "bánh đa cua")),
    ("NEM_CHUA_NUONG", ("nem-chua-nuong", "nem-chua", "nem chua", "nem-nuong-nha-trang", "bo-la-lot", "sate", "nem nướng", "bò lá lốt")),
    ("SUP_CUA", ("sup-cua", "sup cua", "súp cua")),
    ("CA_CHIEN_NUONG", ("ca-chien-nuong", "ikan-goreng", "ca-loc-nuong", "ca-sot-ca-chua", "cha-ca-la-vong", "cá chiên", "cá nướng")),
    ("TRUNG_VIT_LON", ("trung-vit-lon", "cut-lon-xao-me", "trứng vịt lộn", "cút lộn xào me")),
    ("OC_HAI_SAN", ("oc-hai-san", "seafood", "oc-buou-hap", "oc-huong-xao", "oc-len-xao-dua", "cua-hap-bia", "ốc hấp", "hải sản")),
    ("BANH_PIA_TRUNG_THU", ("banh-pia-trung-thu", "banh-pia", "banh pia", "banh-trung-thu", "bánh pía", "bánh trung thu")),
    ("CHE_TROINUOC", ("che-troinuoc", "banh-troi-nuoc", "banh-da-lon", "banh-bo", "chè trôi nước", "bánh da lợn")),
    ("SUSHI_ROLL", ("sushi-roll", "sushi", "sushi-nigiri", "sushi-makizushi", "cơm cuộn")),
    ("SPAGHETTI_PASTA", ("spaghetti-pasta", "spaghetti-bolognese", "macaroni-cheese", "nui-xao", "mì ý", "nui xào")),
    ("WATERMELON", ("watermelon", "semangka", "dưa hấu")),
    ("ORANGE_CITRUS", ("orange-citrus", "orange", "mandarin", "clementine", "cam", "quýt")),
    ("MANGO", ("mango", "xoài", "xoài chín")),
    ("PINEAPPLE", ("pineapple", "dứa", "thơm")),
    ("GRAPES", ("grapes", "grape", "nho", "nho tươi")),
    ("DRAGON_FRUIT", ("dragon-fruit", "dragon_fruit", "dragon fruit", "thanh long")),
    ("STRAWBERRY_BERRY", ("strawberry-berry", "strawberry", "blueberry", "dâu tây", "việt quất")),
    ("CORN_BOILED", ("corn-boiled", "corn", "sweetcorn", "sweet corn", "bắp luộc", "ngô luộc")),
    ("CARROT_VEG", ("carrot-veg", "carrot", "cà rốt")),
    ("CABBAGE_SPINACH", ("cabbage-spinach", "cabbage", "spinach", "bắp cải", "rau bina")),
    ("DRINK_SOY_NUT_MILK", ("drink-soy-nut-milk", "soy milk", "soymilk", "vinasoy", "fami", "almond milk", "oat milk", "sữa đậu nành", "sữa hạt")),
    ("DRINK_KOMBUCHA_HERBAL", ("drink-kombucha-herbal", "kombucha", "herbal tea can", "trà kombucha", "trà thảo mộc")),
    ("DRINK_WINE_CIDER", ("drink-wine-cider", "wine bottle", "cider", "rượu vang", "nước táo lên men")),
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
