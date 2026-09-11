const reportReasons = <String, String>{
  'ARNAQUE_MOBILE_MONEY': 'Arnaque Mobile Money',
  'FAUX_GAIN': 'Faux gain, tombola',
  'DEMANDE_CODE': 'Demande de code ou PIN',
  'FRAIS_DEBLOCAGE': 'Frais de deblocage',
  'FAUSSE_OFFRE_EMPLOI': 'Fausse offre d emploi',
  'PLACEMENT_DOUTEUX': 'Placement douteux',
  'USURPATION_BANQUE': 'Faux message de banque',
  'MENACE_CHANTAGE': 'Menace ou chantage',
  'AUTRE': 'Autre',
};

String reasonLabel(String code) => reportReasons[code] ?? code;

class ReportReceipt {
  final int id;
  final String status;
  final int riskScore;
  final String riskLevel;
  final int reportCount;
  final bool published;
  final List<String> missing;
  final String message;

  ReportReceipt({
    required this.id,
    required this.status,
    required this.riskScore,
    required this.riskLevel,
    required this.reportCount,
    required this.published,
    required this.missing,
    required this.message,
  });

  factory ReportReceipt.fromJson(Map<String, dynamic> json) => ReportReceipt(
        id: json['id'] as int,
        status: json['status'] as String? ?? 'EN_ATTENTE',
        riskScore: json['risk_score'] as int? ?? 0,
        riskLevel: json['risk_level'] as String? ?? 'FAIBLE',
        reportCount: json['report_count'] as int? ?? 1,
        published: json['published'] as bool? ?? false,
        missing: (json['missing_for_publication'] as List? ?? []).cast<String>(),
        message: json['message'] as String? ?? '',
      );
}

class FeedItem {
  final int id;
  final String contentRedacted;
  final String mainReason;
  final String? suspectPhone;
  final int reportCount;
  final int validatedCount;
  final DateTime lastSeenAt;

  FeedItem({
    required this.id,
    required this.contentRedacted,
    required this.mainReason,
    this.suspectPhone,
    required this.reportCount,
    required this.validatedCount,
    required this.lastSeenAt,
  });

  factory FeedItem.fromJson(Map<String, dynamic> json) => FeedItem(
        id: json['id'] as int,
        contentRedacted: json['content_redacted'] as String? ?? '',
        mainReason: json['main_reason'] as String? ?? '',
        suspectPhone: json['suspect_phone'] as String?,
        reportCount: json['report_count'] as int? ?? 0,
        validatedCount: json['validated_count'] as int? ?? 0,
        lastSeenAt: DateTime.parse(json['last_seen_at'] as String),
      );
}

class PendingReport {
  final int id;
  final String contentRedacted;
  final String reason;
  final String comment;
  final String? suspectPhone;
  final String? suspectUrl;
  final int riskScore;
  final String riskLevel;
  final DateTime createdAt;

  PendingReport({
    required this.id,
    required this.contentRedacted,
    required this.reason,
    required this.comment,
    this.suspectPhone,
    this.suspectUrl,
    required this.riskScore,
    required this.riskLevel,
    required this.createdAt,
  });

  factory PendingReport.fromJson(Map<String, dynamic> json) => PendingReport(
        id: json['id'] as int,
        contentRedacted: json['content_redacted'] as String? ?? '',
        reason: json['reason'] as String? ?? '',
        comment: json['comment'] as String? ?? '',
        suspectPhone: json['suspect_phone'] as String?,
        suspectUrl: json['suspect_url'] as String?,
        riskScore: json['risk_score'] as int? ?? 0,
        riskLevel: json['risk_level'] as String? ?? 'FAIBLE',
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class MyReport {
  final int id;
  final String contentRedacted;
  final String reason;
  final String status;
  final int riskScore;
  final String riskLevel;
  final String moderationNote;
  final DateTime createdAt;

  MyReport({
    required this.id,
    required this.contentRedacted,
    required this.reason,
    required this.status,
    required this.riskScore,
    required this.riskLevel,
    required this.moderationNote,
    required this.createdAt,
  });

  factory MyReport.fromJson(Map<String, dynamic> json) => MyReport(
        id: json['id'] as int,
        contentRedacted: json['content_redacted'] as String? ?? '',
        reason: json['reason'] as String? ?? '',
        status: json['status'] as String? ?? 'EN_ATTENTE',
        riskScore: json['risk_score'] as int? ?? 0,
        riskLevel: json['risk_level'] as String? ?? 'FAIBLE',
        moderationNote: json['moderation_note'] as String? ?? '',
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}

class PublicStats {
  final int received;
  final int published;
  final int suspectPhones;
  final List<Map<String, dynamic>> topReasons;

  PublicStats({
    required this.received,
    required this.published,
    required this.suspectPhones,
    required this.topReasons,
  });

  factory PublicStats.fromJson(Map<String, dynamic> json) => PublicStats(
        received: json['signalements_recus'] as int? ?? 0,
        published: json['arnaques_publiees'] as int? ?? 0,
        suspectPhones: json['numeros_suspects'] as int? ?? 0,
        topReasons: (json['motifs_frequents'] as List? ?? [])
            .cast<Map<String, dynamic>>(),
      );
}
