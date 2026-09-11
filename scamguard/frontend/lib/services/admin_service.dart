import '../models/report.dart';
import '../models/user.dart';
import 'api_client.dart';

class AdminService {
  final ApiClient api;

  AdminService(this.api);

  Future<List<PendingReport>> pendingReports({int limit = 30, int offset = 0}) async {
    final body = await api.get('/admin/reports/pending', query: {
      'limit': limit,
      'offset': offset,
    });
    return (body as List)
        .map((item) => PendingReport.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> approve(int reportId, String note) =>
      api.post('/admin/reports/$reportId/approve', body: {'note': note});

  Future<void> reject(int reportId, String note) =>
      api.post('/admin/reports/$reportId/reject', body: {'note': note});

  Future<List<AppUser>> users({int limit = 50, int offset = 0}) async {
    final body = await api.get('/admin/users', query: {'limit': limit, 'offset': offset});
    return (body as List)
        .map((item) => AppUser.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<AppUser> suspend(int userId) async {
    final body = await api.post('/admin/users/$userId/suspend');
    return AppUser.fromJson(body as Map<String, dynamic>);
  }

  Future<AppUser> reactivate(int userId) async {
    final body = await api.post('/admin/users/$userId/reactivate');
    return AppUser.fromJson(body as Map<String, dynamic>);
  }
}
