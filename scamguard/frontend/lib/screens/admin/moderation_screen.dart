import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/report.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';

class ModerationScreen extends ConsumerWidget {
  const ModerationScreen({super.key});

  Future<String?> _askNote(BuildContext context, String title, bool required) {
    final controller = TextEditingController();

    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          maxLines: 3,
          autofocus: true,
          decoration: InputDecoration(
            hintText: required ? 'Motif obligatoire' : 'Commentaire (facultatif)',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () {
              if (required && controller.text.trim().isEmpty) return;
              Navigator.of(context).pop(controller.text.trim());
            },
            child: const Text('Confirmer'),
          ),
        ],
      ),
    );
  }

  Future<void> _decide(
    BuildContext context,
    WidgetRef ref,
    PendingReport report,
    bool approve,
  ) async {
    final note = await _askNote(
      context,
      approve ? 'Valider le signalement' : 'Rejeter le signalement',
      !approve,
    );
    if (note == null) return;

    final service = ref.read(adminServiceProvider);
    try {
      if (approve) {
        await service.approve(report.id, note);
      } else {
        await service.reject(report.id, note);
      }
      ref.invalidate(pendingReportsProvider);
      ref.invalidate(statsProvider);
      if (context.mounted) {
        showMessage(context, approve ? 'Signalement valide' : 'Signalement rejete');
      }
    } catch (error) {
      if (context.mounted) showMessage(context, '$error', danger: true);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pending = ref.watch(pendingReportsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Moderation'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(pendingReportsProvider),
          ),
        ],
      ),
      body: pending.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => ErrorBanner('$error'),
        data: (items) {
          if (items.isEmpty) {
            return const EmptyState(
              icon: Icons.inbox,
              title: 'File vide',
              subtitle: 'Aucun signalement en attente de verification.',
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 780),
                  child: SectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              '#${item.id}',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(width: 10),
                            LevelChip(level: item.riskLevel, score: item.riskScore),
                            const Spacer(),
                            Text(
                              formatDate(item.createdAt),
                              style: const TextStyle(fontSize: 11.5, color: Colors.black45),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF3F5F6),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: SelectableText(
                            item.contentRedacted,
                            style: const TextStyle(fontSize: 13.5),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 8,
                          runSpacing: 6,
                          children: [
                            Chip(
                              label: Text(reasonLabel(item.reason),
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
                            if (item.suspectUrl != null)
                              Chip(
                                avatar: const Icon(Icons.link, size: 14),
                                label: Text(item.suspectUrl!,
                                    style: const TextStyle(fontSize: 11.5)),
                                visualDensity: VisualDensity.compact,
                              ),
                          ],
                        ),
                        if (item.comment.isNotEmpty) ...[
                          const SizedBox(height: 10),
                          Text(
                            'Commentaire : ${item.comment}',
                            style: const TextStyle(
                              fontSize: 12.5,
                              fontStyle: FontStyle.italic,
                              color: Colors.black54,
                            ),
                          ),
                        ],
                        const SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: () => _decide(context, ref, item, false),
                                icon: const Icon(Icons.close, size: 18),
                                label: const Text('Rejeter'),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: FilledButton.icon(
                                onPressed: () => _decide(context, ref, item, true),
                                icon: const Icon(Icons.check, size: 18),
                                label: const Text('Valider'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
