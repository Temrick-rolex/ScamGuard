import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

enum EtatPermission { accordee, refusee, refuseeDefinitivement, indisponible }

class DemandePermission {
  final String titre;
  final String explication;
  final Permission permission;
  final bool obligatoire;

  const DemandePermission({
    required this.titre,
    required this.explication,
    required this.permission,
    required this.obligatoire,
  });
}

class PermissionsService {
  bool get surAndroid => !kIsWeb && defaultTargetPlatform == TargetPlatform.android;

  static const List<DemandePermission> requises = [
    DemandePermission(
      titre: 'Lire les SMS entrants',
      explication:
          'ScamGuard analyse chaque SMS des sa reception, directement sur votre telephone. '
          'Le contenu de vos messages ne quitte jamais l appareil.',
      permission: Permission.sms,
      obligatoire: true,
    ),
    DemandePermission(
      titre: 'Afficher des alertes',
      explication:
          'Sans cette autorisation, ScamGuard detecte les messages dangereux mais ne peut pas '
          'vous prevenir tant que vous n ouvrez pas l application.',
      permission: Permission.notification,
      obligatoire: true,
    ),
    DemandePermission(
      titre: 'Identifier les appels inconnus',
      explication:
          'Permet de verifier pendant la sonnerie si un numero inconnu a deja ete signale '
          'par la communaute. Vos contacts enregistres ne sont jamais analyses.',
      permission: Permission.phone,
      obligatoire: false,
    ),
    DemandePermission(
      titre: 'Scanner les QR codes',
      explication:
          'La camera sert uniquement a lire le QR code. Aucune photo n est enregistree '
          'ni envoyee.',
      permission: Permission.camera,
      obligatoire: false,
    ),
  ];

  Future<EtatPermission> etat(Permission permission) async {
    if (!surAndroid) return EtatPermission.indisponible;
    final statut = await permission.status;
    return _convertir(statut);
  }

  Future<EtatPermission> demander(Permission permission) async {
    if (!surAndroid) return EtatPermission.indisponible;
    final statut = await permission.request();
    return _convertir(statut);
  }

  Future<Map<Permission, EtatPermission>> etatComplet() async {
    final resultat = <Permission, EtatPermission>{};
    for (final demande in requises) {
      resultat[demande.permission] = await etat(demande.permission);
    }
    return resultat;
  }

  Future<bool> toutesLesObligatoiresAccordees() async {
    for (final demande in requises.where((d) => d.obligatoire)) {
      if (await etat(demande.permission) != EtatPermission.accordee) return false;
    }
    return true;
  }

  Future<void> ouvrirReglages() => openAppSettings();

  EtatPermission _convertir(PermissionStatus statut) {
    if (statut.isGranted || statut.isLimited) return EtatPermission.accordee;
    if (statut.isPermanentlyDenied) return EtatPermission.refuseeDefinitivement;
    return EtatPermission.refusee;
  }
}
