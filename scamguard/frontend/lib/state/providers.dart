import 'package:flutter_riverpod/flutter_riverpod.dart';

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
    await store.load();

    if (!store.isLoggedIn) {
      state = const SessionState();
      return;
    }

    try {
      final user = await ref.read(authServiceProvider).profile();
      state = SessionState(user: user);
    } catch (_) {
      await store.clear();
      state = const SessionState();
    }
  }

  Future<void> login(String email, String password) async {
    state = const SessionState(loading: true);
    try {
      final user = await ref.read(authServiceProvider).login(email, password);
      state = SessionState(user: user);
    } catch (error) {
      state = const SessionState();
      rethrow;
    }
  }

  Future<void> logout() async {
    await ref.read(authServiceProvider).logout();
    state = const SessionState();
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
