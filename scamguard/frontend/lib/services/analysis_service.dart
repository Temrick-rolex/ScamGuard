import '../models/analysis.dart';
import 'api_client.dart';

class AnalysisService {
  final ApiClient api;

  AnalysisService(this.api);

  Future<AnalysisResult> analyseMessage(String text) async {
    final body = await api.post('/analyses/message', body: {'text': text});
    return AnalysisResult.fromJson(body as Map<String, dynamic>);
  }

  Future<AnalysisResult> analyseUrl(String url) async {
    final body = await api.post('/analyses/url', body: {'url': url});
    return AnalysisResult.fromJson(body as Map<String, dynamic>);
  }

  Future<AnalysisResult> analyseQr(String payload) async {
    final body = await api.post('/analyses/qr', body: {'url': payload});
    return AnalysisResult.fromJson(body as Map<String, dynamic>);
  }

  Future<AnalysisResult> analysePhone(String phone) async {
    final body = await api.post('/analyses/phone', body: {'phone': phone});
    return AnalysisResult.fromJson(body as Map<String, dynamic>);
  }

  Future<List<HistoryEntry>> history({int limit = 20, int offset = 0}) async {
    final body = await api.get('/analyses/history', query: {
      'limit': limit,
      'offset': offset,
    });
    return (body as List)
        .map((item) => HistoryEntry.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
