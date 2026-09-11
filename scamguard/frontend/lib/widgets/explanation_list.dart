import 'package:flutter/material.dart';

import '../core/branding.dart';
import '../models/analysis.dart';

const _codeLabels = <String, String>{
  'ML': 'Modele d apprentissage',
  'COMMU': 'Signalements de la communaute',
  'REPUT': 'Base de reputation',
  'DEGRADE': 'Verification partielle',
  'OK': 'Aucun signal',
};

IconData _iconFor(String code) {
  if (code.startsWith('R')) return Icons.rule;
  if (code == 'ML') return Icons.psychology;
  if (code == 'COMMU') return Icons.groups;
  if (code == 'REPUT') return Icons.travel_explore;
  if (code == 'DEGRADE') return Icons.cloud_off;
  return Icons.check_circle_outline;
}

class ExplanationList extends StatelessWidget {
  final List<Explanation> explanations;

  const ExplanationList({super.key, required this.explanations});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          Textes.pourquoiCeResultat,
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 10),
        ...explanations.map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(_iconFor(item.code), size: 19, color: Colors.black54),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item.message, style: const TextStyle(fontSize: 14.5)),
                      if (_codeLabels.containsKey(item.code))
                        Text(
                          _codeLabels[item.code]!,
                          style: const TextStyle(fontSize: 11.5, color: Colors.black45),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
