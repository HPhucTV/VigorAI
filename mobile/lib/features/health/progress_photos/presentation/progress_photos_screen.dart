// [OWNER: M1] Man hinh Nhat ky Anh The hinh Before/After + Slider So sanh cuc bo (T-M1-11 / F24)
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_theme.dart';
import '../data/progress_photos_repository.dart';

class ProgressPhotosScreen extends ConsumerStatefulWidget {
  const ProgressPhotosScreen({super.key});

  @override
  ConsumerState<ProgressPhotosScreen> createState() =>
      _ProgressPhotosScreenState();
}

class _ProgressPhotosScreenState extends ConsumerState<ProgressPhotosScreen> {
  String _selectedPoseFilter = 'ALL';
  String _capturePose = 'FRONT';
  ProgressPhotoItem? _beforePhoto;
  ProgressPhotoItem? _afterPhoto;
  double _sliderFraction = 0.5;

  static String _poseLabel(String pose) {
    switch (pose) {
      case 'FRONT':
        return 'Trước';
      case 'SIDE':
        return 'Nghiêng';
      case 'BACK':
        return 'Sau';
      default:
        return pose;
    }
  }

  Future<void> _addPhoto({required bool fromCamera}) async {
    final repo = ref.read(progressPhotosRepositoryProvider);
    final saved = await repo.captureOrPickAndSave(
      fromCamera: fromCamera,
      poseTag: _capturePose,
    );
    if (saved == null) return;
    ref.invalidate(progressPhotosListProvider);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Đã lưu ảnh tiến độ thành công.'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final photosAsync = ref.watch(progressPhotosListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ảnh Tiến độ Cơ thể'),
      ),
      body: photosAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Lỗi tải ảnh: $err')),
        data: (allPhotos) {
          final filtered = _selectedPoseFilter == 'ALL'
              ? allPhotos
              : allPhotos
                  .where((p) => p.poseTag == _selectedPoseFilter)
                  .toList();

          final before = _beforePhoto ??
              (filtered.length >= 2 ? filtered.last : null);
          final after = _afterPhoto ??
              (filtered.length >= 2 ? filtered.first : null);

          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
            children: [
              // Huy hieu bao mat rieng tu CH Play
              Card(
                color: AppColors.tintedSurface(
                  context,
                  AppColors.muscleRecoveredGreen,
                ),
                child: const ListTile(
                  leading: Icon(
                    Icons.lock_outline,
                    color: AppColors.muscleRecoveredGreen,
                  ),
                  title: Text(
                    'Lưu trữ an toàn trên máy',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    'Ảnh chỉ hiển thị trong ứng dụng, không xuất hiện ở thư viện ảnh chung và tự xóa khi bạn xóa tài khoản.',
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Them anh moi
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Chụp / Chọn ảnh mới',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          for (var i = 0; i < 3; i++) ...[
                            if (i > 0) const SizedBox(width: 8),
                            Expanded(
                              child: ChoiceChip(
                                showCheckmark: false,
                                label: SizedBox(
                                  width: double.infinity,
                                  child: FittedBox(
                                    fit: BoxFit.scaleDown,
                                    child: Text(
                                      _poseLabel(
                                        const ['FRONT', 'SIDE', 'BACK'][i],
                                      ),
                                      maxLines: 1,
                                    ),
                                  ),
                                ),
                                selected: _capturePose ==
                                    const ['FRONT', 'SIDE', 'BACK'][i],
                                onSelected: (_) => setState(
                                  () => _capturePose =
                                      const ['FRONT', 'SIDE', 'BACK'][i],
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: FilledButton.icon(
                              onPressed: () => _addPhoto(fromCamera: true),
                              icon: const Icon(Icons.camera_alt_outlined),
                              label: const Text('Chụp ảnh'),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: FilledButton.tonalIcon(
                              onPressed: () => _addPhoto(fromCamera: false),
                              icon: const Icon(Icons.photo_library_outlined),
                              label: const Text('Chọn ảnh'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Slider So sanh Before / After
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'So sánh Before / After (Kéo thanh trượt)',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                      const SizedBox(height: 10),
                      if (before == null || after == null)
                        SizedBox(
                          height: 120,
                          child: Center(
                            child: Text(
                              'Thêm ít nhất 2 ảnh (hoặc chọn Trước / Sau bên dưới) để so sánh trực tiếp.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: AppColors.secondaryText(context),
                              ),
                            ),
                          ),
                        )
                      else ...[
                        _BeforeAfterCompareBox(
                          before: before,
                          after: after,
                          fraction: _sliderFraction,
                          onFractionChanged: (v) =>
                              setState(() => _sliderFraction = v),
                        ),
                        Slider(
                          value: _sliderFraction,
                          min: 0.05,
                          max: 0.95,
                          onChanged: (v) =>
                              setState(() => _sliderFraction = v),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'Trước: ${before.dateLabel}',
                              style: const TextStyle(fontSize: 12),
                            ),
                            Text(
                              'Sau: ${after.dateLabel}',
                              style: const TextStyle(fontSize: 12),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Bo loc & Danh sach anh
              Wrap(
                spacing: 8,
                children: ['ALL', 'FRONT', 'SIDE', 'BACK'].map((pose) {
                  return ChoiceChip(
                    label: Text(pose == 'ALL' ? 'Tất cả' : _poseLabel(pose)),
                    selected: _selectedPoseFilter == pose,
                    onSelected: (_) =>
                        setState(() => _selectedPoseFilter = pose),
                  );
                }).toList(),
              ),
              const SizedBox(height: 10),

              if (filtered.isEmpty)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(20),
                    child: Center(child: Text('Chưa có ảnh tiến độ nào.')),
                  ),
                )
              else
                ...filtered.map(
                  (item) => Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: File(item.localFilePath).existsSync()
                            ? Image.file(
                                File(item.localFilePath),
                                width: 54,
                                height: 54,
                                fit: BoxFit.cover,
                              )
                            : const SizedBox(
                                width: 54,
                                height: 54,
                                child: Icon(Icons.broken_image_outlined),
                              ),
                      ),
                      title: Text('${_poseLabel(item.poseTag)} · ${item.dateLabel}'),
                      subtitle: Wrap(
                        spacing: 6,
                        children: [
                          ActionChip(
                            label: Text(
                              before?.id == item.id
                                  ? 'Đang là Before'
                                  : 'Đặt Before',
                            ),
                            onPressed: () =>
                                setState(() => _beforePhoto = item),
                          ),
                          ActionChip(
                            label: Text(
                              after?.id == item.id ? 'Đang là After' : 'Đặt After',
                            ),
                            onPressed: () =>
                                setState(() => _afterPhoto = item),
                          ),
                        ],
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () async {
                          await ref
                              .read(progressPhotosRepositoryProvider)
                              .deletePhoto(item);
                          if (_beforePhoto?.id == item.id) _beforePhoto = null;
                          if (_afterPhoto?.id == item.id) _afterPhoto = null;
                          ref.invalidate(progressPhotosListProvider);
                        },
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _BeforeAfterCompareBox extends StatelessWidget {
  final ProgressPhotoItem before;
  final ProgressPhotoItem after;
  final double fraction;
  final ValueChanged<double> onFractionChanged;

  const _BeforeAfterCompareBox({
    required this.before,
    required this.after,
    required this.fraction,
    required this.onFractionChanged,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final splitX = width * fraction;
        return GestureDetector(
          onHorizontalDragUpdate: (details) {
            final next = (details.localPosition.dx / width).clamp(0.05, 0.95);
            onFractionChanged(next);
          },
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: SizedBox(
              height: 280,
              width: width,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Image.file(File(after.localFilePath), fit: BoxFit.cover),
                  ClipRect(
                    clipper: _WidthFractionClipper(fraction),
                    child: Image.file(
                      File(before.localFilePath),
                      fit: BoxFit.cover,
                    ),
                  ),
                  Positioned(
                    left: splitX - 1.5,
                    top: 0,
                    bottom: 0,
                    child: Container(width: 3, color: Colors.white),
                  ),
                  Positioned(
                    left: splitX - 16,
                    top: 124,
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: const BoxDecoration(
                        color: AppColors.primary,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.compare_arrows,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

class _WidthFractionClipper extends CustomClipper<Rect> {
  final double fraction;
  _WidthFractionClipper(this.fraction);

  @override
  Rect getClip(Size size) =>
      Rect.fromLTWH(0, 0, size.width * fraction, size.height);

  @override
  bool shouldReclip(covariant _WidthFractionClipper oldClipper) =>
      oldClipper.fraction != fraction;
}
