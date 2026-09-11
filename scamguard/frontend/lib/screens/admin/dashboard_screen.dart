import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../models/report.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../core/branding.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stats = ref.watch(statsProvider);
    final pending = ref.watch(pendingReportsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tableau de bord'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(statsProvider);
              ref.invalidate(pendingReportsProvider);
            },
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 900),
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              stats.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, _) => ErrorBanner('$error'),
                data: (data) => Wrap(
                  spacing: 14,
                  runSpacing: 14,
                  children: [
                    _MetricCard(
                      value: '${data.received}',
                      label: 'Signalements recus',
                      icon: Icons.flag,
                      color: Branding.couleurPrincipale,
                    ),
                    _MetricCard(
                      value: '${data.published}',
                      label: 'Arnaques publiees',
                      icon: Icons.campaign,
                      color: Branding.couleurRisqueFaible,
                    ),
                    _MetricCard(
                      value: '${data.suspectPhones}',
                      label: 'Numeros suspects',
                      icon: Icons.phone_disabled,
                      color: Branding.couleurRisqueDangereux,
                    ),
                    pending.maybeWhen(
                      data: (items) => _MetricCard(
                        value: '${items.length}',
                        label: 'En attente',
                        icon: Icons.hourglass_top,
                        color: Branding.couleurRisqueSuspect,
                      ),
                      orElse: () => const SizedBox.shrink(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 26),
              const Text(
                'Types de fraude les plus signales',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 12),
              stats.when(
                loading: () => const SizedBox.shrink(),
                error: (_, __) => const SizedBox.shrink(),
                data: (data) {
                  if (data.topReasons.isEmpty) {
                    return const SectionCard(
                      child: Text(
                        'Aucune arnaque publiee pour le moment.',
                        style: TextStyle(color: Colors.black54),
                      ),
                    );
                  }

                  final maximum = data.topReasons
                      .map((row) => row['total'] as int)
                      .reduce((a, b) => a > b ? a : b);

                  return SectionCard(
                    child: Column(
                      children: data.topReasons.map((row) {
                        final total = row['total'] as int;
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 7),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    reasonLabel('${row['motif']}'),
                                    style: const TextStyle(fontSize: 13.5),
                                  ),
                                  Text(
                                    '$total',
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 5),
                              ClipRRect(
                                borderRadius: BorderRadius.circular(4),
                                child: LinearProgressIndicator(
                                  value: total / maximum,
                                  minHeight: 7,
                                  backgroundColor: const Color(0xFFE9EDEF),
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;
  final Color color;

  const _MetricCard({
    required this.value,
    required this.label,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 200,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 12),
              Text(
                value,
                style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              Text(label, style: const TextStyle(fontSize: 12.5, color: Colors.black54)),
            ],
          ),
        ),
      ),
    );
  }
}
