// [OWNER: M2] Widget 3D dung chung cho Phong tap 3D (F07-F13) va Ban do Phuc hoi 3D (F23)
import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:model_viewer_plus/model_viewer_plus.dart';

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

  static const Map<String, String> _labelsVi = {
    chest: 'Cơ Ngực (Pectorals)',
    shoulders: 'Cơ Vai (Deltoids)',
    biceps: 'Cơ Tay trước (Biceps)',
    triceps: 'Cơ Tay sau (Triceps)',
    backLats: 'Cơ Lưng Xô (Lats)',
    traps: 'Cơ Cầu vai & Lưng trên (Traps)',
    absCore: 'Cơ Bụng & Lõi (Core)',
    glutes: 'Cơ Mông (Glutes)',
    quads: 'Cơ Đùi trước (Quads)',
    hamstrings: 'Cơ Đùi sau (Hamstrings)',
    calves: 'Cơ Bắp chân (Calves)',
  };

  static String labelVi(String materialId) =>
      _labelsVi[materialId] ?? materialId;
}

enum CameraPreset3D { front, side, back, top }

/// Trong so bien doi hinh the 3D (Morph Targets) dieu khien truc tiep o 60 FPS.
class BodyMorphWeights {
  final double slim;
  final double bodyFat;
  final double muscleMass;

  const BodyMorphWeights({
    this.slim = 0.0,
    this.bodyFat = 0.0,
    this.muscleMass = 0.0,
  });

  static const zero = BodyMorphWeights();

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is BodyMorphWeights &&
        (slim * 1000).round() == (other.slim * 1000).round() &&
        (bodyFat * 1000).round() == (other.bodyFat * 1000).round() &&
        (muscleMass * 1000).round() == (other.muscleMass * 1000).round();
  }

  @override
  int get hashCode => Object.hash(
        (slim * 1000).round(),
        (bodyFat * 1000).round(),
        (muscleMass * 1000).round(),
      );
}

enum BodyAvatarPreset {
  maleSlim(
    code: 'MALE_SLIM',
    labelVi: 'Nam - Thon gầy',
    shortLabelVi: 'Nam Gầy',
    isFemale: false,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_male_slim.glb',
    defaultMorph: BodyMorphWeights(slim: 0.85),
    scaleX: 0.94,
    scaleY: 1.0,
    scaleZ: 0.94,
  ),
  maleFit(
    code: 'MALE_FIT',
    labelVi: 'Nam - Thể thao chuẩn',
    shortLabelVi: 'Nam Chuẩn',
    isFemale: false,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin.glb',
    defaultMorph: BodyMorphWeights.zero,
    scaleX: 1.0,
    scaleY: 1.0,
    scaleZ: 1.0,
  ),
  maleBulk(
    code: 'MALE_BULK',
    labelVi: 'Nam - Cơ bắp V-Taper',
    shortLabelVi: 'Nam Cơ bắp',
    isFemale: false,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_male_muscular.glb',
    defaultMorph: BodyMorphWeights(bodyFat: 0.05, muscleMass: 0.92),
    scaleX: 1.06,
    scaleY: 1.01,
    scaleZ: 1.05,
  ),
  maleHeavy(
    code: 'MALE_HEAVY',
    labelVi: 'Nam - Đầy đặn',
    shortLabelVi: 'Nam Đầy đặn',
    isFemale: false,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_male_heavy.glb',
    defaultMorph: BodyMorphWeights(bodyFat: 0.88, muscleMass: 0.22),
    scaleX: 1.09,
    scaleY: 1.0,
    scaleZ: 1.10,
  ),
  femaleSlim(
    code: 'FEMALE_SLIM',
    labelVi: 'Nữ - Thon mảnh',
    shortLabelVi: 'Nữ Mảnh',
    isFemale: true,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_female_slim.glb',
    defaultMorph: BodyMorphWeights(slim: 0.82),
    scaleX: 0.88,
    scaleY: 0.94,
    scaleZ: 0.88,
  ),
  femaleFit(
    code: 'FEMALE_FIT',
    labelVi: 'Nữ - Fitness chuẩn',
    shortLabelVi: 'Nữ Fitness',
    isFemale: true,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_female.glb',
    defaultMorph: BodyMorphWeights.zero,
    scaleX: 0.92,
    scaleY: 0.94,
    scaleZ: 0.92,
  ),
  femaleToned(
    code: 'FEMALE_TONED',
    labelVi: 'Nữ - Mông & Đùi săn',
    shortLabelVi: 'Nữ Săn chắc',
    isFemale: true,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_female_toned.glb',
    defaultMorph: BodyMorphWeights(slim: 0.15, muscleMass: 0.90),
    scaleX: 0.93,
    scaleY: 0.94,
    scaleZ: 0.95,
  ),
  femaleCurvy(
    code: 'FEMALE_CURVY',
    labelVi: 'Nữ - Đầy đặn',
    shortLabelVi: 'Nữ Đầy đặn',
    isFemale: true,
    mannequinAssetPath: 'assets/3d_bundled/base_mannequin_female_curvy.glb',
    defaultMorph: BodyMorphWeights(bodyFat: 0.85, muscleMass: 0.15),
    scaleX: 0.98,
    scaleY: 0.94,
    scaleZ: 1.00,
  );

  final String code;
  final String labelVi;
  final String shortLabelVi;
  final bool isFemale;
  final String mannequinAssetPath;
  final BodyMorphWeights defaultMorph;
  final double scaleX;
  final double scaleY;
  final double scaleZ;

  const BodyAvatarPreset({
    required this.code,
    required this.labelVi,
    required this.shortLabelVi,
    required this.isFemale,
    required this.mannequinAssetPath,
    required this.defaultMorph,
    required this.scaleX,
    required this.scaleY,
    required this.scaleZ,
  });

  String get baseMannequinAssetPath => mannequinAssetPath;

  String get masterMannequinAssetPath => isFemale
      ? 'assets/3d_bundled/base_mannequin_female.glb'
      : 'assets/3d_bundled/base_mannequin.glb';

  static BodyAvatarPreset fromCode(String? raw) {
    final upper = raw?.toUpperCase();
    for (final p in values) {
      if (p.code == upper) return p;
    }
    return BodyAvatarPreset.maleFit;
  }

  static List<BodyAvatarPreset> forGender(String gender) {
    final wantFemale = gender.toUpperCase() == 'FEMALE';
    return values.where((p) => p.isFemale == wantFemale).toList();
  }
}

/// Giao dien cong khai da duoc khoa de dung chung cho F07-F13 (M2) va F23 (M2/M4 contract).
class Muscle3DViewerWidget extends StatefulWidget {
  final String glbAssetOrUrl;
  final Map<String, Color> muscleColorsMap;
  final String animationName;
  final double playbackSpeed;
  final CameraPreset3D cameraPreset;
  final ValueChanged<String>? onMuscleTap;
  final VoidCallback? onModelLoaded;
  final bool isPlaying;
  final double height;
  final double? normalizedProgress;
  final BodyAvatarPreset avatarPreset;
  final BodyMorphWeights? bodyMorph;

  const Muscle3DViewerWidget({
    super.key,
    required this.glbAssetOrUrl,
    this.muscleColorsMap = const {},
    this.animationName = 'Anim_GoodForm',
    this.playbackSpeed = 1.0,
    this.cameraPreset = CameraPreset3D.front,
    this.onMuscleTap,
    this.onModelLoaded,
    this.isPlaying = true,
    this.height = 340,
    this.normalizedProgress,
    this.avatarPreset = BodyAvatarPreset.maleFit,
    this.bodyMorph,
  });

  /// Tranh nhan doi ty le thu nho / phong to khi dang tai san cac mannequin 3D chuyen biet.
  static ({double x, double y, double z}) effectiveScaleFor(
    BodyAvatarPreset preset,
    String glbAssetOrUrl,
  ) {
    if (glbAssetOrUrl.contains('base_mannequin')) {
      return (x: 1.0, y: 1.0, z: 1.0);
    }
    return (x: preset.scaleX, y: preset.scaleY, z: preset.scaleZ);
  }

  @override
  State<Muscle3DViewerWidget> createState() => _Muscle3DViewerWidgetState();
}

class _Muscle3DViewerWidgetState extends State<Muscle3DViewerWidget> {
  dynamic _webController;
  bool _isModelLoaded = false;
  String? _errorMessage;
  int _reloadNonce = 0;
  Timer? _loadTimeoutTimer;

  @override
  void initState() {
    super.initState();
    _startLoadWatchdog();
  }

  void _startLoadWatchdog() {
    _loadTimeoutTimer?.cancel();
    _loadTimeoutTimer = Timer(const Duration(seconds: 15), () {
      if (!mounted || _isModelLoaded) return;
      setState(() {
        _errorMessage = 'Không thể dựng mô hình 3D. Vui lòng thử tải lại.';
      });
    });
  }

  void _retryLoad() {
    setState(() {
      _isModelLoaded = false;
      _errorMessage = null;
      _reloadNonce++;
    });
    _startLoadWatchdog();
  }

  static double _srgbToLinear(double c) {
    if (c <= 0.04045) return c / 12.92;
    return math.pow((c + 0.055) / 1.055, 2.4).toDouble();
  }

  static String _orbitForPreset(CameraPreset3D preset) {
    switch (preset) {
      case CameraPreset3D.front:
        return '0deg 78deg auto';
      case CameraPreset3D.side:
        return '90deg 78deg auto';
      case CameraPreset3D.back:
        return '180deg 78deg auto';
      case CameraPreset3D.top:
        return '0deg 14deg auto';
    }
  }

  Map<String, List<double>> _buildFullLinearColorPayload(
    Map<String, Color> overrides,
  ) {
    const neutral = [0.341, 0.341, 0.341, 1.0];
    final payload = <String, List<double>>{};
    for (final matId in MuscleMaterialIds.all) {
      final color = overrides[matId];
      if (color == null) {
        payload[matId] = neutral;
      } else {
        payload[matId] = [
          _srgbToLinear(color.r),
          _srgbToLinear(color.g),
          _srgbToLinear(color.b),
          color.a,
        ];
      }
    }
    return payload;
  }

  String _buildBridgeJs() {
    final initialColors = jsonEncode(
      _buildFullLinearColorPayload(widget.muscleColorsMap),
    );
    final initialAnim = jsonEncode(widget.animationName);
    final initialSpeed = widget.playbackSpeed;
    final initialPlaying = widget.isPlaying;
    final initialProgress = widget.normalizedProgress;
    final scale = Muscle3DViewerWidget.effectiveScaleFor(
      widget.avatarPreset,
      widget.glbAssetOrUrl,
    );
    final morph = widget.bodyMorph ?? BodyMorphWeights.zero;

    return '''
(function() {
  const getMv = () => document.getElementById('vigor-mv');
  let pendingMorph = [${morph.slim}, ${morph.bodyFat}, ${morph.muscleMass}];

  window.vigorApplyColors = function(colorMap) {
    try {
      const mv = getMv();
      if (!mv || !mv.model) return;
      for (const [matName, rgba] of Object.entries(colorMap)) {
        const mat = mv.model.getMaterialByName(matName);
        if (!mat || !mat.pbrMetallicRoughness) continue;
        mat.pbrMetallicRoughness.setBaseColorFactor(rgba);
        const isNeutral = Math.abs(rgba[0] - 0.341) < 0.01 &&
                          Math.abs(rgba[1] - 0.341) < 0.01 &&
                          Math.abs(rgba[2] - 0.341) < 0.01;
        if (typeof mat.setEmissiveFactor === 'function') {
          mat.setEmissiveFactor(isNeutral ? [0, 0, 0] : [rgba[0] * 0.14, rgba[1] * 0.14, rgba[2] * 0.14]);
        }
      }
    } catch (e) {}
  };

  window.vigorSetCamera = function(orbit) {
    try {
      const mv = getMv();
      if (mv) mv.cameraOrbit = orbit;
    } catch (e) {}
  };

  window.vigorSetAnim = function(animName, speed, playing) {
    try {
      const mv = getMv();
      if (!mv) return;
      mv.timeScale = speed;
      if (animName && mv.animationName !== animName) {
        mv.animationName = animName;
      }
      if (playing) {
        if (typeof mv.play === 'function') mv.play();
      } else {
        if (typeof mv.pause === 'function') mv.pause();
      }
    } catch (e) {}
  };

  window.vigorSeekNormalized = function(norm) {
    try {
      const mv = getMv();
      if (!mv) return;
      const dur = mv.duration || 3.33;
      const clamped = Math.max(0.0, Math.min(1.0, norm));
      mv.currentTime = clamped * dur;
    } catch (e) {}
  };

  window.vigorSetAvatarPreset = function(sx, sy, sz) {
    try {
      const mv = getMv();
      if (!mv) return;
      mv.scale = sx + ' ' + sy + ' ' + sz;
    } catch (e) {}
  };

  window.vigorSetBodyMorph = function(slim, fat, muscle) {
    pendingMorph = [slim, fat, muscle];
    try {
      const mv = getMv();
      if (!mv || !mv.loaded) return;
      const syms = Object.getOwnPropertySymbols(mv);
      const symScene = syms.find(s => s.description === 'scene');
      const symNeedsRender = syms.find(s => s.description === 'needsRender');
      const scene = symScene ? mv[symScene] : null;
      if (!scene || typeof scene.traverse !== 'function') return;
      scene.traverse(function(node) {
        if (!node || !node.isMesh || !Array.isArray(node.morphTargetInfluences)) return;
        const inf = node.morphTargetInfluences;
        if (inf.length === 0) return;
        const dict = node.morphTargetDictionary || {};
        const idxSlim = dict['Morph_Slim'] !== undefined ? dict['Morph_Slim'] : 0;
        const idxFat = dict['Morph_BodyFat'] !== undefined ? dict['Morph_BodyFat'] : 1;
        const idxMus = dict['Morph_MuscleMass'] !== undefined ? dict['Morph_MuscleMass'] : 2;
        if (idxSlim < inf.length) inf[idxSlim] = slim;
        if (idxFat < inf.length) inf[idxFat] = fat;
        if (idxMus < inf.length) inf[idxMus] = muscle;
      });
      if (typeof scene.queueRender === 'function') scene.queueRender();
      if (symNeedsRender) mv[symNeedsRender] = true;
    } catch (e) {}
  };

  function bindViewer() {
    const mv = getMv();
    if (!mv) {
      setTimeout(bindViewer, 100);
      return;
    }
    const onLoaded = function() {
      if (window.VigorStatusChannel) {
        window.VigorStatusChannel.postMessage('loaded');
      }
      window.vigorApplyColors($initialColors);
      window.vigorSetAvatarPreset(${scale.x}, ${scale.y}, ${scale.z});
      window.vigorSetBodyMorph(pendingMorph[0], pendingMorph[1], pendingMorph[2]);
      window.vigorSetAnim($initialAnim, $initialSpeed, $initialPlaying);
      ${initialProgress != null ? 'window.vigorSeekNormalized($initialProgress);' : ''}
    };
    if (mv.loaded) onLoaded();
    mv.addEventListener('load', onLoaded);
    mv.addEventListener('error', function() {
      if (window.VigorStatusChannel) {
        window.VigorStatusChannel.postMessage('error');
      }
    });

    let downX = 0, downY = 0;
    mv.addEventListener('pointerdown', function(e) {
      downX = e.clientX;
      downY = e.clientY;
    });
    mv.addEventListener('pointerup', function(e) {
      try {
        const dx = e.clientX - downX;
        const dy = e.clientY - downY;
        if (dx * dx + dy * dy > 64) return;
        if (typeof mv.materialFromPoint !== 'function') return;
        const mat = mv.materialFromPoint(e.clientX, e.clientY);
        if (mat && mat.name && mat.name.startsWith('Mat_Muscle_') && window.VigorMuscleChannel) {
          window.VigorMuscleChannel.postMessage(mat.name);
        }
      } catch (_) {}
    });
  }
  bindViewer();
})();
''';
  }

  Future<void> _runJs(String script) async {
    final ctrl = _webController;
    if (ctrl == null) return;
    try {
      await ctrl.runJavaScript(script);
    } catch (_) {
      // Ignore transient calls before WebView finishes mounting
    }
  }

  @override
  void didUpdateWidget(covariant Muscle3DViewerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (oldWidget.glbAssetOrUrl != widget.glbAssetOrUrl) {
      setState(() {
        _isModelLoaded = false;
        _errorMessage = null;
      });
      _startLoadWatchdog();
      return;
    }

    if (!mapEquals(oldWidget.muscleColorsMap, widget.muscleColorsMap)) {
      final payload = jsonEncode(
        _buildFullLinearColorPayload(widget.muscleColorsMap),
      );
      _runJs('window.vigorApplyColors && window.vigorApplyColors($payload);');
    }

    if (oldWidget.cameraPreset != widget.cameraPreset) {
      final orbit = jsonEncode(_orbitForPreset(widget.cameraPreset));
      _runJs('window.vigorSetCamera && window.vigorSetCamera($orbit);');
    }

    if (oldWidget.animationName != widget.animationName ||
        oldWidget.playbackSpeed != widget.playbackSpeed ||
        oldWidget.isPlaying != widget.isPlaying) {
      final anim = jsonEncode(widget.animationName);
      _runJs(
        'window.vigorSetAnim && window.vigorSetAnim($anim, ${widget.playbackSpeed}, ${widget.isPlaying});',
      );
    }

    if (widget.normalizedProgress != null &&
        oldWidget.normalizedProgress != widget.normalizedProgress) {
      _runJs(
        'window.vigorSeekNormalized && window.vigorSeekNormalized(${widget.normalizedProgress});',
      );
    }

    if (oldWidget.avatarPreset != widget.avatarPreset) {
      final scale = Muscle3DViewerWidget.effectiveScaleFor(
        widget.avatarPreset,
        widget.glbAssetOrUrl,
      );
      _runJs(
        'window.vigorSetAvatarPreset && window.vigorSetAvatarPreset(${scale.x}, ${scale.y}, ${scale.z});',
      );
    }

    if (oldWidget.bodyMorph != widget.bodyMorph) {
      final morph = widget.bodyMorph ?? BodyMorphWeights.zero;
      _runJs(
        'window.vigorSetBodyMorph && window.vigorSetBodyMorph(${morph.slim}, ${morph.bodyFat}, ${morph.muscleMass});',
      );
    }
  }

  @override
  void dispose() {
    _loadTimeoutTimer?.cancel();
    _loadTimeoutTimer = null;
    final ctrl = _webController;
    _webController = null;
    if (ctrl != null) {
      try {
        ctrl.runJavaScript(
          "try{const mv=document.getElementById('vigor-mv');if(mv){mv.pause();mv.src='';}}catch(_){}",
        );
      } catch (_) {}
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: widget.height,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: const Color(0xFF12161F),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Stack(
        children: [
          ModelViewer(
            key: ValueKey<String>('${widget.glbAssetOrUrl}#$_reloadNonce'),
            id: 'vigor-mv',
            src: widget.glbAssetOrUrl,
            alt: 'Mô hình giải phẫu cơ bắp 3D VigorAI',
            loading: Loading.eager,
            backgroundColor: const Color(0xFF12161F),
            cameraControls: true,
            disablePan: true,
            autoRotate: false,
            interactionPrompt: InteractionPrompt.none,
            cameraOrbit: _orbitForPreset(widget.cameraPreset),
            interpolationDecay: 120,
            exposure: 1.05,
            animationName: widget.animationName,
            autoPlay: widget.isPlaying,
            ar: false,
            debugLogging: false,
            relatedJs: _buildBridgeJs(),
            javascriptChannels: {
              JavascriptChannel(
                'VigorMuscleChannel',
                onMessageReceived: (message) {
                  widget.onMuscleTap?.call(message.message);
                },
              ),
              JavascriptChannel(
                'VigorStatusChannel',
                onMessageReceived: (message) {
                  if (!mounted) return;
                  if (message.message == 'loaded') {
                    _loadTimeoutTimer?.cancel();
                    setState(() {
                      _isModelLoaded = true;
                      _errorMessage = null;
                    });
                    widget.onModelLoaded?.call();
                  } else if (message.message.startsWith('error')) {
                    _loadTimeoutTimer?.cancel();
                    setState(() {
                      _errorMessage = 'Không thể tải mô hình 3D.';
                    });
                  }
                },
              ),
            },
            onWebViewCreated: (controller) {
              _webController = controller;
            },
          ),
          if (!_isModelLoaded)
            Positioned.fill(
              child: ColoredBox(
                color: const Color(0xFF12161F),
                child: Center(
                  child: _errorMessage != null
                      ? Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(
                                Icons.warning_amber_rounded,
                                color: Colors.amber,
                                size: 32,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _errorMessage!,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  color: Colors.white70,
                                  fontSize: 13,
                                ),
                              ),
                              const SizedBox(height: 12),
                              OutlinedButton.icon(
                                onPressed: _retryLoad,
                                icon: const Icon(
                                  Icons.refresh,
                                  size: 18,
                                  color: Colors.white,
                                ),
                                label: const Text(
                                  'Thử tải lại',
                                  style: TextStyle(color: Colors.white),
                                ),
                                style: OutlinedButton.styleFrom(
                                  side: const BorderSide(color: Colors.white38),
                                ),
                              ),
                            ],
                          ),
                        )
                      : const Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(strokeWidth: 2.5),
                            SizedBox(height: 10),
                            Text(
                              'Đang dựng mô hình 3D...',
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
