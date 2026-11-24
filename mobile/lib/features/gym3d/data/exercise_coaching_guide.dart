// [OWNER: M2] Cam nang Ky thuat 4 Phan chi tiet cho 33 bai tap 3D (Setup -> 3 Pha -> Cam nhan co -> Loi sai & Sua)
import '../../../core/database/workout_tables.drift.dart';
import '../presentation/widgets/muscle_3d_viewer_widget.dart';

class ExerciseBadFormDetail {
  final String error;
  final String risk;
  final String fix;

  const ExerciseBadFormDetail({
    required this.error,
    required this.risk,
    required this.fix,
  });
}

class ExerciseCoachingGuide {
  final List<String> setupSteps;
  final String eccentricDetail;
  final String isometricDetail;
  final String concentricDetail;
  final String mindMuscleCue;
  final List<ExerciseBadFormDetail> badFormDetails;

  const ExerciseCoachingGuide({
    required this.setupSteps,
    required this.eccentricDetail,
    required this.isometricDetail,
    required this.concentricDetail,
    required this.mindMuscleCue,
    required this.badFormDetails,
  });

  static ExerciseCoachingGuide forExercise(ExerciseModel ex) {
    final key = ex.code.trim().toUpperCase();
    final curated = _guidesByCode[key];
    if (curated != null) return curated;
    return _buildFallbackGuide(ex);
  }

  static ExerciseCoachingGuide _buildFallbackGuide(ExerciseModel ex) {
    final primaryNames = ex.primaryMuscles
        .map((m) => MuscleMaterialIds.labelVi(m).split(' (').first)
        .join(', ');
    final setupLines = <String>[
      'Đặt bàn chân trụ chắc trên sàn hoặc bệ tựa, giữ cột sống trung tính.',
      if (ex.setupGuide.isNotEmpty)
        'Thiết lập chuẩn: ${ex.setupGuide.entries.map((e) => '${e.key}: ${e.value}').join(' · ')}.',
      'Hít sâu, gồng nhẹ cơ bụng (Bracing) và hạ bả vai ổn định trước khi bắt đầu rep.',
    ];
    final badDetails = ex.badFormWarnings.isEmpty
        ? const [
            ExerciseBadFormDetail(
              error: 'Vung người theo quán tính hoặc võng thắt lưng.',
              risk: 'Giảm lực tác động vào nhóm cơ đích và tăng tải cột sống.',
              fix: 'Giảm nhẹ mức tạ 10–15%, giữ lõi bụng căng cứng và kiểm soát pha hạ.',
            ),
          ]
        : ex.badFormWarnings
            .map(
              (w) => ExerciseBadFormDetail(
                error: w,
                risk: 'Gây quá tải khớp phụ và làm giảm hiệu quả kích thích $primaryNames.',
                fix: 'Chuyển góc nhìn 3D sang "Ngang" và thực hiện chậm lại pha hạ tạ.',
              ),
            )
            .toList();

    return ExerciseCoachingGuide(
      setupSteps: setupLines,
      eccentricDetail:
          '2–3 giây · Hít sâu bằng mũi, hạ tạ/dẫn chuyển động có kiểm soát để kéo giãn $primaryNames.',
      isometricDetail:
          '0.5–1 giây · Dừng nhẹ tại điểm căng nhất để triệt tiêu quán tính bật nảy.',
      concentricDetail:
          '1–1.5 giây · Thở ra dứt khoát và đẩy/kéo về vị trí khóa an toàn, không giật khớp.',
      mindMuscleCue:
          'Tập trung cảm nhận $primaryNames co duỗi chủ động thay vì dùng đà toàn thân.',
      badFormDetails: badDetails,
    );
  }

  static const Map<String, ExerciseCoachingGuide> _guidesByCode = {
    'BARBELL_BENCH_PRESS': ExerciseCoachingGuide(
      setupSteps: [
        'Nằm ngửa trên ghế phẳng, mắt nằm ngay dưới thanh đòn tạ.',
        'Khép nhẹ và nhấn hai bả vai xuống mặt ghế (Shoulder Packing), ưỡn ngực tự nhiên.',
        'Đặt hai bàn chân đạp chắc xuống sàn, nắm thanh đòn rộng ~1.5 lần độ rộng vai.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu gồng bụng, hạ thanh đòn có kiểm soát về ngang giữa ngực (khép khuỷu ~45°).',
      isometricDetail:
          '0.5 giây · Dừng nhẹ khi thanh đòn chạm nhẹ ngực, giữ ngực cao không nảy tạ.',
      concentricDetail:
          '1–1.5 giây · Đạp gót chân xuống sàn, thở ra và đẩy tạ hướng hơi chéo về phía trên mắt.',
      mindMuscleCue:
          'Tưởng tượng hai bắp tay đang ép thanh đòn vào giữa ngực (căng đều Mat_Muscle_Chest).',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Xòe khuỷu tay 90° ngang vai và nhấc hông khỏi ghế.',
          risk: 'Tăng áp lực chèn ép dây chằng khớp vai trước (Rotator Cuff) và lưng dưới.',
          fix: 'Khép nhẹ khuỷu tay về góc ~45° so với thân, giữ mông dán chặt mặt ghế.',
        ),
      ],
    ),
    'INCLINE_DUMBBELL_PRESS': ExerciseCoachingGuide(
      setupSteps: [
        'Chỉnh ghế dốc lên 30° (không quá dốc để tránh vai trước gánh thay ngực trên).',
        'Đạp chân vững, nhấn lưng trên & vai sát đệm ghế, giữ hai quả tạ đơn ngay trên vai.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ sang hai bên ngực trên với cổ tay thẳng và khuỷu mở ~45–60°.',
      isometricDetail:
          '0.5–1 giây · Giữ tạ ngang tầm ngực trên để cảm nhận cơ ngực trên kéo giãn hết biên độ.',
      concentricDetail:
          '1–1.5 giây · Thở ra, đẩy hai quả tạ theo hình vòng cung hội tụ phía trên ngực trên.',
      mindMuscleCue:
          'Tập trung đẩy bằng phần ngực sát xương đòn và siết nhẹ khi hai quả tạ gần chạm nhau.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Chỉnh ghế quá dốc (>45°) hoặc để hai quả tạ va mạnh vào nhau ở đỉnh.',
          risk: 'Biến bài ngực trên thành đẩy vai trước và mất lực căng liên tục ở cơ ngực.',
          fix: 'Khóa góc ghế 30°, giữ khoảng cách hở ~5 cm ở đỉnh thay vì chạm cụng tạ.',
        ),
      ],
    ),
    'PUSH_UP': ExerciseCoachingGuide(
      setupSteps: [
        'Chống hai lòng bàn tay rộng hơn vai một chút, mũi chân chống vững tạo thân thẳng từ gót tới đầu.',
        'Siết chặt cơ bụng và cơ mông để hông không bị võng xuống.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ ngực xuống gần chạm sàn (~2–3 cm), khuỷu tay hướng chéo 45° về sau.',
      isometricDetail:
          '0.5 giây · Giữ ngực sát mặt sàn mà không buông lỏng thân người xuống đất.',
      concentricDetail:
          '1–1.5 giây · Thở ra mạnh, đẩy lòng bàn tay xuống sàn để nâng thân người thành một khối thống nhất.',
      mindMuscleCue:
          'Cảm giác như đẩy mặt sàn ra xa kết hợp ép hai cánh tay vào nhau để kích hoạt cơ ngực.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Võng thắt lưng hoặc đẩy mông nhô cao như chữ V.',
          risk: 'Chèn ép đốt sống thắt lưng L4–L5 và giảm tải vào cơ ngực/cơ lõi.',
          fix: 'Hơi cuộn xương chậu vào trong, siết bụng & mông suốt 100% chuyển động.',
        ),
      ],
    ),
    'CABLE_CHEST_FLY': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng bước một chân lên trước giữa hai trụ cáp, nắm hai tay cầm với khuỷu tay hơi cong ~15°.',
        'Ưỡn ngực, hạ vai xuống và nghiêng nhẹ thân người 10° về trước.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, mở rộng hai cánh tay sang ngang theo hình cánh cung vừa tầm vai.',
      isometricDetail:
          '0.5 giây · Dừng nhẹ khi cảm thấy dải cơ ngực căng giãn tối đa trước khi khớp vai kéo ra sau quá mức.',
      concentricDetail:
          '1–1.5 giây · Thở ra, khép hai cánh tay lại như đang ôm một thân cây lớn trước ngực.',
      mindMuscleCue:
          'Giữ góc khuỷu tay cố định từ đầu tới cuối — chuyển động chỉ diễn ra ở khớp vai để cô lập cơ ngực.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Gập khuỷu tay quá sâu biến động tác ép ngực thành đẩy tạ.',
          risk: 'Cơ vai trước và tay trước gánh phần lớn tải trọng thay cho cơ ngực.',
          fix: 'Giảm mức tạ cáp, giữ khuỷu tay chỉ hơi cong tự nhiên ~15° suốt rep.',
        ),
      ],
    ),
    'WIDE_GRIP_PULLUP': ExerciseCoachingGuide(
      setupSteps: [
        'Treo người tự nhiên trên xà đơn với khoảng cách tay rộng hơn vai ~1.3–1.5 lần.',
        'Hạ vai xuống (Depress Scapula) rời xa tai và gồng nhẹ lõi để thân không đung đưa.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, duỗi tay hạ người xuống có kiểm soát tới khi cánh tay gần thẳng hết cỡ.',
      isometricDetail:
          '0.5 giây · Tạm dừng nhẹ ở vị trí treo chuẩn (Dead Hang chủ động) mà không thả lỏng khớp vai.',
      concentricDetail:
          '1–1.5 giây · Thở ra, kéo khuỷu tay xuống hướng về hông để đưa ngực trên tiến sát thanh xà.',
      mindMuscleCue:
          'Đừng nghĩ đến việc kéo bằng bàn tay — hãy tưởng tượng đang nhấn hai khuỷu tay xuống túi quần sau.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Vung chân lấy đà (Kipping) và rụt vai sát mang tai khi kéo.',
          risk: 'Lãng phí kích thích cơ xô và dễ căng khớp vai/khuỷu tay.',
          fix: 'Duỗi mũi chân hơi chếch về trước (Hollow Body), giữ nhịp đi chậm và ổn định.',
        ),
      ],
    ),
    'LAT_PULLDOWN': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi khóa đùi chắc dưới đệm giữ gối, nắm thanh đòn rộng hơn vai.',
        'Ưỡn nhẹ ngực, ngả thân người ra sau ~10–15° cố định.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, trả thanh kéo lên cao từ từ để dải cơ xô mở rộng hết tầm.',
      isometricDetail:
          '0.5 giây · Giữ hai cánh tay giãn căng trên đỉnh 0.5s trước khi bắt đầu nhịp kéo mới.',
      concentricDetail:
          '1–1.5 giây · Thở ra, ghì hai bả vai xuống và kéo thanh đòn về trước ngực trên.',
      mindMuscleCue:
          'Nắm hờ bằng 4 ngón + ngón cái đặt cùng phía để giảm mỏi cẳng tay, dẫn lực hoàn toàn bằng cơ xô.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Ngả hẳn lưng ra sau quá 35° để dùng cân nặng cơ thể giật tạ.',
          risk: 'Chuyển tải sang lưng giữa/cầu vai và gây giật cột sống thắt lưng.',
          fix: 'Giữ thân người cố định ~10–15°, chỉ di chuyển cánh tay kéo thẳng xuống.',
        ),
      ],
    ),
    'STRAIGHT_ARM_CABLE_PULLDOWN': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng cách ròng rọc cao 1 bước chân, gập hông nhẹ ~20° giữ lưng phẳng.',
        'Nắm thanh thẳng ngang vai, khóa khuỷu tay chỉ hơi cong ~10° suốt bài.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, đưa thẳng hai tay lên cao ngang tầm trán để kéo giãn hết phần xô ngoài.',
      isometricDetail:
          '0.5 giây · Cảm nhận dải cơ từ nách xuống hông căng rõ rệt tại điểm cao nhất.',
      concentricDetail:
          '1–1.5 giây · Thở ra, quét thẳng cánh tay xuống chạm đùi trước đồng thời siết mạnh xô.',
      mindMuscleCue:
          'Giữ cẳng tay và tay sau như thanh nối cứng — chỉ quay quanh trục khớp vai.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Gập khuỷu tay kéo xuống sát ngực giống động tác đẩy tay sau.',
          risk: 'Cơ tay sau gánh tải thay cho cơ lưng xô.',
          fix: 'Khóa nhẹ góc khuỷu tay ~10° và kéo theo vòng cung lớn chạm đùi.',
        ),
      ],
    ),
    'BARBELL_BENT_OVER_ROW': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng chân rộng bằng hông, đẩy hông ra sau gập thân trên ~40–45° giữ lưng hoàn toàn phẳng.',
        'Nắm thanh đòn rộng hơn vai một chút, tạ treo tự nhiên ngay dưới vai.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ đòn tạ xuống có kiểm soát mà không làm gù lưng trên.',
      isometricDetail:
          '0.5–1 giây · Tạm dừng nhẹ khi hai tay duỗi hết kiểm soát, vẫn giữ gồng bụng.',
      concentricDetail:
          '1–1.5 giây · Thở ra, kéo khuỷu tay hướng lên trần để thanh đòn chạm nhẹ vùng rốn/bụng dưới.',
      mindMuscleCue:
          'Tưởng tượng kéo hai khuỷu tay sát mạn sườn và ép hai bả vai chạm vào nhau ở đỉnh.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Cong lưng dưới hoặc nhún hông bật người lên để giật tạ.',
          risk: 'Chấn thương đĩa đệm thắt lưng khi chịu mô-men gập lớn.',
          fix: 'Hít sâu gồng bụng cứng (Valsalva nhẹ), hạ mức tạ xuống đủ để giữ lưng bất động.',
        ),
      ],
    ),
    'SEATED_CABLE_ROW': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi thẳng lưng, hai chân đặt vững lên bàn đạp với đầu gối hơi chùng ~15°.',
        'Nắm tay chữ V, kéo nhẹ bả vai ra sau hạ thấp cổ, giữ ngực mở.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, thả tay cầm về trước có kiểm soát để hai bả vai mở rộng.',
      isometricDetail:
          '0.5 giây · Giữ thẳng cột sống thắt lưng khi cơ lưng được kéo giãn hết cỡ.',
      concentricDetail:
          '1–1.5 giây · Thở ra, kéo tay chữ V sát vùng bụng dưới và giữ ép lưng giữa 1 giây.',
      mindMuscleCue:
          'Giữ thân người thẳng như tượng đài — không lắc lư trước sau theo khối tạ.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đu người ra trước và ngả quá sâu ra sau khi kéo cáp.',
          risk: 'Dùng động lượng lưng dưới thay vì lực co rút của lưng giữa và xô.',
          fix: 'Cố định góc thân 90–95°, kéo khuỷu tay đi sát thân về phía hông.',
        ),
      ],
    ),
    'BARBELL_DEADLIFT': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng giữa thanh đòn sao cho thanh nằm ngay trên giữa mu bàn chân (~2–3 cm trước ống đồng).',
        'Đẩy hông ra sau, gập người nắm tạ sát ngoài cẳng chân, khóa bả vai xuống (ép xô), ưỡn ngực.',
      ],
      eccentricDetail:
          '2 giây · Hít sâu gồng bụng, đẩy hông ra sau trước để thanh đòn đi sát đùi qua gối rồi hạ xuống sàn.',
      isometricDetail:
          '0.5–1 giây · Đặt tạ ổn định chạm sàn hoàn toàn (Dead Stop), hít lại hơi mới giữ lưng thẳng.',
      concentricDetail:
          '1–1.5 giây · Đạp mạnh chân xuống sàn đẩy hông tiến thẳng về thanh đòn tới khi đứng thẳng hoàn toàn.',
      mindMuscleCue:
          'Kéo độ rơ thanh tạ ("lách tách") trước khi nhấc và giữ đòn tạ bám sát đường thẳng dọc ống chân.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Cong gù lưng dưới (Cat-Back) khi nhấc tạ hoặc ngả người quá mức khi khóa đỉnh.',
          risk: 'Lực cắt cực lớn lên đĩa đệm L4–L5/L5–S1 gây thoát vị hoặc đau lưng cấp.',
          fix: 'Nâng ngực, kéo xô hướng túi quần sau và giữ gót chân đạp chắc xuống sàn.',
        ),
      ],
    ),
    'DUMBBELL_SHOULDER_PRESS': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi tựa lưng trên ghế dốc ~80° giữ lưng áp sát đệm.',
        'Đưa hai quả tạ đơn ngang tai với khuỷu tay hơi hướng về trước (~20–30° trong mặt phẳng xương bả vai).',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ xuống từ từ ngang tầm dái tai mà không bẻ gập cổ tay.',
      isometricDetail:
          '0.5 giây · Giữ khuỷu tay ngay dưới cổ tay để bảo toàn đòn bẩy lực an toàn.',
      concentricDetail:
          '1–1.5 giây · Thở ra, đẩy thẳng hai quả tạ lên gần chạm nhẹ phía trên đỉnh đầu.',
      mindMuscleCue:
          'Không xòe hai khuỷu tay sang ngang 180° — đưa nhẹ về trước giúp khớp vai hoạt động êm mượt.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Ưỡn cong lưng dưới rời khỏi đệm ghế khi đẩy tạ nặng.',
          risk: 'Dồn áp lực lên cột sống thắt lưng và biến động tác thành đẩy ngực trên.',
          fix: 'Siết chặt cơ bụng ấn lưng sát mặt ghế, giảm tạ nếu không giữ được lưng thẳng.',
        ),
      ],
    ),
    'DUMBBELL_LATERAL_RAISE': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng chân rộng bằng vai, hơi nghiêng thân trên 5–10°, cầm hai tạ đơn bên hông với khuỷu hơi cong.',
        'Hạ bả vai xuống để cô lập cầu vai trên.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ xuống từ từ bên đùi, luôn giữ căng nhẹ cơ vai giữa.',
      isometricDetail:
          '0.5 giây · Không đặt tạ nghỉ sát đùi — dừng cách thân ~5 cm để giữ áp lực liên tục.',
      concentricDetail:
          '1 giây · Thở ra, vung nhẹ khuỷu tay sang hai bên chếch 15° về trước lên ngang tầm vai.',
      mindMuscleCue:
          'Tưởng tượng đẩy hai quả tạ sang hai bức tường xa thay vì nhấc lên trời, giữ mu bàn tay song song sàn.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Nhún vai lên mang tai và vung lưng lấy đà quá mức.',
          risk: 'Cơ cầu vai trên (Traps) cướp hết tải và dễ gây kẹt gân vai.',
          fix: 'Chọn tạ vừa sức, giữ vai thấp và đưa tay lên tối đa ngang vai (~85–90°).',
        ),
      ],
    ),
    'CABLE_FACE_PULL': ExerciseCoachingGuide(
      setupSteps: [
        'Chỉnh ròng rọc ngang tầm mặt/ngực trên, nắm hai nhánh dây thừng với ngón cái hướng về phía mình.',
        'Bước lùi 2 bước cho dây căng, chân đặt trước–sau giữ thăng bằng.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, duỗi hai tay về phía trước mặt có kiểm soát để mở hai bả vai.',
      isometricDetail:
          '0.5–1 giây · Tạm dừng nhẹ khi dây căng trước mặt mà vẫn giữ thân đứng vững.',
      concentricDetail:
          '1–1.5 giây · Thở ra, kéo dây về hai bên tai (trán) đồng thời xoay cẳng tay hướng nắm đấm ra sau.',
      mindMuscleCue:
          'Kéo sao cho bàn tay ngang hàng hoặc cao hơn khuỷu tay ở cuối pha kéo (tạo dáng chữ W).',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Hạ khuỷu tay thấp hơn cổ tay hoặc kéo dây đâm thẳng vào trán.',
          risk: 'Mất tác dụng xoay ngoài bảo vệ vai và giảm kích thích cơ vai sau.',
          fix: 'Tách rộng hai nhánh dây sang hai bên đầu như động tác gồng bắp tay thể hình.',
        ),
      ],
    ),
    'BARBELL_BICEP_CURL': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng thẳng chân rộng bằng vai, nắm thanh đòn thẳng hoặc EZ rộng bằng vai, lòng bàn tay ngửa.',
        'Ép hai khuỷu tay sát hai bên mạn sườn, gồng chặt mông & bụng để khóa thân người.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ xuống chậm rãi tới khi tay duỗi gần thẳng mà không thả rơi tự do.',
      isometricDetail:
          '0.5 giây · Giữ khuỷu tay yên tại chỗ bên sườn ở điểm thấp nhất.',
      concentricDetail:
          '1–1.5 giây · Thở ra, cuốn cẳng tay lên uốn tạ về gần ngực trên và siết mạnh tay trước.',
      mindMuscleCue:
          'Khuỷu tay đóng vai trò như bản lề cố định — chỉ phần cẳng tay chuyển động.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Vung lưng ra sau và đẩy khuỷu tay trôi ra trước quá xa.',
          risk: 'Cơ vai trước và lưng dưới gánh thay cơ tay trước (Biceps).',
          fix: 'Giữ bả vai khép sau, không để cổ tay gập gãy về phía trong.',
        ),
      ],
    ),
    'DUMBBELL_HAMMER_CURL': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng thẳng vững vàng, mỗi tay cầm một quả tạ đơn đặt dọc thân với lòng bàn tay hướng vào đùi (Neutral Grip).',
        'Giữ cổ tay thẳng và khuỷu tay ép sát thân.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ dọc thân có kiểm soát, không xoay lật cổ tay.',
      isometricDetail:
          '0.5 giây · Giữ tay căng nhẹ ở đáy rep trước khi cuốn lên.',
      concentricDetail:
          '1–1.5 giây · Thở ra, cuốn tạ thẳng lên hướng về phía vai đồng thời siết chặt cơ cánh tay quay & tay trước.',
      mindMuscleCue:
          'Giữ ngón cái luôn hướng thẳng lên trần như động tác cầm búa gõ.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đu đưa thân người hoặc cuốn tạ vắt chéo qua trước ngực lấy đà.',
          risk: 'Giảm thời gian chịu tải của cơ Brachialis và cẳng tay.',
          fix: 'Cuốn từng tay hoặc luân phiên chậm rãi, giữ vai đứng yên hoàn toàn.',
        ),
      ],
    ),
    'INCLINE_DUMBBELL_CURL': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi tựa lưng trên ghế dốc 45°, để hai cánh tay thả thõng tự nhiên thẳng đứng ra phía sau thân.',
        'Xoay lòng bàn tay hướng về trước, lưng áp chặt đệm ghế.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ tạ từ từ về phía sàn để kéo giãn tối đa đầu dài bắp tay trước.',
      isometricDetail:
          '0.5–1 giây · Tạm dừng nhẹ khi hai cánh tay buông thõng phía sau thân, cảm nhận đầu dài bắp tay căng mạnh.',
      concentricDetail:
          '1–1.5 giây · Thở ra, cuốn cẳng tay lên mà không kéo khuỷu tay chạy về trước.',
      mindMuscleCue:
          'Giữ bắp tay trên áp cố định phía sau đường trục thân để tối đa hóa độ kéo giãn.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Kéo hai khuỷu tay trượt lên phía trước ngực và nhấc đầu khỏi ghế.',
          risk: 'Biến bài tập thành cuốn tạ thường và mất tác dụng kéo giãn đầu dài.',
          fix: 'Giảm tạ nhẹ hơn bài đứng 20%, nhấn vai & đầu sát đệm ghế.',
        ),
      ],
    ),
    'CABLE_TRICEP_PUSHDOWN': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng trước trụ cáp cao, hơi cúi thân nhẹ 10°, ép chặt hai khuỷu tay cố định vào mạn sườn.',
        'Nắm hai đầu dây thừng ngang tầm ngực.',
      ],
      eccentricDetail:
          '2 giây · Hít sâu, cho cẳng tay đi lên cao tối đa ngang tầm ngực sao cho khuỷu tay không nhấc lên theo.',
      isometricDetail:
          '0.5 giây · Giữ dây ở vị trí co khuỷu cao nhất mà lưng và vai vẫn bất động.',
      concentricDetail:
          '1 giây · Thở ra, ấn thẳng cẳng tay xuống và hơi tách nhẹ hai nhánh dây về hai bên đùi.',
      mindMuscleCue:
          'Tưởng tượng chỉ duỗi thẳng khớp khuỷu tay và bóp chặt cơ tam đầu ở điểm đáy 0.5s.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Nhấc khuỷu tay trôi ra trước khi hạ lên hoặc đổ cả trọng lượng thân đè dây.',
          risk: 'Cơ lưng xô và ngực gánh lực đẩy xuống thay cho cơ tay sau.',
          fix: 'Khóa cứng bắp tay trên ép vào sườn, chỉ gập và duỗi khớp khuỷu.',
        ),
      ],
    ),
    'SKULL_CRUSHER': ExerciseCoachingGuide(
      setupSteps: [
        'Nằm ngửa trên ghế phẳng, hai chân đạp chắc xuống sàn, đưa thanh tạ lên thẳng trên vai.',
        'Hơi ngả cánh tay trên về phía đầu ~15° so với phương thẳng đứng để giữ cơ tay sau luôn căng.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, gập khuỷu tay hạ thanh tạ về phía sau đỉnh trán (cách trán ~3–5 cm).',
      isometricDetail:
          '0.5 giây · Giữ góc cánh tay trên cố định phía sau đầu ở điểm giãn sâu nhất.',
      concentricDetail:
          '1–1.5 giây · Thở ra, duỗi thẳng cẳng tay đẩy tạ trở lại vị trí đỉnh trên vai.',
      mindMuscleCue:
          'Giữ hai khuỷu tay hướng song song về phía trần nhà — không để mở loe sang hai bên.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Xòe rộng hai khuỷu tay sang ngang hoặc thả tạ lao sát mặt.',
          risk: 'Gây đau nhức gân khuỷu tay (Triceps Tendonitis) và mất an toàn.',
          fix: 'Khép khuỷu tay rộng bằng vai và kiểm soát chậm pha hạ thanh tạ qua đỉnh đầu.',
        ),
      ],
    ),
    'OVERHEAD_DUMBBELL_TRICEP_EXT': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng hoặc ngồi thẳng lưng, hai tay đan ôm mặt trong đĩa tạ đơn đưa thẳng lên qua đỉnh đầu.',
        'Khép hai khuỷu tay hướng chếch về trước, giữ gồng cơ lõi để không võng lưng.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, gập khuỷu tay đưa tạ ra phía sau gáy tới khi cơ tay sau giãn tối đa.',
      isometricDetail:
          '0.5 giây · Dừng nhẹ sau gáy, tránh để tạ đập vào cổ hoặc gáy.',
      concentricDetail:
          '1–1.5 giây · Thở ra, duỗi cẳng tay đẩy quả tạ thẳng lên đỉnh đầu.',
      mindMuscleCue:
          'Bài tập vàng cho đầu dài cơ tay sau — giữ khuỷu tay càng khép gần đầu càng hiệu quả.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Xòe rộng hai khuỷu tay sang hai bên tai và ưỡn võng lưng dưới.',
          risk: 'Căng khớp vai và giảm kích thích đầu dài cơ tam đầu.',
          fix: 'Siết cơ bụng, hướng hai khuỷu tay thẳng lên phía trên hơi chếch trước.',
        ),
      ],
    ),
    'BARBELL_SQUAT': ExerciseCoachingGuide(
      setupSteps: [
        'Đặt thanh đòn lên phần cầu vai/vai sau (High-Bar/Low-Bar), chân rộng hơn vai một chút, mũi chân mở 15–30°.',
        'Hít một hơi thật sâu vào bụng gồng cứng cơ lõi (Bracing) trước khi hạ hông.',
      ],
      eccentricDetail:
          '2–3 giây · Đẩy nhẹ hông ra sau kết hợp gập gối tiến theo hướng mũi chân, hạ người xuống tới khi đùi song song sàn.',
      isometricDetail:
          '0.5 giây · Dừng nhẹ tại đáy Squat mà không thả lỏng bụng hay nảy gối.',
      concentricDetail:
          '1–1.5 giây · Đạp cả bàn chân xuống sàn đẩy hông & ngực lên cùng tốc độ, thở ra qua điểm nặng.',
      mindMuscleCue:
          'Giữ 3 điểm chạm sàn vững (gót + ụ ngón cái + ụ ngón út) và mở gối theo đúng hướng mũi chân.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Gối chụm vào trong (Knee Valgus), nhón gót hoặc gập cong lưng dưới (Butt Wink).',
          risk: 'Chấn thương dây chằng gối ACL/sụn chêm và chèn ép đĩa đệm thắt lưng.',
          fix: 'Chủ động đẩy hai đầu gối mở nhẹ ra ngoài theo mũi chân và giữ lưng phẳng suốt đường đi.',
        ),
      ],
    ),
    'LEG_PRESS': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi tựa mông & lưng dưới áp sát hoàn toàn vào đệm tựa máy 45°.',
        'Đặt hai bàn chân rộng bằng vai ở nửa dưới/giữa bàn đạp, mở chốt an toàn.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ bệ đạp xuống sâu tới khi góc gối đạt ~90° mà mông vẫn dán chặt ghế.',
      isometricDetail:
          '0.5 giây · Giữ tại đáy hành trình trước khi chuyển hướng đẩy.',
      concentricDetail:
          '1–1.5 giây · Thở ra, đạp đều cả gót và mũi chân đẩy bệ lên gần thẳng (~95% biên độ).',
      mindMuscleCue:
          'KHÔNG bao giờ khóa thẳng khớp gối 180° ở đỉnh để tránh nguy hiểm cho khớp gối.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Hạ bệ quá sâu làm cuộn mông rời khỏi đệm tựa hoặc duỗi khóa cứng khớp gối ở đỉnh.',
          risk: 'Ép gập đốt sống thắt lưng cấp tính và quá tải khớp gối.',
          fix: 'Dừng độ sâu ngay trước khi hông có xu hướng nhấc khỏi đệm và giữ gối hơi mềm ở đỉnh.',
        ),
      ],
    ),
    'LEG_EXTENSION': ExerciseCoachingGuide(
      setupSteps: [
        'Chỉnh tựa lưng sao cho kheo gối khớp đúng tâm trục xoay của máy.',
        'Đặt con lăn ngay trên cổ chân trước (không đè lên mu bàn chân), tay nắm chặt hai tay vịn.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, hạ cẳng chân xuống chậm rãi tới góc gập ~90°.',
      isometricDetail:
          '0.5–1 giây · Siết cứng cơ đùi trước trong 0.5–1 giây ngay tại đỉnh khi chân duỗi thẳng.',
      concentricDetail:
          '1 giây · Thở ra, đá thẳng cẳng chân lên đều cả hai chân mà không nhấc mông khỏi ghế.',
      mindMuscleCue:
          'Giữ mũi chân hướng thẳng lên trên và cảm nhận giọt nước cơ đùi trước (VMO) gần gối siết chặt.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đá giật mạnh tạ lên bằng quán tính rồi thả rơi tự do.',
          risk: 'Gây áp lực xé lên khớp bánh chè và gân gối.',
          fix: 'Giảm mức tạ và thực hiện nhịp 1s lên – 1s giữ đỉnh – 2.5s hạ.',
        ),
      ],
    ),
    'ROMANIAN_DEADLIFT': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng cầm đòn tạ trước đùi rộng bằng vai, mở khóa nhẹ đầu gối (~15°) và giữ nguyên góc gối này suốt bài.',
        'Khép nhẹ bả vai ra sau và giữ ngực mở.',
      ],
      eccentricDetail:
          '3 giây · Hít sâu, đẩy hông trượt thẳng ra phía sau (Hip Hinge) để tạ lướt sát dọc đùi xuống ngang giữa ống đồng.',
      isometricDetail:
          '0.5–1 giây · Tạm dừng khi cơ đùi sau căng hết biên độ và thân song song ~75° (không cần chạm đất).',
      concentricDetail:
          '1.5 giây · Thở ra, siết cơ mông & đùi sau kéo hông tiến về trước để đứng thẳng.',
      mindMuscleCue:
          'Tưởng tượng đang dùng mông đẩy đóng một cánh cửa phía sau — tuyệt đối không gập gối sâu biến thành Squat.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đưa thanh tạ trôi xa khỏi ống chân và hạ quá thấp làm cong lưng dưới.',
          risk: 'Tải trọng dồn 100% lên thắt lưng thay vì đùi sau.',
          fix: 'Dừng ngay khi hông không còn đẩy lùi được nữa và luôn giữ đòn tạ sát da chân.',
        ),
      ],
    ),
    'LEG_CURL_MACHINE': ExerciseCoachingGuide(
      setupSteps: [
        'Nằm sấp trên máy, điều chỉnh con lăn nằm ngay trên gót Achilles (ngay dưới bắp chân).',
        'Ấn chặt hông xuống nệm máy và nắm chặt hai tay cầm phía trước.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, duỗi hai chân xuống từ từ giữ căng nhẹ đùi sau.',
      isometricDetail:
          '0.5 giây · Giữ tại vị trí chân gần thẳng nhưng không thả lỏng hoàn toàn khớp gối.',
      concentricDetail:
          '1 giây · Thở ra, cuộn gót chân tiến sát về phía mông đồng thời ép hông bám sát đệm.',
      mindMuscleCue:
          'Giữ hông dán chặt mặt đệm — không để mông nhô cao lên theo nhịp cuộn chân.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Nhấc hông bổng khỏi nệm mỗi lần gập chân lên.',
          risk: 'Cơ gập hông và lưng dưới bù trừ gây đau thắt lưng.',
          fix: 'Siết cơ bụng/mông ép sát xương mu vào đệm và hạ nhẹ mức tạ.',
        ),
      ],
    ),
    'SEATED_LEG_CURL': ExerciseCoachingGuide(
      setupSteps: [
        'Ngồi tựa lưng thẳng, khóa đệm đè đùi chắc chắn ngay trên đầu gối.',
        'Đặt con lăn nằm dưới gót Achilles, mũi chân hướng lên.',
      ],
      eccentricDetail:
          '2–3 giây · Hít sâu, nhả chân duỗi ra trước hết cỡ để kéo giãn tối đa cơ đùi sau ở tư thế ngồi.',
      isometricDetail:
          '0.5 giây · Giữ thẳng gối kiểm soát ở phía trước.',
      concentricDetail:
          '1 giây · Thở ra, kéo mạnh gót chân xuống dưới gầm ghế và giữ 0.5s ở đáy.',
      mindMuscleCue:
          'Độ giãn ở bài ngồi lớn hơn bài nằm — tận dụng nhịp hạ lên chậm để tăng phì đại đùi sau.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đổ người về trước nhấc lưng khỏi tựa ghế khi kéo tạ nặng.',
          risk: 'Làm lỏng chốt đùi và giảm lực kéo giãn cơ đùi sau.',
          fix: 'Ép lưng sát đệm tựa, dùng hai tay nắm chặt tay cầm khóa đùi.',
        ),
      ],
    ),
    'BARBELL_HIP_THRUST': ExerciseCoachingGuide(
      setupSteps: [
        'Tựa cạnh dưới bả vai lên ghế phẳng, đặt thanh đòn có đệm mút ngay trên nếp gấp hông.',
        'Đặt hai bàn chân phẳng trên sàn sao cho khi đẩy lên đỉnh, cẳng chân vuông góc 90° với mặt sàn.',
      ],
      eccentricDetail:
          '2 giây · Hít sâu, hạ mông xuống gần sàn đồng thời giữ cằm hơi thu về ngực.',
      isometricDetail:
          '1 giây · Dừng giữ mạnh ở đỉnh khi thân từ gối tới vai tạo thành đường thẳng ngang.',
      concentricDetail:
          '1 giây · Thở ra, đạp gót chân đẩy hông lên cao và cuộn nhẹ xương chậu siết căng tối đa cơ mông.',
      mindMuscleCue:
          'Mắt luôn nhìn hơi chếch về phía đầu gối giúp cột sống trung tính, không ngửa cổ ra sau.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đẩy hông quá cao bằng cách ưỡn võng lưng dưới và ngửa cổ ra sau.',
          risk: 'Đau thắt lưng cấp và cơ mông không đạt độ co siết cực đại.',
          fix: 'Cuộn nhẹ xương sườn xuống rốn (Posterior Pelvic Tilt) ở đỉnh thay vì ưỡn lưng.',
        ),
      ],
    ),
    'WALKING_LUNGE': ExerciseCoachingGuide(
      setupSteps: [
        'Đứng thẳng cầm hai quả tạ đơn hai bên thân, chân rộng bằng hông.',
        'Mắt nhìn thẳng phía trước, siết nhẹ cơ bụng giữ thân thẳng đứng.',
      ],
      eccentricDetail:
          '2 giây · Hít sâu, bước một chân vừa phải về trước và hạ gối sau xuống cách sàn ~2–3 cm (gối tạo 90°-90°).',
      isometricDetail:
          '0.5 giây · Giữ thăng bằng ổn định ở đáy trước khi đẩy bước tiếp.',
      concentricDetail:
          '1 giây · Thở ra, đạp mạnh cả bàn chân trước (ưu tiên gót & giữa bàn chân) đứng dậy bước chân sau lên.',
      mindMuscleCue:
          'Hơi nghiêng nhẹ thân 10° nếu muốn vào Mông nhiều hơn, giữ thẳng lưng 90° để vào Đùi trước.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Bước quá hẹp khiến gối trước lao vượt quá mũi chân hoặc đập mạnh gối sau xuống sàn.',
          risk: 'Tổn thương sụn bánh chè và va chạm xương đầu gối.',
          fix: 'Điều chỉnh bước chân dài hơn chút để tạo góc vuông 90° cả hai chân khi hạ xuống.',
        ),
      ],
    ),
    'CABLE_GLUTE_KICKBACK': ExerciseCoachingGuide(
      setupSteps: [
        'Đeo đai cổ chân vào trụ cáp thấp, đứng đối diện máy cách 1 cánh tay, hai tay vịn vững vào khung máy.',
        'Nghiêng nhẹ thân 20° và giữ cột sống khóa cứng cố định.',
      ],
      eccentricDetail:
          '2 giây · Hít sâu, đưa chân đá trả về ngang vị trí chân trụ.',
      isometricDetail:
          '0.5–1 giây · Giữ chân đá thẳng ra sau hơi chếch ngoài 15° và siết căng đỉnh cơ mông.',
      concentricDetail:
          '1 giây · Thở ra, đạp gót chân ra phía sau vừa tầm mà không làm võng lưng.',
      mindMuscleCue:
          'Chỉ đá tới góc ~30–40° phía sau — qua mốc đó toàn bộ chuyển động sẽ do lưng dưới gánh.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đá chân quá cao ra sau khiến thắt lưng võng cong rõ rệt.',
          risk: 'Chèn ép đốt sống thắt lưng và mất cô lập cơ mông.',
          fix: 'Siết chặt cơ bụng giữ lưng cố định và dừng biên độ ngay khi cơ mông siết cứng nhất.',
        ),
      ],
    ),
    'HANGING_LEG_RAISE': ExerciseCoachingGuide(
      setupSteps: [
        'Treo người tự nhiên trên xà đơn, hai tay nắm rộng hơn vai một chút.',
        'Hạ bả vai xuống giữ người đứng yên không lắc trước–sau.',
      ],
      eccentricDetail:
          '2.5 giây · Hít sâu, hạ thẳng hoặc hơi co nhẹ hai chân xuống từ từ mà không đánh võng ra sau.',
      isometricDetail:
          '0.5 giây · Hãm đà ở điểm dưới cùng, giữ lõi căng trước khi nâng lượt mới.',
      concentricDetail:
          '1–1.5 giây · Thở ra, cuộn xương chậu nâng hai chân lên cao ngang hoặc vượt góc 90° trước bụng.',
      mindMuscleCue:
          'Bí quyết vào bụng dưới: phải CUỘN XƯƠNG CHẬU (nhấc mông tiến về phía rốn) chứ không chỉ nhấc đùi.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Đu người lấy đà ra sau rồi vung mạnh hai chân lên.',
          risk: 'Cơ gập hông (Hip Flexors) làm hết việc và gây mỏi vai/cột sống.',
          fix: 'Hạ chậm rãi và dừng 0.5s mỗi rep ở đáy để triệt tiêu toàn bộ quán tính đung đưa.',
        ),
      ],
    ),
    'CABLE_CRUNCH': ExerciseCoachingGuide(
      setupSteps: [
        'Quỳ trên thảm cách trụ ròng rọc cao ~60–70 cm, nắm hai đầu dây thừng đặt cố định sát hai bên thái dương/trán.',
        'Giữ hông ngồi cao ổn định (không hạ mông ngồi lên gót chân).',
      ],
      eccentricDetail:
          '2 giây · Hít sâu, ngẩng nhẹ ngực để dải cơ bụng duỗi căng dài.',
      isometricDetail:
          '0.5–1 giây · Giữ siết chặt múi bụng ở điểm gập khuỷu tay hướng sát đầu gối.',
      concentricDetail:
          '1–1.5 giây · Thở hết hơi ra, cuộn tròn đốt sống lưng trên kéo khuỷu tay hướng xuống gần đùi.',
      mindMuscleCue:
          'Khớp hông phải bất động như bản lề khóa — chỉ gập thân trên như đang cuộn một tấm thảm.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Ngồi thụp mông về phía gót chân bằng lực gập hông hoặc kéo dây bằng hai cánh tay.',
          risk: 'Cơ gập hông & tay sau làm thay cơ bụng, dây cáp dễ cọ sát vào đầu/mặt.',
          fix: 'Khóa cố định hông vuông góc, giữ dây cách trán vài cm và tập trung cuộn ngực về phía xương chậu.',
        ),
      ],
    ),
    'PLANK': ExerciseCoachingGuide(
      setupSteps: [
        'Chống hai cẳng tay song song trên thảm sao cho khuỷu tay nằm ngay dưới đường thẳng của vai.',
        'Mũi chân chống vững, gồng chặt cơ bụng, cơ đùi trước và cơ mông cùng lúc.',
      ],
      eccentricDetail:
          'Nhịp thở đều 3s · Hít sâu qua mũi vào khoang bụng trong khi vẫn giữ khung xương ổn định.',
      isometricDetail:
          'Giữ liên tục 30–60s · Thân từ đầu, vai, hông tới gót chân tạo thành một đường thẳng vững chắc.',
      concentricDetail:
          'Thở ra dứt khoát · Kéo nhẹ tưởng tượng khuỷu tay về phía mũi chân để tăng áp lực siết core.',
      mindMuscleCue:
          'Hơi cuộn nhẹ xương cụt xuống sàn để bảo vệ thắt lưng và kích hoạt sâu cơ ngang bụng.',
      badFormDetails: [
        ExerciseBadFormDetail(
          error: 'Sụp võng hông thấp xuống thảm hoặc đẩy mông nhô cao lên trần.',
          risk: 'Đau mỏi thắt lưng do cơ lõi mất sức giữ cột sống.',
          fix: 'Dừng hiệp ngay khi form bắt đầu sụp võng thay vì cố ráng thêm thời gian sai kỹ thuật.',
        ),
      ],
    ),
  };
}
