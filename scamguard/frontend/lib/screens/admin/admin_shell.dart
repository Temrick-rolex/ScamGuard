import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../state/providers.dart';
import 'dashboard_screen.dart';
import 'moderation_screen.dart';
import 'users_screen.dart';
import '../../core/branding.dart';

class AdminShell extends ConsumerStatefulWidget {
  const AdminShell({super.key});

  @override
  ConsumerState<AdminShell> createState() => _AdminShellState();
}

class _AdminShellState extends ConsumerState<AdminShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    const pages = [DashboardScreen(), ModerationScreen(), UsersScreen()];
    final user = ref.watch(sessionProvider).user;

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            extended: MediaQuery.of(context).size.width >= 1100,
            selectedIndex: _index,
            onDestinationSelected: (index) => setState(() => _index = index),
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 22),
              child: Column(
                children: [
                  const Icon(Icons.shield, color: Branding.couleurPrincipale, size: 30),
                  const SizedBox(height: 6),
                  if (MediaQuery.of(context).size.width >= 1100)
                    const Text(
                      'Administration',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                ],
              ),
            ),
            trailing: Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 20),
                  child: Column(
                    children: [
                      Text(
                        user?.email ?? '',
                        style: const TextStyle(fontSize: 10.5, color: Colors.black45),
                      ),
                      IconButton(
                        tooltip: 'Se deconnecter',
                        icon: const Icon(Icons.logout, color: Branding.couleurRisqueDangereux),
                        onPressed: () => ref.read(sessionProvider.notifier).logout(),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.dashboard_outlined),
                selectedIcon: Icon(Icons.dashboard),
                label: Text('Tableau de bord'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.gavel_outlined),
                selectedIcon: Icon(Icons.gavel),
                label: Text('Moderation'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.people_outline),
                selectedIcon: Icon(Icons.people),
                label: Text('Utilisateurs'),
              ),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(child: pages[_index]),
        ],
      ),
    );
  }
}
