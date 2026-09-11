import 'package:flutter_test/flutter_test.dart';
import 'package:scamguard_app/models/analysis.dart';
import 'package:scamguard_app/models/report.dart';

void main() {
  group('AnalysisResult', () {
    test('lit une reponse complete du backend', () {
      final result = AnalysisResult.fromJson({
        'id': 1,
        'score': 86,
        'level': 'DANGEREUX',
        'confidence': 'REDUITE',
        'recommendation': 'N ouvrez aucun lien',
        'explanations': [
          {'code': 'R1', 'message': 'Demande de code'},
          {'code': 'ML', 'message': 'Formulation typique'},
        ],
        'sources': {'regles': 100, 'modele': 71, 'reputation': null},
        'extracted': {
          'liens': ['http://mtn-momo.xyz'],
          'numeros': [],
          'montants': [],
        },
        'model_version': 'v1',
      });

      expect(result.score, 86);
      expect(result.level, 'DANGEREUX');
      expect(result.isReduced, isTrue);
      expect(result.explanations.length, 2);
      expect(result.links.single, 'http://mtn-momo.xyz');
      expect(result.sources['reputation'], isNull);
    });

    test('survit a une reponse partielle', () {
      final result = AnalysisResult.fromJson({'score': 12, 'level': 'FAIBLE'});

      expect(result.score, 12);
      expect(result.explanations, isEmpty);
      expect(result.links, isEmpty);
      expect(result.modelVersion, 'absent');
    });
  });

  group('ReportReceipt', () {
    test('expose ce qui manque pour la publication', () {
      final receipt = ReportReceipt.fromJson({
        'id': 4,
        'status': 'EN_ATTENTE',
        'risk_score': 84,
        'risk_level': 'DANGEREUX',
        'report_count': 1,
        'published': false,
        'missing_for_publication': [
          '2 signalement(s) supplementaire(s) requis',
          'validation d un moderateur requise',
        ],
        'message': 'Signalement enregistre.',
      });

      expect(receipt.published, isFalse);
      expect(receipt.missing.length, 2);
    });
  });

  group('reasonLabel', () {
    test('traduit les motifs connus', () {
      expect(reasonLabel('DEMANDE_CODE'), 'Demande de code ou PIN');
      expect(reasonLabel('FAUX_GAIN'), 'Faux gain, tombola');
    });

    test('retourne le code brut si inconnu', () {
      expect(reasonLabel('INEXISTANT'), 'INEXISTANT');
    });
  });
}
