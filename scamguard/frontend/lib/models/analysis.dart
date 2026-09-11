class Explanation {
  final String code;
  final String message;

  Explanation({required this.code, required this.message});

  factory Explanation.fromJson(Map<String, dynamic> json) => Explanation(
        code: json['code'] as String? ?? '',
        message: json['message'] as String? ?? '',
      );
}

class AnalysisResult {
  final int? id;
  final int score;
  final String level;
  final String confidence;
  final String recommendation;
  final List<Explanation> explanations;
  final Map<String, int?> sources;
  final Map<String, List<String>> extracted;
  final String modelVersion;

  AnalysisResult({
    this.id,
    required this.score,
    required this.level,
    required this.confidence,
    required this.recommendation,
    required this.explanations,
    required this.sources,
    required this.extracted,
    required this.modelVersion,
  });

  bool get isReduced => confidence == 'REDUITE';
  List<String> get links => extracted['liens'] ?? const [];
  List<String> get phones => extracted['numeros'] ?? const [];

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final rawExtracted = json['extracted'] as Map<String, dynamic>? ?? {};

    return AnalysisResult(
      id: json['id'] as int?,
      score: json['score'] as int? ?? 0,
      level: json['level'] as String? ?? 'FAIBLE',
      confidence: json['confidence'] as String? ?? 'REDUITE',
      recommendation: json['recommendation'] as String? ?? '',
      explanations: (json['explanations'] as List? ?? [])
          .map((item) => Explanation.fromJson(item as Map<String, dynamic>))
          .toList(),
      sources: (json['sources'] as Map<String, dynamic>? ?? {})
          .map((key, value) => MapEntry(key, value as int?)),
      extracted: rawExtracted.map(
        (key, value) => MapEntry(key, (value as List? ?? []).cast<String>()),
      ),
      modelVersion: json['model_version'] as String? ?? 'absent',
    );
  }
}

class HistoryEntry {
  final int id;
  final String analysisType;
  final int riskScore;
  final String riskLevel;
  final String inputRedacted;
  final DateTime createdAt;

  HistoryEntry({
    required this.id,
    required this.analysisType,
    required this.riskScore,
    required this.riskLevel,
    required this.inputRedacted,
    required this.createdAt,
  });

  factory HistoryEntry.fromJson(Map<String, dynamic> json) => HistoryEntry(
        id: json['id'] as int,
        analysisType: json['analysis_type'] as String? ?? 'MESSAGE',
        riskScore: json['risk_score'] as int? ?? 0,
        riskLevel: json['risk_level'] as String? ?? 'FAIBLE',
        inputRedacted: json['input_redacted'] as String? ?? '',
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
