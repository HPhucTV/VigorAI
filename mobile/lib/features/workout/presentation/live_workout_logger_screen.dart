// [OWNER: M2] Man hinh Ghi chep Buoi tap Offline-First, Rest Timer, 1RM, Plate Calculator, Swapper & AI Overload (T-M2-09, T-M2-10 / F14-F18, F21, F25)
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/database/ai_cache_tables.drift.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../../ai_analytics/data/ai_analytics_repository.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../data/workout_repository.dart';
import '../domain/workout_calculators.dart';
import 'widgets/exercise_swapper_sheet.dart';
import 'widgets/plate_calculator_sheet.dart';

class _DraftSetRow {
  static int _nextRowId = 0;

  final String rowKey;
  int inputVersion = 0;
  String? persistedSetId;
  int setNumber;
  String setType; // WARMUP | NORMAL | DROPSET | SUPERSET | FAILURE
  double weightKg;
  int reps;
  double rpe;
  bool isCompleted;
  double estimated1rm;
  bool isPr;
  String? lockedExerciseCode;
  String? lockedExerciseNameVi;

  _DraftSetRow({
    this.persistedSetId,
    required this.setNumber,
    this.setType = 'NORMAL',
    this.weightKg = 60.0,
    this.reps = 8,
    this.rpe = 7.5,
    this.isCompleted = false,
    this.estimated1rm = 0.0,
    this.isPr = false,
    this.lockedExerciseCode,
    this.lockedExerciseNameVi,
  }) : rowKey = 'row-${_nextRowId++}';
}

class _WorkoutExerciseBlock {
  ExerciseModel exercise;
  int defaultRestSeconds;
  int? supersetGroupId;
  List<_DraftSetRow> rows;

  _WorkoutExerciseBlock({
    required this.exercise,
    required this.defaultRestSeconds,
    this.supersetGroupId,
    required this.rows,
  });
}

class LiveWorkoutLoggerScreen extends ConsumerStatefulWidget {
  final String? initialRoutineId;
  final String? initialExerciseCode;

  const LiveWorkoutLoggerScreen({
    super.key,
    this.initialRoutineId,
    this.initialExerciseCode,
  });

  @override
  ConsumerState<LiveWorkoutLoggerScreen> createState() =>
      _LiveWorkoutLoggerScreenState();
}

class _LiveWorkoutLoggerScreenState
    extends ConsumerState<LiveWorkoutLoggerScreen> {
  bool _isLoading = true;
  bool _isFinishing = false;
  bool _useLbs = false;
  bool _restoredFromCrash = false;

  WorkoutSessionModel? _activeSession;
  final List<_WorkoutExerciseBlock> _blocks = [];
  Map<String, WeightRecommendationModel> _aiRecByCode = {};
  String _aiDisclaimer =
      'Gợi ý tải trọng do AI phân tích chỉ phục vụ mục đích tham khảo thể hình, hãy dừng tập ngay nếu thấy đau khớp bất thường.';

  Timer? _sessionClockTimer;
  int _elapsedSeconds = 0;

  Timer? _restTimer;
  int _restRemainingSeconds = 0;
  bool _isResting = false;

  @override
  void initState() {
    super.initState();
    _initWorkout();
    _sessionClockTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || _activeSession == null) return;
      setState(() {
        _elapsedSeconds = DateTime.now()
            .toUtc()
            .difference(_activeSession!.startedAt)
            .inSeconds
            .clamp(0, 86400);
      });
    });
  }

  @override
  void dispose() {
    _sessionClockTimer?.cancel();
    _restTimer?.cancel();
    super.dispose();
  }

  Future<void> _initWorkout() async {
    setState(() => _isLoading = true);
    final repo = ref.read(workoutRepositoryProvider);
    final exRepo = ref.read(exerciseRepositoryProvider);
    final allExercises = await exRepo.loadExercises();
    final exByCode = <String, ExerciseModel>{
      for (final ex in allExercises) ex.code.toUpperCase(): ex,
    };

    try {
      final readiness = await ref.read(aiReadinessProvider.future);
      _aiRecByCode = {
        for (final r in readiness.weightRecommendations)
          r.exerciseCode.toUpperCase(): r,
      };
      _aiDisclaimer = readiness.disclaimer;
    } catch (_) {}

    // 1. Check Crash-Safe active IN_PROGRESS session (F15)
    final activeSnapshot = await repo.getActiveInProgressSession();
    if (activeSnapshot != null &&
        widget.initialRoutineId == null &&
        widget.initialExerciseCode == null) {
      _restoredFromCrash = true;
      _activeSession = activeSnapshot.session;
      _elapsedSeconds = DateTime.now()
          .toUtc()
          .difference(activeSnapshot.session.startedAt)
          .inSeconds
          .clamp(0, 86400);

      final grouped = <String, List<WorkoutSetModel>>{};
      for (final s in activeSnapshot.sets) {
        grouped.putIfAbsent(s.exerciseId.toUpperCase(), () => []).add(s);
      }
      for (final list in grouped.values) {
        list.sort((a, b) => a.setNumber.compareTo(b.setNumber));
      }

      if (activeSnapshot.session.routineId != null) {
        final routine =
            await repo.getRoutineById(activeSnapshot.session.routineId!);
        if (routine != null) {
          for (final item in routine.exercises) {
            final codeUpper = item.exerciseCode.toUpperCase();
            final ex = exByCode[codeUpper];
            if (ex == null) continue;

            final savedForEx =
                grouped.remove(codeUpper) ?? const <WorkoutSetModel>[];
            final rows = <_DraftSetRow>[
              for (final s in savedForEx)
                _DraftSetRow(
                  persistedSetId: s.id,
                  setNumber: s.setNumber,
                  setType: s.setType,
                  weightKg: s.weightKg,
                  reps: s.reps,
                  rpe: s.rpe ?? 7.5,
                  isCompleted: true,
                  estimated1rm: s.estimated1rm,
                  isPr: s.isPr,
                  lockedExerciseCode: s.exerciseId.toUpperCase(),
                  lockedExerciseNameVi: ex.nameVi,
                ),
            ];

            if (rows.length < item.targetSets) {
              final lastSaved = savedForEx.isNotEmpty ? savedForEx.last : null;
              final lastPerf = lastSaved == null
                  ? await repo.getLastPerformanceForExercise(ex.code)
                  : null;
              final aiRec = _aiRecByCode[codeUpper];
              final startWeight = lastSaved?.weightKg ??
                  lastPerf?.weightKg ??
                  aiRec?.recommendedWeightKg ??
                  _defaultStartWeight(ex);
              final startReps =
                  lastSaved?.reps ?? lastPerf?.reps ?? item.targetRepMin;
              final startRpe = lastSaved?.rpe ?? lastPerf?.rpe ?? 7.5;
              var nextSetNum = rows.isEmpty
                  ? 1
                  : rows
                          .map((r) => r.setNumber)
                          .reduce((a, b) => a > b ? a : b) +
                      1;
              while (rows.length < item.targetSets) {
                rows.add(
                  _DraftSetRow(
                    setNumber: nextSetNum++,
                    setType: 'NORMAL',
                    weightKg: startWeight,
                    reps: startReps,
                    rpe: startRpe,
                    estimated1rm: WorkoutCalculators.calculateEstimated1Rm(
                      startWeight,
                      startReps,
                    ),
                  ),
                );
              }
            }

            _blocks.add(
              _WorkoutExerciseBlock(
                exercise: ex,
                defaultRestSeconds: item.defaultRestSeconds,
                supersetGroupId: item.supersetGroupId,
                rows: rows,
              ),
            );
          }
        }
      }

      for (final entry in grouped.entries) {
        final ex = exByCode[entry.key];
        if (ex == null) continue;
        _blocks.add(
          _WorkoutExerciseBlock(
            exercise: ex,
            defaultRestSeconds: ex.equipmentType == 'BARBELL' ? 150 : 90,
            rows: entry.value
                .map(
                  (s) => _DraftSetRow(
                    persistedSetId: s.id,
                    setNumber: s.setNumber,
                    setType: s.setType,
                    weightKg: s.weightKg,
                    reps: s.reps,
                    rpe: s.rpe ?? 7.5,
                    isCompleted: true,
                    estimated1rm: s.estimated1rm,
                    isPr: s.isPr,
                    lockedExerciseCode: s.exerciseId.toUpperCase(),
                    lockedExerciseNameVi: ex.nameVi,
                  ),
                )
                .toList(),
          ),
        );
      }

      if (_blocks.isEmpty && allExercises.isNotEmpty) {
        final fallbackEx = exByCode['BARBELL_BENCH_PRESS'] ?? allExercises.first;
        await _appendExerciseBlock(fallbackEx, repo);
      }

      if (mounted) setState(() => _isLoading = false);
      return;
    }

    // 2. Start fresh session from explicit exerciseCode, routineId, or default Chest Push template
    final routines = await repo.loadRoutines();
    if (widget.initialExerciseCode != null) {
      final ex = exByCode[widget.initialExerciseCode!.toUpperCase()] ??
          allExercises.first;
      _activeSession = await repo.startNewSession(
        title: 'Tập nhanh: ${ex.nameVi}',
      );
      await _appendExerciseBlock(ex, repo);
    } else {
      final chosenRoutine = widget.initialRoutineId != null
          ? routines.firstWhere(
              (r) => r.id == widget.initialRoutineId,
              orElse: () => routines.first,
            )
          : routines.first;
      _activeSession = await repo.startNewSession(
        title: chosenRoutine.name,
        routineId: chosenRoutine.id,
      );
      await _populateBlocksFromRoutine(chosenRoutine, exByCode, repo);
    }

    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _populateBlocksFromRoutine(
    WorkoutRoutineModel routine,
    Map<String, ExerciseModel> exByCode,
    WorkoutRepository repo,
  ) async {
    for (final item in routine.exercises) {
      final ex = exByCode[item.exerciseCode.toUpperCase()];
      if (ex == null) continue;
      await _appendExerciseBlock(
        ex,
        repo,
        targetSets: item.targetSets,
        targetReps: item.targetRepMin,
        defaultRestSeconds: item.defaultRestSeconds,
        supersetGroupId: item.supersetGroupId,
      );
    }
  }

  double _defaultStartWeight(ExerciseModel ex) {
    switch (ex.equipmentType.toUpperCase()) {
      case 'BARBELL':
        return 60.0;
      case 'DUMBBELL':
        return 20.0;
      case 'CABLE':
      case 'MACHINE':
        return 25.0;
      case 'KETTLEBELL':
        return 16.0;
      default:
        return 0.0;
    }
  }

  Future<void> _appendExerciseBlock(
    ExerciseModel ex,
    WorkoutRepository repo, {
    int targetSets = 3,
    int targetReps = 10,
    int? defaultRestSeconds,
    int? supersetGroupId,
  }) async {
    final last = await repo.getLastPerformanceForExercise(ex.code);
    final aiRec = _aiRecByCode[ex.code.toUpperCase()];
    final startWeight =
        last?.weightKg ?? aiRec?.recommendedWeightKg ?? _defaultStartWeight(ex);
    final startReps = last?.reps ?? targetReps;
    final startRpe = last?.rpe ?? 7.5;

    final rows = List.generate(
      targetSets,
      (idx) => _DraftSetRow(
        setNumber: idx + 1,
        setType: 'NORMAL',
        weightKg: startWeight,
        reps: startReps,
        rpe: startRpe,
        estimated1rm:
            WorkoutCalculators.calculateEstimated1Rm(startWeight, startReps),
      ),
    );
    _blocks.add(
      _WorkoutExerciseBlock(
        exercise: ex,
        defaultRestSeconds:
            defaultRestSeconds ?? (ex.equipmentType == 'BARBELL' ? 150 : 90),
        supersetGroupId: supersetGroupId,
        rows: rows,
      ),
    );
  }

  void _startRestTimer(int seconds) {
    _restTimer?.cancel();
    setState(() {
      _restRemainingSeconds = seconds;
      _isResting = true;
    });
    _restTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      if (_restRemainingSeconds <= 1) {
        _restTimer?.cancel();
        setState(() {
          _restRemainingSeconds = 0;
          _isResting = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Hết giờ nghỉ giữa hiệp — sẵn sàng vào hiệp tiếp theo!'),
            duration: Duration(seconds: 2),
          ),
        );
      } else {
        setState(() => _restRemainingSeconds--);
      }
    });
  }

  void _adjustRest(int delta) {
    setState(() {
      _restRemainingSeconds = (_restRemainingSeconds + delta).clamp(0, 600);
      if (_restRemainingSeconds == 0) {
        _restTimer?.cancel();
        _isResting = false;
      }
    });
  }

  Future<void> _toggleCompleteSet(
    _WorkoutExerciseBlock block,
    _DraftSetRow row,
  ) async {
    final sess = _activeSession;
    if (sess == null) return;
    final repo = ref.read(workoutRepositoryProvider);

    if (row.isCompleted && row.persistedSetId != null) {
      await repo.deleteSet(row.persistedSetId!, sess.id);
      setState(() {
        row.isCompleted = false;
        row.persistedSetId = null;
        row.isPr = false;
        row.lockedExerciseCode = null;
        row.lockedExerciseNameVi = null;
      });
      return;
    }

    final saved = await repo.saveSetImmediately(
      sessionId: sess.id,
      exerciseIdOrCode: block.exercise.code,
      setNumber: row.setNumber,
      setType: row.setType,
      weightKg: row.weightKg,
      reps: row.reps,
      rpe: row.rpe,
      existingSetId: row.persistedSetId,
    );

    setState(() {
      row.persistedSetId = saved.id;
      row.isCompleted = true;
      row.estimated1rm = saved.estimated1rm;
      row.isPr = saved.isPr;
      row.lockedExerciseCode = block.exercise.code.toUpperCase();
      row.lockedExerciseNameVi = block.exercise.nameVi;
    });

    if (row.setType != 'WARMUP') {
      _startRestTimer(block.defaultRestSeconds);
    }

    if (saved.isPr && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.calorieOrange,
          content: Text(
            '🏆 Kỷ lục PR mới ở ${block.exercise.nameVi}: 1RM ước tính ${saved.estimated1rm.toStringAsFixed(1)} kg!',
          ),
        ),
      );
    }
  }

  Future<void> _swapExercise(_WorkoutExerciseBlock block) async {
    final replacement = await showExerciseSwapperSheet(
      context,
      ref,
      currentExercise: block.exercise,
    );
    if (replacement == null) return;
    final repo = ref.read(workoutRepositoryProvider);
    final last = await repo.getLastPerformanceForExercise(replacement.code);
    setState(() {
      // Giu nguyen tat ca cac hiep da tick truoc do (F25), chi cap nhat bai & cac hiep chua tick
      block.exercise = replacement;
      block.defaultRestSeconds =
          replacement.equipmentType == 'BARBELL' ? 150 : 90;
      for (final r in block.rows) {
        if (!r.isCompleted) {
          r.weightKg = last?.weightKg ?? _defaultStartWeight(replacement);
          r.reps = last?.reps ?? r.reps;
          r.estimated1rm =
              WorkoutCalculators.calculateEstimated1Rm(r.weightKg, r.reps);
          r.inputVersion++;
        }
      }
    });
  }

  Future<void> _addExerciseFromLibrary() async {
    final all = await ref.read(exercisesListProvider.future);
    if (!mounted) return;
    final picked = await showDialog<ExerciseModel>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Thêm bài tập vào buổi tập'),
        children: all
            .map(
              (ex) => SimpleDialogOption(
                onPressed: () => Navigator.of(ctx).pop(ex),
                child: Text('${ex.nameVi} (${ex.equipmentType})'),
              ),
            )
            .toList(),
      ),
    );
    if (picked == null) return;
    await _appendExerciseBlock(picked, ref.read(workoutRepositoryProvider));
    if (mounted) setState(() {});
  }

  double get _liveTotalVolumeKg {
    var total = 0.0;
    for (final block in _blocks) {
      for (final row in block.rows) {
        if (!row.isCompleted || row.setType == 'WARMUP') continue;
        total += row.weightKg * row.reps;
      }
    }
    return (total * 10).round() / 10.0;
  }

  int get _livePrCount {
    var prs = 0;
    for (final block in _blocks) {
      for (final row in block.rows) {
        if (row.isCompleted && row.isPr) prs++;
      }
    }
    return prs;
  }

  List<WorkoutSetModel> _collectCompletedSets() {
    final list = <WorkoutSetModel>[];
    final sessId = _activeSession?.id ?? '';
    final now = DateTime.now().toUtc();
    for (final block in _blocks) {
      for (final row in block.rows) {
        if (!row.isCompleted) continue;
        list.add(
          WorkoutSetModel(
            id: row.persistedSetId ?? '',
            sessionId: sessId,
            exerciseId: (row.lockedExerciseCode ?? block.exercise.code)
                .toUpperCase(),
            setNumber: row.setNumber,
            setType: row.setType,
            weightKg: row.weightKg,
            reps: row.reps,
            rpe: row.rpe,
            estimated1rm: row.estimated1rm,
            isPr: row.isPr,
            completedAt: now,
            updatedAt: now,
          ),
        );
      }
    }
    return list;
  }

  Future<void> _finishWorkout() async {
    final sess = _activeSession;
    if (sess == null || _isFinishing) return;
    final completedSets = _collectCompletedSets();
    if (completedSets.isEmpty) {
      final abandon = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Chưa có hiệp nào được tick'),
          content: const Text(
            'Bạn chưa đánh dấu hoàn thành hiệp tập nào. Bạn muốn hủy buổi tập này?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(false),
              child: const Text('Tiếp tục tập'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(ctx).pop(true),
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.warningRed,
                minimumSize: const Size(80, 40),
              ),
              child: const Text('Hủy buổi tập'),
            ),
          ],
        ),
      );
      if (abandon == true) {
        await ref.read(workoutRepositoryProvider).abandonActiveSession(sess.id);
        if (mounted) context.pop();
      }
      return;
    }

    setState(() => _isFinishing = true);
    final summary = await ref.read(workoutRepositoryProvider).completeSession(
          session: sess,
          sets: completedSets,
          durationSeconds: _elapsedSeconds,
        );
    ref.invalidate(aiReadinessProvider);
    for (final days in const [7, 30, 90, 365]) {
      ref.invalidate(analyticsSummaryProvider(days));
    }
    if (!mounted) return;
    setState(() => _isFinishing = false);

    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('🎉 Hoàn thành Buổi tập!'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Buổi tập: ${summary.session.sessionTitle}'),
            const SizedBox(height: 6),
            Text('• Thời gian: ${_formatDuration(_elapsedSeconds)}'),
            Text('• Tổng Volume Load: ${summary.session.totalVolumeKg} kg'),
            Text('• Số hiệp hoàn thành: ${summary.totalSets} (${summary.workingSets} hiệp chính)'),
            Text('• Kỷ lục PR mới: ${summary.newPrCount}'),
            Text(
              '• Bù nước thông minh: +${summary.hydrationBonusMl} ml vào mục tiêu hôm nay',
              style: const TextStyle(
                color: AppColors.hydrationBlue,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              summary.syncedToServer
                  ? 'Đã đồng bộ dữ liệu buổi tập.'
                  : 'Đã lưu buổi tập trên máy (tự đồng bộ khi có mạng).',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Xong'),
          ),
        ],
      ),
    );
    if (mounted) context.pop();
  }

  String _formatDuration(int totalSeconds) {
    final m = (totalSeconds ~/ 60).toString().padLeft(2, '0');
    final s = (totalSeconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Đang chuẩn bị Buổi tập...')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _activeSession?.sessionTitle ?? 'Buổi tập Gym',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            ),
            Text(
              '⏱ ${_formatDuration(_elapsedSeconds)} · ${_liveTotalVolumeKg.toStringAsFixed(1)} kg · 🏆 $_livePrCount PR',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Đổi đơn vị kg / lbs',
            icon: Text(
              _useLbs ? 'LBS' : 'KG',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
            ),
            onPressed: () => setState(() => _useLbs = !_useLbs),
          ),
          IconButton(
            tooltip: 'Tính bánh tạ',
            icon: const Icon(Icons.calculate_outlined),
            onPressed: () => showPlateCalculatorSheet(context),
          ),
          IconButton(
            tooltip: 'Giáo án',
            icon: const Icon(Icons.calendar_today_outlined),
            onPressed: () => context.push('/workout/routines'),
          ),
        ],
      ),
      body: Column(
        children: [
          if (_restoredFromCrash)
            MaterialBanner(
              backgroundColor: AppColors.tintedSurface(
                context,
                AppColors.muscleRecoveredGreen,
              ),
              content: const Text(
                'Đã khôi phục buổi tập dang dở của bạn.',
                style: TextStyle(fontSize: 12),
              ),
              actions: [
                TextButton(
                  onPressed: () => setState(() => _restoredFromCrash = false),
                  child: const Text('Đóng'),
                ),
              ],
            ),
          if (_isResting)
            Container(
              color: const Color(0xFF12161E),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              child: Row(
                children: [
                  const Icon(Icons.timer, color: AppColors.volt),
                  const SizedBox(width: 8),
                  Text(
                    'Nghỉ giữa hiệp: ${_formatDuration(_restRemainingSeconds)}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () => _adjustRest(-15),
                    child: const Text('-15s', style: TextStyle(color: Colors.white70)),
                  ),
                  TextButton(
                    onPressed: () => _adjustRest(15),
                    child: const Text('+15s', style: TextStyle(color: Colors.white70)),
                  ),
                  FilledButton.tonal(
                    onPressed: () => _adjustRest(-999),
                    style: FilledButton.styleFrom(
                      minimumSize: const Size(64, 34),
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                    ),
                    child: const Text('Bỏ qua'),
                  ),
                ],
              ),
            ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 96),
              children: [
                ..._blocks.map((block) => _buildExerciseBlockCard(block)),
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: _addExerciseFromLibrary,
                  icon: const Icon(Icons.add),
                  label: const Text('Thêm bài tập vào buổi hôm nay'),
                ),
                const SizedBox(height: 10),
                Text(
                  'Công thức 1RM: Trung bình Epley (1985) & Brzycki (1993) cho 2–10 reps.\n$_aiDisclaimer',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
          child: FilledButton.icon(
            onPressed: _isFinishing ? null : _finishWorkout,
            icon: _isFinishing
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.check_circle_outline),
            label: const Text('Hoàn thành Buổi tập'),
          ),
        ),
      ),
    );
  }

  Widget _buildExerciseBlockCard(_WorkoutExerciseBlock block) {
    final ex = block.exercise;
    final aiRec = _aiRecByCode[ex.code.toUpperCase()];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ex.nameVi,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${ex.equipmentType} · Nghỉ ${block.defaultRestSeconds}s'
                        '${block.supersetGroupId != null ? " · Superset #${block.supersetGroupId}" : ""}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                IconButton(
                  tooltip: 'Xem 3D',
                  icon: Icon(Icons.view_in_ar, color: AppColors.telemetryCyan(context)),
                  onPressed: () => context.push('/gym3d/exercise/${ex.code}'),
                ),
                IconButton(
                  tooltip: 'Đổi bài tập',
                  icon: const Icon(Icons.swap_horiz, color: AppColors.calorieOrange),
                  onPressed: () => _swapExercise(block),
                ),
              ],
            ),
            // F21: AI Weight Recommendation & Deload Advisor card
            if (aiRec != null)
              Container(
                margin: const EdgeInsets.only(top: 8, bottom: 6),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: aiRec.action == 'DELOAD'
                      ? AppColors.tintedSurface(context, AppColors.warningRed)
                      : aiRec.action == 'INCREASE'
                          ? AppColors.tintedSurface(
                              context,
                              AppColors.muscleRecoveredGreen,
                            )
                          : AppColors.tintedSurface(context, AppColors.primary),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    Icon(
                      aiRec.action == 'DELOAD'
                          ? Icons.warning_amber_rounded
                          : aiRec.action == 'INCREASE'
                              ? Icons.trending_up
                              : Icons.auto_awesome,
                      color: aiRec.action == 'DELOAD'
                          ? AppColors.warningRed
                          : aiRec.action == 'INCREASE'
                              ? AppColors.muscleRecoveredGreen
                              : AppColors.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'AI Gợi ý (${aiRec.action}): ${aiRec.recommendedWeightKg} kg × ${aiRec.recommendedReps} reps',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                          Text(
                            aiRec.reason,
                            style: const TextStyle(fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        setState(() {
                          for (final r in block.rows) {
                            if (!r.isCompleted) {
                              r.weightKg = aiRec.recommendedWeightKg;
                              r.estimated1rm =
                                  WorkoutCalculators.calculateEstimated1Rm(
                                r.weightKg,
                                r.reps,
                              );
                            }
                          }
                        });
                      },
                      child: const Text('Áp dụng'),
                    ),
                  ],
                ),
              ),
            const Divider(height: 16),
            ...block.rows.map((row) => _buildSetRow(block, row)),
            const SizedBox(height: 6),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                TextButton.icon(
                  onPressed: () {
                    setState(() {
                      final last = block.rows.isNotEmpty
                          ? block.rows.last
                          : _DraftSetRow(setNumber: 0);
                      block.rows.add(
                        _DraftSetRow(
                          setNumber: block.rows.length + 1,
                          setType: 'NORMAL',
                          weightKg: last.weightKg,
                          reps: last.reps,
                          rpe: last.rpe,
                          estimated1rm: last.estimated1rm,
                        ),
                      );
                    });
                  },
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Thêm hiệp'),
                ),
                if (ex.equipmentType == 'BARBELL')
                  TextButton.icon(
                    onPressed: () async {
                      final target = block.rows.isNotEmpty
                          ? block.rows.last.weightKg
                          : 60.0;
                      final chosen = await showPlateCalculatorSheet(
                        context,
                        initialTargetKg: target,
                      );
                      if (chosen != null) {
                        setState(() {
                          for (final r in block.rows) {
                            if (!r.isCompleted) {
                              r.weightKg = chosen;
                              r.estimated1rm =
                                  WorkoutCalculators.calculateEstimated1Rm(
                                r.weightKg,
                                r.reps,
                              );
                              r.inputVersion++;
                            }
                          }
                        });
                      }
                    },
                    icon: const Icon(Icons.calculate_outlined, size: 18),
                    label: const Text('Tính bánh tạ'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSetRow(_WorkoutExerciseBlock block, _DraftSetRow row) {
    final displayWeight =
        _useLbs ? WorkoutCalculators.kgToLbs(row.weightKg) : row.weightKg;
    final showLockedOrigin = row.isCompleted &&
        row.lockedExerciseCode != null &&
        row.lockedExerciseCode != block.exercise.code.toUpperCase();
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: row.isCompleted
            ? AppColors.tintedSurface(context, AppColors.muscleRecoveredGreen)
            : AppColors.subtleSurface(context),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: row.isPr
              ? AppColors.calorieOrange
              : row.isCompleted
                  ? AppColors.muscleRecoveredGreen.withValues(alpha: 0.45)
                  : AppColors.subtleBorder(context),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              PopupMenuButton<String>(
                enabled: !row.isCompleted,
                tooltip: 'Loại hiệp',
                initialValue: row.setType,
                onSelected: (t) => setState(() => row.setType = t),
                itemBuilder: (_) => const [
                  PopupMenuItem(value: 'WARMUP', child: Text('WARMUP (Khởi động)')),
                  PopupMenuItem(value: 'NORMAL', child: Text('NORMAL (Chính)')),
                  PopupMenuItem(value: 'DROPSET', child: Text('DROPSET')),
                  PopupMenuItem(value: 'SUPERSET', child: Text('SUPERSET')),
                  PopupMenuItem(value: 'FAILURE', child: Text('FAILURE (Tới ngưỡng)')),
                ],
                child: CircleAvatar(
                  radius: 14,
                  backgroundColor: row.setType == 'WARMUP'
                      ? Colors.amber.shade100
                      : AppColors.primary.withValues(alpha: 0.14),
                  child: Text(
                    row.setType == 'WARMUP' ? 'W' : '${row.setNumber}',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 3,
                child: TextFormField(
                  key: ValueKey('w-${row.rowKey}-$_useLbs-${row.inputVersion}'),
                  enabled: !row.isCompleted,
                  initialValue: displayWeight.toStringAsFixed(1),
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: _useLbs ? 'lbs' : 'kg',
                    isDense: true,
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                  ),
                  onChanged: (v) {
                    final parsed = double.tryParse(v.replaceAll(',', '.'));
                    if (parsed != null && parsed >= 0) {
                      row.weightKg = _useLbs
                          ? WorkoutCalculators.lbsToKg(parsed)
                          : parsed;
                      row.estimated1rm =
                          WorkoutCalculators.calculateEstimated1Rm(
                        row.weightKg,
                        row.reps,
                      );
                    }
                  },
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                flex: 2,
                child: TextFormField(
                  key: ValueKey('r-${row.rowKey}-${row.inputVersion}'),
                  enabled: !row.isCompleted,
                  initialValue: '${row.reps}',
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Reps',
                    isDense: true,
                    contentPadding:
                        EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                  ),
                  onChanged: (v) {
                    final parsed = int.tryParse(v);
                    if (parsed != null && parsed >= 0) {
                      row.reps = parsed;
                      row.estimated1rm =
                          WorkoutCalculators.calculateEstimated1Rm(
                        row.weightKg,
                        row.reps,
                      );
                    }
                  },
                ),
              ),
              const SizedBox(width: 6),
              DropdownButton<double>(
                value: row.rpe,
                underline: const SizedBox.shrink(),
                items: const [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
                    .map(
                      (r) => DropdownMenuItem(
                        value: r,
                        child: Text('RPE $r', style: const TextStyle(fontSize: 11)),
                      ),
                    )
                    .toList(),
                onChanged: row.isCompleted
                    ? null
                    : (v) {
                        if (v != null) setState(() => row.rpe = v);
                      },
              ),
              IconButton(
                tooltip: row.isCompleted ? 'Bỏ tick hiệp' : 'Hoàn thành hiệp',
                onPressed: () => _toggleCompleteSet(block, row),
                icon: Icon(
                  row.isCompleted
                      ? Icons.check_circle
                      : Icons.check_circle_outline,
                  color: row.isCompleted ? Colors.green : Colors.grey,
                ),
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  showLockedOrigin
                      ? '1RM ước tính: ${row.estimated1rm.toStringAsFixed(1)} kg · ${row.lockedExerciseNameVi ?? row.lockedExerciseCode}'
                      : '1RM ước tính (Epley/Brzycki): ${row.estimated1rm.toStringAsFixed(1)} kg',
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.secondaryText(context),
                  ),
                ),
              ),
              if (row.isPr)
                const Text(
                  '🏆 PR MỚI!',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: AppColors.calorieOrange,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
