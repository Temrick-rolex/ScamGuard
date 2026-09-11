package cm.scamguard.scamguard_app.sentinelle

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import kotlin.concurrent.thread

class ReceveurSms : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return
        if (!Reglages.surveillanceActive(context)) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent) ?: return
        if (messages.isEmpty()) return

        val expediteur = messages[0].originatingAddress ?: "inconnu"
        val texte = messages.joinToString("") { it.messageBody ?: "" }
        if (texte.isBlank()) return

        val resultat = goAsync()
        thread {
            try {
                traiter(context.applicationContext, expediteur, texte)
            } finally {
                resultat.finish()
            }
        }
    }

    private fun traiter(context: Context, expediteur: String, texte: String) {
        if (Reglages.expediteurAutorise(context, expediteur)) return

        val (scoreRegles, signaux) = ReglesLocales.evaluer(texte)
        val scoreModele = ModeleLocal.obtenir(context)?.scorer(texte)

        val score = fusionner(scoreRegles, scoreModele)
        val niveau = when {
            score >= Reglages.SEUIL_DANGEREUX -> "DANGEREUX"
            score >= Reglages.SEUIL_SUSPECT -> "SUSPECT"
            else -> "FAIBLE"
        }

        Reglages.incrementerAnalyses(context)
        if (niveau == "FAIBLE") return

        val motifs = ArrayList<String>()
        signaux.sortedByDescending { it.poids }.forEach { motifs.add(it.message) }
        if (scoreModele != null && scoreModele >= 50) {
            motifs.add("Le modele reconnait une formulation typique des arnaques")
        }
        if (motifs.isEmpty()) {
            motifs.add("Plusieurs indices faibles se cumulent")
        }

        val element = Element(
            id = System.currentTimeMillis(),
            expediteur = expediteur,
            texte = texte.take(1000),
            score = score,
            niveau = niveau,
            motifs = motifs,
            recu = System.currentTimeMillis()
        )

        Quarantaine.ajouter(context, element)
        Alertes.avertir(context, element)
    }

    private fun fusionner(regles: Int, modele: Int?): Int {
        val score = if (modele == null) {
            regles.toDouble()
        } else {
            regles * 0.5 + modele * 0.5
        }
        return Math.round(score).toInt().coerceIn(0, 100)
    }
}
