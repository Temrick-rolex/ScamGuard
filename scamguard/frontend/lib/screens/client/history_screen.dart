import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/report.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Historique'),
          bottom: const TabBar(
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            indicatorColor: Colors.white,
            tabs: [
              Tab(text: 'Mes analyses'),
              Tab(text: 'Mes signalements'),
              Tab(text: 'Arnaques connues'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [_AnalysesTab(), _MyReportsTab(), _FeedTab()],
        ),
      ),
    );
  }
}

class _AnalysesTab extends ConsumerWidget {
  const _AnalysesTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entries = ref.watch(analysisHistoryProvider);

    return entries.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => ErrorBanner('$error'),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.search_off,
            title: 'Aucune analyse',
            subtitle: 'Analysez un message pour le retrouver ici.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(analysisHistoryProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return SectionCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        LevelChip(level: item.riskLevel, score: item.riskScore),
                        Text(
                          formatDate(item.createdAt),
                          style: const TextStyle(fontSize: 11.5, color: Colors.black45),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      item.inputRedacted,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 13.5),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}

class _MyReportsTab extends ConsumerWidget {
  const _MyReportsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reports = ref.watch(myReportsProvider);

    return reports.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => ErrorBanner('$error'),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.flag_outlined,
            title: 'Aucun signalement',
            subtitle: 'Vos signalements apparaitront ici avec leur statut.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(myReportsProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return SectionCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _StatusBadge(status: item.status),
                        Text(
                          formatDate(item.createdAt),
                          style: const TextStyle(fontSize: 11.5, color: Colors.black45),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      item.contentRedacted,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 13.5),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      reasonLabel(item.reason),
                      style: const TextStyle(fontSize: 12, color: Colors.black54),
                    ),
                    if (item.moderationNote.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Moderateur : ${item.moderationNote}',
                        style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic),
                      ),
                    ],
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}

class _FeedTab extends ConsumerWidget {
  const _FeedTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final feed = ref.watch(feedProvider);

    return feed.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => ErrorBanner('$error'),
      data: (items) {
        if (items.isEmpty) {
          return const EmptyState(
            icon: Icons.public_off,
            title: 'Aucune arnaque publiee',
            subtitle:
                'Un contenu apparait ici apres plusieurs signalements et la validation d un moderateur.',
          );
        }
        return RefreshIndicator(
          onRefresh: () async => ref.invalidate(feedProvider),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return SectionCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.groups, size: 17, color: Colors.black54),
                        const SizedBox(width: 6),
                        Text(
                          '${item.reportCount} signalements',
                          style: const TextStyle(
                            fontSize: 12.5,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          formatDate(item.lastSeenAt),
                          style: const TextStyle(fontSize: 11.5, color: Colors.black45),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(item.contentRedacted, style: const TextStyle(fontSize: 13.5)),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      children: [
                        Chip(
                          label: Text(reasonLabel(item.mainReason),
                              style: const TextStyle(fontSize: 11.5)),
                          visualDensity: VisualDensity.compact,
                        ),
                        if (item.suspectPhone != null)
                          Chip(
                            avatar: const Icon(Icons.phone, size: 14),
                            label: Text(item.suspectPhone!,
                                style: const TextStyle(fontSize: 11.5)),
                            visualDensity: VisualDensity.compact,
                          ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (status) {
      'PUBLIE' => ('Publie', Colors.green),
      'REJETE' => ('Rejete', Colors.red),
      _ => ('En attente', Colors.orange),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600),
      ),
    );
  }
}
