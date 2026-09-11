import 'branding.dart';

class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  static const isAdminBuild = bool.fromEnvironment('ADMIN_BUILD');

  static const requestTimeout = Duration(seconds: 20);
  static const freeDailyQuota = Branding.quotaGratuitParJour;
}
