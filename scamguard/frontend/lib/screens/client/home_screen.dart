import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../widgets/sentinel.dart';
import 'analyse_screen.dart';
import 'report_screen.dart';
import '../../core/branding.dart';

class HomeScreen extends ConsumerWidget {
  final void Function(int) onNavigate;

  const HomeScreen({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    final stats = ref.watch(statsProvider);
    final firstName = (session.user?.fullName ?? '').split(' ').first;

    return Scaffold(
      appBar: AppBar(title: const Text(Branding.nomApplication)),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(statsProvider),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              'Bonjour $firstName',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Sentinel(humeur: HumeurSentinel.patrouille),
            const SizedBox(height: 8),
            const Text(
              'Verifiez un message avant de cliquer ou de repondre.',
              style: TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 20),
            Card(
              color: Branding.couleurPrincipale,
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const AnalyseScreen()),
                ),
                child: const Padding(
                  padding: EdgeInsets.all(22),
                  child: Row(
                    children: [
                      Icon(Icons.search, color: Colors.white, size: 34),
                      SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Analyser un message',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'SMS, lien, numero ou QR code',
                              style: TextStyle(color: Colors.white70, fontSize: 13),
                            ),
                          ],
                        ),
                      ),
                      Icon(Icons.arrow_forward_ios, color: Colors.white70, size: 17),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 6),
            Row(
              children: [
                Expanded(
                  child: _ActionTile(
                    icon: Icons.flag_outlined,
                    label: 'Signaler',
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const ReportScreen()),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _ActionTile(
                    icon: Icons.history,
                    label: 'Historique',
                    onTap: () => onNavigate(1),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            const Text(
              'La communaute ScamGuard',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 10),
            stats.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, _) => ErrorBanner('$error'),
              data: (data) => Row(
                children: [
                  Expanded(
                    child: _StatTile(
                      value: '${data.received}',
                      label: 'signalements',
                      icon: Icons.flag,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _StatTile(
                      value: '${data.published}',
                      label: 'arnaques publiees',
                      icon: Icons.campaign,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _StatTile(
                      value: '${data.suspectPhones}',
                      label: 'numeros suspects',
                      icon: Icons.phone_disabled,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 22),
            SectionCard(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Icon(Icons.lightbulb_outline, color: Branding.couleurRisqueSuspect),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      Textes.conseilAccueil,
                      style: TextStyle(fontSize: 13.5),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _ActionTile({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20),
          child: Column(
            children: [
              Icon(icon, color: Branding.couleurPrincipale, size: 26),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;

  const _StatTile({required this.value, required this.label, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
        child: Column(
          children: [
            Icon(icon, size: 20, color: Branding.couleurPrincipale),
            const SizedBox(height: 6),
            Text(
              value,
              style: const TextStyle(fontSize: 19, fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 11, color: Colors.black54),
            ),
          ],
        ),
      ),
    );
  }
}
