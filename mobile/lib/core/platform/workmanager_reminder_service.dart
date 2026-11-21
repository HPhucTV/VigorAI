// [OWNER: M1] Dich vu nhac lich Uong nuoc (F03), Supplement (F06) & Background Sync qua WorkManager (Chuan CH Play, khong dung SCHEDULE_EXACT_ALARM)
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:workmanager/workmanager.dart';

const String kHydrationPeriodicUniqueName = 'vigorai_hydration_periodic';
const String kHydrationTaskName = 'vigorai_hydration_reminder';
const String kSupplementPeriodicUniqueName = 'vigorai_supplement_periodic';
const String kSupplementTaskName = 'vigorai_supplement_reminder';
const String kBackgroundSyncUniqueName = 'vigorai_background_sync_periodic';
const String kBackgroundSyncTaskName = 'vigorai_background_sync';

@pragma('vm:entry-point')
void vigorAiWorkmanagerCallbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    final now = DateTime.now();
    switch (task) {
      case kHydrationTaskName:
        if (WorkmanagerReminderService.isWithinHydrationWindow(now)) {
          await WorkmanagerReminderService.tryShowNativeHydrationReminder(
            currentMl: (inputData?['water_ml'] as num?)?.toInt() ?? 0,
            targetMl: (inputData?['target_water_ml'] as num?)?.toInt() ?? 2450,
          );
        }
        return true;
      case kSupplementTaskName:
        final supplementId = inputData?['supplement_id'] as String?;
        final supplementName =
            (inputData?['supplement_name'] as String?) ?? 'Thực phẩm bổ sung';
        final dosageLabel =
            (inputData?['dosage_label'] as String?) ?? '1 liều theo lịch';
        if (supplementId != null && supplementId.isNotEmpty) {
          final store = SupplementIntakeStore();
          final taken = await store.getTakenIdsForDate(_todayLocalIso(now));
          if (!taken.contains(supplementId)) {
            await WorkmanagerReminderService.tryShowNativeSupplementReminder(
              supplementId: supplementId,
              supplementName: supplementName,
              dosageLabel: dosageLabel,
              dateIso: _todayLocalIso(now),
            );
          }
        }
        return true;
      case kBackgroundSyncTaskName:
        return true;
      default:
        return true;
    }
  });
}

String _todayLocalIso(DateTime dt) {
  final m = dt.month.toString().padLeft(2, '0');
  final d = dt.day.toString().padLeft(2, '0');
  return '${dt.year}-$m-$d';
}

/// Kho luu trang thai "Da uong" Supplement theo ngay (dung chung giua Flutter UI & Android BroadcastReceiver).
class SupplementIntakeStore {
  static const String fileName = 'supplement_intake_log.json';
  final Future<Directory> Function()? _directoryResolver;

  SupplementIntakeStore({Future<Directory> Function()? directoryResolver})
      : _directoryResolver = directoryResolver;

  Future<File> _resolveFile() async {
    final dir = await (_directoryResolver ?? getApplicationDocumentsDirectory)();
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return File(p.join(dir.path, fileName));
  }

  Future<Map<String, List<String>>> _readAll() async {
    try {
      final file = await _resolveFile();
      if (!await file.exists()) return <String, List<String>>{};
      final raw = await file.readAsString();
      if (raw.trim().isEmpty) return <String, List<String>>{};
      final decoded = jsonDecode(raw);
      if (decoded is! Map<String, dynamic>) return <String, List<String>>{};
      return decoded.map(
        (key, value) => MapEntry(
          key,
          value is List ? value.map((e) => e.toString()).toList() : <String>[],
        ),
      );
    } catch (_) {
      return <String, List<String>>{};
    }
  }

  Future<void> _writeAll(Map<String, List<String>> data) async {
    final file = await _resolveFile();
    await file.writeAsString(jsonEncode(data), flush: true);
  }

  Future<Set<String>> getTakenIdsForDate(String dateIso) async {
    final all = await _readAll();
    return (all[dateIso] ?? const <String>[]).toSet();
  }

  Future<void> markTaken(String supplementId, {String? dateIso}) async {
    final key = dateIso ?? _todayLocalIso(DateTime.now());
    final all = await _readAll();
    final set = (all[key] ?? <String>[]).toSet()..add(supplementId);
    all[key] = set.toList();
    await _writeAll(all);
  }

  Future<void> unmarkTaken(String supplementId, {String? dateIso}) async {
    final key = dateIso ?? _todayLocalIso(DateTime.now());
    final all = await _readAll();
    final list = (all[key] ?? <String>[])..removeWhere((e) => e == supplementId);
    all[key] = list;
    await _writeAll(all);
  }

  /// Ty le tuan thu Supplement trong 7 ngay gan nhat (0.0 -> 100.0).
  Future<double> calculateWeeklyAdherence({
    required int activeSupplementCount,
    DateTime? referenceDate,
  }) async {
    if (activeSupplementCount <= 0) return 0.0;
    final ref = referenceDate ?? DateTime.now();
    final all = await _readAll();
    var takenCount = 0;
    for (var i = 0; i < 7; i++) {
      final day = ref.subtract(Duration(days: i));
      final key = _todayLocalIso(day);
      final dayIds = (all[key] ?? const <String>[]).toSet();
      takenCount += dayIds.length.clamp(0, activeSupplementCount);
    }
    final denominator = activeSupplementCount * 7;
    return ((takenCount / denominator) * 1000).round() / 10.0;
  }

  Future<void> clearAll() async {
    try {
      final file = await _resolveFile();
      if (await file.exists()) {
        await file.delete();
      }
    } catch (_) {}
  }
}

class WorkmanagerReminderService {
  static const MethodChannel _channel =
      MethodChannel('com.vigorai.app/health_reminders');

  bool _initialized = false;

  /// Khung gio nhac uong nuoc cho phep: 07:00 den 21:30 gio dia phuong (F03).
  static bool isWithinHydrationWindow(DateTime localTime) {
    final minutes = localTime.hour * 60 + localTime.minute;
    const startMinutes = 7 * 60; // 07:00
    const endMinutes = 21 * 60 + 30; // 21:30
    return minutes >= startMinutes && minutes <= endMinutes;
  }

  Future<void> ensureInitialized() async {
    if (_initialized || kIsWeb) return;
    try {
      await Workmanager().initialize(vigorAiWorkmanagerCallbackDispatcher);
      _initialized = true;
    } catch (_) {
      // Bo qua trong moi truong unit test khong co Android WorkManager plugin.
    }
  }

  Future<void> scheduleHydrationReminders({
    bool enabled = true,
    int currentMl = 0,
    int targetMl = 2450,
  }) async {
    await ensureInitialized();
    try {
      if (!enabled) {
        await Workmanager().cancelByUniqueName(kHydrationPeriodicUniqueName);
        return;
      }
      await Workmanager().registerPeriodicTask(
        kHydrationPeriodicUniqueName,
        kHydrationTaskName,
        frequency: const Duration(hours: 2),
        existingWorkPolicy: ExistingPeriodicWorkPolicy.update,
        inputData: <String, dynamic>{
          'water_ml': currentMl,
          'target_water_ml': targetMl,
        },
      );
    } catch (_) {}
  }

  Future<void> scheduleSupplementReminders({
    bool enabled = true,
    String? nextSupplementId,
    String? nextSupplementName,
    String? nextDosageLabel,
  }) async {
    await ensureInitialized();
    try {
      if (!enabled) {
        await Workmanager().cancelByUniqueName(kSupplementPeriodicUniqueName);
        return;
      }
      await Workmanager().registerPeriodicTask(
        kSupplementPeriodicUniqueName,
        kSupplementTaskName,
        frequency: const Duration(hours: 1),
        existingWorkPolicy: ExistingPeriodicWorkPolicy.update,
        inputData: <String, dynamic>{
          if (nextSupplementId != null) 'supplement_id': nextSupplementId,
          if (nextSupplementName != null) 'supplement_name': nextSupplementName,
          if (nextDosageLabel != null) 'dosage_label': nextDosageLabel,
        },
      );
    } catch (_) {}
  }

  Future<void> scheduleBackgroundSync() async {
    await ensureInitialized();
    try {
      await Workmanager().registerPeriodicTask(
        kBackgroundSyncUniqueName,
        kBackgroundSyncTaskName,
        frequency: const Duration(hours: 6),
        existingWorkPolicy: ExistingPeriodicWorkPolicy.update,
        constraints: Constraints(networkType: NetworkType.connected),
      );
    } catch (_) {}
  }

  Future<bool> showHydrationNotification({
    required int currentMl,
    required int targetMl,
  }) {
    return tryShowNativeHydrationReminder(
      currentMl: currentMl,
      targetMl: targetMl,
    );
  }

  Future<bool> showSupplementNotification({
    required String supplementId,
    required String supplementName,
    required String dosageLabel,
    String? dateIso,
  }) {
    return tryShowNativeSupplementReminder(
      supplementId: supplementId,
      supplementName: supplementName,
      dosageLabel: dosageLabel,
      dateIso: dateIso ?? _todayLocalIso(DateTime.now()),
    );
  }

  static Future<bool> tryShowNativeHydrationReminder({
    required int currentMl,
    required int targetMl,
  }) async {
    try {
      final result = await _channel.invokeMethod<bool>(
        'showHydrationReminder',
        <String, dynamic>{
          'current_ml': currentMl,
          'target_ml': targetMl,
        },
      );
      return result ?? false;
    } on MissingPluginException {
      return false;
    } on PlatformException {
      return false;
    }
  }

  static Future<bool> tryShowNativeSupplementReminder({
    required String supplementId,
    required String supplementName,
    required String dosageLabel,
    required String dateIso,
  }) async {
    try {
      final result = await _channel.invokeMethod<bool>(
        'showSupplementReminder',
        <String, dynamic>{
          'supplement_id': supplementId,
          'supplement_name': supplementName,
          'dosage_label': dosageLabel,
          'date_iso': dateIso,
        },
      );
      return result ?? false;
    } on MissingPluginException {
      return false;
    } on PlatformException {
      return false;
    }
  }
}

final supplementIntakeStoreProvider = Provider<SupplementIntakeStore>((ref) {
  return SupplementIntakeStore();
});

final workmanagerReminderServiceProvider =
    Provider<WorkmanagerReminderService>((ref) {
  return WorkmanagerReminderService();
});
