// [OWNER: M1] MainNavigationShell 5 Tab muot (RepaintBoundary + Fade/Slide), Floating Dock & Dashboard Mau 01 (T-M1-05..12)
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/database/health_tables.drift.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../../ai_analytics/data/ai_analytics_repository.dart';
import '../../ai_analytics/presentation/ai_coach_hub_screen.dart';
import '../../auth_privacy/data/user_fitness_profile.dart';
import '../../auth_privacy/presentation/auth_controller.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../gym3d/presentation/gym3d_library_screen.dart';
import '../../workout/data/workout_repository.dart';
import '../../workout/presentation/routines_screen.dart';
import '../data/health_repository.dart';

final mainTabIndexProvider = StateProvider<int>((ref) => 0);

class HealthDashboardScreen extends ConsumerStatefulWidget {
  const HealthDashboardScreen({super.key});

  @override
  ConsumerState<HealthDashboardScreen> createState() =>
      _HealthDashboardScreenState();
}

class _HealthDashboardScreenState extends ConsumerState<HealthDashboardScreen>
    with WidgetsBindingObserver {
  final Set<int> _visitedTabs = {0};

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    Future<void>.delayed(const Duration(milliseconds: 350), () {
      if (!mounted) return;
      try {
        ref.read(workoutRoutinesProvider);
        ref.read(exercisesListProvider);
        ref.read(aiReadinessProvider);
      } catch (_) {}
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      ref.read(healthDashboardProvider.notifier).load();
    }
  }

  String _appBarTitleForTab(int index, String displayName) {
    switch (index) {
      case 1:
        return 'Lịch & Giáo án';
      case 2:
        return 'Phòng tập 3D';
      case 3:
        return 'Dinh dưỡng & Bổ sung';
      case 4:
        return 'AI Coach & Cơ thể';
      default:
        return 'Chào, $displayName';
    }
  }

  String _appBarKickerForTab(int index) {
    switch (index) {
      case 1:
        return 'KẾ HOẠCH TẬP LUYỆN';
      case 2:
        return 'BLENDER 3D STUDIO';
      case 3:
        return 'NĂNG LƯỢNG & MACRO';
      case 4:
        return 'PHÂN TÍCH SINH LÝ';
      default:
        return 'VIGORAI · HÔM NAY';
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentTab = ref.watch(mainTabIndexProvider).clamp(0, 4);
    _visitedTabs.add(currentTab);

    final authFullName = ref.watch(
      authControllerProvider.select((s) => s.user?.fullName),
    );
    final profileName = ref.watch(
      userFitnessProfileProvider.select((p) => p.fullName),
    );

    final displayName =
        (authFullName != null && authFullName.trim().isNotEmpty)
            ? authFullName
            : profileName;
    final initialChar =
        (displayName.trim().isNotEmpty ? displayName.trim()[0] : 'V')
            .toUpperCase();
    final isDark = AppColors.isDark(context);

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 62,
        titleSpacing: 20,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _appBarKickerForTab(currentTab),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 10.5,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.2,
                color: AppColors.telemetryCyan(context),
              ),
            ),
            const SizedBox(height: 1),
            Text(
              _appBarTitleForTab(currentTab, displayName),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.4,
              ),
            ),
          ],
        ),
        actions: [
          const _SyncStatusChip(),
          IconButton(
            tooltip: isDark ? 'Chuyển sang Nền Sáng' : 'Chuyển sang Nền Tối',
            visualDensity: VisualDensity.compact,
            onPressed: () {
              HapticFeedback.selectionClick();
              ref
                  .read(themePreferenceProvider.notifier)
                  .toggleQuickLightDark(Theme.of(context).brightness);
            },
            icon: Icon(
              isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
              size: 20,
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 16, left: 2),
            child: _ProfileAvatarButton(initialChar: initialChar),
          ),
        ],
      ),
      body: _SmoothTabViewport(
        selectedIndex: currentTab,
        children: [
          const RepaintBoundary(child: _TodayOverviewTab()),
          RepaintBoundary(
            child: _visitedTabs.contains(1)
                ? const RoutinesScreen(embedded: true)
                : const SizedBox.shrink(),
          ),
          RepaintBoundary(
            child: _visitedTabs.contains(2)
                ? const Gym3DLibraryScreen(embedded: true)
                : const SizedBox.shrink(),
          ),
          RepaintBoundary(
            child: _visitedTabs.contains(3)
                ? const _NutritionAndSupplementsTab()
                : const SizedBox.shrink(),
          ),
          RepaintBoundary(
            child: _visitedTabs.contains(4)
                ? _AiAndBodyTab(isActive: currentTab == 4)
                : const SizedBox.shrink(),
          ),
        ],
      ),
      bottomNavigationBar: _VigorFloatingDock(
        selectedIndex: currentTab,
        onSelected: (idx) {
          if (idx == currentTab) return;
          HapticFeedback.selectionClick();
          setState(() => _visitedTabs.add(idx));
          ref.read(mainTabIndexProvider.notifier).state = idx;
        },
      ),
    );
  }
}

class _SyncStatusChip extends ConsumerWidget {
  const _SyncStatusChip();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pendingCount = ref.watch(
      healthDashboardProvider.select((s) => s.pendingSyncCount),
    );
    final isSyncing = ref.watch(
      healthDashboardProvider.select((s) => s.isSyncing),
    );
    if (pendingCount <= 0 && !isSyncing) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(right: 4),
      child: ActionChip(
        visualDensity: VisualDensity.compact,
        avatar: isSyncing
            ? const SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.cloud_upload_outlined, size: 15),
        label: Text(
          isSyncing ? 'Đang...' : 'Đồng bộ ($pendingCount)',
          style: const TextStyle(fontSize: 11.5),
        ),
        onPressed: isSyncing
            ? null
            : () async {
                final report = await ref
                    .read(healthDashboardProvider.notifier)
                    .syncWithServer();
                if (!context.mounted) return;
                final msg = report.skippedOffline
                    ? 'Chưa có mạng — đã lưu ${report.remainingPendingCount} thay đổi trên thiết bị.'
                    : (report.errorMessage ??
                        'Đồng bộ hoàn tất (${report.pushedCount} mục).');
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(msg)),
                );
              },
      ),
    );
  }
}

class _ProfileAvatarButton extends ConsumerWidget {
  final String initialChar;

  const _ProfileAvatarButton({required this.initialChar});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final hasPendingSync = ref.watch(
      healthDashboardProvider.select((s) => s.pendingSyncCount > 0),
    );
    final isDark = AppColors.isDark(context);
    final ringColor = isDark ? AppColors.volt : AppColors.lightPrimary;

    return Tooltip(
      message: 'Hồ sơ & Cài đặt',
      child: InkWell(
        key: const Key('profile_avatar_button'),
        borderRadius: BorderRadius.circular(20),
        onTap: () => context.push('/profile'),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDark
                    ? AppColors.darkElevated
                    : AppColors.lightPrimary,
                border: Border.all(
                  color: ringColor.withValues(alpha: isDark ? 0.85 : 1.0),
                  width: 1.5,
                ),
              ),
              alignment: Alignment.center,
              child: Text(
                initialChar,
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 15,
                  color: isDark ? AppColors.volt : Colors.white,
                ),
              ),
            ),
            Positioned(
              right: -1,
              bottom: -1,
              child: Container(
                width: 11,
                height: 11,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: hasPendingSync
                      ? AppColors.calorieOrange
                      : AppColors.muscleRecoveredGreen,
                  border: Border.all(
                    color: Theme.of(context).scaffoldBackgroundColor,
                    width: 1.5,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SmoothTabViewport extends StatefulWidget {
  final int selectedIndex;
  final List<Widget> children;

  const _SmoothTabViewport({
    required this.selectedIndex,
    required this.children,
  });

  @override
  State<_SmoothTabViewport> createState() => _SmoothTabViewportState();
}

class _SmoothTabViewportState extends State<_SmoothTabViewport>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 180),
      value: 1.0,
    );
    _fadeAnimation = Tween<double>(begin: 0.88, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.012),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
  }

  @override
  void didUpdateWidget(covariant _SmoothTabViewport oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedIndex != widget.selectedIndex) {
      _controller.forward(from: 0.0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: IndexedStack(
          index: widget.selectedIndex,
          children: widget.children,
        ),
      ),
    );
  }
}

class _VigorFloatingDock extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onSelected;

  const _VigorFloatingDock({
    required this.selectedIndex,
    required this.onSelected,
  });

  static const _items = <({IconData icon, IconData selectedIcon, String label})>[
    (
      icon: Icons.home_outlined,
      selectedIcon: Icons.home_rounded,
      label: 'Hôm nay',
    ),
    (
      icon: Icons.calendar_today_outlined,
      selectedIcon: Icons.calendar_today_rounded,
      label: 'Lịch tập',
    ),
    (
      icon: Icons.view_in_ar_outlined,
      selectedIcon: Icons.view_in_ar_rounded,
      label: '3D Gym',
    ),
    (
      icon: Icons.restaurant_menu_outlined,
      selectedIcon: Icons.restaurant_menu_rounded,
      label: 'Dinh dưỡng',
    ),
    (
      icon: Icons.auto_awesome_outlined,
      selectedIcon: Icons.auto_awesome,
      label: 'AI & Cơ thể',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = AppColors.isDark(context);
    final dockBg = isDark ? AppColors.darkNavBar : AppColors.lightCard;
    final activePillBg = isDark
        ? AppColors.volt.withValues(alpha: 0.16)
        : AppColors.lightPrimary;
    final activeFg = isDark ? AppColors.volt : Colors.white;
    final inactiveFg = AppColors.secondaryText(context);

    return SafeArea(
      top: false,
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 4, 16, 10),
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
        decoration: BoxDecoration(
          color: dockBg,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: AppColors.subtleBorder(context)),
          boxShadow: AppColors.cardShadow(context),
        ),
        child: Row(
          children: [
            for (var i = 0; i < _items.length; i++)
              Expanded(
                child: InkWell(
                  borderRadius: BorderRadius.circular(22),
                  onTap: () => onSelected(i),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 180),
                    curve: Curves.easeOutCubic,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 4,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: selectedIndex == i
                          ? activePillBg
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(22),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          selectedIndex == i
                              ? _items[i].selectedIcon
                              : _items[i].icon,
                          size: 20,
                          color: selectedIndex == i ? activeFg : inactiveFg,
                        ),
                        const SizedBox(height: 3),
                        FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Text(
                            _items[i].label,
                            maxLines: 1,
                            style: TextStyle(
                              fontSize: 10.5,
                              fontWeight: selectedIndex == i
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              color: selectedIndex == i ? activeFg : inactiveFg,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _TodayOverviewTab extends ConsumerWidget {
  const _TodayOverviewTab();

  static String _weekdayName(int weekday) {
    switch (weekday) {
      case 1:
        return 'THỨ 2';
      case 2:
        return 'THỨ 3';
      case 3:
        return 'THỨ 4';
      case 4:
        return 'THỨ 5';
      case 5:
        return 'THỨ 6';
      case 6:
        return 'THỨ 7';
      default:
        return 'CHỦ NHẬT';
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthDashboardProvider);
    final fitnessProfile = ref.watch(userFitnessProfileProvider);
    final controller = ref.read(healthDashboardProvider.notifier);

    if (healthState.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final daily = healthState.dailyHealth;
    final latestBio = healthState.latestBiometric;
    final routinesAsync = ref.watch(workoutRoutinesProvider);
    final readinessAsync = ref.watch(aiReadinessProvider);
    final exercisesAsync = ref.watch(exercisesListProvider);

    final todayRoutine = routinesAsync.maybeWhen(
      data: (list) => WorkoutRepository.pickTodayRoutine(list),
      orElse: () => null,
    );
    final exNameByCode = <String, String>{
      for (final ex in exercisesAsync.valueOrNull ?? const <ExerciseModel>[])
        ex.code.toUpperCase(): ex.nameVi,
    };

    final heroTitle = todayRoutine?.name ??
        '${fitnessProfile.selectedProgram.shortLabelVi} · Sẵn sàng tập';
    final heroMusclesSummary = todayRoutine != null &&
            todayRoutine.exercises.isNotEmpty
        ? todayRoutine.exercises
            .take(3)
            .map(
              (e) =>
                  exNameByCode[e.exerciseCode.toUpperCase()] ?? e.exerciseCode,
            )
            .join(' · ')
        : 'Bài tập 3D mô phỏng chuẩn & đo nhịp nghỉ tự động';

    final readinessScore = readinessAsync.maybeWhen(
      data: (s) => s.readinessScore.round(),
      orElse: () => 85,
    );

    final targetKcal = healthState.targetCaloriesKcal > 0
        ? healthState.targetCaloriesKcal
        : 2400.0;
    final consumedKcal = healthState.totalCaloriesConsumed;
    final remainingKcal = math.max(0, (targetKcal - consumedKcal).round());
    final kcalRatio = (consumedKcal / targetKcal).clamp(0.0, 1.0);

    final stepsCount = daily?.stepsCount ?? 0;
    final targetSteps = (daily?.targetSteps ?? 8000) > 0
        ? (daily?.targetSteps ?? 8000)
        : 8000;
    final stepsRatio = (stepsCount / targetSteps).clamp(0.0, 1.0);

    final sleepHours = daily?.sleepHours ?? 0.0;
    final sleepRatio = (sleepHours / 8.0).clamp(0.0, 1.0);

    return RefreshIndicator(
      onRefresh: controller.load,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
        children: [
          if (healthState.errorMessage != null) ...[
            Card(
              color: AppColors.tintedSurface(context, AppColors.warningRed),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Text(healthState.errorMessage!),
              ),
            ),
            const SizedBox(height: 14),
          ],

          // 1. Obsidian Dual Hero Card (Readiness Ring + Today Workout)
          Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF151C28), Color(0xFF0C1017)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(26),
              border: Border.all(
                color: Colors.white.withValues(alpha: 0.08),
              ),
              boxShadow: AppColors.cardShadow(context),
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    InkWell(
                      borderRadius: BorderRadius.circular(44),
                      onTap: () =>
                          ref.read(mainTabIndexProvider.notifier).state = 4,
                      child: SizedBox(
                        width: 78,
                        height: 78,
                        child: CustomPaint(
                          painter: _ReadinessArcPainter(
                            progress: (readinessScore / 100.0).clamp(0.0, 1.0),
                            color: AppColors.volt,
                            trackColor: const Color(0xFF232C3D),
                          ),
                          child: Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  '$readinessScore',
                                  style: const TextStyle(
                                    color: AppColors.volt,
                                    fontSize: 22,
                                    fontWeight: FontWeight.w800,
                                    height: 1.0,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                const Text(
                                  'SẴN SÀNG',
                                  style: TextStyle(
                                    color: Color(0xFF8B95A5),
                                    fontSize: 7.5,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.6,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${_weekdayName(DateTime.now().weekday)} · ~${fitnessProfile.sessionDurationMin} PHÚT',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: AppColors.volt,
                              fontSize: 10.5,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.1,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            heroTitle,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              letterSpacing: -0.3,
                              height: 1.2,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            heroMusclesSummary,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 12,
                              height: 1.35,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 10,
                  runSpacing: 8,
                  children: [
                    FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.volt,
                        foregroundColor: const Color(0xFF090B0F),
                        minimumSize: const Size(0, 42),
                        padding: const EdgeInsets.symmetric(horizontal: 18),
                      ),
                      onPressed: () {
                        final route = todayRoutine != null
                            ? '/workout/live?routineId=${todayRoutine.id}'
                            : '/workout/live';
                        context.push(route);
                      },
                      icon: const Icon(Icons.play_arrow_rounded, size: 20),
                      label: const Text('Bắt đầu tập ngay'),
                    ),
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white,
                        side: BorderSide(
                          color: Colors.white.withValues(alpha: 0.25),
                        ),
                        minimumSize: const Size(0, 42),
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                      ),
                      onPressed: () =>
                          ref.read(mainTabIndexProvider.notifier).state = 1,
                      icon: const Icon(Icons.swap_horiz_rounded, size: 18),
                      label: const Text('Đổi lịch'),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // 2. Airy 2x2 Bento Telemetry Grid
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  child: _BentoMetricTile(
                    kicker: 'CALO CÒN LẠI',
                    bigValue: '$remainingKcal',
                    unit: 'kcal',
                    progress: kcalRatio,
                    accentColor: AppColors.calorieOrange,
                    subtitle:
                        '${consumedKcal.round()} / ${targetKcal.round()} kcal',
                    onTap: () => context.push('/health/nutrition'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _BentoMetricTile(
                    kicker: 'VẬN ĐỘNG',
                    bigValue: '$stepsCount',
                    unit: 'bước',
                    progress: stepsRatio,
                    accentColor: AppColors.stepTeal,
                    subtitle:
                        '${daily?.distanceKm ?? 0} km · ${daily?.activeCaloriesKcal ?? 0} kcal',
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  child: _BentoMetricTile(
                    kicker: 'GIẤC NGỦ',
                    bigValue: '${sleepHours.toStringAsFixed(1)}h',
                    unit: '',
                    progress: sleepRatio,
                    accentColor: AppColors.sleepPurple,
                    subtitle: DailyHealthModel.classifySleepStatus(sleepHours),
                    onTap: () => context.push('/health/sleep'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _BentoMetricTile(
                    kicker: 'CƠ THỂ',
                    bigValue: latestBio != null
                        ? latestBio.weightKg.toStringAsFixed(1)
                        : '--',
                    unit: 'kg',
                    progress: latestBio != null
                        ? ((latestBio.bmi / 30.0).clamp(0.2, 1.0))
                        : 0.0,
                    accentColor: AppColors.muscleRecoveredGreen,
                    subtitle: latestBio != null
                        ? 'BMI ${latestBio.bmi} · ${BiometricLogModel.classifyAsianBmi(latestBio.bmi)}'
                        : 'Chạm để cập nhật',
                    onTap: () => context.push('/health/biometrics'),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // 3. Smart Hydration Telemetry Card
          if (daily != null)
            Card(
              child: InkWell(
                borderRadius: BorderRadius.circular(24),
                onTap: () => context.push('/health/hydration'),
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Expanded(
                            child: Text(
                              'Lượng nước thông minh',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 15,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '${daily.waterMl} / ${daily.targetWaterMl} ml',
                            style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              color: AppColors.hydrationBlue,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(6),
                        child: LinearProgressIndicator(
                          value: daily.targetWaterMl > 0
                              ? (daily.waterMl / daily.targetWaterMl)
                                  .clamp(0.0, 1.0)
                              : 0.0,
                          color: AppColors.hydrationBlue,
                          backgroundColor: AppColors.subtleSurface(context),
                          minHeight: 8,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        runSpacing: 6,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          OutlinedButton.icon(
                            onPressed: () => controller.addWaterMl(250),
                            icon: const Icon(
                              Icons.water_drop_outlined,
                              size: 16,
                            ),
                            label: const Text('+250 ml'),
                          ),
                          OutlinedButton.icon(
                            onPressed: () => controller.addWaterMl(500),
                            icon: const Icon(
                              Icons.local_drink_outlined,
                              size: 16,
                            ),
                            label: const Text('+500 ml'),
                          ),
                          TextButton(
                            onPressed: () => context.push('/health/hydration'),
                            child: const Text('Chi tiết'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _BentoMetricTile extends StatelessWidget {
  final String kicker;
  final String bigValue;
  final String unit;
  final double progress;
  final Color accentColor;
  final String subtitle;
  final VoidCallback? onTap;

  const _BentoMetricTile({
    required this.kicker,
    required this.bigValue,
    required this.unit,
    required this.progress,
    required this.accentColor,
    required this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.subtleBorder(context)),
        boxShadow: AppColors.cardShadow(context),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                kicker,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 10.5,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.0,
                  color: AppColors.secondaryText(context),
                ),
              ),
              const SizedBox(height: 8),
              FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.baseline,
                  textBaseline: TextBaseline.alphabetic,
                  children: [
                    Text(
                      bigValue,
                      style: const TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.7,
                        fontFeatures: [FontFeature.tabularFigures()],
                      ),
                    ),
                    if (unit.isNotEmpty) ...[
                      const SizedBox(width: 4),
                      Text(
                        unit,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: accentColor,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 10),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progress.clamp(0.0, 1.0),
                  minHeight: 5,
                  color: accentColor,
                  backgroundColor: AppColors.subtleSurface(context),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                subtitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 11.5,
                  color: AppColors.secondaryText(context),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ReadinessArcPainter extends CustomPainter {
  final double progress;
  final Color color;
  final Color trackColor;

  const _ReadinessArcPainter({
    required this.progress,
    required this.color,
    required this.trackColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (math.min(size.width, size.height) - 8) / 2;
    final trackPaint = Paint()
      ..color = trackColor
      ..strokeWidth = 7
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawCircle(center, radius, trackPaint);

    final arcPaint = Paint()
      ..color = color
      ..strokeWidth = 7
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(covariant _ReadinessArcPainter oldDelegate) =>
      oldDelegate.progress != progress || oldDelegate.color != color;
}

class _NutritionAndSupplementsTab extends ConsumerWidget {
  const _NutritionAndSupplementsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);

    final targetKcal = healthState.targetCaloriesKcal > 0
        ? healthState.targetCaloriesKcal
        : 2400.0;
    final kcalRatio =
        (healthState.totalCaloriesConsumed / targetKcal).clamp(0.0, 1.0);
    final macros = healthState.macroTargets;
    final daily = healthState.dailyHealth;

    return RefreshIndicator(
      onRefresh: controller.load,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 10, 20, 24),
        children: [
          // Vong tron Calo & 3 Thanh Macro
          Card(
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: () => context.push('/health/nutrition'),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        SizedBox(
                          width: 72,
                          height: 72,
                          child: Stack(
                            fit: StackFit.expand,
                            children: [
                              CircularProgressIndicator(
                                value: kcalRatio,
                                strokeWidth: 8,
                                color: AppColors.calorieOrange,
                                backgroundColor:
                                    AppColors.subtleSurface(context),
                              ),
                              Center(
                                child: Text(
                                  '${(kcalRatio * 100).round()}%',
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w800,
                                    color: AppColors.calorieOrange,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Mục tiêu Calo & Macro',
                                style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  fontSize: 15,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${healthState.totalCaloriesConsumed.round()} / '
                                '${healthState.targetCaloriesKcal.round()} kcal',
                                style: const TextStyle(
                                  fontSize: 19,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.calorieOrange,
                                ),
                              ),
                              Text(
                                'Theo Mifflin-St Jeor (1990)',
                                style: TextStyle(
                                  fontSize: 11.5,
                                  color: AppColors.secondaryText(context),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.chevron_right),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _CompactMacroBar(
                      label: 'Đạm',
                      current: healthState.totalProteinConsumed,
                      target: macros.proteinG,
                      color: AppColors.musclePrimaryRed,
                    ),
                    const SizedBox(height: 8),
                    _CompactMacroBar(
                      label: 'Carb',
                      current: healthState.totalCarbsConsumed,
                      target: macros.carbsG,
                      color: AppColors.hydrationBlue,
                    ),
                    const SizedBox(height: 8),
                    _CompactMacroBar(
                      label: 'Fat',
                      current: healthState.totalFatConsumed,
                      target: macros.fatG,
                      color: AppColors.calorieOrange,
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // The lon: Quet mon an bang AI (Mau 01 Obsidian/Volt action card)
          Material(
            color: AppColors.isDark(context)
                ? AppColors.darkElevated
                : const Color(0xFF12161E),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
              side: BorderSide(
                color: AppColors.volt.withValues(alpha: 0.35),
              ),
            ),
            clipBehavior: Clip.antiAlias,
            child: ListTile(
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
              onTap: () => context.push('/health/food-scan'),
              leading: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: AppColors.volt,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(
                  Icons.camera_alt_outlined,
                  color: Color(0xFF090B0F),
                ),
              ),
              title: const Text(
                'Quét món ăn bằng AI',
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),
              subtitle: const Text(
                'Chụp ảnh khay cơm để ước tính Calo và Đạm/Carb/Fat tự động',
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12.5),
              ),
              trailing: const Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: AppColors.volt,
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Nhac nuoc nhanh
          if (daily != null) ...[
            Card(
              color: AppColors.tintedSurface(context, AppColors.hydrationBlue),
              child: ListTile(
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 18, vertical: 6),
                onTap: () => context.push('/health/hydration'),
                leading: const Icon(
                  Icons.water_drop_outlined,
                  color: AppColors.hydrationBlue,
                ),
                title: Text(
                  'Nước uống: ${daily.waterMl} / ${daily.targetWaterMl} ml',
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                subtitle: Text(
                  healthState.workoutBonusReason ??
                      'Uống đều suốt ngày để tối ưu phục hồi cơ bắp',
                ),
                trailing: TextButton(
                  onPressed: () => controller.addWaterMl(250),
                  child: const Text('+250 ml'),
                ),
              ),
            ),
            const SizedBox(height: 14),
          ],

          // Checklist Thuc pham bo sung hom nay
          Card(
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: () => context.push('/health/supplements'),
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Expanded(
                          child: Text(
                            'Thực phẩm bổ sung hôm nay',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontWeight: FontWeight.w700,
                              fontSize: 15,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '${healthState.weeklySupplementAdherencePct.toStringAsFixed(0)}% tuần',
                          style: const TextStyle(
                            fontSize: 12.5,
                            color: AppColors.muscleRecoveredGreen,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (healthState.supplements.isEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 6),
                        child: Text(
                          'Chưa có lịch bổ sung — chạm để thêm Creatine, Whey, Omega-3.',
                        ),
                      )
                    else
                      ...healthState.supplements.map(
                        (s) => ListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          onTap: () =>
                              controller.toggleSupplementTakenToday(s.id),
                          leading: Icon(
                            s.takenToday
                                ? Icons.check_circle
                                : Icons.radio_button_unchecked,
                            color: s.takenToday
                                ? AppColors.muscleRecoveredGreen
                                : Colors.grey,
                          ),
                          title: Text('${s.supplementName} (${s.dosageLabel})'),
                          trailing: Text(s.reminderTimeHhMm),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _AiAndBodyTab extends StatelessWidget {
  final bool isActive;

  const _AiAndBodyTab({required this.isActive});

  @override
  Widget build(BuildContext context) {
    final cyan = AppColors.telemetryCyan(context);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 10, 20, 6),
          child: Row(
            children: [
              Expanded(
                child: Card(
                  color: AppColors.tintedSurface(context, cyan),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(24),
                    onTap: () => context.push('/health/biometrics'),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 12,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.monitor_weight_outlined,
                            color: cyan,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Text(
                              'Cân nặng & BMI',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 12.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Card(
                  color: AppColors.tintedSurface(
                    context,
                    AppColors.muscleRecoveredGreen,
                  ),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(24),
                    onTap: () => context.push('/health/progress-photos'),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 12,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.compare,
                            color: AppColors.muscleRecoveredGreen,
                            size: 20,
                          ),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Ảnh tiến độ',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 12.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: AiCoachHubScreen(embedded: true, isActive: isActive),
        ),
      ],
    );
  }
}

class _CompactMacroBar extends StatelessWidget {
  final String label;
  final double current;
  final double target;
  final Color color;

  const _CompactMacroBar({
    required this.label,
    required this.current,
    required this.target,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final safeTarget = target > 0 ? target : 1.0;
    final ratio = (current / safeTarget).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 12.5)),
            Text(
              '${current.round()} / ${target.round()} g',
              style: TextStyle(
                fontSize: 12.5,
                fontWeight: FontWeight.w700,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: ratio,
            minHeight: 6,
            color: color,
            backgroundColor: AppColors.subtleSurface(context),
          ),
        ),
      ],
    );
  }
}
