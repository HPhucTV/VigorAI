// [OWNER: M2] Man hinh Bieu do Radar Can bang 6 Nhom co (Effective Sets 30 ngay qua) (T-M2-11 / F24)
import 'dart:math' as math;

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../data/ai_analytics_repository.dart';

class MuscleRadarView extends ConsumerWidget {
  const MuscleRadarView({super.key});

  static const _axes = <({String key, String label})>[
    (key: 'chest', label: 'Ngực'),
    (key: 'back', label: 'Lưng'),
    (key: 'shoulders', label: 'Vai'),
    (key: 'arms', label: 'Tay'),
    (key: 'legs', label: 'Chân'),
    (key: 'core', label: 'Bụng'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final summaryAsync = ref.watch(analyticsSummaryProvider(30));

    return summaryAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(child: Text('Lỗi tải Radar cơ bắp: $err')),
      data: (summary) {
        final counts = summary.muscleRadarCounts;
        final maxSets = counts.values.fold<int>(
          12,
          (m, v) => v > m ? v : m,
        );
        final targetNorm = (maxSets * 0.75).clamp(8.0, maxSets.toDouble());

        final entries = _axes
            .map(
              (a) => RadarEntry(
                value: math.max(1.0, (counts[a.key] ?? 0).toDouble()),
              ),
            )
            .toList();
        final targetEntries = _axes
            .map((_) => RadarEntry(value: targetNorm))
            .toList();

        // Find weakest muscle axis
        var weakest = _axes.first;
        var minCount = counts[weakest.key] ?? 0;
        for (final a in _axes) {
          final c = counts[a.key] ?? 0;
          if (c < minCount) {
            minCount = c;
            weakest = a;
          }
        }

        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(analyticsSummaryProvider(30)),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Biểu đồ Radar Cân bằng 6 Nhóm cơ (30 ngày)',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tính theo số hiệp hiệu dụng (RPE ≥ 6.0, loại trừ Warmup)',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 270,
                        child: RadarChart(
                          RadarChartData(
                            radarShape: RadarShape.polygon,
                            tickCount: 4,
                            ticksTextStyle: const TextStyle(
                              fontSize: 10,
                              color: Colors.grey,
                            ),
                            tickBorderData:
                                BorderSide(color: Colors.grey.shade300),
                            gridBorderData:
                                BorderSide(color: Colors.grey.shade300),
                            radarBorderData:
                                BorderSide(color: Colors.grey.shade400),
                            titlePositionPercentageOffset: 0.16,
                            titleTextStyle: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                            getTitle: (index, angle) {
                              final axis = _axes[index];
                              final count = counts[axis.key] ?? 0;
                              return RadarChartTitle(
                                text: '${axis.label}\n($count)',
                              );
                            },
                            dataSets: [
                              RadarDataSet(
                                fillColor:
                                    AppColors.accent.withValues(alpha: 0.08),
                                borderColor: AppColors.accent,
                                entryRadius: 0,
                                borderWidth: 1.5,
                                dataEntries: targetEntries,
                              ),
                              RadarDataSet(
                                fillColor:
                                    AppColors.primary.withValues(alpha: 0.28),
                                borderColor: AppColors.primary,
                                entryRadius: 3.5,
                                borderWidth: 2.3,
                                dataEntries: entries,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Pull / Push Balance & Weak Muscle Advice
              Card(
                color: const Color(0xFFE3F2FD),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: AppColors.primary,
                    child: Icon(Icons.balance, color: Colors.white),
                  ),
                  title: Text(
                    'Tỷ lệ Kéo / Đẩy (Pull : Push) = ${summary.pullPushRatio.toStringAsFixed(2)} : 1',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    summary.pullPushRatio >= 0.85 &&
                            summary.pullPushRatio <= 1.25
                        ? 'Cân bằng Kéo/Đẩy tốt (khuyến nghị ~1:1 bảo vệ khớp vai).'
                        : summary.pullPushRatio < 0.85
                            ? 'Khối lượng Đẩy đang nhiều hơn Kéo — nên bổ sung bài Lưng/Xô.'
                            : 'Khối lượng Kéo đang cao hơn Đẩy — có thể tăng thêm bài Ngực/Vai.',
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Card(
                color: const Color(0xFFFFF8E1),
                child: ListTile(
                  leading: const Icon(
                    Icons.lightbulb_outline,
                    color: AppColors.calorieOrange,
                  ),
                  title: Text(
                    'Nhóm cơ cần ưu tiên bổ sung: ${weakest.label}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    '30 ngày qua mới ghi nhận $minCount hiệp hiệu dụng cho nhóm ${weakest.label}.',
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
