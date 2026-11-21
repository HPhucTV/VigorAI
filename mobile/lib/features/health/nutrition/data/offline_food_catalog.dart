// [OWNER: M1] Tu dien Dinh duong Offline VNFood & USDA (F04 / T-M1-09)
class OfflineFoodCatalogItem {
  final String classCode;
  final String nameVi;
  final double kcalPer100g;
  final double proteinPer100g;
  final double carbsPer100g;
  final double fatPer100g;
  final double defaultServingG;
  final String sourceStandard;

  const OfflineFoodCatalogItem({
    required this.classCode,
    required this.nameVi,
    required this.kcalPer100g,
    required this.proteinPer100g,
    required this.carbsPer100g,
    required this.fatPer100g,
    required this.defaultServingG,
    this.sourceStandard = 'NIN_VN_USDA',
  });

  double caloriesForGrams(double grams) =>
      ((kcalPer100g * grams / 100.0) * 10).round() / 10.0;
  double proteinForGrams(double grams) =>
      ((proteinPer100g * grams / 100.0) * 10).round() / 10.0;
  double carbsForGrams(double grams) =>
      ((carbsPer100g * grams / 100.0) * 10).round() / 10.0;
  double fatForGrams(double grams) =>
      ((fatPer100g * grams / 100.0) * 10).round() / 10.0;
}

const List<OfflineFoodCatalogItem> kOfflineFoodCatalog = [
  OfflineFoodCatalogItem(classCode: 'GRILLED_CHICKEN_BREAST', nameVi: 'Ức gà áp chảo', kcalPer100g: 165, proteinPer100g: 31.0, carbsPer100g: 0.0, fatPer100g: 3.6, defaultServingG: 180),
  OfflineFoodCatalogItem(classCode: 'BOILED_CHICKEN_BREAST', nameVi: 'Ức gà luộc', kcalPer100g: 151, proteinPer100g: 30.5, carbsPer100g: 0.0, fatPer100g: 2.8, defaultServingG: 180),
  OfflineFoodCatalogItem(classCode: 'WHITE_RICE', nameVi: 'Cơm trắng', kcalPer100g: 130, proteinPer100g: 2.7, carbsPer100g: 28.2, fatPer100g: 0.3, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'BROWN_RICE', nameVi: 'Cơm gạo lứt', kcalPer100g: 112, proteinPer100g: 2.6, carbsPer100g: 23.5, fatPer100g: 0.9, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'BEEF_STEAK', nameVi: 'Thịt bò bít tết', kcalPer100g: 217, proteinPer100g: 26.1, carbsPer100g: 0.0, fatPer100g: 11.8, defaultServingG: 180),
  OfflineFoodCatalogItem(classCode: 'STIR_FRIED_BEEF', nameVi: 'Thịt bò xào', kcalPer100g: 195, proteinPer100g: 24.5, carbsPer100g: 2.5, fatPer100g: 9.5, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'SALMON_FILLET', nameVi: 'Cá hồi áp chảo', kcalPer100g: 208, proteinPer100g: 20.4, carbsPer100g: 0.0, fatPer100g: 13.4, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'BOILED_EGG', nameVi: 'Trứng gà luộc (2 quả ~100g)', kcalPer100g: 155, proteinPer100g: 12.6, carbsPer100g: 1.1, fatPer100g: 10.6, defaultServingG: 100),
  OfflineFoodCatalogItem(classCode: 'FRIED_EGG', nameVi: 'Trứng ốp la', kcalPer100g: 196, proteinPer100g: 13.6, carbsPer100g: 0.8, fatPer100g: 15.0, defaultServingG: 100),
  OfflineFoodCatalogItem(classCode: 'EGG_WHITE', nameVi: 'Lòng trắng trứng', kcalPer100g: 52, proteinPer100g: 10.9, carbsPer100g: 0.7, fatPer100g: 0.2, defaultServingG: 120),
  OfflineFoodCatalogItem(classCode: 'LEAN_PORK', nameVi: 'Thịt heo nạc luộc', kcalPer100g: 143, proteinPer100g: 26.0, carbsPer100g: 0.0, fatPer100g: 3.5, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'STEAMED_SHRIMP', nameVi: 'Tôm hấp', kcalPer100g: 99, proteinPer100g: 24.0, carbsPer100g: 0.2, fatPer100g: 0.3, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'TOFU', nameVi: 'Đậu hũ trắng', kcalPer100g: 76, proteinPer100g: 8.1, carbsPer100g: 1.9, fatPer100g: 4.8, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'WHEY_SHAKE', nameVi: 'Whey Protein Isolate (1 muỗng)', kcalPer100g: 370, proteinPer100g: 82.0, carbsPer100g: 4.0, fatPer100g: 2.0, defaultServingG: 32),
  OfflineFoodCatalogItem(classCode: 'GREEK_YOGURT', nameVi: 'Sữa chua Hy Lạp không đường', kcalPer100g: 59, proteinPer100g: 10.2, carbsPer100g: 3.6, fatPer100g: 0.4, defaultServingG: 150),
  OfflineFoodCatalogItem(classCode: 'SWEET_POTATO', nameVi: 'Khoai lang luộc', kcalPer100g: 86, proteinPer100g: 1.6, carbsPer100g: 20.1, fatPer100g: 0.1, defaultServingG: 200),
  OfflineFoodCatalogItem(classCode: 'OATMEAL', nameVi: 'Yến mạch cán dẹt', kcalPer100g: 389, proteinPer100g: 16.9, carbsPer100g: 66.3, fatPer100g: 6.9, defaultServingG: 60),
  OfflineFoodCatalogItem(classCode: 'WHOLE_WHEAT_BREAD', nameVi: 'Bánh mì nguyên cám', kcalPer100g: 247, proteinPer100g: 13.0, carbsPer100g: 41.0, fatPer100g: 3.4, defaultServingG: 80),
  OfflineFoodCatalogItem(classCode: 'BEEF_PHO', nameVi: 'Phở bò tái (1 tô)', kcalPer100g: 95, proteinPer100g: 6.2, carbsPer100g: 12.5, fatPer100g: 2.1, defaultServingG: 450),
  OfflineFoodCatalogItem(classCode: 'CHICKEN_PHO', nameVi: 'Phở gà (1 tô)', kcalPer100g: 88, proteinPer100g: 6.5, carbsPer100g: 12.0, fatPer100g: 1.5, defaultServingG: 450),
  OfflineFoodCatalogItem(classCode: 'COM_TAM_SUON', nameVi: 'Cơm tấm sườn nướng', kcalPer100g: 168, proteinPer100g: 8.4, carbsPer100g: 22.0, fatPer100g: 5.2, defaultServingG: 350),
  OfflineFoodCatalogItem(classCode: 'BUN_CHA', nameVi: 'Bún chả Hà Nội', kcalPer100g: 142, proteinPer100g: 7.8, carbsPer100g: 16.4, fatPer100g: 5.1, defaultServingG: 380),
  OfflineFoodCatalogItem(classCode: 'BROCCOLI', nameVi: 'Bông cải xanh luộc', kcalPer100g: 35, proteinPer100g: 2.4, carbsPer100g: 7.2, fatPer100g: 0.4, defaultServingG: 120),
  OfflineFoodCatalogItem(classCode: 'GREEN_SALAD', nameVi: 'Xà lách trộn', kcalPer100g: 20, proteinPer100g: 1.4, carbsPer100g: 3.5, fatPer100g: 0.2, defaultServingG: 100),
  OfflineFoodCatalogItem(classCode: 'BANANA', nameVi: 'Chuối tiêu chín', kcalPer100g: 89, proteinPer100g: 1.1, carbsPer100g: 22.8, fatPer100g: 0.3, defaultServingG: 120),
  OfflineFoodCatalogItem(classCode: 'AVOCADO', nameVi: 'Quả bơ', kcalPer100g: 160, proteinPer100g: 2.0, carbsPer100g: 8.5, fatPer100g: 14.7, defaultServingG: 80),
  OfflineFoodCatalogItem(classCode: 'PEANUT_BUTTER', nameVi: 'Bơ đậu phộng', kcalPer100g: 588, proteinPer100g: 25.1, carbsPer100g: 20.0, fatPer100g: 50.0, defaultServingG: 20),
];
