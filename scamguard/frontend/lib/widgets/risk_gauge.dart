import 'package:flutter/material.dart';

import '../core/theme.dart';

class RiskGauge extends StatelessWidget {
  final int score;
  final String level;

  const RiskGauge({super.key, required this.score, required this.level});

  @override
  Widget build(BuildContext context) {
    final color = levelColor(level);

    return Column(
      children: [
        SizedBox(
          height: 150,
          width: 150,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                height: 150,
                width: 150,
                child: CircularProgressIndicator(
                  value: score / 100,
                  strokeWidth: 12,
                  backgroundColor: color.withOpacity(0.15),
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(levelIcon(level), color: color, size: 30),
                  Text(
                    '$score',
                    style: TextStyle(
                      fontSize: 34,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  const Text('sur 100', style: TextStyle(fontSize: 12, color: Colors.black54)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            levelLabel(level).toUpperCase(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.6,
            ),
          ),
        ),
      ],
    );
  }
}
