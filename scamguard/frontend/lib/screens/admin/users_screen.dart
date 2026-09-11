import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../models/user.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../core/branding.dart';

class UsersScreen extends ConsumerWidget {
  const UsersScreen({super.key});

  Future<void> _toggle(BuildContext context, WidgetRef ref, AppUser user) async {
    final service = ref.read(adminServiceProvider);
    try {
      if (user.isActive) {
        await service.suspend(user.id);
      } else {
        await service.reactivate(user.id);
      }
      ref.invalidate(adminUsersProvider);
      if (context.mounted) {
        showMessage(context, user.isActive ? 'Compte suspendu' : 'Compte reactive');
      }
    } catch (error) {
      if (context.mounted) showMessage(context, '$error', danger: true);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final users = ref.watch(adminUsersProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Utilisateurs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(adminUsersProvider),
          ),
        ],
      ),
      body: users.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => ErrorBanner('$error'),
        data: (items) => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: items.length,
          itemBuilder: (context, index) {
            final user = items[index];
            return Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 780),
                child: SectionCard(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor:
                          user.isActive ? Branding.couleurPrincipale : Colors.black26,
                      child: Text(
                        user.fullName.isEmpty
                            ? '?'
                            : user.fullName.substring(0, 1).toUpperCase(),
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    title: Text(user.fullName),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(user.email, style: const TextStyle(fontSize: 12.5)),
                        const SizedBox(height: 4),
                        Wrap(
                          spacing: 6,
                          children: [
                            _tag(user.role, Branding.couleurPrincipale),
                            _tag(
                              user.isActive ? 'Actif' : 'Suspendu',
                              user.isActive ? Branding.couleurRisqueFaible : Branding.couleurRisqueDangereux,
                            ),
                            if (user.isPremium) _tag('Premium', Branding.couleurRisqueSuspect),
                          ],
                        ),
                      ],
                    ),
                    trailing: user.isAdmin
                        ? null
                        : IconButton(
                            tooltip: user.isActive ? 'Suspendre' : 'Reactiver',
                            icon: Icon(
                              user.isActive ? Icons.block : Icons.check_circle_outline,
                              color: user.isActive
                                  ? Branding.couleurRisqueDangereux
                                  : Branding.couleurRisqueFaible,
                            ),
                            onPressed: () => _toggle(context, ref, user),
                          ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _tag(String label, Color color) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600),
        ),
      );
}
