// [OWNER: M2] Quan ly Lazy-Loading, kiem tra SHA-256 va LRU Cache toi da 250MB cho file .glb (T-M2-05 / F07)
import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import '../../../core/network/dio_client.dart';
import 'sha256_util.dart';

typedef GlbDownloadFn = Future<void> Function(String remoteUrl, String savePath);

class AssetChecksumMismatchException implements Exception {
  final String exerciseCode;
  final String expectedSha256;
  final String actualSha256;

  AssetChecksumMismatchException({
    required this.exerciseCode,
    required this.expectedSha256,
    required this.actualSha256,
  });

  @override
  String toString() =>
      'AssetChecksumMismatchException($exerciseCode: expected $expectedSha256, got $actualSha256)';
}

class _CacheEntry {
  final String fileName;
  final String sha256;
  final int sizeBytes;
  int lastAccessedMs;

  _CacheEntry({
    required this.fileName,
    required this.sha256,
    required this.sizeBytes,
    required this.lastAccessedMs,
  });

  factory _CacheEntry.fromJson(String fileName, Map<String, dynamic> json) {
    return _CacheEntry(
      fileName: fileName,
      sha256: (json['sha256'] as String?) ?? '',
      sizeBytes: (json['size_bytes'] as num?)?.toInt() ?? 0,
      lastAccessedMs: (json['last_accessed_ms'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'sha256': sha256,
        'size_bytes': sizeBytes,
        'last_accessed_ms': lastAccessedMs,
      };
}

class AssetCacheManager {
  static const int maxCacheBytes = 250 * 1024 * 1024; // 250 MB

  final Dio? _dio;
  final GlbDownloadFn? _customDownloadFn;
  final Future<Directory> Function() _cacheBaseDirResolver;
  final int maxBytes;
  final DateTime Function() _nowProvider;

  AssetCacheManager({
    Dio? dio,
    GlbDownloadFn? downloadFn,
    Future<Directory> Function()? cacheDirectoryResolver,
    int? maxCacheBytesOverride,
    DateTime Function()? nowProvider,
  })  : _dio = dio,
        _customDownloadFn = downloadFn,
        _cacheBaseDirResolver =
            cacheDirectoryResolver ?? getApplicationSupportDirectory,
        maxBytes = maxCacheBytesOverride ?? maxCacheBytes,
        _nowProvider = nowProvider ?? (() => DateTime.now().toUtc());

  Future<Directory> _assetsDir() async {
    final base = await _cacheBaseDirResolver();
    final dir = Directory(p.join(base.path, '3d_assets'));
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return dir;
  }

  File _indexFile(Directory dir) => File(p.join(dir.path, 'cache_index.json'));

  Future<Map<String, _CacheEntry>> _readIndex(Directory dir) async {
    final idxFile = _indexFile(dir);
    if (!await idxFile.exists()) return {};
    try {
      final raw = jsonDecode(await idxFile.readAsString()) as Map<String, dynamic>;
      return raw.map(
        (key, value) => MapEntry(
          key,
          _CacheEntry.fromJson(key, value as Map<String, dynamic>),
        ),
      );
    } catch (_) {
      return {};
    }
  }

  Future<void> _writeIndex(Directory dir, Map<String, _CacheEntry> index) async {
    final idxFile = _indexFile(dir);
    final payload = index.map((k, v) => MapEntry(k, v.toJson()));
    await idxFile.writeAsString(jsonEncode(payload), flush: true);
  }

  bool _isValidSha256Hex(String value) {
    if (value.length != 64) return false;
    return RegExp(r'^[0-9a-fA-F]{64}$').hasMatch(value);
  }

  String _sanitizeFileName(String exerciseCode) {
    final clean = exerciseCode.toLowerCase().replaceAll(RegExp(r'[^a-z0-9_-]'), '_');
    return '$clean.glb';
  }

  Future<String> getOrDownloadGlb({
    required String exerciseCode,
    required String remoteUrl,
    required String expectedSha256,
  }) async {
    // 1. Tai nguyen dong goi san trong APK/AAB (base_mannequin + 3 bai mau MVP)
    if (remoteUrl.startsWith('assets/')) {
      return remoteUrl;
    }

    final dir = await _assetsDir();
    final fileName = _sanitizeFileName(exerciseCode);
    final targetFile = File(p.join(dir.path, fileName));
    final tmpFile = File(p.join(dir.path, '$fileName.tmp'));
    final index = await _readIndex(dir);
    final normalizedExpected = expectedSha256.trim().toLowerCase();
    final requireStrictSha = _isValidSha256Hex(normalizedExpected);

    // 2. Kiem tra cache hit & doi chieu checksum
    if (await targetFile.exists()) {
      final existingEntry = index[fileName];
      final diskSha = await sha256File(targetFile);
      final matchesExpected = !requireStrictSha ||
          (diskSha == normalizedExpected &&
              (existingEntry == null || existingEntry.sha256 == normalizedExpected));

      if (matchesExpected) {
        final size = await targetFile.length();
        index[fileName] = _CacheEntry(
          fileName: fileName,
          sha256: diskSha,
          sizeBytes: size,
          lastAccessedMs: _nowProvider().millisecondsSinceEpoch,
        );
        await _writeIndex(dir, index);
        return targetFile.uri.toString();
      }

      // Checksum khong khop (file loi hoac phien ban moi tren CDN) -> xoa tai lai
      await targetFile.delete();
      index.remove(fileName);
      await _writeIndex(dir, index);
    }

    // 3. Lazy-load tu CDN vao file tam `.tmp`
    if (await tmpFile.exists()) {
      await tmpFile.delete();
    }

    try {
      if (_customDownloadFn != null) {
        await _customDownloadFn(remoteUrl, tmpFile.path);
      } else {
        final client = _dio ?? Dio();
        await client.download(remoteUrl, tmpFile.path);
      }

      if (!await tmpFile.exists()) {
        throw StateError('Download completed without creating ${tmpFile.path}');
      }

      final downloadedSha = await sha256File(tmpFile);
      if (requireStrictSha && downloadedSha != normalizedExpected) {
        await tmpFile.delete();
        throw AssetChecksumMismatchException(
          exerciseCode: exerciseCode,
          expectedSha256: normalizedExpected,
          actualSha256: downloadedSha,
        );
      }

      if (await targetFile.exists()) {
        await targetFile.delete();
      }
      await tmpFile.rename(targetFile.path);

      final fileSize = await targetFile.length();
      index[fileName] = _CacheEntry(
        fileName: fileName,
        sha256: downloadedSha,
        sizeBytes: fileSize,
        lastAccessedMs: _nowProvider().millisecondsSinceEpoch,
      );

      // 4. Don dep theo LRU neu tong dung luong vuot qua maxBytes (250 MB)
      await _evictLruIfNeeded(dir, index, protectedFileName: fileName);
      await _writeIndex(dir, index);

      return targetFile.uri.toString();
    } catch (_) {
      if (await tmpFile.exists()) {
        await tmpFile.delete();
      }
      rethrow;
    }
  }

  Future<void> _evictLruIfNeeded(
    Directory dir,
    Map<String, _CacheEntry> index, {
    required String protectedFileName,
  }) async {
    // Sync index with actual disk files
    var totalBytes = 0;
    for (final key in index.keys.toList()) {
      final f = File(p.join(dir.path, key));
      if (!await f.exists()) {
        index.remove(key);
      } else {
        totalBytes += index[key]!.sizeBytes;
      }
    }

    if (totalBytes <= maxBytes) return;

    final evictable = index.values
        .where((e) => e.fileName != protectedFileName)
        .toList()
      ..sort((a, b) => a.lastAccessedMs.compareTo(b.lastAccessedMs));

    for (final entry in evictable) {
      if (totalBytes <= maxBytes) break;
      final f = File(p.join(dir.path, entry.fileName));
      if (await f.exists()) {
        await f.delete();
      }
      totalBytes -= entry.sizeBytes;
      index.remove(entry.fileName);
    }
  }

  Future<int> getCacheSizeBytes() async {
    final dir = await _assetsDir();
    var total = 0;
    await for (final entity in dir.list(followLinks: false)) {
      if (entity is File && p.extension(entity.path) == '.glb') {
        total += await entity.length();
      }
    }
    return total;
  }

  /// Goi boi M1 khi nguoi dung Xoa tai khoan & toan bo du lieu (F26).
  Future<void> clearAllCachedAssets() async {
    final base = await _cacheBaseDirResolver();
    final dir = Directory(p.join(base.path, '3d_assets'));
    if (await dir.exists()) {
      await dir.delete(recursive: true);
    }
  }
}

final assetCacheManagerProvider = Provider<AssetCacheManager>((ref) {
  final dio = ref.watch(dioProvider);
  return AssetCacheManager(dio: dio);
});
