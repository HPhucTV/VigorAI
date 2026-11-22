// [OWNER: M1] Man hinh Nhac lich Thuc pham Bo sung WorkManager + Nut "Da uong" (T-M1-09 / F06)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';

class SupplementsScreen extends ConsumerWidget {
  const SupplementsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Thực phẩm Bổ sung'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openAddSupplementSheet(context, controller),
        icon: const Icon(Icons.add_alarm),
        label: const Text('Thêm lịch'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 88),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const CircleAvatar(
                    radius: 26,
                    backgroundColor: Color(0xFFE8F5E9),
                    child: Icon(
                      Icons.medication_outlined,
                      color: AppColors.muscleRecoveredGreen,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Tuân thủ 7 ngày qua: ${state.weeklySupplementAdherencePct.toStringAsFixed(1)}%',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Bấm "Đã uống" ngay trong ứng dụng hoặc trên thanh thông báo.',
                          style: TextStyle(fontSize: 13, color: Colors.black54),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          Card(
            child: SwitchListTile(
              title: const Text('Nhắc lịch uống định kỳ'),
              subtitle: const Text(
                'Gửi thông báo nhắc nhở theo lịch bạn đã cài đặt.',
              ),
              value: state.supplementReminderEnabled,
              onChanged: controller.toggleSupplementReminders,
            ),
          ),
          const SizedBox(height: 10),

          if (state.supplements.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(20),
                child: Center(
                  child: Text('Chưa có lịch thực phẩm bổ sung nào.'),
                ),
              ),
            )
          else
            ...state.supplements.map(
              (item) => Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  child: Column(
                    children: [
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: IconButton(
                          icon: Icon(
                            item.takenToday
                                ? Icons.check_circle
                                : Icons.radio_button_unchecked,
                            color: item.takenToday
                                ? AppColors.muscleRecoveredGreen
                                : Colors.grey,
                          ),
                          onPressed: () =>
                              controller.toggleSupplementTakenToday(item.id),
                        ),
                        title: Text(
                          item.supplementName,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            decoration: item.takenToday
                                ? TextDecoration.lineThrough
                                : null,
                          ),
                        ),
                        subtitle: Text(
                          '${item.dosageLabel} · Nhắc lúc ${item.reminderTimeHhMm}'
                          '${item.workoutDaysOnly ? " (Chỉ ngày tập)" : ""}',
                        ),
                        trailing: IconButton(
                          tooltip: 'Xóa lịch',
                          icon: const Icon(Icons.delete_outline),
                          onPressed: () => controller.deleteSupplement(item.id),
                        ),
                      ),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () =>
                                  controller.toggleSupplementTakenToday(item.id),
                              icon: Icon(
                                item.takenToday ? Icons.undo : Icons.check,
                                size: 18,
                              ),
                              label: Text(
                                item.takenToday ? 'Bỏ đánh dấu' : 'Đã uống',
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextButton.icon(
                              onPressed: () async {
                                await controller
                                    .sendSampleSupplementReminder(item);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        'Đã đẩy thông báo "${item.supplementName}" kèm nút "Đã uống".',
                                      ),
                                    ),
                                  );
                                }
                              },
                              icon: const Icon(
                                Icons.notifications_outlined,
                                size: 18,
                              ),
                              label: const Text('Thử thông báo'),
                            ),
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

  Future<void> _openAddSupplementSheet(
    BuildContext context,
    HealthDashboardController controller,
  ) async {
    final nameCtrl = TextEditingController(text: 'Whey Protein Isolate');
    final dosageCtrl = TextEditingController(text: '1 muỗng (30g)');
    var selectedTime = const TimeOfDay(hour: 17, minute: 30);
    var workoutDaysOnly = false;

    final saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (sheetCtx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: EdgeInsets.fromLTRB(
            16,
            16,
            16,
            MediaQuery.of(ctx).viewInsets.bottom + 16,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Thêm lịch Thực phẩm bổ sung',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Wrap(
                spacing: 6,
                children: const [
                  ('Whey Protein Isolate', '1 muỗng (30g)'),
                  ('Creatine Monohydrate', '5g / ngày'),
                  ('Pre-Workout', '1 muỗng trước tập'),
                  ('Omega-3 Fish Oil', '2 viên sau ăn'),
                ].map((preset) {
                  return ActionChip(
                    label: Text(preset.$1),
                    onPressed: () {
                      nameCtrl.text = preset.$1;
                      dosageCtrl.text = preset.$2;
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: nameCtrl,
                decoration: const InputDecoration(labelText: 'Tên thực phẩm *'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: dosageCtrl,
                decoration: const InputDecoration(labelText: 'Liều lượng *'),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () async {
                        final picked = await showTimePicker(
                          context: ctx,
                          initialTime: selectedTime,
                        );
                        if (picked != null) {
                          setModalState(() => selectedTime = picked);
                        }
                      },
                      icon: const Icon(Icons.access_time),
                      label: Text(
                        'Giờ nhắc: ${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}',
                      ),
                    ),
                  ),
                ],
              ),
              CheckboxListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Chỉ nhắc vào ngày có lịch tập'),
                value: workoutDaysOnly,
                onChanged: (v) =>
                    setModalState(() => workoutDaysOnly = v ?? false),
              ),
              const SizedBox(height: 10),
              FilledButton(
                onPressed: () => Navigator.of(ctx).pop(true),
                child: const Text('Lưu lịch nhắc'),
              ),
            ],
          ),
        ),
      ),
    );

    if (saved == true && nameCtrl.text.trim().isNotEmpty) {
      final hhMm =
          '${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}';
      await controller.addSupplement(
        name: nameCtrl.text.trim(),
        dosageLabel: dosageCtrl.text.trim().isEmpty
            ? '1 liều'
            : dosageCtrl.text.trim(),
        reminderTimeHhMm: hhMm,
        workoutDaysOnly: workoutDaysOnly,
      );
    }

    nameCtrl.dispose();
    dosageCtrl.dispose();
  }
}
