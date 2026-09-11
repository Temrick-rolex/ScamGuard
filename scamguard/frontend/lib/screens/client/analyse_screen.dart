import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/branding.dart';
import '../../core/theme.dart';
import '../../models/analysis.dart';
import '../../services/api_client.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../widgets/explanation_list.dart';
import '../../widgets/risk_gauge.dart';
import 'report_screen.dart';
import 'scan_qr_screen.dart';

enum AnalysisMode { message, lien, numero }

class AnalyseScreen extends ConsumerStatefulWidget {
  const AnalyseScreen({super.key});

  @override
  ConsumerState<AnalyseScreen> createState() => _AnalyseScreenState();
}

class _AnalyseScreenState extends ConsumerState<AnalyseScreen> {
  final _input = TextEditingController();

  AnalysisMode _mode = AnalysisMode.message;
  AnalysisResult? _result;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _input.dispose();
    super.dispose();
  }

  String get _hint {
    switch (_mode) {
      case AnalysisMode.message:
        return Textes.collerMessage;
      case AnalysisMode.lien:
        return Textes.collerLien;
      case AnalysisMode.numero:
        return Textes.saisirNumero;
    }
  }

  Future<void> _paste() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data?.text != null) _input.text = data!.text!;
  }

  Future<void> _analyse() async {
    final value = _input.text.trim();
    if (value.length < 4) {
      setState(() => _error = 'Saisissez un contenu a analyser');
      return;
    }

    setState(() {
      _busy = true;
      _error = null;
      _result = null;
    });

    final service = ref.read(analysisServiceProvider);

    try {
      final result = switch (_mode) {
        AnalysisMode.message => await service.analyseMessage(value),
        AnalysisMode.lien => await service.analyseUrl(value),
        AnalysisMode.numero => await service.analysePhone(value),
      };
      setState(() => _result = result);
      ref.invalidate(analysisHistoryProvider);
    } on ApiException catch (error) {
      setState(() => _error = error.isQuotaExceeded
          ? Textes.quotaAtteint
          : error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openScanner() async {
    final code = await Navigator.of(context).push<String>(
      MaterialPageRoute(builder: (_) => const ScanQrScreen()),
    );
    if (code == null || !mounted) return;

    setState(() {
      _mode = AnalysisMode.lien;
      _input.text = code;
    });
    await _analyse();
  }

  void _report() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReportScreen(prefilledContent: _input.text.trim()),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analyser'),
        actions: [
          IconButton(
            tooltip: 'Scanner un QR code',
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: _openScanner,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 620),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SegmentedButton<AnalysisMode>(
                  segments: const [
                    ButtonSegment(
                      value: AnalysisMode.message,
                      label: Text('Message'),
                      icon: Icon(Icons.sms_outlined),
                    ),
                    ButtonSegment(
                      value: AnalysisMode.lien,
                      label: Text('Lien'),
                      icon: Icon(Icons.link),
                    ),
                    ButtonSegment(
                      value: AnalysisMode.numero,
                      label: Text('Numero'),
                      icon: Icon(Icons.phone_outlined),
                    ),
                  ],
                  selected: {_mode},
                  onSelectionChanged: (values) => setState(() {
                    _mode = values.first;
                    _result = null;
                    _error = null;
                  }),
                ),
                const SizedBox(height: 16),
                if (_error != null) ErrorBanner(_error!),
                TextField(
                  controller: _input,
                  maxLines: _mode == AnalysisMode.message ? 6 : 2,
                  keyboardType: _mode == AnalysisMode.numero
                      ? TextInputType.phone
                      : TextInputType.multiline,
                  decoration: InputDecoration(
                    hintText: _hint,
                    suffixIcon: IconButton(
                      tooltip: 'Coller',
                      icon: const Icon(Icons.content_paste),
                      onPressed: _paste,
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                FilledButton.icon(
                  onPressed: _busy ? null : _analyse,
                  icon: _busy
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.search),
                  label: Text(_busy ? 'Analyse en cours' : 'Analyser'),
                ),
                const SizedBox(height: 22),
                if (_result != null) _ResultPanel(result: _result!, onReport: _report),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ResultPanel extends StatelessWidget {
  final AnalysisResult result;
  final VoidCallback onReport;

  const _ResultPanel({required this.result, required this.onReport});

  @override
  Widget build(BuildContext context) {
    final color = levelColor(result.level);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SectionCard(
          padding: const EdgeInsets.symmetric(vertical: 22, horizontal: 16),
          child: Column(
            children: [
              RiskGauge(score: result.score, level: result.level),
              const SizedBox(height: 18),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  result.recommendation,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: color, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
        SectionCard(child: ExplanationList(explanations: result.explanations)),
        if (result.links.isNotEmpty)
          SectionCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Liens detectes',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 8),
                ...result.links.map(
                  (link) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Row(
                      children: [
                        const Icon(Icons.link, size: 17, color: Colors.black45),
                        const SizedBox(width: 8),
                        Expanded(
                          child: SelectableText(
                            link,
                            style: const TextStyle(fontSize: 13.5, fontFamily: 'monospace'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  Textes.liensJamaisOuverts,
                  style: TextStyle(fontSize: 12, color: Colors.black54),
                ),
              ],
            ),
          ),
        if (result.isReduced)
          SectionCard(
            child: Row(
              children: [
                const Icon(Icons.info_outline, size: 20, color: Colors.black54),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Analyse en mode reduit : certaines verifications externes '
                    'n etaient pas disponibles. Resultat base sur les regles, '
                    'le modele ${result.modelVersion} et la communaute.',
                    style: const TextStyle(fontSize: 12.5, color: Colors.black54),
                  ),
                ),
              ],
            ),
          ),
        OutlinedButton.icon(
          onPressed: onReport,
          icon: const Icon(Icons.flag_outlined),
          label: const Text('Signaler ce contenu'),
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}
