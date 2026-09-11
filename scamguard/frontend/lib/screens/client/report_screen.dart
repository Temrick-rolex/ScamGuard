import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/theme.dart';
import '../../models/report.dart';
import '../../services/api_client.dart';
import '../../state/providers.dart';
import '../../widgets/common.dart';
import '../../core/branding.dart';

class ReportScreen extends ConsumerStatefulWidget {
  final String prefilledContent;

  const ReportScreen({super.key, this.prefilledContent = ''});

  @override
  ConsumerState<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends ConsumerState<ReportScreen> {
  late final TextEditingController _content =
      TextEditingController(text: widget.prefilledContent);
  final _phone = TextEditingController();
  final _comment = TextEditingController();

  String _reason = 'ARNAQUE_MOBILE_MONEY';
  bool _busy = false;
  String? _error;
  ReportReceipt? _receipt;

  @override
  void dispose() {
    _content.dispose();
    _phone.dispose();
    _comment.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_content.text.trim().length < 15) {
      setState(() => _error = 'Collez le message complet, 15 caracteres minimum');
      return;
    }

    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      final receipt = await ref.read(reportServiceProvider).submit(
            content: _content.text.trim(),
            reason: _reason,
            comment: _comment.text.trim(),
            suspectPhone: _phone.text.trim(),
          );
      setState(() => _receipt = receipt);
      ref.invalidate(myReportsProvider);
      ref.invalidate(feedProvider);
      ref.invalidate(statsProvider);
    } on ApiException catch (error) {
      setState(() => _error = error.isConflict
          ? 'Vous avez deja signale ce contenu.'
          : error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Signaler une fraude')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 620),
            child: _receipt != null
                ? _Receipt(receipt: _receipt!)
                : _buildForm(),
          ),
        ),
      ),
    );
  }

  Widget _buildForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_error != null) ErrorBanner(_error!),
        SectionCard(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.info_outline, size: 20, color: Branding.couleurPrincipale),
              const SizedBox(width: 10),
              const Expanded(
                child: Text(
                  Textes.regleSignalement,
                  style: TextStyle(fontSize: 12.8, color: Colors.black87),
                ),
              ),
            ],
          ),
        ),
        const Text('Le message recu', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: _content,
          maxLines: 6,
          decoration: const InputDecoration(
            hintText: 'Collez le message exactement comme vous l avez recu',
          ),
        ),
        const SizedBox(height: 18),
        const Text('Type de fraude', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: _reason,
          items: reportReasons.entries
              .map((entry) => DropdownMenuItem(value: entry.key, child: Text(entry.value)))
              .toList(),
          onChanged: (value) => setState(() => _reason = value!),
        ),
        const SizedBox(height: 18),
        TextField(
          controller: _phone,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(
            labelText: 'Numero de l expediteur (facultatif)',
            hintText: '6XX XX XX XX',
            prefixIcon: Icon(Icons.phone_outlined),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _comment,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Precisions (facultatif)',
            hintText: 'Comment avez-vous recu ce message ?',
          ),
        ),
        const SizedBox(height: 24),
        FilledButton.icon(
          onPressed: _busy ? null : _submit,
          icon: _busy
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : const Icon(Icons.send),
          label: const Text('Envoyer le signalement'),
        ),
      ],
    );
  }
}

class _Receipt extends StatelessWidget {
  final ReportReceipt receipt;

  const _Receipt({required this.receipt});

  @override
  Widget build(BuildContext context) {
    final color = levelColor(receipt.riskLevel);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 20),
        Icon(
          receipt.published ? Icons.verified : Icons.hourglass_top,
          size: 62,
          color: Branding.couleurPrincipale,
        ),
        const SizedBox(height: 14),
        Text(
          receipt.published ? 'Signalement publie' : 'Signalement enregistre',
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 21, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Text(
          receipt.message,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Colors.black54),
        ),
        const SizedBox(height: 22),
        SectionCard(
          child: Column(
            children: [
              _line('Reference', '#${receipt.id}'),
              _line('Niveau de risque',
                  '${levelLabel(receipt.riskLevel)} (${receipt.riskScore}/100)', color),
              _line('Signalements de ce contenu', '${receipt.reportCount}'),
            ],
          ),
        ),
        if (receipt.missing.isNotEmpty)
          SectionCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Pour apparaitre dans l historique public',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
                ...receipt.missing.map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Row(
                      children: [
                        const Icon(Icons.radio_button_unchecked, size: 16, color: Colors.black45),
                        const SizedBox(width: 8),
                        Expanded(child: Text(item, style: const TextStyle(fontSize: 13.5))),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Terminer'),
        ),
      ],
    );
  }

  Widget _line(String label, String value, [Color? color]) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.black54)),
          Text(
            value,
            style: TextStyle(fontWeight: FontWeight.w600, color: color),
          ),
        ],
      ),
    );
  }
}
