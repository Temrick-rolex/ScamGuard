import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/config.dart';
import '../models/user.dart';
import '../services/admin_service.dart';
import '../services/analysis_service.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../services/permissions_service.dart';
import '../services/report_service.dart';
import '../services/sentinelle_service.dart';
import '../services/token_store.dart';

final tokenStoreProvider = Provider<TokenStore>((ref) => TokenStore());

final apiClientProvider = Provider<ApiClient>(
  (ref) => ApiClient(ref.watch(tokenStoreProvider)),
);

final authServiceProvider = Provider<AuthService>(
  (ref) => AuthService(ref.watch(apiClientProvider), ref.watch(tokenStoreProvider)),
);

final analysisServiceProvider = Provider<AnalysisService>(
  (ref) => AnalysisService(ref.watch(apiClientProvider)),
);

final reportServiceProvider = Provider<ReportService>(
  (ref) => ReportService(ref.watch(apiClientProvider)),
);

final adminServiceProvider = Provider<AdminService>(
  (ref) => AdminService(ref.watch(apiClientProvider)),
);

final sentinelleServiceProvider = Provider<SentinelleService>((ref) => SentinelleService());

final permissionsServiceProvider = Provider<PermissionsService>((ref) => PermissionsService());

final quarantaineProvider =
    FutureProvider.autoDispose<List<ElementQuarantaine>>((ref) async {
  return ref.watch(sentinelleServiceProvider).lireQuarantaine();
});

final surveillanceProvider = FutureProvider.autoDispose<bool>((ref) async {
  return ref.watch(sentinelleServiceProvider).surveillanceActive();
});

class SessionState {
  final AppUser? user;
  final bool loading;

  const SessionState({this.user, this.loading = false});

  bool get isLoggedIn => user != null;
}

class SessionNotifier extends StateNotifier<SessionState> {
  final Ref ref;

  SessionNotifier(this.ref) : super(const SessionState());

  Future<void> restore() async {
    state = const SessionState(loading: true);
    final store = ref.read(tokenStoreProvider);

    try {
      await store.load();

      if (!store.isLoggedIn) {
        state = const SessionState();
        return;
      }

      final user = await ref.read(authServiceProvider).profile();
      await _synchroniserSentinelle();
      state = SessionState(user: user);
    } catch (_) {
      // Session corrompue ou serveur injoignable : on retombe sur l'ecran
      // de connexion plutot que de rester bloque sur le chargement.
      try {
        await store.clear();
      } catch (_) {}
      await _effacerSentinelle();
      state = const SessionState();
    }
  }

  Future<void> login(String email, String password) async {
    state = const SessionState(loading: true);
    try {
      final user = await ref.read(authServiceProvider).login(email, password);
      await _synchroniserSentinelle();
      state = SessionState(user: user);
    } catch (error) {
      state = const SessionState();
      rethrow;
    }
  }

  Future<void> logout() async {
    await ref.read(authServiceProvider).logout();
    await _effacerSentinelle();
    state = const SessionState();
  }

  /// Pousse la session (URL de l API + jeton d acces) a la sentinelle
  /// Android pour le filtrage d appels en arriere plan. Sans cela, le code
  /// natif n a aucun jeton et degarde silencieusement en « numero inconnu ».
  /// Sans effet sur web et iOS (SentinelleService ignore ces plateformes).
  Future<void> _synchroniserSentinelle() async {
    final jeton = ref.read(tokenStoreProvider).accessToken;
    if (jeton == null) return;
    try {
      await ref
          .read(sentinelleServiceProvider)
          .enregistrerSession(AppConfig.apiBaseUrl, jeton);
    } catch (_) {
      // Non bloquant : la sentinelle retombe sur l analyse locale.
    }
  }

  Future<void> _effacerSentinelle() async {
    try {
      await ref.read(sentinelleServiceProvider).effacerSession();
    } catch (_) {}
  }
}

final sessionProvider = StateNotifierProvider<SessionNotifier, SessionState>(
  (ref) => SessionNotifier(ref),
);

final statsProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(reportServiceProvider).stats(),
);

final feedProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(reportServiceProvider).publishedHistory(),
);

final myReportsProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(reportServiceProvider).mine(),
);

final analysisHistoryProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(analysisServiceProvider).history(),
);

final pendingReportsProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(adminServiceProvider).pendingReports(),
);

final adminUsersProvider = FutureProvider.autoDispose(
  (ref) => ref.watch(adminServiceProvider).users(),
);
