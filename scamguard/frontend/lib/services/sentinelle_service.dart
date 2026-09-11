import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class ElementQuarantaine {
  final int id;
  final String expediteur;
  final String texte;
  final int score;
  final String niveau;
  final List<String> motifs;
  final DateTime recu;
  final bool lu;

  const ElementQuarantaine({
    required this.id,
    required this.expediteur,
    required this.texte,
    required this.score,
    required this.niveau,
    required this.motifs,
    required this.recu,
    required this.lu,
  });

  factory ElementQuarantaine.depuisMap(Map<dynamic, dynamic> donnees) {
    return ElementQuarantaine(
      id: (donnees['id'] as num).toInt(),
      expediteur: donnees['expediteur'] as String? ?? 'inconnu',
      texte: donnees['texte'] as String? ?? '',
      score: (donnees['score'] as num?)?.toInt() ?? 0,
      niveau: donnees['niveau'] as String? ?? 'FAIBLE',
      motifs: (donnees['motifs'] as List<dynamic>? ?? []).map((e) => e.toString()).toList(),
      recu: DateTime.fromMillisecondsSinceEpoch((donnees['recu'] as num?)?.toInt() ?? 0),
      lu: donnees['lu'] as bool? ?? false,
    );
  }
}

class SentinelleService {
  static const MethodChannel _canal = MethodChannel('cm.scamguard/sentinelle');

  bool get disponible => !kIsWeb && defaultTargetPlatform == TargetPlatform.android;

  Future<T?> _appeler<T>(String methode, [Map<String, dynamic>? arguments]) async {
    if (!disponible) return null;
    try {
      return await _canal.invokeMethod<T>(methode, arguments);
    } on PlatformException {
      return null;
    } on MissingPluginException {
      return null;
    }
  }

  Future<List<ElementQuarantaine>> lireQuarantaine() async {
    final brut = await _appeler<List<dynamic>>('lireQuarantaine');
    if (brut == null) return const [];
    return brut
        .whereType<Map<dynamic, dynamic>>()
        .map(ElementQuarantaine.depuisMap)
        .toList();
  }

  Future<void> supprimer(int id) => _appeler('supprimerElement', {'id': id});

  Future<void> marquerLu(int id) => _appeler('marquerLu', {'id': id});

  Future<void> vider() => _appeler('viderQuarantaine');

  Future<bool> surveillanceActive() async =>
      await _appeler<bool>('surveillanceActive') ?? false;

  Future<void> definirSurveillance(bool active) =>
      _appeler('definirSurveillance', {'active': active});

  Future<bool> surveillanceAppels() async =>
      await _appeler<bool>('surveillanceAppels') ?? false;

  Future<void> definirSurveillanceAppels(bool active) =>
      _appeler('definirSurveillanceAppels', {'active': active});

  Future<void> autoriser(String expediteur) =>
      _appeler('autoriserExpediteur', {'expediteur': expediteur});

  Future<void> retirerAutorisation(String expediteur) =>
      _appeler('retirerAutorisation', {'expediteur': expediteur});

  Future<List<String>> expediteursAutorises() async {
    final brut = await _appeler<List<dynamic>>('expediteursAutorises');
    return brut?.map((e) => e.toString()).toList() ?? const [];
  }

  Future<int> nombreAnalyses() async => await _appeler<int>('nombreAnalyses') ?? 0;

  Future<bool> modeleCharge() async => await _appeler<bool>('modeleCharge') ?? false;

  Future<String> versionModele() async =>
      await _appeler<String>('versionModele') ?? 'absent';

  Future<int> analyserLocalement(String texte) async =>
      await _appeler<int>('analyserLocalement', {'texte': texte}) ?? -1;

  Future<void> enregistrerSession(String baseUrl, String jeton) =>
      _appeler('enregistrerSession', {'baseUrl': baseUrl, 'jeton': jeton});

  Future<void> effacerSession() => _appeler('effacerSession');
}
