package cm.scamguard.scamguard_app.sentinelle

import android.telecom.Call
import android.telecom.CallScreeningService
import androidx.annotation.RequiresApi
import android.os.Build

@RequiresApi(Build.VERSION_CODES.N)
class ServiceAppels : CallScreeningService() {

    override fun onScreenCall(details: Call.Details) {
        val reponse = CallResponse.Builder().build()
        respondToCall(details, reponse)

        if (!Reglages.surveillanceAppels(this)) return
        if (details.callDirection != Call.Details.DIRECTION_INCOMING) return

        val numero = details.handle?.schemeSpecificPart ?: return
        if (Reglages.expediteurAutorise(this, numero)) return

        Thread {
            val verdict = ReputationAppels.consulter(applicationContext, numero)
            if (verdict != null && verdict.score >= Reglages.SEUIL_SUSPECT) {
                val element = Element(
                    id = System.currentTimeMillis(),
                    expediteur = numero,
                    texte = "Appel entrant de $numero",
                    score = verdict.score,
                    niveau = if (verdict.score >= Reglages.SEUIL_DANGEREUX) "DANGEREUX" else "SUSPECT",
                    motifs = verdict.motifs,
                    recu = System.currentTimeMillis()
                )
                Alertes.avertir(applicationContext, element)
            }
        }.start()
    }
}
