// [OWNER: M1] Man hinh Dang nhap VigorAI theo phong cach Mau 01 (T-M1-04 / F26)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import 'auth_controller.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController(text: 'demo@vigorai.app');
  final _passwordController = TextEditingController(text: 'VigorAI@2026');
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submitLogin() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final success = await ref.read(authControllerProvider.notifier).login(
          email: _emailController.text,
          password: _passwordController.text,
        );
    if (success && mounted) {
      context.go('/health');
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final isDark = AppColors.isDark(context);
    final accentColor = AppColors.accentStrong(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Đăng nhập VigorAI'),
        actions: [
          IconButton(
            tooltip: isDark ? 'Chuyển sang Nền Sáng' : 'Chuyển sang Nền Tối',
            onPressed: () => ref
                .read(themePreferenceProvider.notifier)
                .toggleQuickLightDark(Theme.of(context).brightness),
            icon: Icon(
              isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
              size: 20,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (!authState.disclaimerAccepted) ...[
                  Card(
                    color: AppColors.tintedSurface(context, AppColors.warningRed),
                    child: ListTile(
                      leading: const Icon(
                        Icons.warning_amber_rounded,
                        color: AppColors.warningRed,
                      ),
                      title: const Text('Chưa xác nhận Miễn trừ Y tế'),
                      subtitle: const Text(
                        'Bắt buộc đồng ý điều khoản trước khi sử dụng ứng dụng.',
                      ),
                      trailing: TextButton(
                        onPressed: () => context.go('/onboarding?mode=fresh'),
                        child: const Text('Xem lại'),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [Color(0xFF1A2436), Color(0xFF07090D)],
                        ),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: AppColors.volt.withValues(alpha: 0.45),
                        ),
                      ),
                      child: const Center(
                        child: CustomPaint(
                          size: Size(34, 34),
                          painter: _IronVoltVMarkPainter(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'VIGORAI · TÀI KHOẢN',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.2,
                              color: AppColors.telemetryCyan(context),
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Chào mừng trở lại',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Đăng nhập để tiếp tục theo dõi sức khỏe, dinh dưỡng và lịch tập 3D của bạn.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          decoration: const InputDecoration(
                            labelText: 'Email',
                            prefixIcon: Icon(Icons.email_outlined),
                          ),
                          validator: (v) {
                            if (v == null || !v.contains('@')) {
                              return 'Vui lòng nhập email hợp lệ';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscurePassword,
                          decoration: InputDecoration(
                            labelText: 'Mật khẩu',
                            prefixIcon: const Icon(Icons.lock_outline),
                            suffixIcon: IconButton(
                              onPressed: () => setState(
                                () => _obscurePassword = !_obscurePassword,
                              ),
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                            ),
                          ),
                          validator: (v) {
                            if (v == null || v.length < 8) {
                              return 'Mật khẩu tối thiểu 8 ký tự';
                            }
                            return null;
                          },
                        ),
                        if (authState.errorMessage != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            authState.errorMessage!,
                            style: const TextStyle(
                              color: AppColors.warningRed,
                              fontSize: 13,
                            ),
                          ),
                        ],
                        const SizedBox(height: 20),
                        FilledButton(
                          onPressed: authState.isLoading ? null : _submitLogin,
                          child: authState.isLoading
                              ? SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: isDark
                                        ? AppColors.darkScaffold
                                        : Colors.white,
                                  ),
                                )
                              : const Text('Đăng nhập'),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                  ),
                  onPressed: () => context.go('/register'),
                  child: const Text('Chưa có tài khoản? Đăng ký ngay'),
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => context.go('/onboarding?mode=fresh'),
                  child: Text(
                    'Thiết lập lại phác đồ tập luyện',
                    style: TextStyle(color: accentColor),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}


class _IronVoltVMarkPainter extends CustomPainter {
  const _IronVoltVMarkPainter();

  @override
  void paint(Canvas canvas, Size size) {
    // Map normalized icon coords (20..88 -> 0..size)
    double nx(double v) => ((v - 20.0) / 68.0) * size.width;
    double ny(double v) => ((v - 20.0) / 68.0) * size.height;

    final outerPlatePaint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [Color(0xFF94A3B8), Color(0xFF475569)],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    final innerPlatePaint = Paint()..color = const Color(0xE038BDF8);
    final collarPaint = Paint()..color = const Color(0xFF64748B);

    // Outer plates
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTRB(nx(24), ny(40), nx(28), ny(66)),
        Radius.circular(size.width * 0.03),
      ),
      outerPlatePaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTRB(nx(80), ny(40), nx(84), ny(66)),
        Radius.circular(size.width * 0.03),
      ),
      outerPlatePaint,
    );

    // Inner plates
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTRB(nx(29.5), ny(44), nx(33.5), ny(62)),
        Radius.circular(size.width * 0.03),
      ),
      innerPlatePaint,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTRB(nx(74.5), ny(44), nx(78.5), ny(62)),
        Radius.circular(size.width * 0.03),
      ),
      innerPlatePaint,
    );

    // Collars
    canvas.drawRect(
      Rect.fromLTRB(nx(33.5), ny(51.2), nx(38.5), ny(54.8)),
      collarPaint,
    );
    canvas.drawRect(
      Rect.fromLTRB(nx(69.5), ny(51.2), nx(74.5), ny(54.8)),
      collarPaint,
    );

    // Left white-silver V blade
    final leftV = Path()
      ..moveTo(nx(34.5), ny(35.5))
      ..lineTo(nx(44.2), ny(35.5))
      ..lineTo(nx(53.8), ny(63.2))
      ..lineTo(nx(48.8), ny(76.5))
      ..close();
    canvas.drawPath(
      leftV,
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Colors.white, Color(0xFFCBD5E1)],
        ).createShader(Rect.fromLTWH(0, 0, size.width, size.height)),
    );

    // Right electric-volt V blade
    final rightV = Path()
      ..moveTo(nx(63.8), ny(35.5))
      ..lineTo(nx(73.5), ny(35.5))
      ..lineTo(nx(58.2), ny(76.5))
      ..lineTo(nx(48.8), ny(76.5))
      ..lineTo(nx(53.8), ny(63.2))
      ..close();
    canvas.drawPath(
      rightV,
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [Color(0xFFE6FF5C), Color(0xFFCCFF00), Color(0xFF9BE000)],
        ).createShader(Rect.fromLTWH(0, 0, size.width, size.height)),
    );

    // Top 4-point AI spark star
    final star = Path()
      ..moveTo(nx(54), ny(30))
      ..lineTo(nx(55.8), ny(34.7))
      ..lineTo(nx(60.5), ny(36.5))
      ..lineTo(nx(55.8), ny(38.3))
      ..lineTo(nx(54), ny(43))
      ..lineTo(nx(52.2), ny(38.3))
      ..lineTo(nx(47.5), ny(36.5))
      ..lineTo(nx(52.2), ny(34.7))
      ..close();
    canvas.drawPath(star, Paint()..color = const Color(0xFF38BDF8));
    canvas.drawCircle(
      Offset(nx(54), ny(36.5)),
      (2.2 / 68.0) * size.width,
      Paint()..color = Colors.white,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
