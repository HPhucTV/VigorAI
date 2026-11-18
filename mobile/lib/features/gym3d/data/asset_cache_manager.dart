// [OWNER: M2] Quan ly Lazy-Loading va LRU Cache toi da 250MB cho file .glb (F07)
class AssetCacheManager {
  static const int maxCacheBytes = 250 * 1024 * 1024; // 250 MB

  Future<String> getOrDownloadGlb({
    required String exerciseCode,
    required String remoteUrl,
    required String expectedSha256,
  }) async {
    // Hoan thien tai file tu CDN + kiem tra SHA-256 + don LRU cache trong Task T-M2-05
    return 'assets/3d_bundled/base_mannequin.glb';
  }

  Future<void> clearAllCachedAssets() async {
    // Goi boi M1 khi nguoi dung Xoa tai khoan (F26)
  }
}
