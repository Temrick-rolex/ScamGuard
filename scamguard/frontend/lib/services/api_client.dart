import 'dart:convert';

import 'package:http/http.dart' as http;

import '../core/branding.dart';
import '../core/config.dart';
import 'token_store.dart';
import 'sentinelle_service.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  bool get isQuotaExceeded => statusCode == 429;
  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
  bool get isConflict => statusCode == 409;

  @override
  String toString() => message;
}

class ApiClient {
  final TokenStore store;
  final http.Client _http;

  ApiClient(this.store, {http.Client? client}) : _http = client ?? http.Client();

  Uri _url(String path, [Map<String, dynamic>? query]) {
    final base = Uri.parse('${AppConfig.apiBaseUrl}$path');
    if (query == null) return base;
    return base.replace(
      queryParameters: query.map((key, value) => MapEntry(key, '$value')),
    );
  }

  Map<String, String> _headers(String? token) => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<dynamic> get(String path, {Map<String, dynamic>? query, bool auth = true}) =>
      _send(() async => _http
          .get(_url(path, query), headers: _headers(auth ? store.accessToken : null))
          .timeout(AppConfig.requestTimeout));

  Future<dynamic> post(String path, {Map<String, dynamic>? body, bool auth = true}) =>
      _send(() async => _http
          .post(
            _url(path),
            headers: _headers(auth ? store.accessToken : null),
            body: jsonEncode(body ?? {}),
          )
          .timeout(AppConfig.requestTimeout));

  Future<dynamic> patch(String path, {Map<String, dynamic>? body}) =>
      _send(() async => _http
          .patch(
            _url(path),
            headers: _headers(store.accessToken),
            body: jsonEncode(body ?? {}),
          )
          .timeout(AppConfig.requestTimeout));

  Future<dynamic> delete(String path) => _send(() async =>
      _http.delete(_url(path), headers: _headers(store.accessToken)).timeout(AppConfig.requestTimeout));

  Future<dynamic> _send(Future<http.Response> Function() call) async {
    var response = await _call(call);

    if (response.statusCode == 401 && store.refreshToken != null) {
      final renewed = await _renew();
      if (renewed) response = await _call(call);
    }

    return _decode(response);
  }

  Future<http.Response> _call(Future<http.Response> Function() call) async {
    try {
      return await call();
    } catch (error) {
      throw ApiException(0, Textes.serveurInjoignable);
    }
  }

  Future<bool> _renew() async {
    try {
      final response = await _http
          .post(
            _url('/auth/refresh'),
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({'refresh_token': store.refreshToken}),
          )
          .timeout(AppConfig.requestTimeout);
      if (response.statusCode != 200) {
        await store.clear();
        return false;
      }
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      await store.save(body['access_token'] as String, body['refresh_token'] as String);

      // Le jeton d acces change a chaque renouvellement : on le repousse a
      // la sentinelle Android (filtrage d appels en arriere plan), sinon
      // elle continuerait d utiliser un jeton expire. Sans effet sur web.
      try {
        await SentinelleService().enregistrerSession(
          AppConfig.apiBaseUrl,
          body['access_token'] as String,
        );
      } catch (_) {}
      return true;
    } catch (_) {
      return false;
    }
  }

  dynamic _decode(http.Response response) {
    if (response.statusCode == 204) return null;

    final body = response.body.isEmpty
        ? null
        : jsonDecode(utf8.decode(response.bodyBytes));

    if (response.statusCode >= 400) {
      throw ApiException(response.statusCode, _readDetail(body, response.statusCode));
    }
    return body;
  }

  String _readDetail(dynamic body, int status) {
    if (body is Map && body['detail'] != null) {
      final detail = body['detail'];
      if (detail is String) return detail;
      if (detail is List && detail.isNotEmpty) {
        final first = detail.first;
        if (first is Map && first['msg'] != null) return '${first['msg']}';
      }
    }
    if (status == 429) return 'Quota journalier atteint. Reessayez demain.';
    return 'Une erreur est survenue (code $status)';
  }
}
