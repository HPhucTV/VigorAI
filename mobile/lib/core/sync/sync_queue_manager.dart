// [OWNER: M1] Co che dong bo Offline-First (LWW theo UTC updated_at)
enum SyncStatus {
  synced,
  pendingCreate,
  pendingUpdate,
  pendingDelete,
}

class SyncQueueManager {
  Future<void> pushPendingChanges() async {
    // Hoan thien batch push toi POST /api/v1/sync/push trong Task T-M1-11
  }

  Future<void> pullServerUpdates(DateTime sinceUtc) async {
    // Hoan thien pull tu GET /api/v1/sync/pull trong Task T-M1-11
  }
}
