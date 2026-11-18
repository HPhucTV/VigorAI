// [OWNER: M1] Stub man hinh Onboarding & Mien tru Trach nhiem Y te (F26)
import 'package:flutter/material.dart';

class OnboardingDisclaimerScreen extends StatelessWidget {
  const OnboardingDisclaimerScreen({super.key});

  static const String medicalDisclaimerText =
      'Ung dung VigorAI cung cap cac cong cu theo doi the chat, '
      'uoc tinh nang luong (dua tren cong thuc Mifflin-St Jeor), uoc tinh suc manh '
      '(cong thuc Epley/Brzycki) va goi y luyen tap tu AI chi phuc vu muc dich tham khao '
      'the hinh (Fitness). Ung dung khong thay the cho tu van, chan doan hoac dieu tri y khoa.';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('VigorAI')),
      body: const Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Mien tru Trach nhiem Y te (CH Play Compliance)',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            Text(medicalDisclaimerText),
          ],
        ),
      ),
    );
  }
}
