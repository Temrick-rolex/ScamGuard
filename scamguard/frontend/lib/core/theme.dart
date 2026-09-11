import 'package:flutter/material.dart';

import 'branding.dart';

/// Ce fichier ne fait que traduire branding.dart en theme Flutter.
/// Pour changer une couleur, modifiez branding.dart, pas ce fichier.

Color levelColor(String level) {
  switch (level) {
    case 'DANGEREUX':
      return Branding.couleurRisqueDangereux;
    case 'SUSPECT':
      return Branding.couleurRisqueSuspect;
    default:
      return Branding.couleurRisqueFaible;
  }
}

IconData levelIcon(String level) {
  switch (level) {
    case 'DANGEREUX':
      return Icons.dangerous;
    case 'SUSPECT':
      return Icons.warning_amber_rounded;
    default:
      return Icons.verified_user;
  }
}

String levelLabel(String level) {
  switch (level) {
    case 'DANGEREUX':
      return Textes.niveauDangereux;
    case 'SUSPECT':
      return Textes.niveauSuspect;
    default:
      return Textes.niveauFaible;
  }
}

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: Branding.couleurPrincipale,
    primary: Branding.couleurPrincipale,
    secondary: Branding.couleurSecondaire,
  );

  return ThemeData(
    useMaterial3: true,
    fontFamily: Branding.police,
    colorScheme: scheme,
    scaffoldBackgroundColor: Branding.couleurFond,
    appBarTheme: const AppBarTheme(
      backgroundColor: Branding.couleurPrincipale,
      foregroundColor: Colors.white,
      elevation: 0,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(Branding.hauteurBouton),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Branding.rayonBoutons),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size.fromHeight(Branding.hauteurBouton),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Branding.rayonBoutons),
        ),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Branding.couleurCarte,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Branding.rayonBoutons),
      ),
    ),
    cardTheme: CardTheme(
      elevation: 0,
      color: Branding.couleurCarte,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Branding.rayonCoins),
        side: const BorderSide(color: Branding.couleurBordure),
      ),
    ),
  );
}
