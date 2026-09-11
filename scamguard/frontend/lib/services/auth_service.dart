import '../models/user.dart';
import 'api_client.dart';
import 'token_store.dart';

class AuthService {
  final ApiClient api;
  final TokenStore store;

  AuthService(this.api, this.store);

  Future<AppUser> register({
    required String fullName,
    required String email,
    String? phone,
    required String password,
  }) async {
    final body = await api.post('/auth/register', auth: false, body: {
      'full_name': fullName,
      'email': email,
      'phone': (phone == null || phone.isEmpty) ? null : phone,
      'password': password,
    });
    return AppUser.fromJson(body as Map<String, dynamic>);
  }

  Future<AppUser> login(String email, String password) async {
    final body = await api.post('/auth/login', auth: false, body: {
      'email': email,
      'password': password,
    });
    final tokens = TokenPair.fromJson(body as Map<String, dynamic>);
    await store.save(tokens.accessToken, tokens.refreshToken);
    return profile();
  }

  Future<AppUser> profile() async {
    final body = await api.get('/me');
    return AppUser.fromJson(body as Map<String, dynamic>);
  }

  Future<DeviceSettings> settings() async {
    final body = await api.get('/me/device-settings');
    return DeviceSettings.fromJson(body as Map<String, dynamic>);
  }

  Future<DeviceSettings> updateSettings({
    bool? smsProtection,
    bool? callAlert,
    bool? notifications,
  }) async {
    final body = await api.patch('/me/device-settings', body: {
      if (smsProtection != null) 'sms_protection': smsProtection,
      if (callAlert != null) 'call_alert': callAlert,
      if (notifications != null) 'notifications': notifications,
    });
    return DeviceSettings.fromJson(body as Map<String, dynamic>);
  }

  Future<void> logout() async {
    try {
      await api.post('/auth/logout', body: {'refresh_token': store.refreshToken});
    } catch (_) {
      // Le jeton local est efface meme si le serveur ne repond pas.
    }
    await store.clear();
  }
}
