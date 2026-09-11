import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../core/branding.dart';
import '../../services/permissions_service.dart';
import '../../state/providers.dart';

class PermissionsScreen extends ConsumerStatefulWidget {
  final VoidCallback? onTermine;

  const PermissionsScreen({super.key, this.onTermine});

  @override
  ConsumerState<PermissionsScreen> createState() => _PermissionsScreenState();
}

class _PermissionsScreenState extends ConsumerState<PermissionsScreen> {
  Map<Permission, EtatPermission> _etats = {};
  bool _chargement = true;

  @override
  void initState() {
    super.initState();
    _rafraichir();
  }

  Future<void> _rafraichir() async {
    final etats = await ref.read(permissionsServiceProvider).etatComplet();
    if (!mounted) return;
    setState(() {
      _etats = etats;
      _chargement = false;
    });
  }

  Future<void> _demander(DemandePermission demande) async {
    final service = ref.read(permissionsServiceProvider);
    final resultat = await service.demander(demande.permission);

    if (resultat == EtatPermission.refuseeDefinitivement && mounted) {
      final ouvrir = await showDialog<bool>(
        context: context,
        builder: (contexte) => AlertDialog(
          title: const Text('Autorisation bloquee'),
          content: Text(
            'Vous avez refuse definitivement "${demande.titre}". '
            'Il faut l activer depuis les reglages Android pour que ScamGuard fonctionne.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(contexte, false),
              child: const Text('Plus tard'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(contexte, true),
              child: const Text('Ouvrir les reglages'),
            ),
          ],
        ),
      );
      if (ouvrir == true) await service.ouvrirReglages();
    }
    await _rafraichir();
  }

  @override
  Widget build(BuildContext context) {
    final service = ref.read(permissionsServiceProvider);

    if (!service.surAndroid) {
      return const Scaffold(
        body: Center(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text(
              'La surveillance en arriere plan existe uniquement sur Android. '
              'Sur le web, collez vos messages dans l ecran d analyse.',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Autorisations')),
      body: _chargement
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(Branding.espacement),
              children: [
                const Text(
                  'Pour vous proteger sans que vous ayez a ouvrir l application, '
                  'ScamGuard a besoin des acces suivants.',
                  style: TextStyle(fontSize: 15),
                ),
                const SizedBox(height: Branding.espacement),
                ...PermissionsService.requises.map(_carte),
                const SizedBox(height: Branding.espacement),
                FilledButton(
                  onPressed: widget.onTermine ?? () => Navigator.of(context).maybePop(),
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(Branding.hauteurBouton),
                  ),
                  child: const Text('Continuer'),
                ),
              ],
            ),
    );
  }

  Widget _carte(DemandePermission demande) {
    final etat = _etats[demande.permission] ?? EtatPermission.refusee;
    final accordee = etat == EtatPermission.accordee;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Branding.rayonCoins),
      ),
      child: Padding(
        padding: const EdgeInsets.all(Branding.espacement),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  accordee ? Icons.check_circle : Icons.radio_button_unchecked,
                  color: accordee
                      ? const Color(Branding.risqueFaible)
                      : const Color(Branding.risqueSuspect),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    demande.titre,
                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
                  ),
                ),
                if (demande.obligatoire)
                  const Chip(
                    label: Text('Requis', style: TextStyle(fontSize: 11)),
                    visualDensity: VisualDensity.compact,
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(demande.explication, style: const TextStyle(fontSize: 13.5, height: 1.4)),
            const SizedBox(height: 12),
            if (!accordee)
              OutlinedButton(
                onPressed: () => _demander(demande),
                child: Text(
                  etat == EtatPermission.refuseeDefinitivement
                      ? 'Ouvrir les reglages'
                      : 'Autoriser',
                ),
              )
            else
              const Text(
                'Autorisation accordee',
                style: TextStyle(color: Color(Branding.risqueFaible), fontSize: 13),
              ),
          ],
        ),
      ),
    );
  }
}
