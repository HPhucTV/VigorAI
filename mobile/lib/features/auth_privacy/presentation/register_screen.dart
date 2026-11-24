// [OWNER: M1] Man hinh Dang ky tai khoan VigorAI tu dong nap thong so tu Onboarding Wizard 6 buoc (T-M1-04 / F26)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../health/data/health_repository.dart';
import '../../workout/data/workout_repository.dart';
import '../../workout/domain/smart_routine_generator.dart';
import '../data/user_fitness_profile.dart';
import 'auth_controller.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _heightController = TextEditingController(text: '172');

  String _gender = 'MALE';
  String _fitnessGoal = 'BULK';
  bool _prefilledFromWizard = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_prefilledFromWizard) {
      _prefilledFromWizard = true;
      final profile = ref.read(userFitnessProfileProvider);
      if (profile.hasCompletedWizard) {
        _gender = profile.gender;
        _fitnessGoal = profile.derivedFitnessGoal;
        _heightController.text = profile.heightCm.round().toString();
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _heightController.dispose();
    super.dispose();
  }

  Future<void> _submitRegister() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final profile = ref.read(userFitnessProfileProvider);
    final heightCm = double.tryParse(_heightController.text) ?? profile.heightCm;
    final updatedProfile = profile.copyWith(
      fullName: _nameController.text.trim(),
      gender: _gender,
      heightCm: heightCm.clamp(140.0, 210.0),
      hasCompletedWizard: true,
    );
    await ref
        .read(userFitnessProfileProvider.notifier)
        .saveProfile(updatedProfile);

    final success = await ref.read(authControllerProvider.notifier).register(
          email: _emailController.text,
          password: _passwordController.text,
          fullName: _nameController.text,
          gender: _gender,
          heightCm: heightCm,
          fitnessGoal: _fitnessGoal,
          birthDateIso: updatedProfile.birthDateIso,
          activityLevel: updatedProfile.derivedActivityLevel,
        );
    if (!success) return;

    // Ghi ban ghi sinh trac dau tien + dam bao giao an ca nhan da co trong may
    try {
      await ref.read(healthRepositoryProvider).saveBiometric(
            weightKg: updatedProfile.currentWeightKg,
            heightCm: updatedProfile.heightCm,
            bodyFatPct: updatedProfile.estimatedBodyFatPct,
          );
      final exercises = await ref.read(exercisesListProvider.future);
      final generated = SmartRoutineGenerator.generatePlan(
        profile: updatedProfile,
        allExercises: exercises,
      );
      await ref.read(workoutRepositoryProvider).applyGeneratedPlan(generated);
      ref.invalidate(workoutRoutinesProvider);
      await ref.read(healthDashboardProvider.notifier).load();
    } catch (_) {}

    if (mounted) {
      context.go('/health');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final wizardProfile = ref.watch(userFitnessProfileProvider);
    final primaryColor = Theme.of(context).colorScheme.primary;

    return Scaffold(
      appBar: AppBar(title: const Text('Tạo tài khoản VigorAI')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (wizardProfile.hasCompletedWizard) ...[
                  Card(
                    color: AppColors.tintedSurface(context, primaryColor),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Icon(Icons.auto_awesome, color: primaryColor),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Đã đồng bộ phác đồ: ${wizardProfile.targetCaloriesKcal.round()} kcal/ngày · '
                              '${wizardProfile.selectedProgram.shortLabelVi} (${wizardProfile.sessionsPerWeek} buổi/tuần).',
                              style: const TextStyle(fontSize: 12.5),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Họ và tên',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Nhập họ tên' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  validator: (v) => (v == null || !v.contains('@'))
                      ? 'Email không hợp lệ'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Mật khẩu (tối thiểu 8 ký tự)',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                  validator: (v) => (v == null || v.length < 8)
                      ? 'Mật khẩu tối thiểu 8 ký tự'
                      : null,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _gender,
                        decoration: const InputDecoration(labelText: 'Giới tính'),
                        items: const [
                          DropdownMenuItem(value: 'MALE', child: Text('Nam')),
                          DropdownMenuItem(value: 'FEMALE', child: Text('Nữ')),
                        ],
                        onChanged: (v) => setState(() => _gender = v ?? 'MALE'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _heightController,
                        keyboardType: TextInputType.number,
                        decoration:
                            const InputDecoration(labelText: 'Chiều cao (cm)'),
                        validator: (v) {
                          final h = double.tryParse(v ?? '');
                          if (h == null || h < 100 || h > 240) {
                            return '100 - 240 cm';
                          }
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _fitnessGoal,
                  decoration:
                      const InputDecoration(labelText: 'Mục tiêu luyện tập'),
                  items: const [
                    DropdownMenuItem(value: 'BULK', child: Text('Tăng cơ')),
                    DropdownMenuItem(value: 'CUT', child: Text('Giảm mỡ')),
                    DropdownMenuItem(
                        value: 'MAINTAIN', child: Text('Giữ dáng')),
                  ],
                  onChanged: (v) => setState(() => _fitnessGoal = v ?? 'BULK'),
                ),
                const SizedBox(height: 14),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(
                    authState.disclaimerAccepted
                        ? Icons.check_circle
                        : Icons.cancel,
                    color: authState.disclaimerAccepted
                        ? Colors.green
                        : Colors.red,
                  ),
                  title: Text(
                    authState.disclaimerAccepted
                        ? 'Đã chấp thuận Miễn trừ Trách nhiệm Y tế'
                        : 'Bạn cần đồng ý Miễn trừ Y tế trước khi đăng ký',
                    style: const TextStyle(fontSize: 13),
                  ),
                  trailing: authState.disclaimerAccepted
                      ? null
                      : TextButton(
                          onPressed: () => context.go('/onboarding'),
                          child: const Text('Xem điều khoản'),
                        ),
                ),
                if (authState.errorMessage != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    authState.errorMessage!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ],
                const SizedBox(height: 16),
                FilledButton(
                  onPressed:
                      (authState.isLoading || !authState.disclaimerAccepted)
                          ? null
                          : _submitRegister,
                  child: const Text('Đăng ký & Bắt đầu'),
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: () => context.go('/login'),
                  child: const Text('Đã có tài khoản? Quay lại Đăng nhập'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
