// [OWNER: M2] Man hinh Chi tiet Bai tap 3D: Xoay 360, 4 Goc nhin, Dung/Sai, Timeline 3 Pha & Avatar (T-M2-03, T-M2-08 / F07-F13)
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/feature_flags.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../data/asset_cache_manager.dart';
import '../data/exercise_coaching_guide.dart';
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
      case 'seat_height':
        return 'Chiều cao ghế';
      case 'stance':
        return 'Độ rộng chân đứng';
      case 'range_of_motion':
        return 'Biên độ chuyển động';
      case 'torso_angle_deg':
        return 'Góc gập thân (°)';
      case 'thigh_pad':
        return 'Đệm khóa đùi';
      case 'foot_plate':
        return 'Bàn đạp chân';
      case 'bar_position':
        return 'Vị trí thanh đòn';
      case 'arm_angle':
        return 'Góc khuỷu tay';
      case 'elbow_position':
        return 'Vị trí khuỷu tay';
      case 'knee_bend':
        return 'Độ chùng gối';
      case 'foot_placement':
        return 'Vị trí đặt chân';
      case 'pad_position':
        return 'Vị trí đệm lăn';
      case 'step_length':
        return 'Độ dài bước chân';
      case 'bench_position':
        return 'Vị trí tựa ghế';
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
        final coaching = ExerciseCoachingGuide.forExercise(exercise);
        final primaryColor = Theme.of(context).colorScheme.primary;

        return Scaffold(
          appBar: AppBar(
            title: Text(exercise.nameVi),
          ),
          body: ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
            children: [
              // 1. Immersive 3D Interactive Stage + Floating Smoked-Glass HUD (F07-F13)
              FutureBuilder<String>(
                future: _resolvedGlbFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Container(
                      height: 370,
                      decoration: BoxDecoration(
                        gradient: const RadialGradient(
                          colors: [Color(0xFF192336), Color(0xFF090B0F)],
                          radius: 0.9,
                        ),
                        borderRadius: BorderRadius.circular(28),
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(color: AppColors.volt),
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
                      height: 370,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppColors.tintedSurface(
                          context,
                          AppColors.warningRed,
                        ),
                        borderRadius: BorderRadius.circular(28),
                      ),
                      child: Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.cloud_off_rounded,
                              size: 40,
                              color: AppColors.warningRed,
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Chưa tải được mô hình 3D từ máy chủ. Vui lòng kiểm tra kết nối mạng và thử lại.',
                              textAlign: TextAlign.center,
                              style: TextStyle(height: 1.4),
                            ),
                            const SizedBox(height: 12),
                            FilledButton.icon(
                              onPressed: () {
                                setState(() {
                                  _isViewerLoaded = false;
                                  _resolvedGlbFuture = ref
                                      .read(assetCacheManagerProvider)
                                      .getOrDownloadGlb(
                                        exerciseCode: exercise.code,
                                        remoteUrl: exercise.model3dGlbUrl,
                                        expectedSha256: exercise.assetChecksum,
                                      );
                                });
                              },
                              icon: const Icon(Icons.refresh),
                              label: const Text('Thử lại'),
                            ),
                          ],
                        ),
                      ),
                    );
                  }
                  final src = snapshot.data ?? exercise.model3dGlbUrl;
                  return ClipRRect(
                    borderRadius: BorderRadius.circular(28),
                    child: Stack(
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
                          height: 370,
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
                          top: 12,
                          left: 12,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.72),
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
                            top: 12,
                            right: 12,
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
                                  Icon(
                                    Icons.warning_amber_rounded,
                                    size: 14,
                                    color: Colors.white,
                                  ),
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
                        // Floating Camera Angle Pills on 3D Stage
                        Positioned(
                          left: 12,
                          right: 12,
                          bottom: 12,
                          child: Row(
                            children: [
                              _CameraChip(
                                label: 'Trước',
                                selected: _cameraPreset == CameraPreset3D.front,
                                onTap: () => setState(
                                  () => _cameraPreset = CameraPreset3D.front,
                                ),
                              ),
                              const SizedBox(width: 6),
                              _CameraChip(
                                label: 'Ngang',
                                selected: _cameraPreset == CameraPreset3D.side,
                                onTap: () => setState(
                                  () => _cameraPreset = CameraPreset3D.side,
                                ),
                              ),
                              const SizedBox(width: 6),
                              _CameraChip(
                                label: 'Sau',
                                selected: _cameraPreset == CameraPreset3D.back,
                                onTap: () => setState(
                                  () => _cameraPreset = CameraPreset3D.back,
                                ),
                              ),
                              const SizedBox(width: 6),
                              _CameraChip(
                                label: 'Trên',
                                selected: _cameraPreset == CameraPreset3D.top,
                                onTap: () => setState(
                                  () => _cameraPreset = CameraPreset3D.top,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
              const SizedBox(height: 14),

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
                  color: AppColors.tintedSurface(context, primaryColor),
                  child: ListTile(
                    dense: true,
                    leading: Icon(Icons.touch_app, color: primaryColor),
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
              const SizedBox(height: 14),

              // 5. Cam nang Ky thuat 4 Phan Truc quan (Ket noi 3D & Timeline)
              // Phan 1: Chuan bi Tu the & Diem tua
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.settings_accessibility_outlined,
                            color: primaryColor,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Text(
                              '1. Chuẩn bị Tư thế & Điểm tựa',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ...coaching.setupSteps.asMap().entries.map(
                            (entry) => Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  CircleAvatar(
                                    radius: 10,
                                    backgroundColor: AppColors.tintedSurface(
                                      context,
                                      primaryColor,
                                    ),
                                    child: Text(
                                      '${entry.key + 1}',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.bold,
                                        color: primaryColor,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      entry.value,
                                      style: const TextStyle(height: 1.35),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                      if (exercise.setupGuide.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: exercise.setupGuide.entries
                              .map(
                                (e) => Chip(
                                  visualDensity: VisualDensity.compact,
                                  label: Text(
                                    '${_formatSetupKey(e.key)}: ${e.value}',
                                    style: const TextStyle(fontSize: 11.5),
                                  ),
                                ),
                              )
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),

              // Phan 2: Chuyen dong 3 Pha & Nhip tho (cham de tua 3D)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.air, color: primaryColor, size: 20),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Text(
                              '2. Chuyển động 3 Pha & Nhịp thở',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chạm vào từng pha để tua trực tiếp mô hình 3D đến điểm kỹ thuật tương ứng.',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.secondaryText(context),
                        ),
                      ),
                      const SizedBox(height: 10),
                      _PhaseDetailTile(
                        title: 'Pha 1 — Hạ tạ / Giãn cơ (${exercise.phaseKeyframes.eccentric.breath})',
                        detail: coaching.eccentricDetail,
                        accent: AppColors.hydrationBlue,
                        active: phaseInfo.index == 0,
                        onTap: () => _jumpToPhase(
                          (exercise.phaseKeyframes.eccentric.start +
                                  exercise.phaseKeyframes.eccentric.end) *
                              0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _PhaseDetailTile(
                        title: 'Pha 2 — Giữ đáy / Điểm căng (${exercise.phaseKeyframes.isometric.breath})',
                        detail: coaching.isometricDetail,
                        accent: AppColors.calorieOrange,
                        active: phaseInfo.index == 1,
                        onTap: () => _jumpToPhase(
                          (exercise.phaseKeyframes.isometric.start +
                                  exercise.phaseKeyframes.isometric.end) *
                              0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _PhaseDetailTile(
                        title: 'Pha 3 — Phát lực / Đẩy lên (${exercise.phaseKeyframes.concentric.breath})',
                        detail: coaching.concentricDetail,
                        accent: AppColors.muscleRecoveredGreen,
                        active: phaseInfo.index == 2,
                        onTap: () => _jumpToPhase(
                          (exercise.phaseKeyframes.concentric.start +
                                  exercise.phaseKeyframes.concentric.end) *
                              0.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),

              // Phan 3: Cam nhan Co bap Dung (Mind-Muscle Connection)
              Card(
                color: AppColors.tintedSurface(
                  context,
                  AppColors.muscleRecoveredGreen,
                  lightAlpha: 0.08,
                  darkAlpha: 0.14,
                ),
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(
                            Icons.psychology_outlined,
                            color: AppColors.muscleRecoveredGreen,
                            size: 20,
                          ),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              '3. Cảm nhận Cơ bắp Đúng',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        coaching.mindMuscleCue,
                        style: const TextStyle(height: 1.4),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Chú thích màu trên 3D: Đỏ (Cơ chính) · Cam (Cơ phụ) · Vàng (Cơ giữ thăng bằng).',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.secondaryText(context),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),

              // Phan 4: Phan tich Loi sai & Cach sua (lien ket nut Loi sai 3D)
              Card(
                color: AppColors.tintedSurface(
                  context,
                  _showBadForm ? AppColors.warningRed : AppColors.calorieOrange,
                  lightAlpha: _showBadForm ? 0.12 : 0.08,
                  darkAlpha: _showBadForm ? 0.22 : 0.14,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                  side: BorderSide(
                    color: (_showBadForm
                            ? AppColors.warningRed
                            : AppColors.calorieOrange)
                        .withValues(alpha: _showBadForm ? 0.85 : 0.35),
                    width: _showBadForm ? 1.5 : 1.0,
                  ),
                ),
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
                          Expanded(
                            child: Text(
                              _showBadForm
                                  ? '4. Đang mô phỏng Lỗi sai trên 3D'
                                  : '4. Phân tích Lỗi sai & Cách sửa',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ...coaching.badFormDetails.map(
                        (item) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '❌ Lỗi: ${item.error}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  height: 1.35,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '⚠️ Tác hại: ${item.risk}',
                                style: TextStyle(
                                  fontSize: 12.5,
                                  height: 1.35,
                                  color: AppColors.secondaryText(context),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '✅ Cách sửa: ${item.fix}',
                                style: const TextStyle(
                                  fontSize: 12.5,
                                  height: 1.35,
                                  color: AppColors.muscleRecoveredGreen,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
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

class _PhaseDetailTile extends StatelessWidget {
  final String title;
  final String detail;
  final Color accent;
  final bool active;
  final VoidCallback onTap;

  const _PhaseDetailTile({
    required this.title,
    required this.detail,
    required this.accent,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: active
              ? AppColors.tintedSurface(context, accent, lightAlpha: 0.12, darkAlpha: 0.22)
              : AppColors.subtleSurface(context),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: active
                ? accent.withValues(alpha: 0.8)
                : AppColors.subtleBorder(context),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 13,
                color: accent,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              detail,
              style: const TextStyle(fontSize: 12.5, height: 1.35),
            ),
          ],
        ),
      ),
    );
  }
}
