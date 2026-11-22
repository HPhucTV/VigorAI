// [OWNER: M2] Man hinh Chi tiet Bai tap 3D: Xoay 360, 4 Goc nhin, Dung/Sai, Timeline 3 Pha & Avatar (T-M2-03, T-M2-08 / F07-F13)
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/feature_flags.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../data/asset_cache_manager.dart';
import '../data/exercise_repository.dart';
import 'widgets/muscle_3d_viewer_widget.dart';

class Exercise3DDetailScreen extends ConsumerStatefulWidget {
  final String exerciseCode;

  const Exercise3DDetailScreen({super.key, required this.exerciseCode});

  @override
  ConsumerState<Exercise3DDetailScreen> createState() =>
      _Exercise3DDetailScreenState();
}

class _Exercise3DDetailScreenState
    extends ConsumerState<Exercise3DDetailScreen> {
  CameraPreset3D _cameraPreset = CameraPreset3D.front;
  bool _showBadForm = false;
  double _playbackSpeed = 1.0;
  bool _isPlaying = true;
  bool _isViewerLoaded = false;
  double _phaseProgress = 0.0;
  double? _manualSeekProgress;
  Timer? _phaseTimer;
  String? _tappedMuscleId;
  Future<String>? _resolvedGlbFuture;
  String? _resolvedForCode;

  @override
  void initState() {
    super.initState();
    _phaseTimer = Timer.periodic(const Duration(milliseconds: 100), (_) {
      if (!mounted || !_isPlaying || !_isViewerLoaded) return;
      setState(() {
        _phaseProgress = (_phaseProgress + 0.03 * _playbackSpeed) % 1.0;
      });
    });
  }

  @override
  void dispose() {
    _phaseTimer?.cancel();
    _phaseTimer = null;
    super.dispose();
  }

  ({String label, String breath, Color color, int index}) _activePhaseInfo(
    ExerciseModel ex,
    double progress,
  ) {
    final kf = ex.phaseKeyframes;
    if (progress < kf.eccentric.end) {
      return (
        label: '1. Hạ tạ',
        breath: kf.eccentric.breath,
        color: AppColors.hydrationBlue,
        index: 0,
      );
    }
    if (progress < kf.isometric.end) {
      return (
        label: '2. Giữ đáy',
        breath: kf.isometric.breath,
        color: AppColors.calorieOrange,
        index: 1,
      );
    }
    return (
      label: '3. Phát lực',
      breath: kf.concentric.breath,
      color: AppColors.muscleRecoveredGreen,
      index: 2,
    );
  }

  void _jumpToPhase(double normalizedTarget) {
    setState(() {
      _isPlaying = false;
      _phaseProgress = normalizedTarget.clamp(0.0, 1.0);
      _manualSeekProgress = _phaseProgress;
    });
  }

  Map<String, Color> _buildHeatmapColors(ExerciseModel ex) {
    final map = <String, Color>{};
    for (final m in ex.stabilizerMuscles) {
      map[m] = AppColors.muscleStabilizerYellow;
    }
    for (final m in ex.secondaryMuscles) {
      map[m] = AppColors.muscleSecondaryOrange;
    }
    for (final m in ex.primaryMuscles) {
      map[m] = AppColors.musclePrimaryRed;
    }
    return map;
  }

  String _muscleRoleLabel(ExerciseModel ex, String matId) {
    if (ex.primaryMuscles.contains(matId)) return 'Cơ chính chịu tải (Primary)';
    if (ex.secondaryMuscles.contains(matId)) {
      return 'Cơ phụ trợ lực (Secondary)';
    }
    if (ex.stabilizerMuscles.contains(matId)) {
      return 'Cơ giữ thăng bằng (Stabilizer)';
    }
    return 'Nhóm cơ không chịu tải chính';
  }

  String _formatSetupKey(String key) {
    switch (key) {
      case 'rack_height':
        return 'Độ cao chốt Rack';
      case 'bench_angle_deg':
        return 'Góc ghế Bench (°)';
      case 'grip_width':
        return 'Độ rộng nắm tạ';
      case 'hand_width':
        return 'Khoảng cách đặt tay';
      case 'pulley_height':
        return 'Vị trí ròng rọc';
      case 'grip':
        return 'Cách nắm tay';
      default:
        return key;
    }
  }

  @override
  Widget build(BuildContext context) {
    final exerciseAsync = ref.watch(exerciseByCodeProvider(widget.exerciseCode));
    final avatarPreset = ref.watch(bodyAvatarPresetProvider);

    return exerciseAsync.when(
      loading: () => Scaffold(
        appBar: AppBar(title: const Text('Đang tải bài tập 3D...')),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => Scaffold(
        appBar: AppBar(title: const Text('Lỗi tải dữ liệu')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.error_outline,
                  size: 42,
                  color: AppColors.warningRed,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Không thể tải chi tiết bài tập 3D lúc này. Vui lòng thử lại.',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      ref.invalidate(exerciseByCodeProvider(widget.exerciseCode)),
                  child: const Text('Thử lại'),
                ),
              ],
            ),
          ),
        ),
      ),
      data: (exercise) {
        if (exercise == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Không tìm thấy bài tập')),
            body: Center(
              child: Text('Không tìm thấy mã bài tập ${widget.exerciseCode}.'),
            ),
          );
        }

        if (_resolvedForCode != exercise.code) {
          _resolvedForCode = exercise.code;
          _isViewerLoaded = false;
          _phaseProgress = 0.0;
          _resolvedGlbFuture =
              ref.read(assetCacheManagerProvider).getOrDownloadGlb(
                    exerciseCode: exercise.code,
                    remoteUrl: exercise.model3dGlbUrl,
                    expectedSha256: exercise.assetChecksum,
                  );
        }

        final muscleColors = _buildHeatmapColors(exercise);
        final activeClip = (_showBadForm && exercise.hasBadFormClip)
            ? 'Anim_BadForm'
            : 'Anim_GoodForm';
        final phaseInfo = _activePhaseInfo(exercise, _phaseProgress);

        return Scaffold(
          appBar: AppBar(
            title: Text(exercise.nameVi),
          ),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 1. 3D Interactive Viewport + Live Phase/BadForm Overlay (F07-F13)
              FutureBuilder<String>(
                future: _resolvedGlbFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Container(
                      height: 340,
                      decoration: BoxDecoration(
                        color: const Color(0xFF12161F),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(),
                            SizedBox(height: 10),
                            Text(
                              'Đang nạp mô hình 3D...',
                              style: TextStyle(color: Colors.white70),
                            ),
                          ],
                        ),
                      ),
                    );
                  }
                  if (snapshot.hasError) {
                    return Container(
                      height: 340,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Center(
                        child: Text(
                          'Không tải được mô hình 3D: ${snapshot.error}',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    );
                  }
                  final src = snapshot.data ?? exercise.model3dGlbUrl;
                  return Stack(
                    children: [
                      Muscle3DViewerWidget(
                        glbAssetOrUrl: src,
                        muscleColorsMap: muscleColors,
                        animationName: activeClip,
                        playbackSpeed: _playbackSpeed,
                        cameraPreset: _cameraPreset,
                        isPlaying: _isPlaying,
                        normalizedProgress: _manualSeekProgress,
                        avatarPreset: avatarPreset,
                        height: 340,
                        onModelLoaded: () {
                          if (mounted && !_isViewerLoaded) {
                            setState(() {
                              _isViewerLoaded = true;
                              _phaseProgress = 0.0;
                            });
                          }
                        },
                        onMuscleTap: (matId) {
                          setState(() => _tappedMuscleId = matId);
                        },
                      ),
                      Positioned(
                        top: 10,
                        left: 10,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 5,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.68),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: phaseInfo.color.withValues(alpha: 0.85),
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.air, size: 14, color: phaseInfo.color),
                              const SizedBox(width: 6),
                              Text(
                                '${phaseInfo.label} · ${phaseInfo.breath}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      if (_showBadForm)
                        Positioned(
                          top: 10,
                          right: 10,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.warningRed.withValues(alpha: 0.92),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.warning_amber_rounded,
                                    size: 14, color: Colors.white),
                                SizedBox(width: 4),
                                Text(
                                  'LỖI SAI CHẤN THƯƠNG',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 10),

              // 2. 4 Camera Angle Presets (F08: < 300ms)
              Row(
                children: [
                  _CameraChip(
                    label: 'Trước',
                    selected: _cameraPreset == CameraPreset3D.front,
                    onTap: () =>
                        setState(() => _cameraPreset = CameraPreset3D.front),
                  ),
                  const SizedBox(width: 6),
                  _CameraChip(
                    label: 'Ngang',
                    selected: _cameraPreset == CameraPreset3D.side,
                    onTap: () =>
                        setState(() => _cameraPreset = CameraPreset3D.side),
                  ),
                  const SizedBox(width: 6),
                  _CameraChip(
                    label: 'Sau',
                    selected: _cameraPreset == CameraPreset3D.back,
                    onTap: () =>
                        setState(() => _cameraPreset = CameraPreset3D.back),
                  ),
                  const SizedBox(width: 6),
                  _CameraChip(
                    label: 'Trên',
                    selected: _cameraPreset == CameraPreset3D.top,
                    onTap: () =>
                        setState(() => _cameraPreset = CameraPreset3D.top),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // 3. Good Form vs Bad Form Switch + Speed / Play Controls (F10, F11)
              Row(
                children: [
                  if (exercise.hasBadFormClip)
                    Expanded(
                      child: SegmentedButton<bool>(
                        segments: const [
                          ButtonSegment<bool>(
                            value: false,
                            icon: Icon(Icons.check_circle_outline, size: 18),
                            label: Text('Chuẩn'),
                          ),
                          ButtonSegment<bool>(
                            value: true,
                            icon: Icon(Icons.warning_amber_rounded, size: 18),
                            label: Text('Lỗi sai'),
                          ),
                        ],
                        selected: <bool>{_showBadForm},
                        onSelectionChanged: (s) {
                          setState(() => _showBadForm = s.first);
                        },
                      ),
                    )
                  else
                    const Expanded(
                      child: Text(
                        'Chế độ Tư thế chuẩn',
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                  const SizedBox(width: 8),
                  IconButton.filledTonal(
                    tooltip: _isPlaying ? 'Tạm dừng' : 'Phát',
                    onPressed: () {
                      setState(() {
                        _isPlaying = !_isPlaying;
                        if (_isPlaying) {
                          _manualSeekProgress = null;
                        }
                      });
                    },
                    icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                  ),
                  const SizedBox(width: 4),
                  ActionChip(
                    label: Text('${_playbackSpeed}x'),
                    onPressed: () {
                      setState(() {
                        if (_playbackSpeed == 1.0) {
                          _playbackSpeed = 0.5;
                        } else if (_playbackSpeed == 0.5) {
                          _playbackSpeed = 0.25;
                        } else {
                          _playbackSpeed = 1.0;
                        }
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // 3b. Timeline Scrubber & 3-Phase Jump Buttons (F11)
              Card(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(12, 8, 12, 10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Tua từng pha (${(_phaseProgress * 100).round()}%)',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Flexible(
                            child: Text(
                              '${phaseInfo.label} · ${phaseInfo.breath}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              textAlign: TextAlign.end,
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                color: phaseInfo.color,
                              ),
                            ),
                          ),
                        ],
                      ),
                      Slider(
                        value: _phaseProgress.clamp(0.0, 1.0),
                        onChanged: (val) => _jumpToPhase(val),
                      ),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => _jumpToPhase(
                                (exercise.phaseKeyframes.eccentric.start +
                                        exercise.phaseKeyframes.eccentric.end) *
                                    0.5,
                              ),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 6),
                                side: BorderSide(
                                  color: phaseInfo.index == 0
                                      ? AppColors.hydrationBlue
                                      : Colors.grey.shade400,
                                ),
                              ),
                              child: const Text('1. Hạ tạ',
                                  style: TextStyle(fontSize: 12)),
                            ),
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => _jumpToPhase(
                                (exercise.phaseKeyframes.isometric.start +
                                        exercise.phaseKeyframes.isometric.end) *
                                    0.5,
                              ),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 6),
                                side: BorderSide(
                                  color: phaseInfo.index == 1
                                      ? AppColors.calorieOrange
                                      : Colors.grey.shade400,
                                ),
                              ),
                              child: const Text('2. Giữ đáy',
                                  style: TextStyle(fontSize: 12)),
                            ),
                          ),
                          const SizedBox(width: 6),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => _jumpToPhase(
                                (exercise.phaseKeyframes.concentric.start +
                                        exercise.phaseKeyframes.concentric.end) *
                                    0.5,
                              ),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 6),
                                side: BorderSide(
                                  color: phaseInfo.index == 2
                                      ? AppColors.muscleRecoveredGreen
                                      : Colors.grey.shade400,
                                ),
                              ),
                              child: const Text('3. Phát lực',
                                  style: TextStyle(fontSize: 12)),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),

              // 3c. Body Avatar Selector (F13)
              Row(
                children: [
                  const Text(
                    'Avatar:',
                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: BodyAvatarPreset.values.map((preset) {
                          return Padding(
                            padding: const EdgeInsets.only(right: 6),
                            child: ChoiceChip(
                              label: Text(preset.shortLabelVi),
                              selected: avatarPreset == preset,
                              visualDensity: VisualDensity.compact,
                              onSelected: (_) {
                                ref
                                    .read(bodyAvatarPresetProvider.notifier)
                                    .state = preset;
                              },
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // 4. Muscle Tap Feedback + Interactive Muscle Chips (F09)
              if (_tappedMuscleId != null)
                Card(
                  color: const Color(0xFFEDE7F6),
                  child: ListTile(
                    dense: true,
                    leading: const Icon(Icons.touch_app, color: AppColors.primary),
                    title: Text(
                      MuscleMaterialIds.labelVi(_tappedMuscleId!),
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(_muscleRoleLabel(exercise, _tappedMuscleId!)),
                    trailing: IconButton(
                      icon: const Icon(Icons.close, size: 18),
                      onPressed: () => setState(() => _tappedMuscleId = null),
                    ),
                  ),
                ),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  ...exercise.primaryMuscles.map(
                    (m) => ActionChip(
                      avatar: const CircleAvatar(
                        backgroundColor: AppColors.musclePrimaryRed,
                        radius: 6,
                      ),
                      label: Text(
                        'Chính: ${MuscleMaterialIds.labelVi(m).split(' (').first}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      onPressed: () => setState(() => _tappedMuscleId = m),
                    ),
                  ),
                  ...exercise.secondaryMuscles.map(
                    (m) => ActionChip(
                      avatar: const CircleAvatar(
                        backgroundColor: AppColors.muscleSecondaryOrange,
                        radius: 6,
                      ),
                      label: Text(
                        'Phụ: ${MuscleMaterialIds.labelVi(m).split(' (').first}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      onPressed: () => setState(() => _tappedMuscleId = m),
                    ),
                  ),
                  ...exercise.stabilizerMuscles.map(
                    (m) => ActionChip(
                      avatar: const CircleAvatar(
                        backgroundColor: AppColors.muscleStabilizerYellow,
                        radius: 6,
                      ),
                      label: Text(
                        'Giữ: ${MuscleMaterialIds.labelVi(m).split(' (').first}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      onPressed: () => setState(() => _tappedMuscleId = m),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // 5. Phase & Breathing Guide
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Nhịp 3 Pha Chuyển động & Hít thở',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      _PhaseRow(
                        phase: '1. Hạ tạ (Eccentric)',
                        breath: exercise.phaseKeyframes.eccentric.breath,
                      ),
                      _PhaseRow(
                        phase: '2. Giữ đáy (Isometric)',
                        breath: exercise.phaseKeyframes.isometric.breath,
                      ),
                      _PhaseRow(
                        phase: '3. Phát lực (Concentric)',
                        breath: exercise.phaseKeyframes.concentric.breath,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),

              // 6. Setup Guide (F12)
              if (exercise.setupGuide.isNotEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Thiết lập Dụng cụ & Tư thế ban đầu',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 6),
                        ...exercise.setupGuide.entries.map(
                          (e) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text(
                              '• ${_formatSetupKey(e.key)}: ${e.value}',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 10),

              // 7. Bad Form Warnings (F10)
              if (exercise.badFormWarnings.isNotEmpty)
                Card(
                  color: _showBadForm
                      ? const Color(0xFFFFEBEE)
                      : const Color(0xFFFFF8E1),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.warning_amber_rounded,
                              color: _showBadForm
                                  ? AppColors.warningRed
                                  : AppColors.calorieOrange,
                            ),
                            const SizedBox(width: 8),
                            const Text(
                              'Lỗi sai cần tránh & Cách khắc phục',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        ...exercise.badFormWarnings.map(
                          (w) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text('• $w'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              if (!FeatureFlags.isMvpClosedTesting) ...[
                const SizedBox(height: 14),
                FilledButton.icon(
                  onPressed: () =>
                      context.push('/workout/live?exerciseCode=${exercise.code}'),
                  icon: const Icon(Icons.fitness_center),
                  label: const Text('Bắt đầu tập bài này ngay'),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

class _CameraChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _CameraChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: ChoiceChip(
        label: Center(child: Text(label)),
        selected: selected,
        showCheckmark: false,
        onSelected: (_) => onTap(),
      ),
    );
  }
}

class _PhaseRow extends StatelessWidget {
  final String phase;
  final String breath;

  const _PhaseRow({required this.phase, required this.breath});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(phase),
          Text(
            breath,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}
