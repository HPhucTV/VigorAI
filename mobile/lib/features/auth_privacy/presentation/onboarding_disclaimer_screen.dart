// [OWNER: M1] Onboarding Wizard 6 Buoc Tuong tac 3D + Nut Dang nhap nhanh + Mien tru Trach nhiem Y te CH Play (T-M1-04 / F26)
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import '../../health/data/health_repository.dart';
import '../../workout/data/workout_repository.dart';
import '../../workout/domain/smart_routine_generator.dart';
import '../data/auth_repository.dart';
import '../data/user_fitness_profile.dart';
import 'auth_controller.dart';

class OnboardingDisclaimerScreen extends ConsumerStatefulWidget {
  final int initialStep;
  final bool isReconfigureMode;

  const OnboardingDisclaimerScreen({
    super.key,
    this.initialStep = 0,
    this.isReconfigureMode = false,
  });

  static const String medicalDisclaimerText =
      'Ứng dụng VigorAI cung cấp các công cụ theo dõi thể chất, ước tính năng lượng '
      '(dựa trên công thức Mifflin-St Jeor), ước tính sức mạnh (công thức Epley/Brzycki) '
      'và gợi ý luyện tập từ AI chỉ phục vụ mục đích tham khảo thể hình (Fitness). '
      'Ứng dụng không thay thế cho tư vấn, chẩn đoán hoặc điều trị y khoa chuyên nghiệp. '
      'Vui lòng tham khảo ý kiến bác sĩ trước khi bắt đầu chế độ ăn kiêng hoặc tập luyện cường độ cao.';

  static const String formulaCitationText =
      'Nguồn công thức: Mifflin-St Jeor (1990) · Epley (1985) & Brzycki (1993) · WHO Asia-Pacific BMI.';

  @override
  ConsumerState<OnboardingDisclaimerScreen> createState() =>
      _OnboardingDisclaimerScreenState();
}

class _OnboardingDisclaimerScreenState
    extends ConsumerState<OnboardingDisclaimerScreen> {
  static const int _totalSteps = 6;
  static const Map<int, String> _weekdayLabels = {
    1: 'T2',
    2: 'T3',
    3: 'T4',
    4: 'T5',
    5: 'T6',
    6: 'T7',
    7: 'CN',
  };

  late int _step;
  bool _accepted = false;
  bool _syncedInitial = false;
  bool _isSaving = false;
  late UserFitnessProfile _draft;

  @override
  void initState() {
    super.initState();
    _step = widget.initialStep.clamp(0, _totalSteps - 1);
    _draft = ref.read(userFitnessProfileProvider);
  }

  void _updateDraft(UserFitnessProfile next) {
    HapticFeedback.selectionClick();
    setState(() => _draft = next);
  }

  void _goNext() {
    if (_step < _totalSteps - 1) {
      HapticFeedback.lightImpact();
      setState(() => _step++);
    }
  }

  void _goBack() {
    if (_step > 0) {
      setState(() => _step--);
    } else if (widget.isReconfigureMode && context.canPop()) {
      context.pop();
    }
  }

  Future<void> _openQuickLoginDialog() async {
    var dialogAccepted =
        ref.read(authControllerProvider).disclaimerAccepted || _accepted;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogCtx) => VigorAdaptiveTheme(
        child: StatefulBuilder(
          builder: (ctx, setDialogState) => AlertDialog(
            title: const Row(
              children: [
                Icon(
                  Icons.health_and_safety_outlined,
                  color: Colors.deepOrange,
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Xác nhận trước khi Đăng nhập',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.tintedSurface(ctx, Colors.amber),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          OnboardingDisclaimerScreen.medicalDisclaimerText,
                          style: TextStyle(fontSize: 12.5, height: 1.4),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          OnboardingDisclaimerScreen.formulaCitationText,
                          style: TextStyle(
                            fontSize: 11.5,
                            fontStyle: FontStyle.italic,
                            color: AppColors.secondaryText(ctx),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  CheckboxListTile(
                    value: dialogAccepted,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                    onChanged: (v) =>
                        setDialogState(() => dialogAccepted = v ?? false),
                    title: const Text(
                      'Tôi đã đọc, hiểu rõ và đồng ý với Miễn trừ Trách nhiệm Y tế.',
                      style: TextStyle(fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(dialogCtx).pop(false),
                child: const Text('Đóng'),
              ),
              FilledButton(
                onPressed: dialogAccepted
                    ? () => Navigator.of(dialogCtx).pop(true)
                    : null,
                child: const Text('Vào Đăng nhập'),
              ),
            ],
          ),
        ),
      ),
    );

    if (confirmed == true) {
      await ref.read(authControllerProvider.notifier).acceptMedicalDisclaimer();
      if (!mounted) return;
      context.go('/login');
    }
  }

  Future<void> _onFinishWizard() async {
    if (!_accepted || _isSaving) return;
    setState(() => _isSaving = true);
    try {
      final completed = _draft.copyWith(hasCompletedWizard: true);
      await ref
          .read(userFitnessProfileProvider.notifier)
          .saveProfile(completed);
      ref.read(bodyAvatarPresetProvider.notifier).state =
          completed.recommendedAvatarPreset;
      await ref.read(authControllerProvider.notifier).acceptMedicalDisclaimer();

      // Sinh lich tap & luu chi so sinh trac dau tien neu kho luu tru da san sang
      try {
        final exercises = await ref.read(exercisesListProvider.future);
        final generated = SmartRoutineGenerator.generatePlan(
          profile: completed,
          allExercises: exercises,
        );
        await ref.read(workoutRepositoryProvider).applyGeneratedPlan(generated);
        ref.invalidate(workoutRoutinesProvider);
      } catch (_) {
        // An toan trong moi truong test mock toi gian
      }

      if (widget.isReconfigureMode ||
          ref.read(authControllerProvider).isAuthenticated) {
        try {
          final currentUser = ref.read(authControllerProvider).user;
          if (currentUser != null) {
            await ref.read(authControllerProvider.notifier).updateLocalProfile(
                  AuthUserProfile(
                    id: currentUser.id,
                    email: currentUser.email,
                    fullName: currentUser.fullName,
                    gender: completed.gender,
                    birthDateIso: completed.birthDateIso,
                    heightCm: completed.heightCm,
                    activityLevel: completed.derivedActivityLevel,
                    fitnessGoal: completed.derivedFitnessGoal,
                    medicalDisclaimerAccepted: true,
                  ),
                );
          }
          await ref.read(healthRepositoryProvider).saveBiometric(
                weightKg: completed.currentWeightKg,
                heightCm: completed.heightCm,
                bodyFatPct: completed.estimatedBodyFatPct,
              );
          await ref.read(healthDashboardProvider.notifier).load();
        } catch (_) {}
        if (!mounted) return;
        context.go('/health');
      } else {
        if (!mounted) return;
        context.go('/register');
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).colorScheme.primary;

    if (!widget.isReconfigureMode) {
      ref.listen<AuthState>(authControllerProvider, (_, next) {
        if (next.isInitialized && next.isAuthenticated && mounted) {
          context.go('/health');
        }
      });
    }

    if (!_syncedInitial && authState.isInitialized) {
      _syncedInitial = true;
      if (authState.disclaimerAccepted || widget.isReconfigureMode) {
        _accepted = true;
      }
    }

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Thanh dau trang tinh gon chong be layout 360dp + 1.3x
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 6),
              child: Row(
                children: [
                  if (_step > 0 || widget.isReconfigureMode)
                    IconButton(
                      visualDensity: VisualDensity.compact,
                      tooltip: 'Quay lại',
                      onPressed: _goBack,
                      icon: const Icon(Icons.arrow_back_ios_new, size: 18),
                    ),
                  Expanded(
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Text(
                          'Bước ${_step + 1}/$_totalSteps',
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
                  IconButton(
                    tooltip: isDark ? 'Chuyển sang Nền Sáng' : 'Chuyển sang Nền Tối',
                    visualDensity: VisualDensity.compact,
                    onPressed: () {
                      ref
                          .read(themePreferenceProvider.notifier)
                          .toggleQuickLightDark(Theme.of(context).brightness);
                    },
                    icon: Icon(
                      isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 4),
                  if (!widget.isReconfigureMode)
                    TextButton(
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        visualDensity: VisualDensity.compact,
                      ),
                      onPressed: _openQuickLoginDialog,
                      child: const FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Text('Đăng nhập'),
                      ),
                    )
                  else
                    TextButton(
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        visualDensity: VisualDensity.compact,
                      ),
                      onPressed: () => context.pop(),
                      child: const Text('Đóng'),
                    ),
                ],
              ),
            ),
            // Thanh tien do muot
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: TweenAnimationBuilder<double>(
                tween: Tween<double>(end: (_step + 1) / _totalSteps),
                duration: const Duration(milliseconds: 280),
                curve: Curves.easeOutCubic,
                builder: (_, val, __) => ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: val,
                    minHeight: 6,
                    color: primaryColor,
                    backgroundColor: AppColors.subtleSurface(context),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),

            // Noi dung tung buoc voi hieu ung truot muot 280ms
            Expanded(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 280),
                switchInCurve: Curves.easeOutCubic,
                transitionBuilder: (child, animation) => FadeTransition(
                  opacity: animation,
                  child: SlideTransition(
                    position: Tween<Offset>(
                      begin: const Offset(0.06, 0),
                      end: Offset.zero,
                    ).animate(animation),
                    child: child,
                  ),
                ),
                child: KeyedSubtree(
                  key: ValueKey<int>(_step),
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
                    child: _buildCurrentStepContent(context),
                  ),
                ),
              ),
            ),

            // Thanh dieu huong duoi
            Container(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                border: Border(
                  top: BorderSide(color: AppColors.subtleBorder(context)),
                ),
              ),
              child: _step < _totalSteps - 1
                  ? FilledButton.icon(
                      onPressed: _goNext,
                      icon: const Icon(Icons.arrow_forward, size: 18),
                      label: const Text('Tiếp tục'),
                    )
                  : FilledButton.icon(
                      onPressed: (_accepted && !_isSaving)
                          ? _onFinishWizard
                          : null,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.check_circle_outline, size: 18),
                      label: Text(
                        widget.isReconfigureMode
                            ? 'Lưu Phác đồ & Quay lại'
                            : 'Hoàn tất & Tạo tài khoản',
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStepContent(BuildContext context) {
    switch (_step) {
      case 0:
        return _buildStep1BodyProfile(context);
      case 1:
        return _buildStep2BodyFatAndSomatotype(context);
      case 2:
        return _buildStep3ExperienceAndLocation(context);
      case 3:
        return _buildStep4ScheduleAndMuscles(context);
      case 4:
        return _buildStep5ProgramChoice(context);
      default:
        return _buildStep6SummaryAndDisclaimer(context);
    }
  }

  Widget _buildAvatarPreviewCard(
    BuildContext context, {
    required bool highlightPriorityMuscles,
  }) {
    final preset = _draft.recommendedAvatarPreset;
    final morph = _draft.computedBodyMorph;
    final muscleColors = highlightPriorityMuscles
        ? {
            for (final matId in _draft.priorityMuscleMaterialIds)
              matId: AppColors.musclePrimaryRed,
          }
        : const <String, Color>{};

    return _SafeOnboarding3DStage(
      avatarPreset: preset,
      bodyMorph: morph,
      statusBadgeText: '${preset.shortLabelVi} · BMI ${_draft.bmi}',
      muscleColorsMap: muscleColors,
      highlightedGroupLabels:
          _draft.priorityMuscles.map((m) => m.labelVi).toList(),
      showMuscleLegend: highlightPriorityMuscles,
    );
  }

  Widget _buildStep1BodyProfile(BuildContext context) {
    final bmi = _draft.bmi;
    final bmiLabel = _draft.bmiLabel;
    final bmiColor = bmi < 18.5
        ? AppColors.hydrationBlue
        : (bmi < 23.0
            ? AppColors.muscleRecoveredGreen
            : (bmi < 25.0
                ? AppColors.calorieOrange
                : AppColors.warningRed));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Hồ sơ Cơ thể & Avatar 3D của bạn',
          style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Chọn giới tính và chỉ số hiện tại để hệ thống chọn Avatar 3D & tính BMR chính xác.',
          style: TextStyle(
            fontSize: 13,
            color: AppColors.secondaryText(context),
          ),
        ),
        const SizedBox(height: 12),
        _buildAvatarPreviewCard(context, highlightPriorityMuscles: false),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _SelectableOptionCard(
                selected: _draft.gender == 'MALE',
                icon: Icons.male_rounded,
                title: 'Nam',
                subtitle: 'Avatar Nam',
                onTap: () => _updateDraft(
                  _draft.copyWith(
                    gender: 'MALE',
                    preferredAvatarCode: 'MALE_FIT',
                    estimatedBodyFatPct:
                        _draft.bodyFatPreset.estimatedPctForGender('MALE'),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _SelectableOptionCard(
                selected: _draft.gender == 'FEMALE',
                icon: Icons.female_rounded,
                title: 'Nữ',
                subtitle: 'Avatar Nữ Fitness',
                onTap: () => _updateDraft(
                  _draft.copyWith(
                    gender: 'FEMALE',
                    preferredAvatarCode: 'FEMALE_FIT',
                    estimatedBodyFatPct:
                        _draft.bodyFatPreset.estimatedPctForGender('FEMALE'),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              children: [
                _RulerSliderRow(
                  label: 'Tuổi',
                  valueText: '${_draft.ageYears} tuổi',
                  value: _draft.ageYears.toDouble(),
                  min: 16,
                  max: 75,
                  divisions: 59,
                  onChanged: (v) =>
                      _updateDraft(_draft.copyWith(ageYears: v.round())),
                ),
                const Divider(height: 16),
                _RulerSliderRow(
                  label: 'Chiều cao',
                  valueText: '${_draft.heightCm.round()} cm',
                  value: _draft.heightCm,
                  min: 140,
                  max: 210,
                  divisions: 70,
                  onChanged: (v) => _updateDraft(
                    _draft.copyWith(heightCm: v.roundToDouble()),
                  ),
                ),
                const Divider(height: 16),
                _RulerSliderRow(
                  label: 'Cân nặng hiện tại',
                  valueText: '${_draft.currentWeightKg.toStringAsFixed(1)} kg',
                  value: _draft.currentWeightKg,
                  min: 35,
                  max: 180,
                  divisions: 290,
                  onChanged: (v) => _updateDraft(
                    _draft.copyWith(
                      currentWeightKg: (v * 2).round() / 2.0,
                    ),
                  ),
                ),
                const Divider(height: 16),
                _RulerSliderRow(
                  label: 'Cân nặng mục tiêu',
                  valueText: '${_draft.targetWeightKg.toStringAsFixed(1)} kg',
                  value: _draft.targetWeightKg,
                  min: 35,
                  max: 180,
                  divisions: 290,
                  onChanged: (v) => _updateDraft(
                    _draft.copyWith(
                      targetWeightKg: (v * 2).round() / 2.0,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 10),
        Card(
          color: AppColors.tintedSurface(context, bmiColor),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Wrap(
              spacing: 10,
              runSpacing: 6,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  'BMI Châu Á: $bmi ($bmiLabel)',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: bmiColor,
                  ),
                ),
                Chip(
                  visualDensity: VisualDensity.compact,
                  label: Text(
                    'Định hướng: ${_draft.fitnessGoalLabelVi}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStep2BodyFatAndSomatotype(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Vóc dáng & Ước lượng Tỷ lệ Mỡ',
          style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Không cần đo máy — chỉ cần chọn dáng người gần giống bạn nhất.',
          style: TextStyle(
            fontSize: 13,
            color: AppColors.secondaryText(context),
          ),
        ),
        const SizedBox(height: 12),
        _buildAvatarPreviewCard(context, highlightPriorityMuscles: false),
        const SizedBox(height: 12),
        const Text(
          '1. Chọn tỷ lệ mỡ cơ thể ước lượng',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.32,
          children: BodyFatPreset.values.map((preset) {
            final selected = _draft.bodyFatPreset == preset;
            final pct = preset.estimatedPctForGender(_draft.gender);
            final useBulkAvatar = _draft.gender == 'MALE' &&
                preset == BodyFatPreset.athletic &&
                _draft.derivedFitnessGoal == 'BULK';
            return _SelectableOptionCard(
              selected: selected,
              icon: Icons.accessibility_new_rounded,
              title: preset.labelVi,
              subtitle:
                  '~${pct.round()}% (${preset.rangeLabelForGender(_draft.gender)})',
              onTap: () => _updateDraft(
                _draft.copyWith(
                  bodyFatPreset: preset,
                  estimatedBodyFatPct: pct,
                  preferredAvatarCode: _draft.gender == 'FEMALE'
                      ? 'FEMALE_FIT'
                      : (useBulkAvatar ? 'MALE_BULK' : 'MALE_FIT'),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 14),
        const Text(
          '2. Tạng người (Somatotype)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        ...Somatotype.values.map((soma) {
          final selected = _draft.somatotype == soma;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _SelectableOptionCard(
              selected: selected,
              icon: Icons.straighten_rounded,
              title: soma.labelVi,
              subtitle: soma.descriptionVi,
              onTap: () => _updateDraft(_draft.copyWith(somatotype: soma)),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStep3ExperienceAndLocation(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Kinh nghiệm & Địa điểm Tập luyện',
          style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Hệ thống sẽ tự lọc bài tập & điều chỉnh số hiệp phù hợp với dụng cụ bạn có.',
          style: TextStyle(
            fontSize: 13,
            color: AppColors.secondaryText(context),
          ),
        ),
        const SizedBox(height: 14),
        const Text(
          '1. Kinh nghiệm tập luyện',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        ...ExperienceLevel.values.map((exp) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _SelectableOptionCard(
              selected: _draft.experienceLevel == exp,
              icon: Icons.military_tech_outlined,
              title: exp.labelVi,
              subtitle: exp.descriptionVi,
              onTap: () => _updateDraft(_draft.copyWith(experienceLevel: exp)),
            ),
          );
        }),
        const SizedBox(height: 14),
        const Text(
          '2. Nơi bạn tập luyện chính',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        ...TrainingLocation.values.map((loc) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _SelectableOptionCard(
              selected: _draft.trainingLocation == loc,
              icon: loc == TrainingLocation.fullGym
                  ? Icons.fitness_center
                  : (loc == TrainingLocation.homeDumbbell
                      ? Icons.home_outlined
                      : Icons.self_improvement),
              title: loc.labelVi,
              subtitle: loc.descriptionVi,
              onTap: () => _updateDraft(
                _draft.copyWith(
                  trainingLocation: loc,
                  selectedProgram:
                      loc == TrainingLocation.bodyweightOnly &&
                              _draft.selectedProgram ==
                                  ProgramChoiceType.cbumPpl
                          ? ProgramChoiceType.homeShred
                          : _draft.selectedProgram,
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStep4ScheduleAndMuscles(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quỹ Thời gian & Nhóm cơ Ưu tiên',
          style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Chạm chọn nhóm cơ muốn tập trung — bó cơ 3D sẽ phát sáng ngay lập tức.',
          style: TextStyle(
            fontSize: 13,
            color: AppColors.secondaryText(context),
          ),
        ),
        const SizedBox(height: 10),
        _buildAvatarPreviewCard(context, highlightPriorityMuscles: true),
        const SizedBox(height: 12),
        const Text(
          '1. Số buổi / tuần & Các ngày tập',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [3, 4, 5, 6].map((cnt) {
            return ChoiceChip(
              label: Text('$cnt buổi/tuần'),
              selected: _draft.sessionsPerWeek == cnt,
              onSelected: (_) => _updateDraft(
                _draft.copyWith(
                  sessionsPerWeek: cnt,
                  weeklyDays: UserFitnessProfile.defaultDaysForSessions(cnt),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: _weekdayLabels.entries.map((entry) {
            final selected = _draft.weeklyDays.contains(entry.key);
            return FilterChip(
              label: Text(entry.value),
              selected: selected,
              visualDensity: VisualDensity.compact,
              onSelected: (on) {
                final next = List<int>.from(_draft.weeklyDays);
                if (on && !next.contains(entry.key)) {
                  next.add(entry.key);
                } else if (!on && next.length > 1) {
                  next.remove(entry.key);
                }
                next.sort();
                _updateDraft(
                  _draft.copyWith(
                    weeklyDays: next,
                    sessionsPerWeek: next.length,
                  ),
                );
              },
            );
          }).toList(),
        ),
        const SizedBox(height: 14),
        const Text(
          '2. Thời lượng mỗi buổi',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: const [
            (min: 30, label: '30 phút · Nhanh gọn'),
            (min: 55, label: '45–60 phút · Tiêu chuẩn'),
            (min: 80, label: '75–90 phút · Chuyên sâu'),
          ].map((opt) {
            return ChoiceChip(
              label: Text(opt.label),
              selected: _draft.sessionDurationMin == opt.min,
              onSelected: (_) =>
                  _updateDraft(_draft.copyWith(sessionDurationMin: opt.min)),
            );
          }).toList(),
        ),
        const SizedBox(height: 14),
        const Text(
          '3. Nhóm cơ muốn ưu tiên (chọn nhiều)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: PriorityMuscleGroup.values.map((group) {
            final selected = _draft.priorityMuscles.contains(group);
            return FilterChip(
              avatar: CircleAvatar(
                radius: 6,
                backgroundColor: selected
                    ? AppColors.musclePrimaryRed
                    : AppColors.muscleNeutralGrey,
              ),
              label: Text(group.labelVi),
              selected: selected,
              onSelected: (on) {
                final next =
                    List<PriorityMuscleGroup>.from(_draft.priorityMuscles);
                if (on && !next.contains(group)) {
                  next.add(group);
                } else if (!on && next.length > 1) {
                  next.remove(group);
                }
                _updateDraft(_draft.copyWith(priorityMuscles: next));
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildStep5ProgramChoice(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Chọn Phác đồ Tập luyện',
          style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Tự tạo giáo án cá nhân hóa hoặc theo khung chương trình VĐV nổi tiếng.',
          style: TextStyle(
            fontSize: 13,
            color: AppColors.secondaryText(context),
          ),
        ),
        const SizedBox(height: 12),
        _SelectableOptionCard(
          selected: _draft.selectedProgram == ProgramChoiceType.aiCustom,
          icon: Icons.auto_awesome,
          title: ProgramChoiceType.aiCustom.labelVi,
          subtitle: ProgramChoiceType.aiCustom.subtitleVi,
          onTap: () => _updateDraft(
            _draft.copyWith(selectedProgram: ProgramChoiceType.aiCustom),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Hoặc chọn Chương trình Vận động viên',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 8),
        ...SmartRoutineGenerator.proProgramsCatalog.map((item) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _SelectableOptionCard(
              selected: _draft.selectedProgram == item.type,
              icon: Icons.emoji_events_outlined,
              title: '${item.title} (${item.frequencyLabel})',
              subtitle: '${item.athleteTag} · ${item.focusSummary}',
              onTap: () =>
                  _updateDraft(_draft.copyWith(selectedProgram: item.type)),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStep6SummaryAndDisclaimer(BuildContext context) {
    final macros = _draft.macroTargets;
    final primaryColor = Theme.of(context).colorScheme.primary;
    final dayNames = _draft.weeklyDays
        .map((d) => _weekdayLabels[d] ?? 'T$d')
        .join(' · ');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Phác đồ Của Riêng Bạn Đã Sẵn Sàng!',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          'Chương trình: ${_draft.selectedProgram.labelVi} · ${_draft.trainingLocation.shortLabelVi}',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: primaryColor,
          ),
        ),
        const SizedBox(height: 12),
        Card(
          color: AppColors.tintedSurface(context, primaryColor),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: _AnimatedCounterTile(
                        label: 'Calo mục tiêu',
                        targetValue: _draft.targetCaloriesKcal.round(),
                        suffix: ' kcal',
                        color: AppColors.calorieOrange,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _AnimatedCounterTile(
                        label: 'Đạm / ngày',
                        targetValue: macros.proteinG.round(),
                        suffix: ' g',
                        color: AppColors.musclePrimaryRed,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: _AnimatedCounterTile(
                        label: 'Nước nền / ngày',
                        targetValue: _draft.baseWaterTargetMl,
                        suffix: ' ml',
                        color: AppColors.hydrationBlue,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _AnimatedCounterTile(
                        label: 'Ngày có tập',
                        targetValue: _draft.workoutDayWaterTargetMl,
                        suffix: ' ml',
                        color: AppColors.stepTeal,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  'Carb ${macros.carbsG.round()}g · Fat ${macros.fatG.round()}g · '
                  'BMR ${_draft.bmrKcal.round()} kcal · Lịch: $dayNames (${_draft.sessionDurationMin}p)',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.secondaryText(context),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Card(
          color: AppColors.tintedSurface(context, Colors.amber),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(
                      Icons.health_and_safety_outlined,
                      color: Colors.deepOrange,
                    ),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Miễn trừ Trách nhiệm Y tế',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  OnboardingDisclaimerScreen.medicalDisclaimerText,
                  style: TextStyle(fontSize: 12.5, height: 1.4),
                ),
                const SizedBox(height: 6),
                Text(
                  OnboardingDisclaimerScreen.formulaCitationText,
                  style: TextStyle(
                    fontSize: 11.5,
                    color: AppColors.secondaryText(context),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ),
        CheckboxListTile(
          value: _accepted,
          contentPadding: EdgeInsets.zero,
          controlAffinity: ListTileControlAffinity.leading,
          onChanged: (value) => setState(() => _accepted = value ?? false),
          title: const Text(
            'Tôi đã đọc, hiểu rõ và đồng ý với điều khoản Miễn trừ Trách nhiệm Y tế.',
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
          ),
        ),
      ],
    );
  }
}

class _SafeOnboarding3DStage extends StatelessWidget {
  final BodyAvatarPreset avatarPreset;
  final BodyMorphWeights bodyMorph;
  final String statusBadgeText;
  final Map<String, Color> muscleColorsMap;
  final List<String> highlightedGroupLabels;
  final bool showMuscleLegend;

  const _SafeOnboarding3DStage({
    required this.avatarPreset,
    required this.bodyMorph,
    required this.statusBadgeText,
    required this.muscleColorsMap,
    required this.highlightedGroupLabels,
    required this.showMuscleLegend,
  });

  static bool get _isWidgetTestEnv =>
      !kIsWeb && Platform.environment.containsKey('FLUTTER_TEST');

  @override
  Widget build(BuildContext context) {
    if (_isWidgetTestEnv) {
      return Container(
        height: 175,
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF12161F),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppColors.darkPrimary.withValues(alpha: 0.4),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.accessibility_new_rounded,
              size: 46,
              color: Colors.white,
            ),
            const SizedBox(height: 6),
            Text(
              'Mô hình 3D: ${avatarPreset.labelVi}',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 13.5,
              ),
              textAlign: TextAlign.center,
            ),
            if (showMuscleLegend && highlightedGroupLabels.isNotEmpty) ...[
              const SizedBox(height: 6),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                alignment: WrapAlignment.center,
                children: highlightedGroupLabels
                    .map(
                      (label) => Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: AppColors.musclePrimaryRed
                              .withValues(alpha: 0.25),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          label,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ),
            ],
          ],
        ),
      );
    }

    return Stack(
      children: [
        Muscle3DViewerWidget(
          glbAssetOrUrl: avatarPreset.masterMannequinAssetPath,
          muscleColorsMap: muscleColorsMap,
          avatarPreset: avatarPreset,
          bodyMorph: bodyMorph,
          isPlaying: false,
          height: 205,
        ),
        Positioned(
          top: 8,
          left: 8,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.65),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              statusBadgeText,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _SelectableOptionCard extends StatelessWidget {
  final bool selected;
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _SelectableOptionCard({
    required this.selected,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;
    return AnimatedScale(
      scale: selected ? 1.015 : 1.0,
      duration: const Duration(milliseconds: 180),
      curve: Curves.easeOutCubic,
      child: Card(
        color: selected
            ? AppColors.tintedSurface(context, primary, lightAlpha: 0.1, darkAlpha: 0.2)
            : null,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: selected ? primary : AppColors.subtleBorder(context),
            width: selected ? 1.6 : 1.0,
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  icon,
                  color: selected ? primary : AppColors.secondaryText(context),
                  size: 22,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        title,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13.5,
                          color: selected ? primary : null,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontSize: 11.5,
                          color: AppColors.secondaryText(context),
                        ),
                      ),
                    ],
                  ),
                ),
                if (selected)
                  Icon(Icons.check_circle, color: primary, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RulerSliderRow extends StatelessWidget {
  final String label;
  final String valueText;
  final double value;
  final double min;
  final double max;
  final int divisions;
  final ValueChanged<double> onChanged;

  const _RulerSliderRow({
    required this.label,
    required this.valueText,
    required this.value,
    required this.min,
    required this.max,
    required this.divisions,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                label,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
            Text(
              valueText,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: primary,
                fontSize: 15,
              ),
            ),
          ],
        ),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: divisions,
          onChanged: onChanged,
        ),
      ],
    );
  }
}

class _AnimatedCounterTile extends StatelessWidget {
  final String label;
  final int targetValue;
  final String suffix;
  final Color color;

  const _AnimatedCounterTile({
    required this.label,
    required this.targetValue,
    required this.suffix,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.subtleBorder(context)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 11.5,
              color: AppColors.secondaryText(context),
            ),
          ),
          const SizedBox(height: 4),
          TweenAnimationBuilder<int>(
            tween: IntTween(begin: 0, end: targetValue),
            duration: const Duration(milliseconds: 600),
            curve: Curves.easeOutCubic,
            builder: (_, val, __) => FittedBox(
              fit: BoxFit.scaleDown,
              alignment: Alignment.centerLeft,
              child: Text(
                '$val$suffix',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
