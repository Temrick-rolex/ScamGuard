import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../core/theme.dart';
import '../core/branding.dart';

String formatDate(DateTime date) =>
    DateFormat('dd/MM/yyyy a HH:mm').format(date.toLocal());

class ErrorBanner extends StatelessWidget {
  final String message;

  const ErrorBanner(this.message, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Branding.couleurRisqueDangereux.withOpacity(0.08),
        border: Border.all(color: Branding.couleurRisqueDangereux.withOpacity(0.4)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Branding.couleurRisqueDangereux, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(message, style: const TextStyle(color: Branding.couleurRisqueDangereux)),
          ),
        ],
      ),
    );
  }
}

class EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const EmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 56, color: Colors.black26),
            const SizedBox(height: 14),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.black54),
            ),
          ],
        ),
      ),
    );
  }
}

class LevelChip extends StatelessWidget {
  final String level;
  final int? score;

  const LevelChip({super.key, required this.level, this.score});

  @override
  Widget build(BuildContext context) {
    final color = levelColor(level);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(
        score == null ? levelLabel(level) : '${levelLabel(level)} $score',
        style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12.5),
      ),
    );
  }
}

class SectionCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;

  const SectionCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      child: Padding(padding: padding, child: child),
    );
  }
}

Future<void> showMessage(BuildContext context, String text, {bool danger = false}) async {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(text),
      backgroundColor: danger ? Branding.couleurRisqueDangereux : Branding.couleurPrincipale,
      behavior: SnackBarBehavior.floating,
    ),
  );
}
