// [OWNER: M1] Man hinh Can nang, BMI WHO Chau A, 5 vong do & 7-Day Moving Average (T-M1-08 / F01)
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/database/health_tables.drift.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';

class BiometricsScreen extends ConsumerWidget {
  const BiometricsScreen({super.key});

  static const List<({String key, String label})> _circumferenceFields = [
    (key: 'chest', label: 'Ngực'),
    (key: 'waist', label: 'Eo'),
    (key: 'hips', label: 'Mông'),
    (key: 'arm', label: 'Bắp tay'),
    (key: 'thigh', label: 'Đùi'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);
    final logs = state.biometrics;
    final latest = state.latestBiometric;
    final previous = logs.length > 1 ? logs[1] : null;
    final chronological = logs.reversed.toList();
    final ma7 = BiometricLogModel.calculateMovingAverage7Day(chronological);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cân nặng & Thành phần Cơ thể'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openAddBiometricSheet(context, controller, latest),
        icon: const Icon(Icons.add),
        label: const Text('Ghi nhận'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 88),
        children: [
          if (latest != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Flexible(
                          flex: 5,
                          child: FittedBox(
                            fit: BoxFit.scaleDown,
                            alignment: Alignment.centerLeft,
                            child: Text(
                              '${latest.weightKg.toStringAsFixed(1)} kg',
                              maxLines: 1,
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: AppColors.telemetryCyan(context),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          flex: 6,
                          child: Align(
                            alignment: Alignment.centerRight,
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: AppColors.tintedSurface(
                                  context,
                                  AppColors.telemetryCyan(context),
                                ),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: AppColors.telemetryCyan(context)
                                      .withValues(alpha: 0.3),
                                ),
                              ),
                              child: FittedBox(
                                fit: BoxFit.scaleDown,
                                child: Text(
                                  'BMI ${latest.bmi.toStringAsFixed(1)} · '
                                  '${BiometricLogModel.classifyAsianBmi(latest.bmi)}',
                                  maxLines: 1,
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600,
                                    color: AppColors.telemetryCyan(context),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Cập nhật: ${latest.loggedDateIso}',
                      style: TextStyle(
                        fontSize: 13,
                        color: AppColors.secondaryText(context),
                      ),
                    ),
                    const SizedBox(height: 12),
                    IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Expanded(
                            child: _MetricTile(
                              label: 'Tỷ lệ mỡ',
                              value: latest.bodyFatPct != null
                                  ? '${latest.bodyFatPct!.toStringAsFixed(1)}%'
                                  : '--',
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _MetricTile(
                              label: 'Khối cơ',
                              value: latest.muscleMassKg != null
                                  ? '${latest.muscleMassKg!.toStringAsFixed(1)} kg'
                                  : '--',
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _MetricTile(
                              label: 'TB 7 ngày',
                              value: ma7.isNotEmpty
                                  ? '${ma7.last.toStringAsFixed(1)} kg'
                                  : '--',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],

          // Bieu do xu huong can nang + duong trung binh truot 7 ngay
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Biểu đồ Cân nặng & Đường xu hướng 7 ngày',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 6),
                  const Wrap(
                    spacing: 16,
                    runSpacing: 6,
                    children: [
                      _LegendDot(color: AppColors.primary, label: 'Thực tế'),
                      _LegendDot(
                        color: AppColors.calorieOrange,
                        label: 'Trung bình 7 ngày',
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (chronological.length < 2)
                    const SizedBox(
                      height: 140,
                      child: Center(
                        child: Text('Cần ít nhất 2 mốc cân nặng để vẽ biểu đồ.'),
                      ),
                    )
                  else
                    SizedBox(
                      height: 210,
                      child: _WeightTrendChart(
                        logs: chronological,
                        ma7: ma7,
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Bang 5 so do vong co the
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Số đo 5 vòng cơ thể (cm)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 8),
                  ..._circumferenceFields.map((field) {
                    final curr = latest?.circumferencesCm[field.key];
                    final prev = previous?.circumferencesCm[field.key];
                    final delta = (curr != null && prev != null)
                        ? (curr - prev)
                        : null;
                    return ListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: Text(field.label),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            curr != null ? '${curr.toStringAsFixed(1)} cm' : '--',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          if (delta != null && delta.abs() >= 0.05) ...[
                            const SizedBox(width: 8),
                            Text(
                              '${delta > 0 ? '+' : ''}${delta.toStringAsFixed(1)}',
                              style: TextStyle(
                                fontSize: 12,
                                color: delta > 0
                                    ? AppColors.stepTeal
                                    : AppColors.calorieOrange,
                              ),
                            ),
                          ],
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Lich su nhap gan day
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Lịch sử ghi nhận gần đây',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const SizedBox(height: 8),
                  ...logs.take(14).map(
                        (item) => ListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(
                            item.syncStatus == 'SYNCED'
                                ? Icons.cloud_done_outlined
                                : Icons.cloud_upload_outlined,
                            size: 18,
                            color: item.syncStatus == 'SYNCED'
                                ? AppColors.muscleRecoveredGreen
                                : AppColors.calorieOrange,
                          ),
                          title: Text(
                            '${item.weightKg.toStringAsFixed(1)} kg · BMI ${item.bmi.toStringAsFixed(1)}',
                          ),
                          subtitle: Text(
                            '${item.loggedDateIso} · '
                            '${BiometricLogModel.classifyAsianBmi(item.bmi)}',
                          ),
                        ),
                      ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _openAddBiometricSheet(
    BuildContext context,
    HealthDashboardController controller,
    BiometricLogModel? latest,
  ) async {
    final weightCtrl = TextEditingController(
      text: latest != null ? latest.weightKg.toStringAsFixed(1) : '70.0',
    );
    final fatCtrl = TextEditingController(
      text: latest?.bodyFatPct?.toStringAsFixed(1) ?? '',
    );
    final muscleCtrl = TextEditingController(
      text: latest?.muscleMassKg?.toStringAsFixed(1) ?? '',
    );
    final circCtrls = {
      for (final f in _circumferenceFields)
        f.key: TextEditingController(
          text: latest?.circumferencesCm[f.key]?.toStringAsFixed(1) ?? '',
        ),
    };
    final formKey = GlobalKey<FormState>();

    final saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (sheetCtx) => Padding(
        padding: EdgeInsets.fromLTRB(
          16,
          16,
          16,
          MediaQuery.of(sheetCtx).viewInsets.bottom + 16,
        ),
        child: Form(
          key: formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Ghi nhận Cân nặng & Số đo',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: weightCtrl,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(
                    labelText: 'Cân nặng (kg) *',
                  ),
                  validator: (v) {
                    final parsed = double.tryParse((v ?? '').trim());
                    if (parsed == null || parsed < 25 || parsed > 300) {
                      return 'Nhập cân nặng hợp lệ (25–300 kg)';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: fatCtrl,
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        decoration: const InputDecoration(
                          labelText: 'Tỷ lệ mỡ (%)',
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: TextFormField(
                        controller: muscleCtrl,
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        decoration: const InputDecoration(
                          labelText: 'Khối lượng cơ (kg)',
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  '5 vòng đo cơ thể (cm — tùy chọn)',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _circumferenceFields.map((f) {
                    return SizedBox(
                      width: 150,
                      child: TextFormField(
                        controller: circCtrls[f.key],
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        decoration: InputDecoration(labelText: '${f.label} (cm)'),
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () {
                    if (formKey.currentState?.validate() ?? false) {
                      Navigator.of(sheetCtx).pop(true);
                    }
                  },
                  child: const Text('Lưu chỉ số'),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    if (saved == true) {
      final weight = double.parse(weightCtrl.text.trim());
      final fat = double.tryParse(fatCtrl.text.trim());
      final muscle = double.tryParse(muscleCtrl.text.trim());
      final circ = <String, double>{};
      for (final f in _circumferenceFields) {
        final v = double.tryParse(circCtrls[f.key]!.text.trim());
        if (v != null && v > 0) {
          circ[f.key] = v;
        }
      }
      await controller.addBiometric(
        weightKg: weight,
        bodyFatPct: fat,
        muscleMassKg: muscle,
        circumferencesCm: circ,
      );
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Đã lưu chỉ số cân nặng.'),
          ),
        );
      }
    }

    weightCtrl.dispose();
    fatCtrl.dispose();
    muscleCtrl.dispose();
    for (final c in circCtrls.values) {
      c.dispose();
    }
  }
}

class _WeightTrendChart extends StatelessWidget {
  final List<BiometricLogModel> logs;
  final List<double> ma7;

  const _WeightTrendChart({required this.logs, required this.ma7});

  @override
  Widget build(BuildContext context) {
    final weights = logs.map((e) => e.weightKg).toList();
    final minY =
        (weights.reduce((a, b) => a < b ? a : b) - 1.5).floorToDouble();
    final maxY =
        (weights.reduce((a, b) => a > b ? a : b) + 1.5).ceilToDouble();

    final rawSpots = <FlSpot>[
      for (var i = 0; i < logs.length; i++)
        FlSpot(i.toDouble(), logs[i].weightKg),
    ];
    final maSpots = <FlSpot>[
      for (var i = 0; i < ma7.length; i++) FlSpot(i.toDouble(), ma7[i]),
    ];

    return LineChart(
      LineChartData(
        minY: minY,
        maxY: maxY,
        gridData: const FlGridData(show: true, drawVerticalLine: false),
        borderData: FlBorderData(show: false),
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
                if (idx < 0 || idx >= logs.length) {
                  return const SizedBox.shrink();
                }
                if (logs.length > 6 && idx % 2 != 0 && idx != logs.length - 1) {
                  return const SizedBox.shrink();
                }
                final iso = logs[idx].loggedDateIso;
                final label = iso.length >= 10 ? iso.substring(5) : iso;
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(label, style: const TextStyle(fontSize: 10)),
                );
              },
            ),
          ),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: rawSpots,
            isCurved: true,
            color: AppColors.primary,
            barWidth: 3,
            dotData: const FlDotData(show: true),
          ),
          LineChartBarData(
            spots: maSpots,
            isCurved: true,
            color: AppColors.calorieOrange,
            barWidth: 2.5,
            dashArray: [6, 4],
            dotData: const FlDotData(show: false),
          ),
        ],
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  final String label;
  final String value;

  const _MetricTile({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.subtleSurface(context),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 12,
              color: AppColors.secondaryText(context),
            ),
          ),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              maxLines: 1,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendDot({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
