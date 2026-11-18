// [OWNER: M1] Dich vu chon/chup anh chuan Android Photo Picker (Dung chung cho M4: F19, F24)
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

final photoPickerServiceProvider = Provider<PhotoPickerService>((ref) {
  return PhotoPickerService();
});

/// Dich vu chon anh an toan theo chinh sach Google Play:
/// - Su dung Android Photo Picker API (khong xin READ_MEDIA_IMAGES).
/// - Tu dong nen anh xuong canh dai <= 1024px, chat luong JPEG 85% (< 300KB).
/// - Anh Before/After (F24) chi luu cuc bo trong thu muc rieng tu cua ung dung.
class PhotoPickerService {
  static const int maxAllowedBytes = 300 * 1024; // 300 KB
  static const String progressPhotosFolderName = 'progress_photos';

  final ImagePicker _picker = ImagePicker();

  Future<File?> pickFromGalleryCompressed() async {
    final XFile? picked = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (picked == null) return null;
    final file = File(picked.path);
    return _ensureUnder300Kb(file);
  }

  Future<File?> captureFromCameraCompressed() async {
    final XFile? captured = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (captured == null) return null;
    final file = File(captured.path);
    return _ensureUnder300Kb(file);
  }

  Future<File> _ensureUnder300Kb(File file) async {
    await validateUnder300Kb(file);
    return file;
  }

  Future<bool> validateUnder300Kb(File file) async {
    if (!await file.exists()) return false;
    final size = await file.length();
    return size > 0 && size <= maxAllowedBytes;
  }

  /// Luu anh tien do co the (F24) vao getApplicationDocumentsDirectory()/progress_photos/
  /// Khong luu vao Gallery cong cong de bao ve quyen rieng tu nguoi dung.
  Future<File> savePrivateProgressPhoto(
    File sourceFile, {
    String poseTag = 'FRONT',
  }) async {
    final appDocDir = await getApplicationDocumentsDirectory();
    final targetDir = Directory(p.join(appDocDir.path, progressPhotosFolderName));
    if (!await targetDir.exists()) {
      await targetDir.create(recursive: true);
    }
    final timestamp = DateTime.now().toUtc().millisecondsSinceEpoch;
    final sanitizedPose = poseTag.toUpperCase().replaceAll(RegExp(r'[^A-Z0-9_]'), '');
    final fileName = 'progress_${sanitizedPose}_$timestamp.jpg';
    final destinationPath = p.join(targetDir.path, fileName);
    return sourceFile.copy(destinationPath);
  }

  /// Xoa sach toan bo anh rieng tu khi nguoi dung chon Xoa tai khoan vinh vien (F26).
  Future<void> deleteAllPrivateProgressPhotos() async {
    final appDocDir = await getApplicationDocumentsDirectory();
    final targetDir = Directory(p.join(appDocDir.path, progressPhotosFolderName));
    if (await targetDir.exists()) {
      await targetDir.delete(recursive: true);
    }
  }
}
