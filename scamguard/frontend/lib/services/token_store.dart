import 'package:shared_preferences/shared_preferences.dart';

class TokenStore {
  static const _accessKey = 'scamguard_access';
  static const _refreshKey = 'scamguard_refresh';

  String? accessToken;
  String? refreshToken;

  bool get isLoggedIn => accessToken != null;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    accessToken = prefs.getString(_accessKey);
    refreshToken = prefs.getString(_refreshKey);
  }

  Future<void> save(String access, String refresh) async {
    accessToken = access;
    refreshToken = refresh;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, access);
    await prefs.setString(_refreshKey, refresh);
  }

  Future<void> clear() async {
    accessToken = null;
    refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessKey);
    await prefs.remove(_refreshKey);
  }
}
