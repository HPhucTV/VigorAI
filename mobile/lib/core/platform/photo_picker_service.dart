// [OWNER: M1] Dich vu chon/chup anh chuan Android Photo Picker (Dung chung cho M4: F19, F24)
import 'dart:io';

import 'package:image_picker/image_picker.dart';

/// Dich vu chon anh an toan theo chinh sach Google Play:
/// - Su dung Android Photo Picker API (khong xin READ_MEDIA_IMAGES).
/// - Tu dong nen anh xuong canh dai <= 1024px, chat luong JPEG 85% (< 300KB).
class PhotoPickerService {
  final ImagePicker _picker = ImagePicker();

  Future<File?> pickFromGalleryCompressed() async {
    final XFile? picked = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (picked == null) return null;
    return File(picked.path);
  }

  Future<File?> captureFromCameraCompressed() async {
    final XFile? captured = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    if (captured == null) return null;
    return File(captured.path);
  }
}
