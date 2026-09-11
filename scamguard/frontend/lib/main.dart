import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/config.dart';
import 'core/theme.dart';
import 'screens/admin/admin_shell.dart';
import 'screens/auth/login_screen.dart';
import 'screens/client/client_shell.dart';
import 'state/providers.dart';
import 'core/branding.dart';

void main() {
  runApp(const ProviderScope(child: ScamGuardApp()));
}

class ScamGuardApp extends StatelessWidget {
  const ScamGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConfig.isAdminBuild ? Branding.nomApplicationAdmin : Branding.nomApplication,
      debugShowCheckedModeBanner: false,
      theme: buildTheme(),
      home: const RootPage(),
    );
  }
}

class RootPage extends ConsumerStatefulWidget {
  const RootPage({super.key});

  @override
  ConsumerState<RootPage> createState() => _RootPageState();
}

class _RootPageState extends ConsumerState<RootPage> {
  bool _restored = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await ref.read(sessionProvider.notifier).restore();
      if (mounted) setState(() => _restored = true);
    });
  }

  @override
  Widget build(BuildContext context) {
    final session = ref.watch(sessionProvider);

    if (!_restored || session.loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (!session.isLoggedIn) return const LoginScreen();

    final user = session.user!;

    if (AppConfig.isAdminBuild) {
      return user.isAdmin ? const AdminShell() : const _AccessDenied();
    }

    return user.isAdmin ? const AdminShell() : const ClientShell();
  }
}

class _AccessDenied extends ConsumerWidget {
  const _AccessDenied();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.lock_outline, size: 60, color: Branding.couleurRisqueDangereux),
            const SizedBox(height: 14),
            const Text(
              'Acces reserve aux administrateurs',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            TextButton(
              onPressed: () => ref.read(sessionProvider.notifier).logout(),
              child: const Text('Se deconnecter'),
            ),
          ],
        ),
      ),
    );
  }
}
