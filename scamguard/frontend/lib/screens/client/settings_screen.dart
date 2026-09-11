import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../models/user.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../core/branding.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  DeviceSettings? _settings;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final settings = await ref.read(authServiceProvider).settings();
      if (mounted) setState(() => _settings = settings);
    } catch (error) {
      if (mounted) setState(() => _error = '$error');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _update({bool? sms, bool? call, bool? notif}) async {
    try {
      final updated = await ref.read(authServiceProvider).updateSettings(
            smsProtection: sms,
            callAlert: call,
            notifications: notif,
          );
      setState(() => _settings = updated);
    } catch (error) {
      if (mounted) showMessage(context, '$error', danger: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(sessionProvider).user;

    return Scaffold(
      appBar: AppBar(title: const Text('Mon compte')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_error != null) ErrorBanner(_error!),
                SectionCard(
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 26,
                        backgroundColor: Branding.couleurPrincipale,
                        child: Text(
                          (user?.fullName ?? '?').substring(0, 1).toUpperCase(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 21,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user?.fullName ?? '',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              user?.email ?? '',
                              style: const TextStyle(fontSize: 13, color: Colors.black54),
                            ),
                            if (user?.phone != null)
                              Text(
                                user!.phone!,
                                style: const TextStyle(fontSize: 13, color: Colors.black54),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                SectionCard(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Column(
                    children: [
                      const Padding(
                        padding: EdgeInsets.fromLTRB(16, 12, 16, 4),
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: Text(
                            'Protection automatique',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                      SwitchListTile(
                        value: _settings?.smsProtection ?? false,
                        onChanged: kIsWeb ? null : (value) => _update(sms: value),
                        title: const Text('Analyse des SMS en arriere-plan'),
                        subtitle: Text(
                          kIsWeb
                              ? 'Disponible uniquement sur l application Android'
                              : 'Analyse les SMS des numeros inconnus des leur reception',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ),
                      SwitchListTile(
                        value: _settings?.callAlert ?? false,
                        onChanged: kIsWeb ? null : (value) => _update(call: value),
                        title: const Text('Alerte sur les appels inconnus'),
                        subtitle: const Text(
                          'Verifie le numero pendant la sonnerie, sans jamais couper l appel',
                          style: TextStyle(fontSize: 12),
                        ),
                      ),
                      SwitchListTile(
                        value: _settings?.notifications ?? true,
                        onChanged: (value) => _update(notif: value),
                        title: const Text('Notifications'),
                      ),
                    ],
                  ),
                ),
                SectionCard(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      ListTile(
                        leading: const Icon(Icons.workspace_premium_outlined),
                        title: const Text('Formule'),
                        subtitle: Text(
                          (user?.isPremium ?? false)
                              ? 'Premium, analyses illimitees'
                              : 'Gratuite, 20 analyses par jour',
                        ),
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.logout, color: Branding.couleurRisqueDangereux),
                        title: const Text(
                          'Se deconnecter',
                          style: TextStyle(color: Branding.couleurRisqueDangereux),
                        ),
                        onTap: () => ref.read(sessionProvider.notifier).logout(),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
                const Center(
                  child: Text(
                    '${Branding.nomApplication} v${Branding.version}',
                    style: TextStyle(fontSize: 12, color: Colors.black38),
                  ),
                ),
              ],
            ),
    );
  }
}
