// [OWNER: M1] Riverpod StateNotifier quan ly trang thai Onboarding Disclaimer & Auth (T-M1-04)
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/auth_repository.dart';

class AuthState {
  final bool isInitialized;
  final bool isLoading;
  final bool disclaimerAccepted;
  final String? disclaimerAcceptedAt;
  final bool isAuthenticated;
  final AuthUserProfile? user;
  final String? errorMessage;

  const AuthState({
    this.isInitialized = false,
    this.isLoading = false,
    this.disclaimerAccepted = false,
    this.disclaimerAcceptedAt,
    this.isAuthenticated = false,
    this.user,
    this.errorMessage,
  });

  AuthState copyWith({
    bool? isInitialized,
    bool? isLoading,
    bool? disclaimerAccepted,
    String? disclaimerAcceptedAt,
    bool? isAuthenticated,
    AuthUserProfile? user,
    String? errorMessage,
    bool clearUser = false,
    bool clearError = false,
  }) {
    return AuthState(
      isInitialized: isInitialized ?? this.isInitialized,
      isLoading: isLoading ?? this.isLoading,
      disclaimerAccepted: disclaimerAccepted ?? this.disclaimerAccepted,
      disclaimerAcceptedAt: disclaimerAcceptedAt ?? this.disclaimerAcceptedAt,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      user: clearUser ? null : (user ?? this.user),
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class AuthController extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthController(this._repository) : super(const AuthState()) {
    restoreSession();
  }

  static String mapAuthErrorMessage(
    Object error, {
    required bool isLogin,
    required String fallback,
  }) {
    if (error is DioException) {
      final code = error.response?.statusCode;
      if (isLogin && (code == 400 || code == 401 || code == 404)) {
        return 'Tài khoản hoặc mật khẩu không chính xác.';
      }
      if (code == 401) {
        return 'Tài khoản hoặc mật khẩu không chính xác.';
      }
      if (code == 409) {
        return 'Email này đã được đăng ký. Vui lòng đăng nhập hoặc dùng email khác.';
      }
      if (code == 422) {
        return 'Thông tin nhập chưa hợp lệ. Vui lòng kiểm tra lại email và mật khẩu.';
      }
      if (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.sendTimeout ||
          error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.connectionError) {
        return 'Không thể kết nối tới máy chủ. Vui lòng kiểm tra kết nối mạng.';
      }
      final data = error.response?.data;
      if (data is Map && data['detail'] is String) {
        final detail = (data['detail'] as String).trim();
        if (detail.isNotEmpty) return detail;
      }
      return fallback;
    }
    if (error is StateError) {
      return error.message;
    }
    return fallback;
  }

  Future<void> restoreSession() async {
    final disclaimer = await _repository.hasAcceptedDisclaimer();
    final hasToken = await _repository.hasValidToken();
    final cachedUser = await _repository.getCachedUserProfile();
    state = state.copyWith(
      isInitialized: true,
      disclaimerAccepted: disclaimer,
      isAuthenticated: disclaimer && hasToken,
      user: cachedUser,
      clearError: true,
    );
  }

  Future<void> acceptMedicalDisclaimer() async {
    final acceptedAt = await _repository.acceptMedicalDisclaimer();
    state = state.copyWith(
      disclaimerAccepted: true,
      disclaimerAcceptedAt: acceptedAt,
      clearError: true,
    );
  }

  Future<bool> login({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final profile = await _repository.login(email: email, password: password);
      if (!state.disclaimerAccepted) {
        await _repository.acceptMedicalDisclaimer();
      }
      state = state.copyWith(
        isLoading: false,
        disclaimerAccepted: true,
        isAuthenticated: true,
        user: profile,
        clearError: true,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: mapAuthErrorMessage(
          e,
          isLogin: true,
          fallback: 'Tài khoản hoặc mật khẩu không chính xác.',
        ),
      );
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String fullName,
    required String gender,
    required double heightCm,
    required String fitnessGoal,
  }) async {
    if (!state.disclaimerAccepted) {
      state = state.copyWith(
        errorMessage: 'Bạn cần chấp nhận Miễn trừ Trách nhiệm Y tế trước khi đăng ký.',
      );
      return false;
    }
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final profile = await _repository.register(
        email: email,
        password: password,
        fullName: fullName,
        gender: gender,
        heightCm: heightCm,
        fitnessGoal: fitnessGoal,
        medicalDisclaimerAccepted: state.disclaimerAccepted,
      );
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: true,
        user: profile,
        clearError: true,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: mapAuthErrorMessage(
          e,
          isLogin: false,
          fallback: 'Đăng ký không thành công. Vui lòng kiểm tra lại thông tin.',
        ),
      );
      return false;
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = state.copyWith(
      isAuthenticated: false,
      clearUser: true,
      clearError: true,
    );
  }

  Future<bool> deleteAccount() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _repository.deleteAccountAndLocalData();
      state = const AuthState(
        isInitialized: true,
        isLoading: false,
        disclaimerAccepted: false,
        isAuthenticated: false,
        user: null,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: mapAuthErrorMessage(
          e,
          isLogin: false,
          fallback: 'Không thể xóa tài khoản lúc này. Vui lòng thử lại.',
        ),
      );
      return false;
    }
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  final repo = ref.watch(authRepositoryProvider);
  return AuthController(repo);
});
