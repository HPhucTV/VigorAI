// [OWNER: M1] Man hinh Dang nhap VigorAI (T-M1-04 / F26)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

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

    return Scaffold(
      appBar: AppBar(title: const Text('Đăng nhập VigorAI')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (!authState.disclaimerAccepted)
                  Card(
                    color: Colors.red.shade50,
                    child: ListTile(
                      leading: const Icon(Icons.warning_amber, color: Colors.red),
                      title: const Text('Chưa xác nhận Miễn trừ Y tế'),
                      subtitle: const Text(
                        'Bắt buộc đồng ý điều khoản trước khi sử dụng ứng dụng.',
                      ),
                      trailing: TextButton(
                        onPressed: () => context.go('/onboarding'),
                        child: const Text('Xem lại'),
                      ),
                    ),
                  ),
                const SizedBox(height: 12),
                Text(
                  'Chào mừng trở lại',
                  style: Theme.of(context)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  'Đăng nhập để theo dõi sức khỏe và lịch tập của bạn.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 20),
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
                      onPressed: () =>
                          setState(() => _obscurePassword = !_obscurePassword),
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
                    style: const TextStyle(color: Colors.red),
                  ),
                ],
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: authState.isLoading ? null : _submitLogin,
                  child: authState.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Đăng nhập'),
                ),
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: () => context.go('/register'),
                  child: const Text('Chưa có tài khoản? Đăng ký ngay'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
