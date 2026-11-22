// [OWNER: M2] Cong cu Tinh Banh Ta Truc quan (Visual Barbell Plate Calculator) (T-M2-09 / F18)
import 'package:flutter/material.dart';

import '../../../../core/theme/app_theme.dart';
import '../../domain/workout_calculators.dart';

Future<double?> showPlateCalculatorSheet(
  BuildContext context, {
  double initialTargetKg = 95.0,
}) {
  return showModalBottomSheet<double>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (ctx) => _PlateCalculatorSheetContent(
      initialTargetKg: initialTargetKg,
    ),
  );
}

class _PlateCalculatorSheetContent extends StatefulWidget {
  final double initialTargetKg;

  const _PlateCalculatorSheetContent({required this.initialTargetKg});

  @override
  State<_PlateCalculatorSheetContent> createState() =>
      _PlateCalculatorSheetContentState();
}

class _PlateCalculatorSheetContentState
    extends State<_PlateCalculatorSheetContent> {
  late double _targetKg;
  double _barWeightKg = 20.0;
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _targetKg = widget.initialTargetKg >= 20 ? widget.initialTargetKg : 60.0;
    _controller = TextEditingController(text: _formatKg(_targetKg));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String _formatKg(double v) =>
      v == v.roundToDouble() ? v.toInt().toString() : v.toStringAsFixed(2);

  void _setTarget(double nextKg) {
    final clamped = nextKg.clamp(0.0, 400.0);
    setState(() {
      _targetKg = clamped;
      _controller.text = _formatKg(clamped);
    });
  }

  @override
  Widget build(BuildContext context) {
    final result = WorkoutCalculators.calculateBarbellPlates(
      targetWeightKg: _targetKg,
      barWeightKg: _barWeightKg,
    );

    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Tính Bánh Tạ Trực quan',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Chọn loại thanh đòn:',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('20 kg (Nam Olympic)'),
                  selected: _barWeightKg == 20.0,
                  onSelected: (_) => setState(() => _barWeightKg = 20.0),
                ),
                ChoiceChip(
                  label: const Text('15 kg (Nữ)'),
                  selected: _barWeightKg == 15.0,
                  onSelected: (_) => setState(() => _barWeightKg = 15.0),
                ),
                ChoiceChip(
                  label: const Text('10 kg (Đòn EZ)'),
                  selected: _barWeightKg == 10.0,
                  onSelected: (_) => setState(() => _barWeightKg = 10.0),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: 'Tổng mức tạ mục tiêu (kg)',
                      suffixText: 'kg',
                      isDense: true,
                    ),
                    onChanged: (raw) {
                      final parsed = double.tryParse(raw.replaceAll(',', '.'));
                      if (parsed != null && parsed >= 0) {
                        setState(() => _targetKg = parsed);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filledTonal(
                  tooltip: '-2.5 kg',
                  onPressed: () => _setTarget(_targetKg - 2.5),
                  icon: const Icon(Icons.remove),
                ),
                const SizedBox(width: 4),
                IconButton.filledTonal(
                  tooltip: '+2.5 kg',
                  onPressed: () => _setTarget(_targetKg + 2.5),
                  icon: const Icon(Icons.add),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [40.0, 60.0, 80.0, 95.0, 100.0, 120.0]
                  .map(
                    (preset) => ActionChip(
                      label: Text('${preset.toInt()} kg'),
                      visualDensity: VisualDensity.compact,
                      onPressed: () => _setTarget(preset),
                    ),
                  )
                  .toList(),
            ),
            const SizedBox(height: 14),
            // 2D SVG-like CustomPainter visualization of loaded Olympic barbell
            Container(
              height: 128,
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFF12161F),
                borderRadius: BorderRadius.circular(14),
              ),
              child: CustomPaint(
                painter: _BarbellPlatesPainter(
                  perSidePlates: result.perSidePlates,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              color: const Color(0xFFE3F2FD),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Mỗi bên lắp: ${result.perSideTotalKg.toStringAsFixed(2).replaceAll(RegExp(r"\.?0+$"), "")} kg '
                      '(Tổng thực tế: ${result.achievedWeightKg} kg)',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    if (result.perSidePlates.isEmpty)
                      const Text('Chỉ dùng thanh đòn trống (chưa cần lắp bánh tạ).')
                    else
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: result.plateCounts.entries.map((e) {
                          return Chip(
                            avatar: CircleAvatar(
                              backgroundColor: _colorForPlate(e.key),
                              radius: 8,
                            ),
                            label: Text('${e.value}x ${e.key} kg'),
                            visualDensity: VisualDensity.compact,
                          );
                        }).toList(),
                      ),
                  ],
                ),
              ),
            ),
            if (result.warningMessage != null) ...[
              const SizedBox(height: 8),
              Card(
                color: const Color(0xFFFFF3E0),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        color: AppColors.calorieOrange,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          result.warningMessage!,
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: () =>
                  Navigator.of(context).pop(result.achievedWeightKg),
              icon: const Icon(Icons.check),
              label: Text('Áp dụng mức ${result.achievedWeightKg} kg'),
            ),
          ],
        ),
      ),
    );
  }
}

Color _colorForPlate(double kg) {
  if (kg >= 20.0) return const Color(0xFF1E88E5);
  if (kg >= 15.0) return const Color(0xFFFDD835);
  if (kg >= 10.0) return const Color(0xFF43A047);
  if (kg >= 5.0) return const Color(0xFFB0BEC5);
  if (kg >= 2.5) return const Color(0xFFE53935);
  return const Color(0xFFFB8C00);
}

class _BarbellPlatesPainter extends CustomPainter {
  final List<double> perSidePlates;

  const _BarbellPlatesPainter({required this.perSidePlates});

  double _heightRatio(double kg) {
    if (kg >= 20.0) return 0.92;
    if (kg >= 15.0) return 0.80;
    if (kg >= 10.0) return 0.68;
    if (kg >= 5.0) return 0.54;
    if (kg >= 2.5) return 0.42;
    return 0.34;
  }

  double _widthPx(double kg) {
    if (kg >= 20.0) return 14.0;
    if (kg >= 15.0) return 12.0;
    if (kg >= 10.0) return 11.0;
    if (kg >= 5.0) return 9.0;
    return 7.5;
  }

  @override
  void paint(Canvas canvas, Size size) {
    final cy = size.height / 2;
    final barPaint = Paint()..color = const Color(0xFF90A4AE);
    final sleevePaint = Paint()..color = const Color(0xFFCFD8DC);

    // Main shaft across center
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(center: Offset(size.width / 2, cy), width: size.width - 12, height: 8),
        const Radius.circular(4),
      ),
      barPaint,
    );

    // Center collar markers at 28% from center
    final leftStop = size.width * 0.28;
    final rightStop = size.width * 0.72;
    canvas.drawRect(
      Rect.fromCenter(center: Offset(leftStop, cy), width: 6, height: 24),
      sleevePaint,
    );
    canvas.drawRect(
      Rect.fromCenter(center: Offset(rightStop, cy), width: 6, height: 24),
      sleevePaint,
    );

    final maxPlateHeight = size.height * 0.86;
    var leftCursor = leftStop - 6;
    var rightCursor = rightStop + 6;

    for (final kg in perSidePlates) {
      final w = _widthPx(kg);
      final h = maxPlateHeight * _heightRatio(kg);
      final paint = Paint()..color = _colorForPlate(kg);
      final border = Paint()
        ..color = Colors.black45
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;

      if (leftCursor - w >= 4) {
        final rectL = RRect.fromRectAndRadius(
          Rect.fromLTWH(leftCursor - w, cy - h / 2, w, h),
          const Radius.circular(3),
        );
        canvas.drawRRect(rectL, paint);
        canvas.drawRRect(rectL, border);
        leftCursor -= (w + 2);
      }

      if (rightCursor + w <= size.width - 4) {
        final rectR = RRect.fromRectAndRadius(
          Rect.fromLTWH(rightCursor, cy - h / 2, w, h),
          const Radius.circular(3),
        );
        canvas.drawRRect(rectR, paint);
        canvas.drawRRect(rectR, border);
        rightCursor += (w + 2);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _BarbellPlatesPainter oldDelegate) {
    return oldDelegate.perSidePlates != perSidePlates;
  }
}
