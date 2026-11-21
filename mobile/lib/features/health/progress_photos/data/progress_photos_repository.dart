// [OWNER: M1] Repository Nhat ky Anh The hinh Before/After luu 100% cuc bo (T-M1-11 / F24)
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../../core/database/app_database.dart';
import '../../../../core/platform/photo_picker_service.dart';

class ProgressPhotoItem {
  final String id;
  final String localFilePath;
  final String poseTag; // FRONT | SIDE | BACK
  final DateTime capturedAt;

  const ProgressPhotoItem({
    required this.id,
    required this.localFilePath,
    required this.poseTag,
    required this.capturedAt,
  });

  String get dateLabel {
    final local = capturedAt.toLocal();
    final m = local.month.toString().padLeft(2, '0');
    final d = local.day.toString().padLeft(2, '0');
    return '$d/$m/${local.year}';
  }
}

class ProgressPhotosRepository {
  final AppDatabase _db;
  final PhotoPickerService _photoPickerService;
  final Uuid _uuid = const Uuid();

  ProgressPhotosRepository(this._db, this._photoPickerService);

  Future<List<ProgressPhotoItem>> loadPhotos() async {
    final rows = await (_db.select(_db.localProgressPhotosTable)
          ..orderBy([(t) => OrderingTerm.desc(t.capturedAt)]))
        .get();
    return rows
        .map(
          (r) => ProgressPhotoItem(
            id: r.id,
            localFilePath: r.localFilePath,
            poseTag: r.poseTag,
            capturedAt: r.capturedAt,
          ),
        )
        .toList();
  }

  /// Chon/chup anh qua Android Photo Picker API va luu vao thu muc rieng tu getApplicationDocumentsDirectory()/progress_photos/
  Future<ProgressPhotoItem?> captureOrPickAndSave({
    required bool fromCamera,
    required String poseTag,
  }) async {
    final picked = fromCamera
        ? await _photoPickerService.captureFromCameraCompressed()
        : await _photoPickerService.pickFromGalleryCompressed();
    if (picked == null) return null;

    final savedFile = await _photoPickerService.savePrivateProgressPhoto(
      picked,
      poseTag: poseTag,
    );
    final nowUtc = DateTime.now().toUtc();
    final id = _uuid.v4();

    await _db.into(_db.localProgressPhotosTable).insert(
          LocalProgressPhotosTableCompanion.insert(
            id: id,
            localFilePath: savedFile.path,
            poseTag: Value(poseTag.toUpperCase()),
            capturedAt: nowUtc,
          ),
        );

    return ProgressPhotoItem(
      id: id,
      localFilePath: savedFile.path,
      poseTag: poseTag.toUpperCase(),
      capturedAt: nowUtc,
    );
  }

  Future<void> deletePhoto(ProgressPhotoItem item) async {
    try {
      final f = File(item.localFilePath);
      if (await f.exists()) {
        await f.delete();
      }
    } catch (_) {}
    await (_db.delete(_db.localProgressPhotosTable)
          ..where((t) => t.id.equals(item.id)))
        .go();
  }
}

final progressPhotosRepositoryProvider =
    Provider<ProgressPhotosRepository>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final picker = ref.watch(photoPickerServiceProvider);
  return ProgressPhotosRepository(db, picker);
});

final progressPhotosListProvider =
    FutureProvider<List<ProgressPhotoItem>>((ref) async {
  return ref.watch(progressPhotosRepositoryProvider).loadPhotos();
});
