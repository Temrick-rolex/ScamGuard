import '../models/report.dart';
import 'api_client.dart';

class ReportService {
  final ApiClient api;

  ReportService(this.api);

  Future<ReportReceipt> submit({
    required String content,
    required String reason,
    String comment = '',
    String? suspectPhone,
  }) async {
    final body = await api.post('/reports', body: {
      'content': content,
      'reason': reason,
      'comment': comment,
      'evidence_kind': 'TEXTE',
      'suspect_phone': (suspectPhone == null || suspectPhone.isEmpty) ? null : suspectPhone,
    });
    return ReportReceipt.fromJson(body as Map<String, dynamic>);
  }

  Future<List<FeedItem>> publishedHistory({
    String? reason,
    int limit = 20,
    int offset = 0,
  }) async {
    final body = await api.get('/reports/history', query: {
      'limit': limit,
      'offset': offset,
      if (reason != null) 'reason': reason,
    });
    return (body as List)
        .map((item) => FeedItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<MyReport>> mine({int limit = 20, int offset = 0}) async {
    final body = await api.get('/reports/mine', query: {'limit': limit, 'offset': offset});
    return (body as List)
        .map((item) => MyReport.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<PublicStats> stats() async {
    final body = await api.get('/reports/stats');
    return PublicStats.fromJson(body as Map<String, dynamic>);
  }
}
