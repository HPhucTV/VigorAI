// [OWNER: M1] Man hinh Ho so Ca nhan (/profile): Chinh sua Chi so, Giao dien Sang/Toi, Dong bo & Xoa tai khoan
import 'package:flutter/material.dart';
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
import 'onboarding_disclaimer_screen.dart';

class ProfileSettingsScreen extends ConsumerStatefulWidget {
  const ProfileSettingsScreen({super.key});

  @override
  ConsumerState<ProfileSettingsScreen> createState() =>
      _ProfileSettingsScreenState();
}

class _ProfileSettingsScreenState extends ConsumerState<ProfileSettingsScreen> {
  static const Map<int, String> _weekdayLabels = {
    1: 'T2',
    2: 'T3',
    3: 'T4',
    4: 'T5',
    5: 'T6',
    6: 'T7',
    7: 'CN',
  };

  late TextEditingController _nameCtrl;
  late TextEditingController _ageCtrl;
  late TextEditingController _heightCtrl;
  late TextEditingController _weightCtrl;
  late TextEditingController _targetWeightCtrl;
  late TextEditingController _bodyFatCtrl;

  late String _gender;
  late Somatotype _somatotype;
  late ExperienceLevel _experience;
  late TrainingLocation _location;
  late int _durationMin;
  late List<int> _weeklyDays;
  late List<PriorityMuscleGroup> _priorityMuscles;
  late ProgramChoiceType _selectedProgram;
  late BodyAvatarPreset _avatarPreset;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    final fp = ref.read(userFitnessProfileProvider);
    final authUser = ref.read(authControllerProvider).user;
    final healthState = ref.read(healthDashboardProvider);
    final latestWeight = healthState.latestBiometric?.weightKg ?? fp.currentWeightKg;

    _nameCtrl = TextEditingController(
      text: authUser?.fullName ?? fp.fullName,
    );
    _gender = authUser?.gender ?? fp.gender;
    _ageCtrl = TextEditingController(
      text: (fp.hasCompletedWizard
              ? fp.ageYears
              : (authUser?.calculateAgeYears() ?? fp.ageYears))
          .toString(),
    );
    _heightCtrl = TextEditingController(
      text: (fp.hasCompletedWizard
              ? fp.heightCm
              : (authUser?.heightCm ?? fp.heightCm))
          .round()
          .toString(),
    );
    _weightCtrl = TextEditingController(text: latestWeight.toStringAsFixed(1));
    _targetWeightCtrl =
        TextEditingController(text: fp.targetWeightKg.toStringAsFixed(1));
    _bodyFatCtrl = TextEditingController(
      text: (healthState.latestBiometric?.bodyFatPct ?? fp.estimatedBodyFatPct)
          .toStringAsFixed(1),
    );

    _somatotype = fp.somatotype;
    _experience = fp.experienceLevel;
    _location = fp.trainingLocation;
    _durationMin = fp.sessionDurationMin;
    _weeklyDays = List<int>.from(fp.weeklyDays);
    _priorityMuscles = List<PriorityMuscleGroup>.from(fp.priorityMuscles);
    _selectedProgram = fp.selectedProgram;
    _avatarPreset = ref.read(bodyAvatarPresetProvider);
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    _targetWeightCtrl.dispose();
    _bodyFatCtrl.dispose();
    super.dispose();
  }

  UserFitnessProfile _buildEditedProfile() {
    final prev = ref.read(userFitnessProfileProvider);
    final age = (int.tryParse(_ageCtrl.text.trim()) ?? prev.ageYears).clamp(16, 75);
    final height =
        (double.tryParse(_heightCtrl.text.trim()) ?? prev.heightCm).clamp(140.0, 210.0);
    final weight =
        (double.tryParse(_weightCtrl.text.trim()) ?? prev.currentWeightKg).clamp(35.0, 180.0);
    final targetWeight =
        (double.tryParse(_targetWeightCtrl.text.trim()) ?? prev.targetWeightKg)
            .clamp(35.0, 180.0);
    final bodyFat =
        (double.tryParse(_bodyFatCtrl.text.trim()) ?? prev.estimatedBodyFatPct)
            .clamp(5.0, 50.0);
    final sortedDays = (List<int>.from(_weeklyDays)..sort());

    return prev.copyWith(
      fullName: _nameCtrl.text.trim().isEmpty
          ? prev.fullName
          : _nameCtrl.text.trim(),
      gender: _gender,
      ageYears: age,
      heightCm: height,
      currentWeightKg: weight,
      targetWeightKg: targetWeight,
      estimatedBodyFatPct: bodyFat,
      somatotype: _somatotype,
      experienceLevel: _experience,
      trainingLocation: _location,
      sessionsPerWeek: sortedDays.length.clamp(1, 7),
      weeklyDays: sortedDays.isEmpty ? const [1, 3, 5] : sortedDays,
      sessionDurationMin: _durationMin,
      priorityMuscles: _priorityMuscles,
      selectedProgram: _selectedProgram,
      preferredAvatarCode: _avatarPreset.code,
      hasCompletedWizard: true,
    );
  }

  Future<void> _saveAndRecalculate() async {
    if (_isSaving) return;
    setState(() => _isSaving = true);
    try {
      final next = _buildEditedProfile();
      await ref.read(userFitnessProfileProvider.notifier).saveProfile(next);
      ref.read(bodyAvatarPresetProvider.notifier).state = _avatarPreset;

      final authUser = ref.read(authControllerProvider).user;
      if (authUser != null) {
        await ref.read(authControllerProvider.notifier).updateLocalProfile(
              AuthUserProfile(
                id: authUser.id,
                email: authUser.email,
                fullName: next.fullName,
                gender: next.gender,
                birthDateIso: next.birthDateIso,
                heightCm: next.heightCm,
                activityLevel: next.derivedActivityLevel,
                fitnessGoal: next.derivedFitnessGoal,
                medicalDisclaimerAccepted: true,
              ),
            );
      }

      try {
        await ref.read(healthRepositoryProvider).saveBiometric(
              weightKg: next.currentWeightKg,
              heightCm: next.heightCm,
              bodyFatPct: next.estimatedBodyFatPct,
            );
        await ref.read(healthDashboardProvider.notifier).load();
      } catch (_) {}

      if (!mounted) return;
      final regenerate = await showDialog<bool>(
        context: context,
        builder: (dialogCtx) => VigorAdaptiveTheme(
          child: AlertDialog(
            title: const Text('Đã cập nhật Phác đồ mới'),
            content: Text(
              'BMI: ${next.bmi} (${next.bmiLabel}) · '
              'Mục tiêu: ${next.targetCaloriesKcal.round()} kcal/ngày · '
              'Nước: ${next.baseWaterTargetMl} ml.\n\n'
              'Bạn có muốn tạo lại Lịch tập tuần theo thông số mới không?',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(dialogCtx).pop(false),
                child: const Text('Giữ lịch cũ'),
              ),
              FilledButton(
                onPressed: () => Navigator.of(dialogCtx).pop(true),
                child: const Text('Tạo lại Lịch tập'),
              ),
            ],
          ),
        ),
      );

      if (regenerate == true) {
        final exercises = await ref.read(exercisesListProvider.future);
        final generated = SmartRoutineGenerator.generatePlan(
          profile: next,
          allExercises: exercises,
        );
        await ref.read(workoutRepositoryProvider).applyGeneratedPlan(generated);
        ref.invalidate(workoutRoutinesProvider);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Đã cập nhật chỉ số và tạo lại ${generated.length} buổi tập tuần.',
            ),
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Đã lưu hồ sơ và tính lại Calo/Macro/Nước.'),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  Future<void> _showMedicalDisclaimerModal() async {
    await showDialog<void>(
      context: context,
      builder: (dialogCtx) => VigorAdaptiveTheme(
        child: AlertDialog(
          title: const Text('Miễn trừ Trách nhiệm Y tế'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  OnboardingDisclaimerScreen.medicalDisclaimerText,
                  style: TextStyle(fontSize: 13, height: 1.4),
                ),
                const SizedBox(height: 10),
                Text(
                  OnboardingDisclaimerScreen.formulaCitationText,
                  style: TextStyle(
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                    color: AppColors.secondaryText(dialogCtx),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            FilledButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: const Text('Đã hiểu'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _confirmDeleteAccount() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogCtx) => VigorAdaptiveTheme(
        child: AlertDialog(
          title: const Text('Xóa vĩnh viễn tài khoản?'),
          content: const Text(
            'Hành động này sẽ xóa toàn bộ dữ liệu trên máy chủ VigorAI '
            'và trên thiết bị này. Không thể khôi phục sau khi xóa.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(false),
              child: const Text('Hủy'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.warningRed,
              ),
              onPressed: () => Navigator.of(dialogCtx).pop(true),
              child: const Text('Xác nhận Xóa'),
            ),
          ],
        ),
      ),
    );

    if (confirmed != true) return;
    final deleted =
        await ref.read(authControllerProvider.notifier).deleteAccount();
    await ref.read(userFitnessProfileProvider.notifier).clearProfile();
    if (!mounted) return;
    if (deleted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Tài khoản và toàn bộ dữ liệu đã được xóa vĩnh viễn.'),
        ),
      );
      context.go('/onboarding');
    } else {
      final err = ref.read(authControllerProvider).errorMessage;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(err ?? 'Xóa tài khoản thất bại.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final healthState = ref.watch(healthDashboardProvider);
    final themePref = ref.watch(themePreferenceProvider);
    final preview = _buildEditedProfile();
    final primaryColor = Theme.of(context).colorScheme.primary;
    final initials = (_nameCtrl.text.trim().isNotEmpty
            ? _nameCtrl.text.trim()[0]
            : 'V')
        .toUpperCase();

    return Scaffold(
      appBar: AppBar(title: const Text('Hồ sơ & Cài đặt')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Header Card: Avatar + Giao dien Sang/Toi
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 26,
                        backgroundColor:
                            AppColors.tintedSurface(context, primaryColor),
                        child: Text(
                          initials,
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: primaryColor,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _nameCtrl.text.trim().isEmpty
                                  ? 'Vận động viên VigorAI'
                                  : _nameCtrl.text.trim(),
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            Text(
                              authState.user?.email ?? 'Tài khoản cá nhân',
                              style: TextStyle(
                                fontSize: 12.5,
                                color: AppColors.secondaryText(context),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Giao diện hiển thị',
                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  const SizedBox(height: 6),
                  SegmentedButton<AppThemePreference>(
                    segments: AppThemePreference.values
                        .map(
                          (pref) => ButtonSegment<AppThemePreference>(
                            value: pref,
                            label: Text(
                              pref.labelVi,
                              style: const TextStyle(fontSize: 12),
                            ),
                          ),
                        )
                        .toList(),
                    selected: {themePref},
                    onSelectionChanged: (sel) {
                      ref
                          .read(themePreferenceProvider.notifier)
                          .setPreference(sel.first);
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // Nhom 1: Chi so Co the & Voc dang
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Chỉ số Cơ thể & Vóc dáng',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _nameCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Họ và tên',
                      isDense: true,
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          initialValue: _gender,
                          decoration: const InputDecoration(
                            labelText: 'Giới tính',
                            isDense: true,
                          ),
                          items: const [
                            DropdownMenuItem(value: 'MALE', child: Text('Nam')),
                            DropdownMenuItem(
                                value: 'FEMALE', child: Text('Nữ')),
                          ],
                          onChanged: (v) {
                            if (v == null) return;
                            setState(() {
                              _gender = v;
                              final wantFemale = v == 'FEMALE';
                              if (_avatarPreset.isFemale != wantFemale) {
                                _avatarPreset = wantFemale
                                    ? BodyAvatarPreset.femaleFit
                                    : BodyAvatarPreset.maleFit;
                              }
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _ageCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Tuổi',
                            isDense: true,
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _heightCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Chiều cao (cm)',
                            isDense: true,
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _weightCtrl,
                          keyboardType: const TextInputType.numberWithOptions(
                              decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Cân nặng (kg)',
                            isDense: true,
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _targetWeightCtrl,
                          keyboardType: const TextInputType.numberWithOptions(
                              decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Mục tiêu (kg)',
                            isDense: true,
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _bodyFatCtrl,
                          keyboardType: const TextInputType.numberWithOptions(
                              decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Tỷ lệ mỡ (%)',
                            isDense: true,
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  DropdownButtonFormField<Somatotype>(
                    initialValue: _somatotype,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'Tạng người',
                      isDense: true,
                    ),
                    items: Somatotype.values
                        .map(
                          (s) => DropdownMenuItem(
                            value: s,
                            child: Text(
                              s.labelVi,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _somatotype = v);
                    },
                  ),
                  const SizedBox(height: 10),
                  DropdownButtonFormField<BodyAvatarPreset>(
                    initialValue: _avatarPreset,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'Avatar 3D mặc định',
                      isDense: true,
                    ),
                    items: BodyAvatarPreset.values
                        .map(
                          (p) => DropdownMenuItem(
                            value: p,
                            child: Text(
                              p.labelVi,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _avatarPreset = v);
                    },
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppColors.tintedSurface(context, primaryColor),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      'Xem trước phác đồ (${preview.fitnessGoalLabelVi}): BMI ${preview.bmi} (${preview.bmiLabel}) · '
                      '${preview.targetCaloriesKcal.round()} kcal/ngày · '
                      'Đạm ${preview.macroTargets.proteinG.round()}g · Nước ${preview.baseWaterTargetMl} ml',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // Nhom 2: Cau hinh Tap luyen & Muc tieu
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        const Text(
                          'Cấu hình Tập luyện',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                        TextButton.icon(
                          style: TextButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            visualDensity: VisualDensity.compact,
                          ),
                          onPressed: () =>
                              context.push('/onboarding?mode=reconfigure'),
                          icon: const Icon(Icons.auto_fix_high, size: 17),
                          label: const Text('Làm lại Khảo sát'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<ExperienceLevel>(
                    initialValue: _experience,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'Trình độ tập luyện',
                      isDense: true,
                    ),
                    items: ExperienceLevel.values
                        .map(
                          (e) => DropdownMenuItem(
                            value: e,
                            child: Text(
                              e.labelVi,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _experience = v);
                    },
                  ),
                  const SizedBox(height: 10),
                  DropdownButtonFormField<TrainingLocation>(
                    initialValue: _location,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'Địa điểm & Dụng cụ',
                      isDense: true,
                    ),
                    items: TrainingLocation.values
                        .map(
                          (l) => DropdownMenuItem(
                            value: l,
                            child: Text(
                              l.labelVi,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _location = v);
                    },
                  ),
                  const SizedBox(height: 10),
                  DropdownButtonFormField<ProgramChoiceType>(
                    initialValue: _selectedProgram,
                    isExpanded: true,
                    decoration: const InputDecoration(
                      labelText: 'Chương trình tập',
                      isDense: true,
                    ),
                    items: ProgramChoiceType.values
                        .map(
                          (p) => DropdownMenuItem(
                            value: p,
                            child: Text(
                              p.labelVi,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: (v) {
                      if (v != null) setState(() => _selectedProgram = v);
                    },
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Thời lượng mỗi buổi',
                    style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    children: const [
                      (min: 30, label: '30 phút'),
                      (min: 55, label: '45–60 phút'),
                      (min: 80, label: '75–90 phút'),
                    ].map((opt) {
                      return ChoiceChip(
                        label: Text(opt.label),
                        selected: _durationMin == opt.min,
                        visualDensity: VisualDensity.compact,
                        onSelected: (_) =>
                            setState(() => _durationMin = opt.min),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Ngày tập trong tuần',
                    style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    children: _weekdayLabels.entries.map((entry) {
                      final selected = _weeklyDays.contains(entry.key);
                      return FilterChip(
                        label: Text(entry.value),
                        selected: selected,
                        visualDensity: VisualDensity.compact,
                        onSelected: (on) {
                          setState(() {
                            if (on && !_weeklyDays.contains(entry.key)) {
                              _weeklyDays.add(entry.key);
                            } else if (!on && _weeklyDays.length > 1) {
                              _weeklyDays.remove(entry.key);
                            }
                            _weeklyDays.sort();
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Nhóm cơ ưu tiên',
                    style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: PriorityMuscleGroup.values.map((group) {
                      final selected = _priorityMuscles.contains(group);
                      return FilterChip(
                        label: Text(group.labelVi),
                        selected: selected,
                        visualDensity: VisualDensity.compact,
                        onSelected: (on) {
                          setState(() {
                            if (on && !_priorityMuscles.contains(group)) {
                              _priorityMuscles.add(group);
                            } else if (!on && _priorityMuscles.length > 1) {
                              _priorityMuscles.remove(group);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          FilledButton.icon(
            onPressed: _isSaving ? null : _saveAndRecalculate,
            icon: _isSaving
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.save_outlined),
            label: const Text('Lưu thay đổi & Tính lại Phác đồ'),
          ),
          const SizedBox(height: 14),

          // Nhom 3: Dong bo, Phap ly & Tai khoan
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: Icon(
                    Icons.cloud_sync_outlined,
                    color: primaryColor,
                  ),
                  title: const Text('Đồng bộ dữ liệu ngay'),
                  subtitle: Text(
                    healthState.pendingSyncCount > 0
                        ? '${healthState.pendingSyncCount} thay đổi đang chờ đồng bộ'
                        : 'Dữ liệu đã đồng bộ mới nhất',
                  ),
                  onTap: healthState.isSyncing
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
                          ScaffoldMessenger.of(context)
                              .showSnackBar(SnackBar(content: Text(msg)));
                        },
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.health_and_safety_outlined),
                  title: const Text('Xem lại Miễn trừ Trách nhiệm Y tế'),
                  onTap: _showMedicalDisclaimerModal,
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.logout),
                  title: const Text('Đăng xuất'),
                  onTap: () async {
                    await ref.read(authControllerProvider.notifier).logout();
                    if (context.mounted) context.go('/login');
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),

          Card(
            color: AppColors.tintedSurface(context, AppColors.warningRed),
            child: ListTile(
              leading: const Icon(
                Icons.delete_forever_outlined,
                color: AppColors.warningRed,
              ),
              title: const Text(
                'Xóa tài khoản',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: const Text(
                'Xóa vĩnh viễn tài khoản, hồ sơ sức khỏe và dữ liệu trên thiết bị.',
              ),
              trailing: TextButton(
                onPressed: authState.isLoading ? null : _confirmDeleteAccount,
                style: TextButton.styleFrom(
                  foregroundColor: AppColors.warningRed,
                ),
                child: const Text('Xóa'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
