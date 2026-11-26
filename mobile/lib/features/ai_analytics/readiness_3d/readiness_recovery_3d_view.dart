// [OWNER: M2] Man hinh AI Readiness Dashboard, Ban do Phuc hoi Co bap 3D & Goi y Tai trong (T-M2-10 / F20, F21, F23)
import 'dart:async';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/database/ai_cache_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import '../data/ai_analytics_repository.dart';

class ReadinessRecovery3DView extends ConsumerStatefulWidget {
  final bool isActive;

  const ReadinessRecovery3DView({super.key, this.isActive = true});

  @override
  ConsumerState<ReadinessRecovery3DView> createState() =>
      _ReadinessRecovery3DViewState();
}

class _ReadinessRecovery3DViewState
    extends ConsumerState<ReadinessRecovery3DView> {
  CameraPreset3D _cameraPreset = CameraPreset3D.front;
  String? _selectedMuscleId;
  bool _mountWebView = false;
  Timer? _deferTimer;

  bool get _isFlutterTest =>
      !kIsWeb && Platform.environment.containsKey('FLUTTER_TEST');

  @override
  void initState() {
    super.initState();
    _syncWebViewMount(widget.isActive);
  }

  @override
  void didUpdateWidget(covariant ReadinessRecovery3DView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.isActive != widget.isActive) {
      _syncWebViewMount(widget.isActive);
    }
  }

  @override
  void dispose() {
    _deferTimer?.cancel();
    super.dispose();
  }

  void _syncWebViewMount(bool active) {
    _deferTimer?.cancel();
    if (!active || _isFlutterTest) {
      if (_mountWebView) {
        setState(() => _mountWebView = false);
      }
      return;
    }
    _deferTimer = Timer(const Duration(milliseconds: 220), () {
      if (mounted && widget.isActive && !_mountWebView) {
        setState(() => _mountWebView = true);
      }
    });
  }

  Color _scoreColor(double score) {
    if (score >= 75.0) return AppColors.muscleRecoveredGreen;
    if (score >= 45.0) return AppColors.muscleSecondaryOrange;
    return AppColors.musclePrimaryRed;
  }

  String _readinessHeadline(double score) {
    if (score >= 75.0) return 'Sung sức — Sẵn sàng tăng tiến tải trọng';
    if (score >= 45.0) return 'Bình thường — Giữ tạ vừa & tập chuẩn kỹ thuật';
    return 'Mệt mỏi cao — Khuyến nghị nghỉ ngơi hoặc Deload';
  }

  @override
  Widget build(BuildContext context) {
    final readinessAsync = ref.watch(aiReadinessProvider);
    final avatarPreset = ref.watch(bodyAvatarPresetProvider);

    return readinessAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Không thể tải dữ liệu AI Readiness: $err'),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: () => ref.invalidate(aiReadinessProvider),
                child: const Text('Thử lại'),
              ),
            ],
          ),
        ),
      ),
      data: (snapshot) => _buildContent(context, snapshot, avatarPreset),
    );
  }

  Widget _buildContent(
    BuildContext context,
    AiReadinessSnapshotModel snapshot,
    BodyAvatarPreset avatarPreset,
  ) {
    final scoreColor = _scoreColor(snapshot.readinessScore);
    final muscleColors =
        AiAnalyticsRepository.buildRecovery3DColorsMap(snapshot.muscleFatigueMap);

    final tappedFatigue = _selectedMuscleId != null
        ? (snapshot.muscleFatigueMap[_selectedMuscleId!] ?? 0.0)
        : null;

    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(aiReadinessProvider),
      child: ListView(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
        children: [
          // 1. Readiness Score Gauge Card (F20)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  SizedBox(
                    width: 82,
                    height: 82,
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        CircularProgressIndicator(
                          value: (snapshot.readinessScore / 100.0).clamp(0.0, 1.0),
                          strokeWidth: 9,
                          backgroundColor: AppColors.subtleSurface(context),
                          color: scoreColor,
                        ),
                        Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                snapshot.readinessScore.round().toString(),
                                style: TextStyle(
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                  color: scoreColor,
                                ),
                              ),
                              const Text('điểm', style: TextStyle(fontSize: 10)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Điểm Sẵn sàng Tập luyện',
                          style: TextStyle(
                            fontSize: 13,
                            color: AppColors.secondaryText(context),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _readinessHeadline(snapshot.readinessScore),
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                            color: scoreColor,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Ngày ${snapshot.targetDateIso}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // 2. AI Insights
          if (snapshot.insights.isNotEmpty)
            Card(
              color: AppColors.subtleSurface(context),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.auto_awesome,
                          color: AppColors.telemetryCyan(context),
                          size: 18,
                        ),
                        const SizedBox(width: 6),
                        const Expanded(
                          child: Text(
                            'Phân tích từ AI Sinh lý & Tập luyện',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ...snapshot.insights.map(
                      (line) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text('• $line', style: const TextStyle(fontSize: 13)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 12),

          // 3. 3D Muscle Recovery Map (F23) with Floating Camera HUD
          const Text(
            'Bản đồ Phục hồi Cơ bắp 3D (Chạm vào từng bó cơ)',
            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: BodyAvatarPreset.values.map((preset) {
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(
                      preset.shortLabelVi,
                      style: const TextStyle(fontSize: 12),
                    ),
                    selected: avatarPreset == preset,
                    visualDensity: VisualDensity.compact,
                    onSelected: (_) {
                      ref.read(bodyAvatarPresetProvider.notifier).state =
                          preset;
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(26),
            child: Stack(
              children: [
                if (_mountWebView)
                  Muscle3DViewerWidget(
                    glbAssetOrUrl: avatarPreset.baseMannequinAssetPath,
                    muscleColorsMap: muscleColors,
                    cameraPreset: _cameraPreset,
                    avatarPreset: avatarPreset,
                    isPlaying: false,
                    height: 330,
                    onMuscleTap: (matId) {
                      setState(() => _selectedMuscleId = matId);
                    },
                  )
                else
                  Container(
                    height: 330,
                    decoration: const BoxDecoration(
                      gradient: RadialGradient(
                        colors: [Color(0xFF192336), Color(0xFF090B0F)],
                        radius: 0.9,
                      ),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.accessibility_new_rounded,
                            size: 52,
                            color: AppColors.volt.withValues(alpha: 0.85),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            _isFlutterTest
                                ? 'Mô hình Phục hồi Cơ bắp 3D'
                                : 'Đang chuẩn bị mô hình 3D...',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                Positioned(
                  left: 12,
                  right: 12,
                  bottom: 12,
                  child: Row(
                    children: [
                      _CamBtn(
                        label: 'Trước',
                        selected: _cameraPreset == CameraPreset3D.front,
                        onTap: () =>
                            setState(() => _cameraPreset = CameraPreset3D.front),
                      ),
                      const SizedBox(width: 6),
                      _CamBtn(
                        label: 'Ngang',
                        selected: _cameraPreset == CameraPreset3D.side,
                        onTap: () =>
                            setState(() => _cameraPreset = CameraPreset3D.side),
                      ),
                      const SizedBox(width: 6),
                      _CamBtn(
                        label: 'Sau',
                        selected: _cameraPreset == CameraPreset3D.back,
                        onTap: () =>
                            setState(() => _cameraPreset = CameraPreset3D.back),
                      ),
                      const SizedBox(width: 6),
                      _CamBtn(
                        label: 'Trên',
                        selected: _cameraPreset == CameraPreset3D.top,
                        onTap: () =>
                            setState(() => _cameraPreset = CameraPreset3D.top),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          const Wrap(
            spacing: 10,
            runSpacing: 4,
            children: [
              _RecoveryLegend(
                color: AppColors.muscleRecoveredGreen,
                label: '75–100% Hồi phục (Sẵn sàng)',
              ),
              _RecoveryLegend(
                color: AppColors.muscleSecondaryOrange,
                label: '35–74% Đang phục hồi',
              ),
              _RecoveryLegend(
                color: AppColors.musclePrimaryRed,
                label: '0–34% Đang mỏi cao',
              ),
            ],
          ),
          if (_selectedMuscleId != null && tappedFatigue != null) ...[
            const SizedBox(height: 10),
            _buildMuscleTapPopup(
              _selectedMuscleId!,
              tappedFatigue,
            ),
          ],
          const SizedBox(height: 14),

          // 4. Smart Overload & Deload Recommendations (F21)
          const Text(
            'Đề xuất Mức tạ & Cảnh báo Quá tải',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
          ),
          const SizedBox(height: 8),
          if (snapshot.weightRecommendations.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(14),
                child: Text(
                  'Hãy hoàn thành 1–2 buổi tập để AI đề xuất tăng tiến tải trọng cho từng bài.',
                ),
              ),
            )
          else
            ...snapshot.weightRecommendations.map((rec) {
              final isDeload = rec.action == 'DELOAD';
              final isIncrease = rec.action == 'INCREASE';
              return Card(
                color: isDeload
                    ? AppColors.tintedSurface(context, AppColors.warningRed)
                    : isIncrease
                        ? AppColors.tintedSurface(
                            context,
                            AppColors.muscleRecoveredGreen,
                          )
                        : null,
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: (isDeload
                            ? AppColors.warningRed
                            : isIncrease
                                ? AppColors.muscleRecoveredGreen
                                : AppColors.primary)
                        .withValues(alpha: 0.14),
                    child: Icon(
                      isDeload
                          ? Icons.warning_amber_rounded
                          : isIncrease
                              ? Icons.trending_up
                              : Icons.balance,
                      color: isDeload
                          ? AppColors.warningRed
                          : isIncrease
                              ? AppColors.muscleRecoveredGreen
                              : AppColors.primary,
                    ),
                  ),
                  title: Text(
                    '${rec.exerciseCode} · ${rec.action}',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  subtitle: Text(
                    'Đề xuất: ${rec.recommendedWeightKg} kg × ${rec.recommendedReps} reps\n${rec.reason}',
                  ),
                  trailing: TextButton(
                    onPressed: () => context
                        .push('/workout/live?exerciseCode=${rec.exerciseCode}'),
                    child: const Text('Tập'),
                  ),
                ),
              );
            }),
          const SizedBox(height: 8),
          Card(
            color: AppColors.tintedSurface(context, AppColors.calorieOrange),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(
                    Icons.health_and_safety_outlined,
                    color: AppColors.calorieOrange,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      snapshot.disclaimer,
                      style: const TextStyle(fontSize: 12),
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

  Widget _buildMuscleTapPopup(String matId, double fatigue) {
    final recoveryPct = ((1.0 - fatigue) * 100.0).round().clamp(0, 100);
    final etaHours =
        AiAnalyticsRepository.estimatedHoursToFullRecovery(matId, fatigue);
    final color = AiAnalyticsRepository.recoveryColorForFatigue(fatigue);

    return Card(
      color: color.withValues(alpha: 0.12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: color),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Text(
            '$recoveryPct%',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          MuscleMaterialIds.labelVi(matId),
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '${AiAnalyticsRepository.recoveryStatusLabel(fatigue)}\n'
          '${etaHours == 0 ? "Đã hồi phục hoàn toàn" : "Dự kiến đạt 100% sau ~$etaHours giờ"}',
        ),
        trailing: IconButton(
          icon: const Icon(Icons.close, size: 18),
          onPressed: () => setState(() => _selectedMuscleId = null),
        ),
      ),
    );
  }
}

class _CamBtn extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _CamBtn({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(100),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: selected
                ? AppColors.volt
                : Colors.black.withValues(alpha: 0.65),
            borderRadius: BorderRadius.circular(100),
            border: Border.all(
              color: selected
                  ? AppColors.volt
                  : Colors.white.withValues(alpha: 0.16),
            ),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
              color: selected ? const Color(0xFF090B0F) : Colors.white,
            ),
          ),
        ),
      ),
    );
  }
}

class _RecoveryLegend extends StatelessWidget {
  final Color color;
  final String label;

  const _RecoveryLegend({required this.color, required this.label});

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
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11)),
      ],
    );
  }
}
