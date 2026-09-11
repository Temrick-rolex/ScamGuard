import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/branding.dart';
import '../../services/sentinelle_service.dart';
import '../../state/providers.dart';

class QuarantaineScreen extends ConsumerWidget {
  const QuarantaineScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final service = ref.watch(sentinelleServiceProvider);
    final quarantaine = ref.watch(quarantaineProvider);
    final surveillance = ref.watch(surveillanceProvider);

    if (!service.disponible) {
      return const Scaffold(
        body: Center(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text(
              'La quarantaine regroupe les SMS bloques sur votre telephone Android. '
              'Elle n existe pas sur la version web.',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Quarantaine'),
        actions: [
          IconButton(
            tooltip: 'Tout vider',
            icon: const Icon(Icons.delete_sweep_outlined),
            onPressed: () async {
              final confirme = await _confirmer(context, 'Vider toute la quarantaine ?');
              if (confirme) {
                await service.vider();
                ref.invalidate(quarantaineProvider);
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          surveillance.when(
            data: (active) => SwitchListTile(
              value: active,
              title: const Text('Surveillance des SMS'),
              subtitle: Text(
                active
                    ? 'Chaque SMS recu est analyse sur votre telephone'
                    : 'Aucun SMS n est analyse pour le moment',
              ),
              onChanged: (valeur) async {
                await service.definirSurveillance(valeur);
                ref.invalidate(surveillanceProvider);
              },
            ),
            loading: () => const LinearProgressIndicator(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const Divider(height: 1),
          Expanded(
            child: quarantaine.when(
              data: (elements) => elements.isEmpty
                  ? const _Vide()
                  : RefreshIndicator(
                      onRefresh: () async => ref.invalidate(quarantaineProvider),
                      child: ListView.separated(
                        padding: const EdgeInsets.all(Branding.espacement),
                        itemCount: elements.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (contexte, index) => _Carte(
                          element: elements[index],
                          onSupprimer: () async {
                            await service.supprimer(elements[index].id);
                            ref.invalidate(quarantaineProvider);
                          },
                          onAutoriser: () async {
                            await service.autoriser(elements[index].expediteur);
                            await service.supprimer(elements[index].id);
                            ref.invalidate(quarantaineProvider);
                          },
                        ),
                      ),
                    ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (erreur, __) => Center(child: Text('Erreur : $erreur')),
            ),
          ),
        ],
      ),
    );
  }

  Future<bool> _confirmer(BuildContext context, String question) async {
    final reponse = await showDialog<bool>(
      context: context,
      builder: (contexte) => AlertDialog(
        content: Text(question),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(contexte, false),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(contexte, true),
            child: const Text('Confirmer'),
          ),
        ],
      ),
    );
    return reponse ?? false;
  }
}

class _Vide extends StatelessWidget {
  const _Vide();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.verified_user_outlined, size: 64, color: Color(Branding.risqueFaible)),
            SizedBox(height: 16),
            Text(
              'Aucun message en quarantaine',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 8),
            Text(
              'Sentinel surveille vos SMS. Les messages dangereux apparaitront ici.',
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _Carte extends StatelessWidget {
  final ElementQuarantaine element;
  final VoidCallback onSupprimer;
  final VoidCallback onAutoriser;

  const _Carte({
    required this.element,
    required this.onSupprimer,
    required this.onAutoriser,
  });

  @override
  Widget build(BuildContext context) {
    final dangereux = element.niveau == 'DANGEREUX';
    final couleur = dangereux
        ? const Color(Branding.risqueDangereux)
        : const Color(Branding.risqueSuspect);

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(Branding.rayonCoins),
        border: Border.all(color: couleur.withOpacity(0.5)),
        color: couleur.withOpacity(0.05),
      ),
      padding: const EdgeInsets.all(Branding.espacement),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: couleur,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${element.niveau} ${element.score}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                DateFormat('dd/MM HH:mm').format(element.recu),
                style: const TextStyle(fontSize: 12, color: Colors.black54),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            element.expediteur,
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
          ),
          const SizedBox(height: 6),
          Text(element.texte, style: const TextStyle(fontSize: 14, height: 1.35)),
          const SizedBox(height: 10),
          ...element.motifs.take(3).map(
                (motif) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• '),
                      Expanded(
                        child: Text(motif, style: const TextStyle(fontSize: 13)),
                      ),
                    ],
                  ),
                ),
              ),
          const SizedBox(height: 8),
          Row(
            children: [
              TextButton.icon(
                onPressed: onAutoriser,
                icon: const Icon(Icons.shield_outlined, size: 18),
                label: const Text('Expediteur de confiance'),
              ),
              const Spacer(),
              IconButton(
                tooltip: 'Retirer',
                onPressed: onSupprimer,
                icon: const Icon(Icons.close),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
