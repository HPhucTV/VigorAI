// [OWNER: M2] Widget 3D dung chung cho Phong tap 3D (M2: F07-F13) va Ban do Phuc hoi 3D (M4: F23)
import 'package:flutter/material.dart';

/// 11 dinh danh Material co bap bat buoc khop 1-1 voi Blender MCP & AI Model C
class MuscleMaterialIds {
  MuscleMaterialIds._();

  static const String chest = 'Mat_Muscle_Chest';
  static const String shoulders = 'Mat_Muscle_Shoulders';
  static const String biceps = 'Mat_Muscle_Biceps';
  static const String triceps = 'Mat_Muscle_Triceps';
  static const String backLats = 'Mat_Muscle_Back_Lats';
  static const String traps = 'Mat_Muscle_Traps';
  static const String absCore = 'Mat_Muscle_Abs_Core';
  static const String glutes = 'Mat_Muscle_Glutes';
  static const String quads = 'Mat_Muscle_Quads';
  static const String hamstrings = 'Mat_Muscle_Hamstrings';
  static const String calves = 'Mat_Muscle_Calves';

  static const List<String> all = [
    chest,
    shoulders,
    biceps,
    triceps,
    backLats,
    traps,
    absCore,
    glutes,
    quads,
    hamstrings,
    calves,
  ];
}

enum CameraPreset3D { front, side, back, top }

/// Giao dien cong khai da duoc khoa de M4 nhung truc tiep vao F23 ma khong sua code cua M2.
class Muscle3DViewerWidget extends StatelessWidget {
  final String glbAssetOrUrl;
  final Map<String, Color> muscleColorsMap;
  final String animationName;
  final double playbackSpeed;
  final CameraPreset3D cameraPreset;
  final ValueChanged<String>? onMuscleTap;

  const Muscle3DViewerWidget({
    super.key,
    required this.glbAssetOrUrl,
    this.muscleColorsMap = const {},
    this.animationName = 'Anim_GoodForm',
    this.playbackSpeed = 1.0,
    this.cameraPreset = CameraPreset3D.front,
    this.onMuscleTap,
  });

  @override
  Widget build(BuildContext context) {
    // Hoan thien tich hop ModelViewer + JS Bridge trong Task T-M2-03, T-M2-07 & T-M2-13
    return Container(
      height: 320,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.view_in_ar, size: 48),
          const SizedBox(height: 8),
          Text('3D Viewer Stub: $glbAssetOrUrl ($animationName @ ${playbackSpeed}x)'),
          Text('Highlighted materials: ${muscleColorsMap.length}'),
        ],
      ),
    );
  }
}
