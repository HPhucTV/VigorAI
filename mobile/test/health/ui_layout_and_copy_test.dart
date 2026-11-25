// [OWNER: M1] Widget & Layout Verification Suite cho note.md Muc 1 & Muc 2 (360dp + fontScale 1.3x + Copy/Policy Audit)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:vigorai_app/core/database/health_tables.drift.dart';
import 'package:vigorai_app/core/database/workout_tables.drift.dart';
import 'package:vigorai_app/core/platform/workmanager_reminder_service.dart';
import 'package:vigorai_app/core/sync/sync_queue_manager.dart';
import 'package:vigorai_app/core/theme/app_theme.dart';
import 'package:vigorai_app/features/ai_analytics/data/ai_analytics_repository.dart';
import 'package:vigorai_app/features/auth_privacy/data/auth_repository.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/app_launch_gate.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/auth_controller.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/login_screen.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/onboarding_disclaimer_screen.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/profile_settings_screen.dart';
import 'package:vigorai_app/features/auth_privacy/presentation/register_screen.dart';
import 'package:vigorai_app/features/gym3d/data/exercise_repository.dart';
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
import 'package:vigorai_app/features/workout/data/workout_repository.dart';

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
  ThemeData? themeData,
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
        theme: themeData ?? AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
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

    for (final themeEntry in [
      (label: 'Light', theme: AppTheme.lightTheme),
      (label: 'Dark', theme: AppTheme.darkTheme),
    ]) {
      testWidgets(
        'HealthDashboardScreen 5-tab shell (${themeEntry.label}) has zero overflow and non-overlapping headers on 360dp + 1.3x',
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

          final sampleRoutine = WorkoutRoutineModel(
            id: 'ai-plan-test-day1',
            name: 'CBum Push — Ngực trên & Vai',
            splitType: 'PUSH_PULL_LEGS',
            scheduledWeekdays: [DateTime.now().weekday],
            updatedAt: DateTime.utc(2026, 11, 23),
            exercises: const [
              RoutineExerciseItem(
                exerciseCode: 'BARBELL_BENCH_PRESS',
                orderIndex: 0,
              ),
            ],
          );

          await _pumpNarrowScreen(
            tester,
            home: const HealthDashboardScreen(),
            healthState: state,
            themeData: themeEntry.theme,
            extraOverrides: [
              workoutRoutinesProvider.overrideWith((_) async => [sampleRoutine]),
              exercisesListProvider.overrideWith((_) async => const [
                    ExerciseModel(
                      id: 'ex-bench',
                      code: 'BARBELL_BENCH_PRESS',
                      nameVi: 'Đẩy ngực ngang với tạ đòn',
                      equipmentType: 'BARBELL',
                      model3dGlbUrl: 'assets/3d_bundled/barbell_bench_press.glb',
                      assetChecksum: 'abc',
                      primaryMuscles: ['Mat_Muscle_Chest'],
                    ),
                  ]),
              aiReadinessProvider.overrideWith(
                (_) async => AiAnalyticsRepository.newUserFallbackSnapshot(),
              ),
            ],
            width: 360.0,
            textScale: 1.3,
          );

          // Tab 0 (Hom nay): Hero Card, Circular Avatar, Sync chip, Water header
          expect(find.byKey(const Key('profile_avatar_button')), findsOneWidget);
          expect(find.text('CBum Push — Ngực trên & Vai'), findsOneWidget);
          expect(find.text('Bắt đầu tập ngay'), findsOneWidget);

          await tester.scrollUntilVisible(find.text('Lượng nước thông minh'), 200);
          final waterTitleRect =
              tester.getRect(find.text('Lượng nước thông minh'));
          final waterValRect = tester.getRect(find.text('0 / 2443 ml'));
          expect(waterTitleRect.right, lessThanOrEqualTo(waterValRect.left));

          final tab0Text = _collectAllVisibleStrings(tester).join('\n');
          expect(tab0Text, contains('Đồng bộ (3)'));
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
            expect(tab0Text, isNot(contains(forbidden)));
          }

      // Switch to Tab 3 (Dinh duong): FoodScan Card & Supplement header
          await tester.tap(find.text('Dinh dưỡng'));
          await tester.pumpAndSettle();
          expect(find.text('Quét món ăn bằng AI'), findsOneWidget);

          await tester.scrollUntilVisible(
            find.text('Thực phẩm bổ sung hôm nay'),
            200,
          );
          final suppTitleRect =
              tester.getRect(find.text('Thực phẩm bổ sung hôm nay'));
          final suppValRect = tester.getRect(find.text('0% tuần'));
          expect(suppTitleRect.right, lessThanOrEqualTo(suppValRect.left));

          // Switch across remaining tabs (Tab 1, Tab 2, Tab 4) smoothly with zero overflow
          await tester.tap(find.text('Lịch tập'));
          await tester.pumpAndSettle();
          expect(find.text('Lịch tập trong tuần'), findsOneWidget);

          await tester.tap(find.text('3D Gym'));
          await tester.pumpAndSettle();
          expect(find.textContaining('bài tập 3D tương tác'), findsOneWidget);

          await tester.tap(find.text('AI & Cơ thể'));
          await tester.pumpAndSettle();
          expect(find.text('Phục hồi 3D'), findsOneWidget);
        },
      );
    }

    testWidgets(
      'ProfileSettingsScreen renders Light & Dark Mode cleanly on 360dp + 1.3x with Delete Account & Medical Disclaimer',
      (tester) async {
        final state = _sampleHealthState(biometrics: const []);
        for (final theme in [AppTheme.lightTheme, AppTheme.darkTheme]) {
          await _pumpNarrowScreen(
            tester,
            home: ProfileSettingsScreen(
              key: ValueKey('profile-${theme.brightness}'),
            ),
            healthState: state,
            themeData: theme,
            width: 360.0,
            textScale: 1.3,
          );
          expect(find.text('Hồ sơ & Cài đặt'), findsOneWidget);
          expect(find.text('Giao diện hiển thị'), findsOneWidget);
          final mainListScrollable = find
              .descendant(
                of: find.byType(ListView),
                matching: find.byType(Scrollable),
              )
              .first;
          await tester.scrollUntilVisible(
            find.text('Xóa tài khoản'),
            250,
            scrollable: mainListScrollable,
          );
          final allText = _collectAllVisibleStrings(tester).join('\n');
          expect(allText, contains('Xem lại Miễn trừ Trách nhiệm Y tế'));
          expect(allText, contains('Xóa tài khoản'));
          for (final forbidden in const [
            'Offline-First',
            'SQLite',
            'SharedPreferences',
            'CH Play',
            '(F26)',
          ]) {
            expect(allText, isNot(contains(forbidden)));
          }
        }
      },
    );
  });

  group('Note.md Section 1 — M1 Screens Copy, CH Play Disclaimers & Narrow Layout',
      () {
    testWidgets(
        'OnboardingDisclaimerScreen 6-step wizard, quick login modal & Step 6 medical disclaimer on 360dp',
        (tester) async {
      // 1. Step 1 + Quick Login Medical Disclaimer dialog (360dp + 1.3x)
      await _pumpNarrowScreen(
        tester,
        home: const OnboardingDisclaimerScreen(initialStep: 0),
        authState: const AuthState(
          isInitialized: true,
          disclaimerAccepted: false,
          isAuthenticated: false,
        ),
        width: 360.0,
        height: 820.0,
        textScale: 1.3,
      );

      expect(find.text('Bước 1/6'), findsOneWidget);
      expect(find.textContaining('Mô hình 3D: Nam'), findsOneWidget);
      await tester.tap(find.text('Nữ'));
      await tester.pumpAndSettle();
      expect(find.text('Mô hình 3D: Nữ - Fitness'), findsOneWidget);
      await tester.tap(find.text('Đăng nhập'));
      await tester.pumpAndSettle();

      final dialogText = _collectAllVisibleStrings(tester).join('\n');
      expect(dialogText, contains('Mifflin-St Jeor'));
      expect(dialogText, contains('Epley (1985) & Brzycki (1993)'));
      final quickLoginBtn = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'Vào Đăng nhập'),
      );
      expect(quickLoginBtn.onPressed, isNull);
      await tester.tap(find.text('Đóng'));
      await tester.pumpAndSettle();

      // 2. Step 6 summary & mandatory medical disclaimer checkbox in Dark Mode
      await _pumpNarrowScreen(
        tester,
        home: const OnboardingDisclaimerScreen(
          key: ValueKey('onboarding-step6'),
          initialStep: 5,
        ),
        authState: const AuthState(
          isInitialized: true,
          disclaimerAccepted: false,
          isAuthenticated: false,
        ),
        themeData: AppTheme.darkTheme,
        width: 360.0,
        height: 820.0,
        textScale: 1.0,
      );

      final step6Text = _collectAllVisibleStrings(tester).join('\n');
      expect(step6Text, contains('Bước 6/6'));
      expect(step6Text, contains('Mifflin-St Jeor'));
      expect(step6Text, contains('Epley (1985) & Brzycki (1993)'));
      for (final forbidden in const [
        'Offline-First',
        'Blender MCP',
        'YOLOv8',
        'Android Health Connect',
        'CH Play Mandatory',
        '(Bulk)',
        '(Cut)',
      ]) {
        expect(step6Text, isNot(contains(forbidden)));
      }

      // Finish button must remain disabled until checkbox is ticked
      final finishBtn = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'Hoàn tất & Tạo tài khoản'),
      );
      expect(finishBtn.onPressed, isNull);
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

    testWidgets(
      'AppLaunchGate prevents Onboarding/Login flash on cold start and routes directly',
      (tester) async {
        GoRouter buildTestRouter() => GoRouter(
              initialLocation: '/onboarding',
              routes: [
                GoRoute(
                  path: '/onboarding',
                  builder: (_, __) => const AppLaunchGate(),
                ),
                GoRoute(
                  path: '/login',
                  builder: (_, __) => const Scaffold(body: Text('LOGIN_TARGET')),
                ),
                GoRoute(
                  path: '/health',
                  builder: (_, __) =>
                      const Scaffold(body: Text('HEALTH_TARGET')),
                ),
              ],
            );

        // 1. Uninitialized: shows launch splash, never flashes Bước 1/6 or Login
        await tester.pumpWidget(
          ProviderScope(
            key: UniqueKey(),
            overrides: [
              authControllerProvider.overrideWith(
                (_) => _FakeAuthController(
                  const AuthState(isInitialized: false),
                ),
              ),
            ],
            child: MaterialApp.router(
              theme: AppTheme.darkTheme,
              routerConfig: buildTestRouter(),
            ),
          ),
        );
        await tester.pump();
        expect(find.byKey(const Key('vigor_launch_splash')), findsOneWidget);
        expect(find.text('Bước 1/6'), findsNothing);
        expect(find.text('LOGIN_TARGET'), findsNothing);

        // 2. Initialized + Authenticated: jumps straight to /health
        await tester.pumpWidget(
          ProviderScope(
            key: UniqueKey(),
            overrides: [
              authControllerProvider.overrideWith(
                (_) => _FakeAuthController(
                  const AuthState(
                    isInitialized: true,
                    disclaimerAccepted: true,
                    isAuthenticated: true,
                  ),
                ),
              ),
            ],
            child: MaterialApp.router(
              theme: AppTheme.lightTheme,
              routerConfig: buildTestRouter(),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text('HEALTH_TARGET'), findsOneWidget);

        // 3. Initialized + Disclaimer accepted + Logged out: jumps straight to /login
        await tester.pumpWidget(
          ProviderScope(
            key: UniqueKey(),
            overrides: [
              authControllerProvider.overrideWith(
                (_) => _FakeAuthController(
                  const AuthState(
                    isInitialized: true,
                    disclaimerAccepted: true,
                    isAuthenticated: false,
                  ),
                ),
              ),
            ],
            child: MaterialApp.router(
              theme: AppTheme.darkTheme,
              routerConfig: buildTestRouter(),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text('LOGIN_TARGET'), findsOneWidget);
      },
    );
  });
}
