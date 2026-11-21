// [OWNER: M1] BroadcastReceiver xu ly nut "Da uong" ngay tren Android Notification (F06)
package com.vigorai.app

import android.app.NotificationManager
import android.content.BroadcastReceiver
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.database.sqlite.SQLiteDatabase
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

class SupplementTakenReceiver : BroadcastReceiver() {
    companion object {
        const val ACTION_MARK_TAKEN = "com.vigorai.app.ACTION_MARK_SUPPLEMENT_TAKEN"
        const val EXTRA_SUPPLEMENT_ID = "supplement_id"
        const val EXTRA_DATE_ISO = "date_iso"
        const val EXTRA_NOTIFICATION_ID = "notification_id"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != ACTION_MARK_TAKEN) return
        val supplementId = intent.getStringExtra(EXTRA_SUPPLEMENT_ID) ?: return
        val dateIso = intent.getStringExtra(EXTRA_DATE_ISO) ?: todayLocalIso()
        val notificationId = intent.getIntExtra(EXTRA_NOTIFICATION_ID, 2001)

        val flutterDir = context.getDir("flutter", Context.MODE_PRIVATE)
        markTakenInJsonLog(flutterDir, dateIso, supplementId)
        touchSqliteSupplementRow(flutterDir, supplementId)

        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
        nm?.cancel(notificationId)
    }

    private fun todayLocalIso(): String {
        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.US)
        return sdf.format(Date())
    }

    private fun markTakenInJsonLog(flutterDir: File, dateIso: String, supplementId: String) {
        try {
            if (!flutterDir.exists()) flutterDir.mkdirs()
            val logFile = File(flutterDir, "supplement_intake_log.json")
            val root = if (logFile.exists() && logFile.readText().isNotBlank()) {
                JSONObject(logFile.readText())
            } else {
                JSONObject()
            }
            val arr = root.optJSONArray(dateIso) ?: JSONArray()
            var exists = false
            for (i in 0 until arr.length()) {
                if (arr.optString(i) == supplementId) {
                    exists = true
                    break
                }
            }
            if (!exists) {
                arr.put(supplementId)
            }
            root.put(dateIso, arr)
            logFile.writeText(root.toString())
        } catch (_: Exception) {
        }
    }

    private fun touchSqliteSupplementRow(flutterDir: File, supplementId: String) {
        val dbFile = File(flutterDir, "vigorai.sqlite")
        if (!dbFile.exists()) return
        var db: SQLiteDatabase? = null
        try {
            db = SQLiteDatabase.openDatabase(dbFile.absolutePath, null, SQLiteDatabase.OPEN_READWRITE)
            val values = ContentValues().apply {
                put("updated_at", System.currentTimeMillis() / 1000L)
                put("sync_status", "PENDING_UPDATE")
            }
            db.update(
                "supplement_schedules_table",
                values,
                "id = ?",
                arrayOf(supplementId)
            )
        } catch (_: Exception) {
        } finally {
            try {
                db?.close()
            } catch (_: Exception) {
            }
        }
    }
}
