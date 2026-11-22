// [OWNER: M1] Man hinh Theo doi Luong nuoc Thong minh & Nhac lich WorkManager (T-M1-08 / F03)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/database/health_tables.drift.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';

class HydrationScreen extends ConsumerWidget {
  const HydrationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);
    final daily = state.dailyHealth;
    final weightKg = state.latestBiometric?.weightKg ?? 70.0;
    final baseWater = DailyHealthModel.calculateTargetWaterMl(weightKg);
    final currentWater = daily?.waterMl ?? 0;
    final targetWater = daily?.targetWaterMl ?? baseWater;
    final progress =
        targetWater > 0 ? (currentWater / targetWater).clamp(0.0, 1.0) : 0.0;
    final pct = (progress * 100).round();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lượng nước Thông minh'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  SizedBox(
                    width: 150,
                    height: 150,
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        CircularProgressIndicator(
                          value: progress,
                          strokeWidth: 14,
                          backgroundColor:
                              AppColors.hydrationBlue.withValues(alpha: 0.15),
                          color: AppColors.hydrationBlue,
                        ),
                        Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '$pct%',
                                style: const TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.hydrationBlue,
                                ),
                              ),
                              Text(
                                '$currentWater / $targetWater ml',
                                style: const TextStyle(fontSize: 13),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Nước nền: 35 ml × ${weightKg.toStringAsFixed(1)} kg = $baseWater ml',
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                  if (state.workoutBonusWaterMl > 0) ...[
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.hydrationBlue.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.fitness_center,
                            size: 18,
                            color: AppColors.hydrationBlue,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              state.workoutBonusReason ??
                                  'Đã cộng bù +${state.workoutBonusWaterMl} ml theo buổi tập hôm nay.',
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: AppColors.hydrationBlue,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Nut bam nhanh
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Ghi nhận nhanh lượng nước',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      OutlinedButton.icon(
                        onPressed: () => controller.addWaterMl(150),
                        icon: const Icon(Icons.water_drop_outlined, size: 18),
                        label: const Text('+150 ml'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () => controller.addWaterMl(250),
                        icon: const Icon(Icons.local_drink_outlined, size: 18),
                        label: const Text('+250 ml'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () => controller.addWaterMl(500),
                        icon: const Icon(Icons.sports_bar_outlined, size: 18),
                        label: const Text('+500 ml'),
                      ),
                      FilledButton.tonalIcon(
                        onPressed: () =>
                            _showCustomWaterDialog(context, controller),
                        icon: const Icon(Icons.tune, size: 18),
                        label: const Text('Tùy chỉnh'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Cap nhat bu nuoc theo cuong do tap trong ngay
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Bù nước theo Buổi tập Gym hôm nay',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Tự động cộng thêm khi bạn hoàn thành buổi tập, hoặc chọn nhanh mức vận động hôm nay:',
                    style: TextStyle(fontSize: 13, color: Colors.black54),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => controller.applyWorkoutHydrationBonus(
                            workoutMinutes: 40,
                            workoutRpe: 6.0,
                          ),
                          child: const Text('Tập vừa (+500ml)'),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => controller.applyWorkoutHydrationBonus(
                            workoutMinutes: 60,
                            workoutRpe: 8.0,
                          ),
                          child: const Text('Tập nặng (+750ml)'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Nhac nho bang WorkManager (chuan CH Play, khong dung SCHEDULE_EXACT_ALARM)
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Nhắc uống nước định kỳ'),
                  subtitle: const Text(
                    'Nhắc mỗi 2 tiếng trong khung giờ 07:00 – 21:30',
                  ),
                  value: state.hydrationReminderEnabled,
                  onChanged: controller.toggleHydrationReminder,
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                  child: SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () async {
                        await controller.sendSampleHydrationReminder();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Đã gửi thông báo nhắc uống nước thử nghiệm.',
                              ),
                            ),
                          );
                        }
                      },
                      icon: const Icon(Icons.notifications_active_outlined),
                      label: const Text('Gửi thử thông báo nhắc uống nước'),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showCustomWaterDialog(
    BuildContext context,
    HealthDashboardController controller,
  ) async {
    final textCtrl = TextEditingController(text: '300');
    final value = await showDialog<int>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('Nhập lượng nước (ml)'),
        content: TextField(
          controller: textCtrl,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Số ml muốn thêm',
            suffixText: 'ml',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogCtx).pop(),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () {
              final parsed = int.tryParse(textCtrl.text.trim());
              if (parsed != null && parsed > 0) {
                Navigator.of(dialogCtx).pop(parsed);
              }
            },
            child: const Text('Thêm'),
          ),
        ],
      ),
    );
    textCtrl.dispose();
    if (value != null && value > 0) {
      await controller.addWaterMl(value);
    }
  }
}
