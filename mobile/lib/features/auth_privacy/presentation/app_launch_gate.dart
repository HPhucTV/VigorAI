// [OWNER: M1] Cong dieu huong khoi dong khong nhay man hinh (Splash -> Health / Login / Onboarding)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import 'auth_controller.dart';
import 'onboarding_disclaimer_screen.dart';

class AppLaunchGate extends ConsumerStatefulWidget {
  const AppLaunchGate({super.key});

  @override
  ConsumerState<AppLaunchGate> createState() => _AppLaunchGateState();
}

class _AppLaunchGateState extends ConsumerState<AppLaunchGate> {
  bool _didRedirect = false;

  void _scheduleRedirectIfNeeded(AuthState authState) {
    if (_didRedirect || !authState.isInitialized) return;
    if (authState.isAuthenticated) {
      _didRedirect = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) context.go('/health');
      });
    } else if (authState.disclaimerAccepted) {
      _didRedirect = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) context.go('/login');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    _scheduleRedirectIfNeeded(authState);

    final showOnboarding = authState.isInitialized &&
        !authState.isAuthenticated &&
        !authState.disclaimerAccepted;

    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 200),
      switchInCurve: Curves.easeOutCubic,
      child: showOnboarding
          ? const OnboardingDisclaimerScreen(
              key: ValueKey('launch-onboarding'),
            )
          : const _VigorLaunchSplash(
              key: ValueKey('launch-splash'),
            ),
    );
  }
}

class _VigorLaunchSplash extends StatelessWidget {
  const _VigorLaunchSplash({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = AppColors.isDark(context);
    return Scaffold(
      key: const Key('vigor_launch_splash'),
      backgroundColor:
          isDark ? AppColors.darkScaffold : AppColors.lightScaffold,
      body: const SizedBox.expand(),
    );
  }
}
