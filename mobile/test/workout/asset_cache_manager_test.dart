// [OWNER: M2] Unit tests cho AssetCacheManager & SHA-256 (T-M2-05)
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:vigorai_app/features/gym3d/data/asset_cache_manager.dart';
import 'package:vigorai_app/features/gym3d/data/sha256_util.dart';

void main() {
  group('Sha256Util (FIPS 180-4 vectors)', () {
    test('computes standard NIST test vectors accurately', () {
      expect(
        sha256String(''),
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      );
      expect(
        sha256String('abc'),
        'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
      );
      expect(
        sha256String('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq'),
        '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1',
      );
    });
  });

  group('AssetCacheManager', () {
    late Directory tempDir;

    setUp(() async {
      tempDir = await Directory.systemTemp.createTemp('vigorai_cache_test_');
    });

    tearDown(() async {
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    test('returns bundled asset paths directly without network download', () async {
      var downloadCalled = false;
      final mgr = AssetCacheManager(
        cacheDirectoryResolver: () async => tempDir,
        downloadFn: (_, __) async {
          downloadCalled = true;
        },
      );

      final result = await mgr.getOrDownloadGlb(
        exerciseCode: 'BARBELL_SQUAT',
        remoteUrl: 'assets/3d_bundled/barbell_squat.glb',
        expectedSha256: 'ignored',
      );

      expect(result, 'assets/3d_bundled/barbell_squat.glb');
      expect(downloadCalled, isFalse);
    });

    test('downloads remote glb once, verifies SHA-256, and serves subsequent calls from cache',
        () async {
      final payload = Uint8List.fromList(List<int>.generate(2048, (i) => i % 251));
      final expectedSha = sha256Hex(payload);
      var downloadCount = 0;

      final mgr = AssetCacheManager(
        cacheDirectoryResolver: () async => tempDir,
        downloadFn: (url, savePath) async {
          downloadCount++;
          await File(savePath).writeAsBytes(payload, flush: true);
        },
      );

      final firstPath = await mgr.getOrDownloadGlb(
        exerciseCode: 'BARBELL_DEADLIFT',
        remoteUrl: 'https://cdn.vigorai.app/exercises/barbell_deadlift.glb',
        expectedSha256: expectedSha,
      );
      final secondPath = await mgr.getOrDownloadGlb(
        exerciseCode: 'BARBELL_DEADLIFT',
        remoteUrl: 'https://cdn.vigorai.app/exercises/barbell_deadlift.glb',
        expectedSha256: expectedSha,
      );

      expect(downloadCount, 1);
      expect(firstPath, startsWith('file://'));
      expect(secondPath, firstPath);
      expect(await File(Uri.parse(firstPath).toFilePath()).exists(), isTrue);
      expect(await mgr.getCacheSizeBytes(), payload.length);
    });

    test('rejects corrupted download when SHA-256 mismatches and cleans tmp file', () async {
      final badPayload = Uint8List.fromList(List<int>.filled(512, 42));
      const wrongSha =
          '0000000000000000000000000000000000000000000000000000000000000000';

      final mgr = AssetCacheManager(
        cacheDirectoryResolver: () async => tempDir,
        downloadFn: (_, savePath) async {
          await File(savePath).writeAsBytes(badPayload, flush: true);
        },
      );

      await expectLater(
        () => mgr.getOrDownloadGlb(
          exerciseCode: 'LAT_PULLDOWN',
          remoteUrl: 'https://cdn.vigorai.app/exercises/lat_pulldown.glb',
          expectedSha256: wrongSha,
        ),
        throwsA(isA<AssetChecksumMismatchException>()),
      );

      expect(await mgr.getCacheSizeBytes(), 0);
      final dir = Directory('${tempDir.path}${Platform.pathSeparator}3d_assets');
      final entries = await dir.list().toList();
      expect(entries.where((e) => e.path.endsWith('.tmp')), isEmpty);
    });

    test('evicts least-recently-used files when cache exceeds limit and clears all cleanly',
        () async {
      var nowMs = 1000;
      final payloads = <String, Uint8List>{
        'EX_A': Uint8List.fromList(List<int>.filled(600, 1)),
        'EX_B': Uint8List.fromList(List<int>.filled(600, 2)),
        'EX_C': Uint8List.fromList(List<int>.filled(600, 3)),
      };

      final mgr = AssetCacheManager(
        cacheDirectoryResolver: () async => tempDir,
        maxCacheBytesOverride: 1300, // fits at most 2 files of 600 bytes
        nowProvider: () => DateTime.fromMillisecondsSinceEpoch(nowMs, isUtc: true),
        downloadFn: (url, savePath) async {
          final code = payloads.keys.firstWhere((k) => url.contains(k.toLowerCase()));
          await File(savePath).writeAsBytes(payloads[code]!, flush: true);
        },
      );

      await mgr.getOrDownloadGlb(
        exerciseCode: 'EX_A',
        remoteUrl: 'https://cdn.vigorai.app/exercises/ex_a.glb',
        expectedSha256: sha256Hex(payloads['EX_A']!),
      );
      nowMs = 2000;
      await mgr.getOrDownloadGlb(
        exerciseCode: 'EX_B',
        remoteUrl: 'https://cdn.vigorai.app/exercises/ex_b.glb',
        expectedSha256: sha256Hex(payloads['EX_B']!),
      );
      // Touch EX_A so EX_B becomes the least recently used
      nowMs = 3000;
      await mgr.getOrDownloadGlb(
        exerciseCode: 'EX_A',
        remoteUrl: 'https://cdn.vigorai.app/exercises/ex_a.glb',
        expectedSha256: sha256Hex(payloads['EX_A']!),
      );
      // Downloading EX_C (600B) should evict EX_B, keeping EX_A and EX_C (1200B <= 1300B)
      nowMs = 4000;
      await mgr.getOrDownloadGlb(
        exerciseCode: 'EX_C',
        remoteUrl: 'https://cdn.vigorai.app/exercises/ex_c.glb',
        expectedSha256: sha256Hex(payloads['EX_C']!),
      );

      expect(await mgr.getCacheSizeBytes(), 1200);
      final assetsPath = '${tempDir.path}${Platform.pathSeparator}3d_assets';
      expect(await File('$assetsPath${Platform.pathSeparator}ex_a.glb').exists(), isTrue);
      expect(await File('$assetsPath${Platform.pathSeparator}ex_b.glb').exists(), isFalse);
      expect(await File('$assetsPath${Platform.pathSeparator}ex_c.glb').exists(), isTrue);

      await mgr.clearAllCachedAssets();
      expect(await Directory(assetsPath).exists(), isFalse);
    });
  });
}
