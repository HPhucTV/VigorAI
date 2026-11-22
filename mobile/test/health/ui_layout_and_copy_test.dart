// [OWNER: M1] Widget & Layout Verification Suite cho note.md Muc 1 & Muc 2 (360dp + fontScale 1.3x + Copy/Policy Audit)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vigorai_app/core/database/health_tables.drift.dart';
import 'package:vigorai_app/core/platform/workmanager_reminder_service.dart';
import 'package:vigorai_app/core/sync/sync_queue_manager.dart';
import 'package:vigorai_app/core/theme/app_theme.dart';
import 'package:vigorai_app/features/auth_privacy/data/auth_repository.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/auth_controller.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/login_screen.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/register_screen.dart';
import 'package:vigorai_app/features/health/biometrics/presentation/biometrics_screen.dart';
import 'package:vigorai_app/features/health/data/health_repository.dart';
import 'package:vigorai_app/features/health/food_scan/presentation/food_scan_screen.dart';
import 'package:vigorai_app/features/health/hydration/presentation/hydration_screen.dart';
import 'package:vigorai_app/features/health/nutrition/presentation/nutrition_screen.dart';
import 'package:vigorai_app/features/health/presentation/health_dashboard_screen.dart';
import 'package:vigorai_app/features/health/progress_photos/data/progress_photos_repository.dart';
import 'package:vigorai_app/features/health/progress_photos/presentation/progress_photos_screen.dart';
import 'package:vigorai_app/features/health/sleep/presentation/sleep_screen.dart';
import 'package:vigorai_app/features/health/supplements/presentation/supplements_screen.dart';

class _StubAuthRepository implements AuthRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => null;
}

class _FakeAuthController extends AuthController {
  _FakeAuthController(AuthState initial) : super(_StubAuthRepository()) {
    state = initial;
  }

  @override
  Future<void> restoreSession() async {}

  @override
  Future<void> acceptMedicalDisclaimer() async {
    state = state.copyWith(disclaimerAccepted: true);
  }
}

class _StubHealthRepository implements HealthRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => null;
}

class _StubSyncQueueManager implements SyncQueueManager {
  @override
  dynamic noSuchMethod(Invocation invocation) => null;
}

class _FakeHealthDashboardController extends HealthDashboardController {
  _FakeHealthDashboardController(
    HealthDashboardState initial, {
    AuthUserProfile? user,
  }) : super(
          _StubHealthRepository(),
          _StubSyncQueueManager(),
          WorkmanagerReminderService(),
          user,
        ) {
    state = initial;
  }

  @override
  Future<void> load({
    String? activityLevelOverride,
    String? fitnessGoalOverride,
  }) async {}
}

List<String> _collectAllVisibleStrings(WidgetTester tester) {
  final out = <String>[];
  for (final w in tester.widgetList<Text>(find.byType(Text))) {
    final s = w.data ?? w.textSpan?.toPlainText();
    if (s != null && s.isNotEmpty) out.add(s);
  }
  for (final w in tester.widgetList<RichText>(find.byType(RichText))) {
    final s = w.text.toPlainText();
    if (s.isNotEmpty) out.add(s);
  }
  return out;
}

Future<void> _pumpNarrowScreen(
  WidgetTester tester, {
  required Widget home,
  HealthDashboardState? healthState,
  AuthState? authState,
  List<Override> extraOverrides = const [],
  double width = 360.0,
  double height = 780.0,
  double textScale = 1.3,
}) async {
  tester.view.devicePixelRatio = 1.0;
  tester.view.physicalSize = Size(width, height);
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });

  final defaultAuth = authState ??
      const AuthState(
        isInitialized: true,
        disclaimerAccepted: true,
        isAuthenticated: true,
        user: AuthUserProfile(
          id: 'u-test',
          email: 'demo@vigorai.app',
          fullName: 'Nguyễn Văn An',
          heightCm: 172.0,
        ),
      );

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authControllerProvider.overrideWith(
          (_) => _FakeAuthController(defaultAuth),
        ),
        if (healthState != null)
          healthDashboardProvider.overrideWith(
            (_) => _FakeHealthDashboardController(
              healthState,
              user: defaultAuth.user,
            ),
          ),
        ...extraOverrides,
      ],
      child: MaterialApp(
        theme: AppTheme.lightTheme,
        builder: (context, child) {
          final mq = MediaQuery.of(context);
          return MediaQuery(
            data: mq.copyWith(textScaler: TextScaler.linear(textScale)),
            child: child!,
          );
        },
        home: home,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

HealthDashboardState _sampleHealthState({
  required List<BiometricLogModel> biometrics,
  int waterMl = 0,
  int targetWaterMl = 2443,
  double weeklyAdherence = 0.0,
  int pendingSyncCount = 2,
}) {
  final now = DateTime.utc(2026, 11, 22, 10, 0);
  return HealthDashboardState(
    isLoading: false,
    biometrics: biometrics,
    dailyHealth: DailyHealthModel(
      id: 'daily-2026-11-22',
      logDateIso: '2026-11-22',
      stepsCount: 6420,
      targetSteps: 8000,
      distanceKm: 4.8,
      activeCaloriesKcal: 310,
      waterMl: waterMl,
      targetWaterMl: targetWaterMl,
      sleepHours: 7.5,
      sleepQualityScore: 4,
      updatedAt: now,
    ),
    sleepHistory7Days: [
      DailyHealthModel(
        id: 'daily-2026-11-21',
        logDateIso: '2026-11-21',
        sleepHours: 7.5,
        updatedAt: now,
      ),
      DailyHealthModel(
        id: 'daily-2026-11-22',
        logDateIso: '2026-11-22',
        sleepHours: 7.5,
        updatedAt: now,
      ),
    ],
    supplements: [
      SupplementScheduleModel(
        id: 'supp-1',
        supplementName: 'Whey Protein',
        dosageLabel: '1 muỗng',
        reminderTimeHhMm: '17:30',
        updatedAt: now,
      ),
    ],
    targetCaloriesKcal: 2700,
    bmrKcal: 1660,
    weeklySupplementAdherencePct: weeklyAdherence,
    pendingSyncCount: pendingSyncCount,
  );
}

void main() {
  group('Note.md Section 2 — Layout Verification on 360dp + 1.3x Font Scale', () {
    for (final testCase in [
      (
        label: 'Normal 70.0 kg BMI 23.6 Thua can with metrics',
        weightKg: 70.0,
        bmi: 23.6,
        fat: 18.2,
        muscle: 35.4,
      ),
      (
        label: 'Longest 125.5 kg BMI 26.8 Beo phi',
        weightKg: 125.5,
        bmi: 26.8,
        fat: 28.5,
        muscle: 48.2,
      ),
      (
        label: 'Longest normal label 125.5 kg BMI 22.9 Binh thuong',
        weightKg: 125.5,
        bmi: 22.9,
        fat: 19.0,
        muscle: 52.0,
      ),
      (
        label: 'Null bodyFatPct & muscleMassKg fallback "--"',
        weightKg: 70.0,
        bmi: 23.6,
        fat: null,
        muscle: null,
      ),
    ]) {
      testWidgets(
        'BiometricsScreen fits BMI badge inside Card and aligns 3 metric tiles equally: ${testCase.label}',
        (tester) async {
          final now = DateTime.utc(2026, 11, 22);
          final state = _sampleHealthState(
            biometrics: [
              BiometricLogModel(
                id: 'b-1',
                weightKg: testCase.weightKg,
                bodyFatPct: testCase.fat,
                muscleMassKg: testCase.muscle,
                bmi: testCase.bmi,
                loggedDateIso: '2026-11-22',
                updatedAt: now,
              ),
              BiometricLogModel(
                id: 'b-0',
                weightKg: testCase.weightKg - 0.5,
                bmi: testCase.bmi - 0.1,
                loggedDateIso: '2026-11-21',
                updatedAt: now.subtract(const Duration(days: 1)),
              ),
            ],
          );

          await _pumpNarrowScreen(
            tester,
            home: const BiometricsScreen(),
            healthState: state,
            width: 360.0,
            textScale: 1.3,
          );

          // 1. BMI badge must sit strictly inside its enclosing Card
          final bmiFinder =
              find.textContaining('BMI ${testCase.bmi.toStringAsFixed(1)}');
          expect(bmiFinder, findsWidgets);
          final cardFinder = find.ancestor(
            of: bmiFinder.first,
            matching: find.byType(Card),
          );
          final cardRect = tester.getRect(cardFinder.first);
          final badgeContainerFinder = find.ancestor(
            of: bmiFinder.first,
            matching: find.byType(Container),
          );
          final badgeRect = tester.getRect(badgeContainerFinder.first);
          expect(badgeRect.left, greaterThanOrEqualTo(cardRect.left));
          expect(badgeRect.right, lessThanOrEqualTo(cardRect.right));
          expect(badgeRect.top, greaterThanOrEqualTo(cardRect.top));
          expect(badgeRect.bottom, lessThanOrEqualTo(cardRect.bottom));

          // 2. Three metric tiles (Ty le mo, Khoi co, TB 7 ngay) must match width, height, and gaps
          Rect tileRectFor(String title) {
            final containerFinder = find.ancestor(
              of: find.text(title),
              matching: find.byType(Container),
            );
            return tester.getRect(containerFinder.first);
          }

          final rFat = tileRectFor('Tỷ lệ mỡ');
          final rMuscle = tileRectFor('Khối cơ');
          final rAvg = tileRectFor('TB 7 ngày');

          expect(rFat.height, closeTo(rMuscle.height, 0.5));
          expect(rMuscle.height, closeTo(rAvg.height, 0.5));
          expect(rFat.width, closeTo(rMuscle.width, 0.5));
          expect(rMuscle.width, closeTo(rAvg.width, 0.5));

          final gap12 = rMuscle.left - rFat.right;
          final gap23 = rAvg.left - rMuscle.right;
          expect(gap12, closeTo(8.0, 0.5));
          expect(gap23, closeTo(8.0, 0.5));

          if (testCase.fat == null) {
            expect(find.text('--'), findsWidgets);
          }
        },
      );
    }

    testWidgets(
      'HealthDashboardScreen has zero overflow and non-overlapping headers on 360dp + 1.3x',
      (tester) async {
        final state = _sampleHealthState(
          biometrics: [
            BiometricLogModel(
              id: 'b-1',
              weightKg: 70.0,
              bodyFatPct: 18.0,
              muscleMassKg: 35.0,
              bmi: 23.6,
              loggedDateIso: '2026-11-22',
              updatedAt: DateTime.utc(2026, 11, 22),
            ),
          ],
          waterMl: 0,
          targetWaterMl: 2443,
          weeklyAdherence: 0.0,
          pendingSyncCount: 3,
        );

        await _pumpNarrowScreen(
          tester,
          home: const HealthDashboardScreen(),
          healthState: state,
          width: 360.0,
          textScale: 1.3,
        );

        // Verify non-overlapping headers on water & supplement cards
        final waterTitleRect = tester.getRect(find.text('Lượng nước thông minh'));
        final waterValRect = tester.getRect(find.text('0 / 2443 ml'));
        expect(waterTitleRect.right, lessThanOrEqualTo(waterValRect.left));

        // Verify equal height for Food Scan & Progress Photos cards
        await tester.scrollUntilVisible(find.text('Quét món AI'), 200);
        final foodCardRect = tester.getRect(
          find
              .ancestor(
                of: find.text('Quét món AI'),
                matching: find.byType(Card),
              )
              .first,
        );
        final photoCardRect = tester.getRect(
          find
              .ancestor(
                of: find.text('Ảnh tiến độ'),
                matching: find.byType(Card),
              )
              .first,
        );
        expect(foodCardRect.height, closeTo(photoCardRect.height, 0.5));

        await tester.scrollUntilVisible(
          find.text('Thực phẩm bổ sung hôm nay'),
          200,
        );
        final suppTitleRect =
            tester.getRect(find.text('Thực phẩm bổ sung hôm nay'));
        final suppValRect = tester.getRect(find.text('0% tuần'));
        expect(suppTitleRect.right, lessThanOrEqualTo(suppValRect.left));

        await tester.scrollUntilVisible(find.text('Xóa tài khoản'), 200);

        // Verify cleaned copy on Dashboard
        final allText = _collectAllVisibleStrings(tester).join('\n');
        for (final forbidden in const [
          'Offline-First',
          'Mock API',
          '(F03)',
          '(F06)',
          '(F19)',
          '(F24)',
          '(F26)',
          '(M2)',
          '(M4)',
          'SQLite',
          'Mifflin-St Jeor',
          '3 bài mẫu MVP',
          'Ảnh Progress',
          'cục bộ',
        ]) {
          expect(allText, isNot(contains(forbidden)));
        }
        expect(allText, contains('Đồng bộ (3)'));
      },
    );
  });

  group('Note.md Section 1 — M1 Screens Copy, CH Play Disclaimers & Narrow Layout',
      () {
    testWidgets(
        'OnboardingDisclaimerScreen preserves medical disclaimer & citations without IT jargon',
        (tester) async {
      await _pumpNarrowScreen(
        tester,
        home: const OnboardingDisclaimerScreen(),
        authState: const AuthState(
          isInitialized: true,
          disclaimerAccepted: false,
          isAuthenticated: false,
        ),
        width: 360.0,
        height: 820.0,
        textScale: 1.0,
      );

      final allText = _collectAllVisibleStrings(tester).join('\n');
      expect(allText, contains('Mifflin-St Jeor'));
      expect(allText, contains('Epley (1985) & Brzycki (1993)'));
      for (final forbidden in const [
        'Offline-First',
        'Blender MCP',
        'YOLOv8',
        'Android Health Connect',
        'CH Play Mandatory',
      ]) {
        expect(allText, isNot(contains(forbidden)));
      }

      // Continue button must remain disabled until checkbox is ticked
      final continueBtn = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'Đồng ý & Tiếp tục Đăng nhập'),
      );
      expect(continueBtn.onPressed, isNull);
    });

    testWidgets(
        'LoginScreen and RegisterScreen remove debug strings & (Bulk)/(Cut)/(Maintain)',
        (tester) async {
      await _pumpNarrowScreen(
        tester,
        home: const LoginScreen(),
        width: 360.0,
        textScale: 1.3,
      );
      final loginText = _collectAllVisibleStrings(tester).join('\n');
      for (final forbidden in const [
        'useMockApi',
        '10.0.2.2',
        'Onboarding',
        '(CH Play)',
        'https://',
      ]) {
        expect(loginText, isNot(contains(forbidden)));
      }

      await _pumpNarrowScreen(
        tester,
        home: const RegisterScreen(),
        width: 360.0,
        textScale: 1.3,
      );
      final regText = _collectAllVisibleStrings(tester).join('\n');
      for (final forbidden in const [
        '(Bulk)',
        '(Cut)',
        '(Maintain)',
        'Onboarding',
        '(CH Play)',
        'useMockApi',
        '10.0.2.2',
      ]) {
        expect(regText, isNot(contains(forbidden)));
      }
      expect(regText, contains('Tăng cơ'));
    });

    testWidgets(
        'NutritionScreen retains Mifflin-St Jeor (1990) & has no IT jargon on 360dp',
        (tester) async {
      final state = _sampleHealthState(biometrics: const []);
      await _pumpNarrowScreen(
        tester,
        home: const NutritionScreen(),
        healthState: state,
        width: 360.0,
        textScale: 1.3,
      );
      final allText = _collectAllVisibleStrings(tester).join('\n');
      expect(allText, contains('Mifflin-St Jeor (1990)'));
      for (final forbidden in const [
        '(F04)',
        '(F19)',
        'Photo Picker',
        'Từ điển Offline',
      ]) {
        expect(allText, isNot(contains(forbidden)));
      }
    });

    testWidgets(
        'ProgressPhotosScreen fits 3 pose chips on 1 row & removes forbidden strings',
        (tester) async {
      await _pumpNarrowScreen(
        tester,
        home: const ProgressPhotosScreen(),
        extraOverrides: [
          progressPhotosListProvider.overrideWith((ref) async => const []),
        ],
        width: 360.0,
        textScale: 1.3,
      );

      // 3 pose chips (Truoc, Nghieng, Sau) inside capture card must sit on one single row
      Rect chipRect(String label) => tester.getRect(
            find
                .ancestor(
                  of: find.text(label).first,
                  matching: find.byType(ChoiceChip),
                )
                .first,
          );
      final frontRect = chipRect('Trước');
      final sideRect = chipRect('Nghiêng');
      final backRect = chipRect('Sau');
      expect(frontRect.top, closeTo(sideRect.top, 1.0));
      expect(sideRect.top, closeTo(backRect.top, 1.0));

      final allText = _collectAllVisibleStrings(tester).join('\n');
      for (final forbidden in const [
        '(F24)',
        'cục bộ',
        'progress_photos/',
        'Gallery',
        'Photo Picker',
      ]) {
        expect(allText, isNot(contains(forbidden)));
      }
    });

    testWidgets(
        'Hydration, Sleep, Supplements & FoodScan screens render cleanly at 360dp + 1.3x',
        (tester) async {
      final state = _sampleHealthState(biometrics: const []);
      for (final screen in const <Widget>[
        HydrationScreen(),
        SleepScreen(),
        SupplementsScreen(),
        FoodScanScreen(),
      ]) {
        await _pumpNarrowScreen(
          tester,
          home: screen,
          healthState: state,
          width: 360.0,
          textScale: 1.3,
        );
        final allText = _collectAllVisibleStrings(tester).join('\n');
        for (final forbidden in const [
          '(F03)',
          '(F05)',
          '(F06)',
          '(F19)',
          'WorkManager',
          'CH Play',
          'SCHEDULE_EXACT_ALARM',
          'Exact Alarm',
          'SQLite',
          'SleepSessionRecord',
          'READ_SLEEP',
          'Photo Picker',
          'AI Model B',
          '(nén < 300 KB)',
        ]) {
          expect(
            allText,
            isNot(contains(forbidden)),
            reason: '${screen.runtimeType} still contains $forbidden',
          );
        }
      }
    });
  });
}
