// [OWNER: M2] Man hinh Thong ke Tien do Volume Load & Bang Ky luc PR / Streak (T-M2-11 / F22, F25)
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../data/ai_analytics_repository.dart';

class VolumeAnalyticsView extends ConsumerStatefulWidget {
  const VolumeAnalyticsView({super.key});

  @override
  ConsumerState<VolumeAnalyticsView> createState() =>
      _VolumeAnalyticsViewState();
}

class _VolumeAnalyticsViewState extends ConsumerState<VolumeAnalyticsView> {
  int _selectedDays = 90;

  static const _periodOptions = <int, String>{
    7: '7 ngày',
    30: '30 ngày',
    90: '90 ngày',
    365: '1 năm',
  };

  static const _axisLabelsVi = <String, String>{
    'chest': 'Ngực',
    'back': 'Lưng',
    'shoulders': 'Vai',
    'arms': 'Tay',
    'legs': 'Chân',
    'core': 'Bụng',
  };

  @override
  Widget build(BuildContext context) {
    final summaryAsync = ref.watch(analyticsSummaryProvider(_selectedDays));

    return summaryAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(child: Text('Lỗi tải thống kê Volume: $err')),
      data: (summary) {
        final maxWeeklyVol = summary.weeklyVolume.fold<double>(
          100.0,
          (m, e) => e.totalVolumeKg > m ? e.totalVolumeKg : m,
        );
        final maxMuscleVol = summary.volumeByMuscleAxis.values.fold<double>(
          1.0,
          (m, v) => v > m ? v : m,
        );

        return RefreshIndicator(
          onRefresh: () async =>
              ref.invalidate(analyticsSummaryProvider(_selectedDays)),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 1. Period Filter (7d, 30d, 90d, 1y)
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: _periodOptions.entries.map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(entry.value),
                        selected: _selectedDays == entry.key,
                        onSelected: (_) =>
                            setState(() => _selectedDays = entry.key),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 12),

              // 2. KPI Summary Row + Streak Badge (F22, F25)
              Row(
                children: [
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Tổng Volume Load',
                              style: TextStyle(fontSize: 12, color: Colors.black54),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${summary.totalVolumeKg.toStringAsFixed(0)} kg',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: AppColors.primary,
                              ),
                            ),
                            Text(
                              '${summary.totalWorkingSets} hiệp hiệu dụng',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Card(
                      color: const Color(0xFFFFF3E0),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(
                                  Icons.local_fire_department,
                                  color: AppColors.calorieOrange,
                                  size: 18,
                                ),
                                SizedBox(width: 4),
                                Text(
                                  'Chuỗi Tập luyện',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.black54,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${summary.streakDays} buổi',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: AppColors.calorieOrange,
                              ),
                            ),
                            Text(
                              '${summary.personalRecords.length} bài có PR',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // 3. Weekly Volume Bar Chart (F22)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Biểu đồ Volume Load theo Tuần (kg)',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 12),
                      if (summary.weeklyVolume.isEmpty)
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 28),
                          child: Center(
                            child: Text(
                              'Chưa có buổi tập hoàn thành trong khoảng thời gian này.\nHãy hoàn thành 1 buổi tập để xem biểu đồ!',
                              textAlign: TextAlign.center,
                              style: TextStyle(color: Colors.black54),
                            ),
                          ),
                        )
                      else
                        SizedBox(
                          height: 210,
                          child: BarChart(
                            BarChartData(
                              maxY: maxWeeklyVol * 1.18,
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
                                leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    reservedSize: 44,
                                    getTitlesWidget: (val, meta) => Padding(
                                      padding: const EdgeInsets.only(right: 4),
                                      child: Text(
                                        val >= 1000
                                            ? '${(val / 1000).toStringAsFixed(1)}k'
                                            : val.toInt().toString(),
                                        style: const TextStyle(fontSize: 10),
                                      ),
                                    ),
                                  ),
                                ),
                                bottomTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    reservedSize: 28,
                                    getTitlesWidget: (val, meta) {
                                      final idx = val.toInt();
                                      if (idx < 0 ||
                                          idx >= summary.weeklyVolume.length) {
                                        return const SizedBox.shrink();
                                      }
                                      return Padding(
                                        padding: const EdgeInsets.only(top: 6),
                                        child: Text(
                                          summary.weeklyVolume[idx].weekLabel,
                                          style: const TextStyle(fontSize: 10),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              ),
                              barGroups: summary.weeklyVolume
                                  .asMap()
                                  .entries
                                  .map(
                                    (entry) => BarChartGroupData(
                                      x: entry.key,
                                      barRods: [
                                        BarChartRodData(
                                          toY: entry.value.totalVolumeKg,
                                          color: AppColors.primary,
                                          width: 18,
                                          borderRadius:
                                              const BorderRadius.vertical(
                                            top: Radius.circular(6),
                                          ),
                                        ),
                                      ],
                                    ),
                                  )
                                  .toList(),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // 4. Volume by Muscle Group Bars
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Phân bổ Khối lượng theo Nhóm cơ',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 10),
                      ..._axisLabelsVi.entries.map((e) {
                        final vol = summary.volumeByMuscleAxis[e.key] ?? 0.0;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 5),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(e.value),
                                  Text('${vol.toStringAsFixed(0)} kg'),
                                ],
                              ),
                              const SizedBox(height: 4),
                              LinearProgressIndicator(
                                value: (vol / maxMuscleVol).clamp(0.0, 1.0),
                                minHeight: 7,
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // 5. Personal Records Wall (F25)
              const Text(
                'Bảng Kỷ lục Cá nhân (PR Wall · 1RM Epley/Brzycki)',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 8),
              if (summary.personalRecords.isEmpty)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(14),
                    child: Text('Chưa ghi nhận kỷ lục PR nào.'),
                  ),
                )
              else
                ...summary.personalRecords.map(
                  (pr) => Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: const CircleAvatar(
                        backgroundColor: Color(0xFFFFF3E0),
                        child: Icon(
                          Icons.emoji_events,
                          color: AppColors.calorieOrange,
                        ),
                      ),
                      title: Text(
                        pr.exerciseNameVi,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(
                        'Tốt nhất: ${pr.bestWeightKg} kg × ${pr.bestReps} reps',
                      ),
                      trailing: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            '${pr.best1rmKg.toStringAsFixed(1)} kg',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: AppColors.primary,
                              fontSize: 15,
                            ),
                          ),
                          const Text('1RM ước tính', style: TextStyle(fontSize: 10)),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}
