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
        final totalRadarSets = counts.values.fold<int>(0, (a, b) => a + b);
        final pushSets = (counts['chest'] ?? 0) + (counts['shoulders'] ?? 0);
        final pullSets = counts['back'] ?? 0;
        final hasPushPull = pushSets + pullSets > 0;

        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(analyticsSummaryProvider(30)),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
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
                      const SizedBox(height: 28),
                      SizedBox(
                        height: 270,
                        child: RadarChart(
                          RadarChartData(
                            radarShape: RadarShape.polygon,
                            tickCount: 4,
                            ticksTextStyle: TextStyle(
                              fontSize: 10,
                              color: AppColors.secondaryText(context),
                            ),
                            tickBorderData: BorderSide(
                              color: AppColors.subtleBorder(context),
                            ),
                            gridBorderData: BorderSide(
                              color: AppColors.subtleBorder(context),
                            ),
                            radarBorderData: BorderSide(
                              color: AppColors.secondaryText(context)
                                  .withValues(alpha: 0.4),
                            ),
                            titlePositionPercentageOffset: 0.20,
                            titleTextStyle: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Theme.of(context).colorScheme.onSurface,
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
                                fillColor: AppColors.telemetryCyan(context)
                                    .withValues(alpha: 0.28),
                                borderColor: AppColors.telemetryCyan(context),
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
                color: AppColors.tintedSurface(context, AppColors.primary),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: AppColors.primary,
                    child: Icon(Icons.balance, color: Colors.white),
                  ),
                  title: Text(
                    !hasPushPull
                        ? 'Tỷ lệ Kéo / Đẩy (Pull : Push) — Chưa đủ dữ liệu'
                        : pushSets == 0
                            ? 'Tỷ lệ Kéo / Đẩy: Chỉ có bài Kéo ($pullSets hiệp)'
                            : 'Tỷ lệ Kéo / Đẩy (Pull : Push) = ${summary.pullPushRatio.toStringAsFixed(2)} : 1',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    !hasPushPull
                        ? 'Hoàn thành buổi tập Ngực/Vai/Lưng (RPE ≥ 6.0) để đánh giá cân bằng Kéo/Đẩy.'
                        : pushSets == 0
                            ? 'Khối lượng Kéo đang cao hơn Đẩy — nên bổ sung thêm bài Ngực/Vai.'
                            : (summary.pullPushRatio >= 0.85 &&
                                    summary.pullPushRatio <= 1.25
                                ? 'Cân bằng Kéo/Đẩy tốt (khuyến nghị ~1:1 bảo vệ khớp vai).'
                                : summary.pullPushRatio < 0.85
                                    ? 'Khối lượng Đẩy đang nhiều hơn Kéo — nên bổ sung bài Lưng/Xô.'
                                    : 'Khối lượng Kéo đang cao hơn Đẩy — có thể tăng thêm bài Ngực/Vai.'),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Card(
                color: AppColors.tintedSurface(context, AppColors.calorieOrange),
                child: ListTile(
                  leading: const Icon(
                    Icons.lightbulb_outline,
                    color: AppColors.calorieOrange,
                  ),
                  title: Text(
                    totalRadarSets == 0
                        ? 'Chưa có dữ liệu nhóm cơ trong 30 ngày qua'
                        : 'Nhóm cơ cần ưu tiên bổ sung: ${weakest.label}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    totalRadarSets == 0
                        ? 'Hãy hoàn thành buổi tập đầu tiên để Radar tự động phân tích cân bằng cơ bắp.'
                        : '30 ngày qua mới ghi nhận $minCount hiệp hiệu dụng cho nhóm ${weakest.label}.',
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
