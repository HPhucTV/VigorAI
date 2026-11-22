// [OWNER: M2] Man hinh AI Readiness Dashboard, Ban do Phuc hoi Co bap 3D & Goi y Tai trong (T-M2-10 / F20, F21, F23)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/database/ai_cache_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import '../data/ai_analytics_repository.dart';

class ReadinessRecovery3DView extends ConsumerStatefulWidget {
  const ReadinessRecovery3DView({super.key});

  @override
  ConsumerState<ReadinessRecovery3DView> createState() =>
      _ReadinessRecovery3DViewState();
}

class _ReadinessRecovery3DViewState
    extends ConsumerState<ReadinessRecovery3DView> {
  CameraPreset3D _cameraPreset = CameraPreset3D.front;
  String? _selectedMuscleId;

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
        padding: const EdgeInsets.all(16),
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
                          backgroundColor: Colors.grey.shade200,
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
                        const Text(
                          'Điểm Sẵn sàng Tập luyện',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.black54,
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
              color: const Color(0xFFF3F6FB),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome, color: AppColors.primary, size: 18),
                        SizedBox(width: 6),
                        Text(
                          'Phân tích từ AI Sinh lý & Tập luyện',
                          style: TextStyle(fontWeight: FontWeight.bold),
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

          // 3. 3D Muscle Recovery Map (F23)
          const Text(
            'Bản đồ Phục hồi Cơ bắp 3D (Chạm vào từng bó cơ)',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
          ),
          const SizedBox(height: 8),
          Muscle3DViewerWidget(
            glbAssetOrUrl: avatarPreset.baseMannequinAssetPath,
            muscleColorsMap: muscleColors,
            cameraPreset: _cameraPreset,
            avatarPreset: avatarPreset,
            isPlaying: false,
            height: 320,
            onMuscleTap: (matId) {
              setState(() => _selectedMuscleId = matId);
            },
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _CamBtn(
                label: 'Trước',
                selected: _cameraPreset == CameraPreset3D.front,
                onTap: () => setState(() => _cameraPreset = CameraPreset3D.front),
              ),
              const SizedBox(width: 6),
              _CamBtn(
                label: 'Ngang',
                selected: _cameraPreset == CameraPreset3D.side,
                onTap: () => setState(() => _cameraPreset = CameraPreset3D.side),
              ),
              const SizedBox(width: 6),
              _CamBtn(
                label: 'Sau',
                selected: _cameraPreset == CameraPreset3D.back,
                onTap: () => setState(() => _cameraPreset = CameraPreset3D.back),
              ),
              const SizedBox(width: 6),
              _CamBtn(
                label: 'Trên',
                selected: _cameraPreset == CameraPreset3D.top,
                onTap: () => setState(() => _cameraPreset = CameraPreset3D.top),
              ),
            ],
          ),
          const SizedBox(height: 8),
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
                    ? const Color(0xFFFFEBEE)
                    : isIncrease
                        ? const Color(0xFFE8F5E9)
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
            color: const Color(0xFFFFF8E1),
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
      child: ChoiceChip(
        label: Center(child: Text(label, style: const TextStyle(fontSize: 12))),
        selected: selected,
        showCheckmark: false,
        visualDensity: VisualDensity.compact,
        onSelected: (_) => onTap(),
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
