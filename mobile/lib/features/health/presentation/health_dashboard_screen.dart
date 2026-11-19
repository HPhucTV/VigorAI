// [OWNER: M1] Dashboard Tong quan Suc khoe Offline-First (T-M1-05 / F01-F06 Preview)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/feature_flags.dart';
import '../../../core/database/health_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/theme/app_theme.dart';
import '../../auth_privacy/presentation/auth_controller.dart';
import '../data/health_repository.dart';

class HealthDashboardScreen extends ConsumerWidget {
  const HealthDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final healthState = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);

    final daily = healthState.dailyHealth;
    final latestBio = healthState.latestBiometric;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Xin chào, ${authState.user?.fullName ?? "Vận động viên"}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(
              ApiEndpoints.useMockApi
                  ? 'VigorAI · Mock Offline-First'
                  : 'VigorAI · Live API',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          if (healthState.pendingSyncCount > 0)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: ActionChip(
                avatar: const Icon(Icons.cloud_upload_outlined, size: 16),
                label: Text('Sync (${healthState.pendingSyncCount})'),
                onPressed: controller.markSynced,
              ),
            ),
          IconButton(
            tooltip: 'Đăng xuất',
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authControllerProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: controller.load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (healthState.errorMessage != null)
                    Card(
                      color: Colors.red.shade50,
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(healthState.errorMessage!),
                      ),
                    ),
                  // F01: Can nang & BMI WHO Asia-Pacific
                  if (latestBio != null)
                    Card(
                      child: ListTile(
                        leading: const CircleAvatar(
                          backgroundColor: Color(0xFFE3F2FD),
                          child: Icon(Icons.monitor_weight_outlined,
                              color: AppColors.primary),
                        ),
                        title: Text(
                          'Cân nặng: ${latestBio.weightKg} kg · BMI ${latestBio.bmi}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          'Phân loại Châu Á: ${BiometricLogModel.classifyAsianBmi(latestBio.bmi)} · '
                          'Body Fat: ${latestBio.bodyFatPct ?? "-"}%',
                        ),
                      ),
                    ),
                  const SizedBox(height: 10),
                  // F02 & F05: Buoc chan (Health Connect) & Giac ngu
                  if (daily != null)
                    Row(
                      children: [
                        Expanded(
                          child: Card(
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Row(
                                    children: [
                                      Icon(Icons.directions_walk,
                                          color: AppColors.stepTeal),
                                      SizedBox(width: 6),
                                      Text('Bước chân',
                                          style: TextStyle(
                                              fontWeight: FontWeight.w600)),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    '${daily.stepsCount} / ${daily.targetSteps}',
                                    style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold),
                                  ),
                                  Text('${daily.distanceKm} km · ${daily.activeCaloriesKcal} kcal'),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Card(
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Row(
                                    children: [
                                      Icon(Icons.bedtime_outlined,
                                          color: AppColors.sleepPurple),
                                      SizedBox(width: 6),
                                      Text('Giấc ngủ',
                                          style: TextStyle(
                                              fontWeight: FontWeight.w600)),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    '${daily.sleepHours} giờ',
                                    style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold),
                                  ),
                                  Text(daily.sleepHours >= 7.0
                                      ? 'Đạt chuẩn 7–9h'
                                      : 'Cần ngủ thêm'),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  const SizedBox(height: 10),
                  // F03: Luong nuoc thong minh
                  if (daily != null)
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Lượng nước thông minh (F03)',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Text('${daily.waterMl} / ${daily.targetWaterMl} ml'),
                              ],
                            ),
                            const SizedBox(height: 8),
                            LinearProgressIndicator(
                              value: daily.targetWaterMl > 0
                                  ? (daily.waterMl / daily.targetWaterMl)
                                      .clamp(0.0, 1.0)
                                  : 0.0,
                              color: AppColors.hydrationBlue,
                              minHeight: 8,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: [
                                OutlinedButton.icon(
                                  onPressed: () => controller.addWaterMl(250),
                                  icon: const Icon(Icons.water_drop_outlined,
                                      size: 18),
                                  label: const Text('+250 ml'),
                                ),
                                const SizedBox(width: 8),
                                OutlinedButton.icon(
                                  onPressed: () => controller.addWaterMl(500),
                                  icon: const Icon(Icons.local_drink_outlined,
                                      size: 18),
                                  label: const Text('+500 ml'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 10),
                  // F04: Calo & Macro (Mifflin-St Jeor)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Dinh dưỡng hôm nay (Mifflin-St Jeor)',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            '${healthState.totalCaloriesConsumed.round()} / '
                            '${healthState.targetCaloriesKcal.round()} kcal',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: AppColors.calorieOrange,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Đạm: ${healthState.totalProteinConsumed.toStringAsFixed(1)}g · '
                            'Carb: ${healthState.totalCarbsConsumed.toStringAsFixed(1)}g · '
                            'Fat: ${healthState.totalFatConsumed.toStringAsFixed(1)}g',
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  // F06: Supplement Reminder Checklist
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Thực phẩm bổ sung hôm nay (F06)',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 6),
                          ...healthState.supplements.map(
                            (s) => ListTile(
                              dense: true,
                              contentPadding: EdgeInsets.zero,
                              leading: Icon(
                                s.takenToday
                                    ? Icons.check_circle
                                    : Icons.radio_button_unchecked,
                                color: s.takenToday ? Colors.green : Colors.grey,
                              ),
                              title: Text('${s.supplementName} (${s.dosageLabel})'),
                              trailing: Text(s.reminderTimeHhMm),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  // An cac nut tro sang man hinh stub o ban MVP Closed Testing v1.0.0+1
                  if (!FeatureFlags.isMvpClosedTesting) ...[
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: () => context.push('/workout/live'),
                            icon: const Icon(Icons.fitness_center),
                            label: const Text('Tập Gym 3D (M2)'),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: FilledButton.tonalIcon(
                            onPressed: () => context.push('/ai-coach'),
                            icon: const Icon(Icons.auto_awesome),
                            label: const Text('AI Coach (M4)'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                  ],
                  // T-M1-06 (F26): Nut Xoa tai khoan & toan bo du lieu bat buoc CH Play
                  Card(
                    color: Colors.red.shade50,
                    child: ListTile(
                      leading: const Icon(Icons.delete_forever_outlined,
                          color: AppColors.warningRed),
                      title: const Text(
                        'Quyền riêng tư & Xóa Tài khoản (F26)',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: const Text(
                        'Xóa vĩnh viễn tài khoản, hồ sơ sức khỏe, SQLite và ảnh cục bộ.',
                      ),
                      trailing: TextButton(
                        onPressed: authState.isLoading
                            ? null
                            : () => _confirmDeleteAccount(context, ref),
                        style: TextButton.styleFrom(
                          foregroundColor: AppColors.warningRed,
                        ),
                        child: const Text('Xóa'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Future<void> _confirmDeleteAccount(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('Xóa vĩnh viễn tài khoản?'),
        content: const Text(
          'Hành động này sẽ xóa toàn bộ dữ liệu trên máy chủ VigorAI, '
          'CSDL SQLite cục bộ và ảnh tiến độ riêng tư. Không thể khôi phục sau khi xóa.',
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
    );

    if (confirmed != true) return;
    final deleted =
        await ref.read(authControllerProvider.notifier).deleteAccount();
    if (!context.mounted) return;
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
}
