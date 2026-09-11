class AppUser {
  final int id;
  final String fullName;
  final String email;
  final String? phone;
  final String role;
  final String status;
  final bool isPremium;

  AppUser({
    required this.id,
    required this.fullName,
    required this.email,
    this.phone,
    required this.role,
    required this.status,
    required this.isPremium,
  });

  bool get isAdmin => role == 'ADMIN';
  bool get isActive => status == 'ACTIVE';

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: json['id'] as int,
        fullName: json['full_name'] as String? ?? '',
        email: json['email'] as String? ?? '',
        phone: json['phone'] as String?,
        role: json['role'] as String? ?? 'CLIENT',
        status: json['status'] as String? ?? 'ACTIVE',
        isPremium: json['is_premium'] as bool? ?? false,
      );
}

class TokenPair {
  final String accessToken;
  final String refreshToken;
  final int expiresInMinutes;

  TokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresInMinutes,
  });

  factory TokenPair.fromJson(Map<String, dynamic> json) => TokenPair(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        expiresInMinutes: json['expires_in_minutes'] as int? ?? 15,
      );
}

class DeviceSettings {
  final bool smsProtection;
  final bool callAlert;
  final bool notifications;

  DeviceSettings({
    required this.smsProtection,
    required this.callAlert,
    required this.notifications,
  });

  factory DeviceSettings.fromJson(Map<String, dynamic> json) => DeviceSettings(
        smsProtection: json['sms_protection'] as bool? ?? false,
        callAlert: json['call_alert'] as bool? ?? false,
        notifications: json['notifications'] as bool? ?? true,
      );
}
