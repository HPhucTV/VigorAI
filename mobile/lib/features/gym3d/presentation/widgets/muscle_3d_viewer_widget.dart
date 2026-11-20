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

/// Giao dien cong khai da duoc khoa de dung chung cho F07-F13 (M2) va F23 (M2/M4 contract).
class Muscle3DViewerWidget extends StatefulWidget {
  final String glbAssetOrUrl;
  final Map<String, Color> muscleColorsMap;
  final String animationName;
  final double playbackSpeed;
  final CameraPreset3D cameraPreset;
  final ValueChanged<String>? onMuscleTap;
  final bool isPlaying;
  final double height;

  const Muscle3DViewerWidget({
    super.key,
    required this.glbAssetOrUrl,
    this.muscleColorsMap = const {},
    this.animationName = 'Anim_GoodForm',
    this.playbackSpeed = 1.0,
    this.cameraPreset = CameraPreset3D.front,
    this.onMuscleTap,
    this.isPlaying = true,
    this.height = 340,
  });

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
    _loadTimeoutTimer = Timer(const Duration(seconds: 8), () {
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

    return '''
(function() {
  const getMv = () => document.getElementById('vigor-mv');

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
      window.vigorSetAnim($initialAnim, $initialSpeed, $initialPlaying);
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
