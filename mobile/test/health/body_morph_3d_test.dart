// [OWNER: M1] Unit tests cho bien doi hinh the 3D theo Can nang / Chieu cao / % Mo (Nam & Nu)
import 'package:flutter_test/flutter_test.dart';
import 'package:vigorai_app/features/auth_privacy/data/user_fitness_profile.dart';
import 'package:vigorai_app/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';

void main() {
  group('UserFitnessProfile 3D Morph & Avatar Presets', () {
    test('male weight progression updates morphs monotonically across 48 -> 70 -> 105 kg', () {
      const slimMale = UserFitnessProfile(
        gender: 'MALE',
        heightCm: 175,
        currentWeightKg: 48,
        targetWeightKg: 58,
        somatotype: Somatotype.ectomorph,
        bodyFatPreset: BodyFatPreset.lean,
        estimatedBodyFatPct: 10,
      );
      const fitMale = UserFitnessProfile(
        gender: 'MALE',
        heightCm: 175,
        currentWeightKg: 70,
        targetWeightKg: 70,
        somatotype: Somatotype.mesomorph,
        bodyFatPreset: BodyFatPreset.athletic,
        estimatedBodyFatPct: 15,
      );
      const heavyMale = UserFitnessProfile(
        gender: 'MALE',
        heightCm: 175,
        currentWeightKg: 105,
        targetWeightKg: 85,
        somatotype: Somatotype.endomorph,
        bodyFatPreset: BodyFatPreset.higherFat,
        estimatedBodyFatPct: 28,
      );

      expect(slimMale.computedBodyMorph.slim, greaterThan(0.5));
      expect(slimMale.computedBodyMorph.bodyFat, 0.0);
      expect(slimMale.recommendedAvatarPreset, BodyAvatarPreset.maleSlim);

      expect(fitMale.computedBodyMorph.slim, 0.0);
      expect(fitMale.recommendedAvatarPreset, BodyAvatarPreset.maleFit);

      expect(heavyMale.computedBodyMorph.bodyFat, greaterThan(0.8));
      expect(heavyMale.recommendedAvatarPreset, BodyAvatarPreset.maleHeavy);
    });

    test('female weight and bodyfat progression covers all 4 female presets', () {
      const slimFemale = UserFitnessProfile(
        gender: 'FEMALE',
        heightCm: 162,
        currentWeightKg: 44,
        targetWeightKg: 48,
        somatotype: Somatotype.ectomorph,
        bodyFatPreset: BodyFatPreset.lean,
        estimatedBodyFatPct: 17,
      );
      const fitFemale = UserFitnessProfile(
        gender: 'FEMALE',
        heightCm: 162,
        currentWeightKg: 52,
        targetWeightKg: 52,
        somatotype: Somatotype.mesomorph,
        bodyFatPreset: BodyFatPreset.athletic,
        estimatedBodyFatPct: 22,
      );
      const tonedFemale = UserFitnessProfile(
        gender: 'FEMALE',
        heightCm: 162,
        currentWeightKg: 56,
        targetWeightKg: 59,
        somatotype: Somatotype.mesomorph,
        bodyFatPreset: BodyFatPreset.athletic,
        estimatedBodyFatPct: 20,
      );
      const curvyFemale = UserFitnessProfile(
        gender: 'FEMALE',
        heightCm: 162,
        currentWeightKg: 78,
        targetWeightKg: 62,
        somatotype: Somatotype.endomorph,
        bodyFatPreset: BodyFatPreset.higherFat,
        estimatedBodyFatPct: 34,
      );

      expect(slimFemale.recommendedAvatarPreset, BodyAvatarPreset.femaleSlim);
      expect(slimFemale.computedBodyMorph.slim, greaterThan(0.4));

      expect(fitFemale.recommendedAvatarPreset, BodyAvatarPreset.femaleFit);

      expect(tonedFemale.recommendedAvatarPreset, BodyAvatarPreset.femaleToned);
      expect(tonedFemale.computedBodyMorph.muscleMass, greaterThan(0.3));

      expect(curvyFemale.recommendedAvatarPreset, BodyAvatarPreset.femaleCurvy);
      expect(curvyFemale.computedBodyMorph.bodyFat, greaterThan(0.7));
    });
  });
}
