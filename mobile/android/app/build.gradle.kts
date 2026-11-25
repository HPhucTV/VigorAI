// [OWNER: M1] Cau hinh Android Gradle chuan CH Play (Android 15 Target SDK 35, 16KB Page Size)
import java.io.FileInputStream
import java.util.Properties

plugins {
    id("com.android.application")
    id("dev.flutter.flutter-gradle-plugin")
}

val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    FileInputStream(keystorePropertiesFile).use { keystoreProperties.load(it) }
}

android {
    namespace = "com.vigorai.app"
    compileSdk = 36
    // NDK r27+ / r28+ ho tro 16 KB page size alignment tren Android 15+
    ndkVersion = "28.2.13676358"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "com.vigorai.app"
        // Android 8.0 (API 26) la muc toi thieu bat buoc cua Android Health Connect
        minSdk = 26
        // Android 16 (API 36) bat buoc voi ung dung moi nop Google Play Console
        targetSdk = 36
        versionCode = flutter.versionCode
        versionName = flutter.versionName

        // Chi dong goi kien truc 64-bit theo quy dinh CH Play
        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64")
        }

        // Flag lien ket ELF 16 KB page size alignment cho thu vien C/C++
        externalNativeBuild {
            cmake {
                arguments += listOf("-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON")
                cFlags += listOf("-Wl,-z,max-page-size=16384")
                cppFlags += listOf("-Wl,-z,max-page-size=16384")
            }
        }
    }

    packaging {
        jniLibs {
            // Khong nen thu vien .so de tuong thich 16 KB page size tren Android 15+
            useLegacyPackaging = false
        }
    }

    signingConfigs {
        if (keystorePropertiesFile.exists()) {
            create("release") {
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
                storeFile = file(keystoreProperties.getProperty("storeFile"))
                storePassword = keystoreProperties.getProperty("storePassword")
            }
        }
    }

    buildTypes {
        release {
            // Toi uu R8 & thu gon tai nguyen giu dung luong .aab < 40 MB
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            // Dung Upload Keystore tu key.properties neu da tao (T-M2-06), nguoc lai fallback debug
            signingConfig = if (keystorePropertiesFile.exists()) {
                signingConfigs.getByName("release")
            } else {
                signingConfigs.getByName("debug")
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
