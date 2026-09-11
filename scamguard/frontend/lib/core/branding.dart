import 'package:flutter/material.dart';

/// FICHIER DE PERSONNALISATION
///
/// Tout ce qui concerne l'apparence et les textes de l'application se change
/// ICI, et nulle part ailleurs. Aucune couleur ni aucun nom n'est ecrit en dur
/// dans les ecrans.
///
/// Pour changer la couleur principale : modifiez Branding.couleurPrincipale.
/// Pour renommer l'application : modifiez Branding.nomApplication.
/// Pour changer un texte affiche : cherchez-le dans la classe Textes ci-dessous.

class Branding {
  Branding._();

  // ---------------------------------------------------------------
  // IDENTITE
  // ---------------------------------------------------------------

  static const nomApplication = 'ScamGuard';
  static const nomApplicationAdmin = 'ScamGuard Admin';
  static const slogan = 'Detectez les arnaques avant de vous faire avoir';
  static const version = '1.0.0';
  static const organisation = 'SHADERL';

  // ---------------------------------------------------------------
  // COULEURS
  // Changez une valeur hexadecimale et toute l'application suit.
  // Format : 0xFF suivi du code couleur a 6 chiffres.
  // ---------------------------------------------------------------

  static const couleurPrincipale = Color(0xFF0B7285);
  static const couleurSecondaire = Color(0xFF1098AD);
  static const couleurFond = Color(0xFFF6F8F9);
  static const couleurCarte = Color(0xFFFFFFFF);
  static const couleurBordure = Color(0xFFE3E8EA);
  static const couleurTexte = Color(0xFF1A1A1A);
  static const couleurTexteSecondaire = Color(0xFF6B7679);

  // Couleurs des trois niveaux de risque.
  static const couleurRisqueFaible = Color(0xFF2F9E44);
  static const couleurRisqueSuspect = Color(0xFFE8A317);
  static const couleurRisqueDangereux = Color(0xFFC92A2A);

  // ---------------------------------------------------------------
  // FORMES ET ESPACEMENTS
  // ---------------------------------------------------------------

  static const rayonCoins = 12.0;
  static const rayonBoutons = 10.0;
  static const hauteurBouton = 50.0;
  static const espacement = 16.0;
  static const largeurMaxContenu = 620.0;
  static const largeurMaxAdmin = 900.0;

  // ---------------------------------------------------------------
  // TYPOGRAPHIE
  // Laissez police a null pour utiliser la police du systeme.
  // ---------------------------------------------------------------

  static const String? police = null;
  static const tailleTitre = 22.0;
  static const tailleSousTitre = 16.0;
  static const tailleTexte = 14.0;
  static const taillePetitTexte = 12.0;

  // ---------------------------------------------------------------
  // REGLES METIER AFFICHEES
  // Ces valeurs doivent rester identiques a celles du backend.
  // Backend : app/services/analyses.py et app/services/reports/rules.py
  // ---------------------------------------------------------------

  static const quotaGratuitParJour = 20;
  static const signalementsAvantPublication = 3;
  static const seuilSuspect = 40;
  static const seuilDangereux = 70;
}

/// Tous les textes affiches a l'utilisateur.
/// Pour traduire ou reformuler l'application, tout se passe ici.
class Textes {
  Textes._();

  // Navigation
  static const accueil = 'Accueil';
  static const historique = 'Historique';
  static const analyser = 'Analyser';
  static const compte = 'Compte';
  static const tableauDeBord = 'Tableau de bord';
  static const moderation = 'Moderation';
  static const utilisateurs = 'Utilisateurs';

  // Connexion
  static const seConnecter = 'Se connecter';
  static const creerCompte = 'Creer un compte';
  static const seDeconnecter = 'Se deconnecter';
  static const email = 'Adresse e-mail';
  static const motDePasse = 'Mot de passe';
  static const nomComplet = 'Nom complet';
  static const telephone = 'Telephone (facultatif)';

  // Analyse
  static const titreAnalyse = 'Analyser';
  static const boutonAnalyser = 'Analyser';
  static const analyseEnCours = 'Analyse en cours';
  static const collerMessage = 'Collez ici le SMS ou le message WhatsApp recu';
  static const collerLien = 'Collez le lien sans l ouvrir';
  static const saisirNumero = '6XX XX XX XX';
  static const pourquoiCeResultat = 'Pourquoi ce resultat';
  static const liensDetectes = 'Liens detectes';
  static const liensJamaisOuverts = 'ScamGuard n ouvre jamais ces liens pour vous.';

  // Niveaux de risque
  static const niveauFaible = 'Rien de suspect';
  static const niveauSuspect = 'Suspect';
  static const niveauDangereux = 'Danger';

  // Signalement
  static const signaler = 'Signaler';
  static const signalerFraude = 'Signaler une fraude';
  static const envoyerSignalement = 'Envoyer le signalement';
  static const messageRecu = 'Le message recu';
  static const typeFraude = 'Type de fraude';

  static const regleSignalement =
      'Un signalement apparait dans l historique public seulement apres '
      'plusieurs signalements du meme contenu et la validation d un '
      'moderateur. Votre identite n est jamais publiee.';

  // Conseil affiche sur l'accueil
  static const conseilAccueil =
      'Aucun operateur ni aucune banque ne vous demandera jamais votre code '
      'secret par SMS. En cas de doute, appelez le service client par le '
      'numero officiel.';

  // Messages d'erreur
  static const serveurInjoignable =
      'Serveur injoignable. Verifiez votre connexion.';
  static const quotaAtteint =
      'Vous avez atteint vos 20 analyses gratuites du jour.';
  static const dejaSignale = 'Vous avez deja signale ce contenu.';
}
