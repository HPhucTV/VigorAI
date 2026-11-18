// [OWNER: M1] Cau hinh Android Gradle chuan CH Play (Android 15 Target SDK 35, 16KB Page Size)
plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.vigorai.app"
    compileSdk = 35
    // NDK r27+ bat buoc de ho tro 16 KB page size alignment tren Android 15+
    ndkVersion = "27.0.12077973"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        applicationId = "com.vigorai.app"
        // Android 8.0 (API 26) la muc toi thieu bat buoc cua Android Health Connect
        minSdk = 26
        // Android 15 (API 35) bat buoc voi ung dung moi nop Google Play Console
        targetSdk = 35
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

    buildTypes {
        release {
            // Toi uu R8 & thu gon tai nguyen giu dung luong .aab < 40 MB
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

flutter {
    source = "../.."
}
