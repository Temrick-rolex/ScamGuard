import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../core/branding.dart';

enum HumeurSentinel { patrouille, analyse, alerte, calme }

class Sentinel extends StatefulWidget {
  final HumeurSentinel humeur;
  final String? message;
  final VoidCallback? onTap;
  final double hauteur;

  const Sentinel({
    super.key,
    this.humeur = HumeurSentinel.patrouille,
    this.message,
    this.onTap,
    this.hauteur = 150,
  });

  @override
  State<Sentinel> createState() => _SentinelState();
}

class _SentinelState extends State<Sentinel> with TickerProviderStateMixin {
  late final AnimationController _deplacement;
  late final AnimationController _flottement;

  @override
  void initState() {
    super.initState();
    _deplacement = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 7),
    )..repeat(reverse: true);
    _flottement = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _deplacement.dispose();
    _flottement.dispose();
    super.dispose();
  }

  Color get _couleur => switch (widget.humeur) {
        HumeurSentinel.alerte => const Color(Branding.risqueDangereux),
        HumeurSentinel.analyse => const Color(Branding.risqueSuspect),
        _ => const Color(Branding.couleurPrincipale),
      };

  String get _phrase {
    if (widget.message != null) return widget.message!;
    return switch (widget.humeur) {
      HumeurSentinel.patrouille => 'Sentinel patrouille, tout est calme',
      HumeurSentinel.analyse => 'Sentinel analyse le contenu...',
      HumeurSentinel.alerte => 'Sentinel a repere un danger',
      HumeurSentinel.calme => 'Sentinel veille sur vos messages',
    };
  }

  @override
  Widget build(BuildContext context) {
    final immobile = widget.humeur != HumeurSentinel.patrouille;

    return GestureDetector(
      onTap: widget.onTap,
      child: SizedBox(
        height: widget.hauteur,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Expanded(
              child: LayoutBuilder(
                builder: (contexte, contraintes) {
                  return AnimatedBuilder(
                    animation: Listenable.merge([_deplacement, _flottement]),
                    builder: (contexte, _) {
                      final course = contraintes.maxWidth - 76;
                      final x = immobile
                          ? course / 2
                          : Curves.easeInOut.transform(_deplacement.value) * course;
                      final y = math.sin(_flottement.value * math.pi) * 6;

                      return Stack(
                        children: [
                          Positioned(
                            left: x.clamp(0.0, math.max(0.0, course)),
                            top: 8 + y,
                            child: _Corps(
                              couleur: _couleur,
                              regardeADroite: _deplacement.value < 0.5,
                              humeur: widget.humeur,
                            ),
                          ),
                        ],
                      );
                    },
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(
                _phrase,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 13,
                  color: _couleur,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Corps extends StatelessWidget {
  final Color couleur;
  final bool regardeADroite;
  final HumeurSentinel humeur;

  const _Corps({
    required this.couleur,
    required this.regardeADroite,
    required this.humeur,
  });

  @override
  Widget build(BuildContext context) {
    return Transform.flip(
      flipX: !regardeADroite,
      child: CustomPaint(
        size: const Size(72, 78),
        painter: _PeintreSentinel(couleur: couleur, humeur: humeur),
      ),
    );
  }
}

class _PeintreSentinel extends CustomPainter {
  final Color couleur;
  final HumeurSentinel humeur;

  _PeintreSentinel({required this.couleur, required this.humeur});

  @override
  void paint(Canvas canvas, Size size) {
    final corps = Paint()..color = couleur;
    final clair = Paint()..color = Colors.white;
    final sombre = Paint()..color = couleur.withOpacity(0.75);

    canvas.drawOval(
      Rect.fromLTWH(10, size.height - 10, size.width - 20, 8),
      Paint()..color = Colors.black.withOpacity(0.10),
    );

    final buste = RRect.fromRectAndRadius(
      Rect.fromLTWH(14, 30, 44, 38),
      const Radius.circular(14),
    );
    canvas.drawRRect(buste, corps);

    final tete = RRect.fromRectAndRadius(
      Rect.fromLTWH(10, 4, 52, 34),
      const Radius.circular(16),
    );
    canvas.drawRRect(tete, corps);

    final visiere = RRect.fromRectAndRadius(
      Rect.fromLTWH(16, 12, 40, 18),
      const Radius.circular(9),
    );
    canvas.drawRRect(visiere, Paint()..color = const Color(0xFF10243A));

    canvas.drawCircle(Offset(28, 21), 4.2, clair);
    canvas.drawCircle(Offset(44, 21), 4.2, clair);

    if (humeur == HumeurSentinel.alerte) {
      canvas.drawCircle(Offset(28, 21), 2.0, Paint()..color = const Color(Branding.risqueDangereux));
      canvas.drawCircle(Offset(44, 21), 2.0, Paint()..color = const Color(Branding.risqueDangereux));
    } else {
      canvas.drawCircle(Offset(29, 22), 1.9, Paint()..color = const Color(0xFF10243A));
      canvas.drawCircle(Offset(45, 22), 1.9, Paint()..color = const Color(0xFF10243A));
    }

    canvas.drawLine(
      const Offset(36, 4),
      const Offset(36, -4),
      Paint()
        ..color = couleur
        ..strokeWidth = 2.4,
    );
    canvas.drawCircle(const Offset(36, -6), 3.4, sombre);

    final bouclier = Path()
      ..moveTo(54, 38)
      ..lineTo(68, 43)
      ..lineTo(68, 54)
      ..quadraticBezierTo(68, 63, 54, 68)
      ..quadraticBezierTo(40, 63, 40, 54)
      ..lineTo(40, 43)
      ..close();
    canvas.drawPath(bouclier, Paint()..color = Colors.white.withOpacity(0.92));
    canvas.drawPath(
      bouclier,
      Paint()
        ..color = couleur
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.2,
    );

    final coche = Path()
      ..moveTo(48, 52)
      ..lineTo(53, 57)
      ..lineTo(61, 47);
    canvas.drawPath(
      coche,
      Paint()
        ..color = couleur
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_PeintreSentinel ancien) =>
      ancien.couleur != couleur || ancien.humeur != humeur;
}
