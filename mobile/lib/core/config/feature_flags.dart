// [OWNER: M1] Co bat/tat tinh nang theo 2 nhip phat hanh CH Play (T-M1-06)
class FeatureFlags {
  FeatureFlags._();

  /// Ban MVP v1.0.0+1 (Closed Testing) mac dinh true de an toan bo nut tro sang man hinh stub.
  /// Truyen `--dart-define=MVP_CLOSED_TESTING=false` khi len Production v1.1.0 / v1.2.0.
  static const bool isMvpClosedTesting = bool.fromEnvironment(
    'MVP_CLOSED_TESTING',
    defaultValue: true,
  );

  /// Tam tat Health Connect o ban MVP v1.0.0+1 & v1.1.0 de duyet nhanh.
  /// Bat true o ban v1.2.0 sau khi da nop video chung minh Google Play.
  static const bool enableHealthConnect = bool.fromEnvironment(
    'ENABLE_HEALTH_CONNECT',
    defaultValue: false,
  );
}
