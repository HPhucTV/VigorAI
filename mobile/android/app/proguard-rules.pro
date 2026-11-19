# [OWNER: M1] Luat R8/ProGuard cho VigorAI Release .aab
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Giu lai lop JNI cua SQLite / Drift & Secure Storage
-keep class org.sqlite.** { *; }
-keepclassmembers class * {
    native <methods>;
}
-dontwarn com.google.errorprone.annotations.**
# Flutter embedding optional deferred-components Play Core references
-dontwarn com.google.android.play.core.**
