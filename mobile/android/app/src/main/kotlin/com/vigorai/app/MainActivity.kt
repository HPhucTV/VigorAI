// [OWNER: M1] Android MainActivity + MethodChannel Notification Reminder (F03, F06)
package com.vigorai.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.drawable.Icon
import android.os.Build
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    companion object {
        private const val CHANNEL_NAME = "com.vigorai.app/health_reminders"
        private const val NOTIF_CHANNEL_ID = "vigorai_health_reminders"
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL_NAME)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "showHydrationReminder" -> {
                        val currentMl = call.argument<Int>("current_ml") ?: 0
                        val targetMl = call.argument<Int>("target_ml") ?: 2450
                        val shown = showHydrationNotification(currentMl, targetMl)
                        result.success(shown)
                    }
                    "showSupplementReminder" -> {
                        val supplementId = call.argument<String>("supplement_id") ?: ""
                        val name = call.argument<String>("supplement_name") ?: "Thực phẩm bổ sung"
                        val dosage = call.argument<String>("dosage_label") ?: "1 liều"
                        val dateIso = call.argument<String>("date_iso") ?: ""
                        val shown = showSupplementNotification(supplementId, name, dosage, dateIso)
                        result.success(shown)
                    }
                    else -> result.notImplemented()
                }
            }
    }

    private fun ensureNotificationChannel(): NotificationManager? {
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return null
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                NOTIF_CHANNEL_ID,
                "Nhắc uống nước & Supplement VigorAI",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Thông báo nhắc nhở uống nước thông minh và thực phẩm bổ sung hàng ngày"
            }
            nm.createNotificationChannel(channel)
        }
        return nm
    }

    private fun showHydrationNotification(currentMl: Int, targetMl: Int): Boolean {
        val nm = ensureNotificationChannel() ?: return false
        val remaining = (targetMl - currentMl).coerceAtLeast(0)
        val body = if (remaining > 0) {
            "Bạn đã uống $currentMl / $targetMl ml. Còn thiếu $remaining ml hôm nay!"
        } else {
            "Tuyệt vời! Bạn đã đạt mục tiêu $targetMl ml nước hôm nay."
        }
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, NOTIF_CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        builder.setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("VigorAI · Nhắc uống nước")
            .setContentText(body)
            .setAutoCancel(true)
        nm.notify(1001, builder.build())
        return true
    }

    private fun showSupplementNotification(
        supplementId: String,
        name: String,
        dosage: String,
        dateIso: String
    ): Boolean {
        val nm = ensureNotificationChannel() ?: return false
        val notificationId = 2000 + (supplementId.hashCode() and 0x0FFF)
        val actionIntent = Intent(this, SupplementTakenReceiver::class.java).apply {
            action = SupplementTakenReceiver.ACTION_MARK_TAKEN
            putExtra(SupplementTakenReceiver.EXTRA_SUPPLEMENT_ID, supplementId)
            putExtra(SupplementTakenReceiver.EXTRA_DATE_ISO, dateIso)
            putExtra(SupplementTakenReceiver.EXTRA_NOTIFICATION_ID, notificationId)
        }
        val flags = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        val pendingIntent = PendingIntent.getBroadcast(this, notificationId, actionIntent, flags)

        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, NOTIF_CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        builder.setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("VigorAI · Đến giờ uống $name")
            .setContentText("Liều dùng: $dosage")
            .setAutoCancel(true)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val icon = Icon.createWithResource(this, android.R.drawable.checkbox_on_background)
            val action = Notification.Action.Builder(icon, "Đã uống", pendingIntent).build()
            builder.addAction(action)
        }

        nm.notify(notificationId, builder.build())
        return true
    }
}
