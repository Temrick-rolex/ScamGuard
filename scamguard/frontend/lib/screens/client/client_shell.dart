import 'package:flutter/material.dart';

import 'analyse_screen.dart';
import 'history_screen.dart';
import 'home_screen.dart';
import 'quarantaine_screen.dart';
import 'settings_screen.dart';

class ClientShell extends StatefulWidget {
  const ClientShell({super.key});

  @override
  State<ClientShell> createState() => _ClientShellState();
}

class _ClientShellState extends State<ClientShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(onNavigate: (index) => setState(() => _index = index)),
      const HistoryScreen(),
      const AnalyseScreen(),
      const QuarantaineScreen(),
      const SettingsScreen(),
    ];

    final wide = MediaQuery.of(context).size.width >= 900;

    if (wide) {
      return Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _index,
              onDestinationSelected: (index) => setState(() => _index = index),
              labelType: NavigationRailLabelType.all,
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home),
                  label: Text('Accueil'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.history_outlined),
                  selectedIcon: Icon(Icons.history),
                  label: Text('Historique'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.search),
                  selectedIcon: Icon(Icons.saved_search),
                  label: Text('Analyser'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.shield_outlined),
                  selectedIcon: Icon(Icons.shield),
                  label: Text('Quarantaine'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person),
                  label: Text('Compte'),
                ),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(child: pages[_index]),
          ],
        ),
      );
    }

    return Scaffold(
      body: pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) => setState(() => _index = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.history), label: 'Historique'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Analyser'),
          NavigationDestination(icon: Icon(Icons.shield_outlined), label: 'Quarantaine'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Compte'),
        ],
      ),
    );
  }
}
