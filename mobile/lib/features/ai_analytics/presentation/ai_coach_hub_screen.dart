// [OWNER: M2] Hub man hinh AI Readiness & Phuc hoi 3D (F20-F23) va Bieu do Volume / Radar (F22, F24) (T-M2-10, T-M2-11)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/ai_analytics_repository.dart';
import '../muscle_balance/muscle_radar_view.dart';
import '../readiness_3d/readiness_recovery_3d_view.dart';
import '../volume_analytics/volume_analytics_view.dart';

class AiCoachHubScreen extends ConsumerWidget {
  const AiCoachHubScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('AI Coach & Phân tích (F20–F24)'),
          actions: [
            IconButton(
              tooltip: 'Làm mới dữ liệu',
              icon: const Icon(Icons.refresh),
              onPressed: () {
                ref.invalidate(aiReadinessProvider);
                for (final days in const [7, 30, 90, 365]) {
                  ref.invalidate(analyticsSummaryProvider(days));
                }
              },
            ),
            IconButton(
              tooltip: 'Vào buổi tập',
              icon: const Icon(Icons.fitness_center),
              onPressed: () => context.push('/workout/live'),
            ),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.accessibility_new, size: 18), text: 'Phục hồi 3D'),
              Tab(icon: Icon(Icons.bar_chart, size: 18), text: 'Volume & PR'),
              Tab(icon: Icon(Icons.radar, size: 18), text: 'Radar Cơ'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            ReadinessRecovery3DView(),
            VolumeAnalyticsView(),
            MuscleRadarView(),
          ],
        ),
      ),
    );
  }
}
