// [OWNER: M1] Man hinh Theo doi Giac ngu 7 ngay (T-M1-09 / F05)
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/feature_flags.dart';
import '../../../../core/database/health_tables.drift.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';

class SleepScreen extends ConsumerStatefulWidget {
  const SleepScreen({super.key});

  @override
  ConsumerState<SleepScreen> createState() => _SleepScreenState();
}

class _SleepScreenState extends ConsumerState<SleepScreen> {
  TimeOfDay _bedTime = const TimeOfDay(hour: 23, minute: 0);
  TimeOfDay _wakeTime = const TimeOfDay(hour: 6, minute: 30);
  int _qualityStars = 4;

  double _computeDurationHours() {
    final bedMin = _bedTime.hour * 60 + _bedTime.minute;
    var wakeMin = _wakeTime.hour * 60 + _wakeTime.minute;
    if (wakeMin <= bedMin) {
      wakeMin += 24 * 60;
    }
    return (((wakeMin - bedMin) / 60.0) * 10).round() / 10.0;
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);
    final daily = state.dailyHealth;
    final history = state.sleepHistory7Days;
    final previewHours = _computeDurationHours();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Theo dõi Giấc ngủ'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (daily != null)
            Card(
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Color(0xFFEDE7F6),
                  child: Icon(Icons.bedtime_outlined, color: AppColors.sleepPurple),
                ),
                title: Text(
                  'Giấc ngủ hôm nay: ${daily.sleepHours.toStringAsFixed(1)} giờ',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  'Trạng thái: ${DailyHealthModel.classifySleepStatus(daily.sleepHours)} · '
                  'Chất lượng: ${daily.sleepQualityScore ?? "-"}/5 sao',
                ),
              ),
            ),
          const SizedBox(height: 10),

          // Nhap tay 2 cham
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Ghi nhận giấc ngủ (2 chạm)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final picked = await showTimePicker(
                              context: context,
                              initialTime: _bedTime,
                            );
                            if (picked != null) {
                              setState(() => _bedTime = picked);
                            }
                          },
                          icon: const Icon(Icons.nights_stay_outlined),
                          label: Text('Ngủ: ${_bedTime.format(context)}'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final picked = await showTimePicker(
                              context: context,
                              initialTime: _wakeTime,
                            );
                            if (picked != null) {
                              setState(() => _wakeTime = picked);
                            }
                          },
                          icon: const Icon(Icons.wb_sunny_outlined),
                          label: Text('Dậy: ${_wakeTime.format(context)}'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Tổng thời lượng: $previewHours giờ (${DailyHealthModel.classifySleepStatus(previewHours)})',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Text('Chất lượng: '),
                      ...List.generate(5, (idx) {
                        final star = idx + 1;
                        return IconButton(
                          onPressed: () => setState(() => _qualityStars = star),
                          icon: Icon(
                            star <= _qualityStars
                                ? Icons.star
                                : Icons.star_border,
                            color: Colors.amber,
                          ),
                        );
                      }),
                    ],
                  ),
                  const SizedBox(height: 8),
                  FilledButton(
                    onPressed: () async {
                      await controller.logSleep(
                        sleepHours: previewHours,
                        qualityScore: _qualityStars,
                      );
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              'Đã lưu $previewHours giờ ngủ hôm nay.',
                            ),
                          ),
                        );
                      }
                    },
                    child: const Text('Lưu giấc ngủ hôm nay'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Bieu do cot 7 ngay
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Biểu đồ Giấc ngủ 7 ngày gần nhất',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 14),
                  if (history.isEmpty)
                    const SizedBox(
                      height: 120,
                      child: Center(child: Text('Chưa có dữ liệu giấc ngủ.')),
                    )
                  else
                    SizedBox(
                      height: 190,
                      child: BarChart(
                        BarChartData(
                          maxY: 11,
                          minY: 0,
                          borderData: FlBorderData(show: false),
                          gridData: const FlGridData(
                            show: true,
                            drawVerticalLine: false,
                          ),
                          titlesData: FlTitlesData(
                            topTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            rightTitles: const AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                reservedSize: 24,
                                getTitlesWidget: (value, meta) {
                                  final idx = value.toInt();
                                  if (idx < 0 || idx >= history.length) {
                                    return const SizedBox.shrink();
                                  }
                                  final iso = history[idx].logDateIso;
                                  final short = iso.length >= 10
                                      ? iso.substring(5)
                                      : iso;
                                  return Padding(
                                    padding: const EdgeInsets.only(top: 6),
                                    child: Text(
                                      short,
                                      style: const TextStyle(fontSize: 10),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ),
                          barGroups: [
                            for (var i = 0; i < history.length; i++)
                              BarChartGroupData(
                                x: i,
                                barRods: [
                                  BarChartRodData(
                                    toY: history[i].sleepHours,
                                    width: 18,
                                    borderRadius: BorderRadius.circular(6),
                                    color: history[i].sleepHours < 6.5
                                        ? AppColors.warningRed
                                        : AppColors.sleepPurple,
                                  ),
                                ],
                              ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          if (FeatureFlags.enableHealthConnect) ...[
            const SizedBox(height: 12),
            const Card(
              color: Color(0xFFF3F6FA),
              child: ListTile(
                leading: Icon(Icons.health_and_safety_outlined),
                title: Text('Đồng bộ giấc ngủ tự động'),
                subtitle: Text(
                  'Đã bật tự động đồng bộ dữ liệu giấc ngủ từ Health Connect.',
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
