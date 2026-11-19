// [OWNER: M2] Stub man hinh AI Readiness & Ban do Phuc hoi 3D (F20-F23) & Analytics (F22, F24 Radar)
import 'package:flutter/material.dart';

import '../../../core/theme/app_theme.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';

class AiCoachHubScreen extends StatelessWidget {
  const AiCoachHubScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Coach & Phục hồi 3D (F20 - F24)')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Muscle3DViewerWidget(
              glbAssetOrUrl: 'assets/3d_bundled/base_mannequin.glb',
              muscleColorsMap: const {
                MuscleMaterialIds.quads: AppColors.muscleSecondaryOrange,
                MuscleMaterialIds.chest: AppColors.muscleRecoveredGreen,
              },
              onMuscleTap: (muscleId) {},
            ),
            const SizedBox(height: 16),
            const Text('AI Coach & Recovery 3D Hub — Triển khai đầy đủ ở Sprint 2 (T-M2-10/11)'),
          ],
        ),
      ),
    );
  }
}
