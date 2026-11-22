// [OWNER: M1] Man hinh Onboarding & Bat buoc chap nhan Mien tru Trach nhiem Y te (T-M1-04 / F26)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import 'auth_controller.dart';

class OnboardingDisclaimerScreen extends ConsumerStatefulWidget {
  const OnboardingDisclaimerScreen({super.key});

  static const String medicalDisclaimerText =
      'Ứng dụng VigorAI cung cấp các công cụ theo dõi thể chất, ước tính năng lượng '
      '(dựa trên công thức Mifflin-St Jeor), ước tính sức mạnh (công thức Epley/Brzycki) '
      'và gợi ý luyện tập từ AI chỉ phục vụ mục đích tham khảo thể hình (Fitness). '
      'Ứng dụng không thay thế cho tư vấn, chẩn đoán hoặc điều trị y khoa chuyên nghiệp. '
      'Vui lòng tham khảo ý kiến bác sĩ trước khi bắt đầu chế độ ăn kiêng hoặc tập luyện cường độ cao.';

  @override
  ConsumerState<OnboardingDisclaimerScreen> createState() =>
      _OnboardingDisclaimerScreenState();
}

class _OnboardingDisclaimerScreenState
    extends ConsumerState<OnboardingDisclaimerScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _accepted = false;
  bool _syncedInitialDisclaimer = false;

  static const _slides = [
    (
      icon: Icons.favorite_rounded,
      color: AppColors.stepTeal,
      title: 'Quản lý Sức khỏe Toàn diện',
      subtitle:
          'Theo dõi cân nặng, BMI chuẩn Châu Á, bước chân hàng ngày, '
          'lượng nước bù theo buổi tập, Calo/Macro & giấc ngủ.',
    ),
    (
      icon: Icons.view_in_ar_rounded,
      color: AppColors.primary,
      title: 'Phòng tập 3D Tương tác',
      subtitle:
          'Quan sát 360° từng bài tập Gym trên mô hình giải phẫu 11 nhóm cơ, '
          'so sánh tư thế Đúng/Sai và tua chậm 0.25x theo nhịp hít thở.',
    ),
    (
      icon: Icons.auto_awesome_rounded,
      color: AppColors.calorieOrange,
      title: 'Trợ lý AI Dinh dưỡng & Phục hồi',
      subtitle:
          'Chụp ảnh bữa ăn để ước tính Calo/Macro tự động và dự báo điểm Sẵn sàng '
          'tập luyện kèm Bản đồ Mỏi cơ 3D cá nhân hóa.',
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _onConfirmAndContinue() async {
    await ref.read(authControllerProvider.notifier).acceptMedicalDisclaimer();
    if (!mounted) return;
    context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);

    ref.listen<AuthState>(authControllerProvider, (_, next) {
      if (next.isInitialized && next.isAuthenticated && mounted) {
        context.go('/health');
      }
    });

    if (authState.isInitialized && !_syncedInitialDisclaimer) {
      _syncedInitialDisclaimer = true;
      if (authState.disclaimerAccepted) {
        _accepted = true;
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chào mừng đến với VigorAI'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Expanded(
                flex: 4,
                child: PageView.builder(
                  controller: _pageController,
                  itemCount: _slides.length,
                  onPageChanged: (index) => setState(() => _currentPage = index),
                  itemBuilder: (context, index) {
                    final slide = _slides[index];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircleAvatar(
                              radius: 34,
                              backgroundColor: slide.color.withValues(alpha: 0.14),
                              child: Icon(slide.icon, size: 36, color: slide.color),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              slide.title,
                              textAlign: TextAlign.center,
                              style: Theme.of(context)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              slide.subtitle,
                              textAlign: TextAlign.center,
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  _slides.length,
                  (i) => Container(
                    width: _currentPage == i ? 20 : 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      color: _currentPage == i
                          ? AppColors.primary
                          : Colors.grey.shade400,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Card(
                color: Colors.amber.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.health_and_safety_outlined,
                              color: Colors.deepOrange),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Miễn trừ Trách nhiệm Y tế',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        OnboardingDisclaimerScreen.medicalDisclaimerText,
                        style: TextStyle(fontSize: 12.5, height: 1.4),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Nguồn công thức: Mifflin-St Jeor (1990) · Epley (1985) & Brzycki (1993) · WHO Asia-Pacific BMI.',
                        style: TextStyle(
                          fontSize: 11.5,
                          color: Colors.grey.shade800,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              CheckboxListTile(
                value: _accepted,
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
                onChanged: (value) => setState(() => _accepted = value ?? false),
                title: const Text(
                  'Tôi đã đọc, hiểu rõ và đồng ý với điều khoản Miễn trừ Trách nhiệm Y tế.',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                ),
              ),
              const SizedBox(height: 8),
              FilledButton(
                onPressed: _accepted ? _onConfirmAndContinue : null,
                child: const Text('Đồng ý & Tiếp tục Đăng nhập'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
