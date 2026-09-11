package cm.scamguard.scamguard_app.sentinelle

import android.content.Context

object Reglages {

    const val SEUIL_SUSPECT = 40
    const val SEUIL_DANGEREUX = 70

    private const val FICHIER = "scamguard_reglages"
    private const val CLE_SURVEILLANCE = "surveillance_sms"
    private const val CLE_APPELS = "surveillance_appels"
    private const val CLE_AUTORISES = "expediteurs_autorises"
    private const val CLE_COMPTEUR = "analyses_effectuees"

    private fun prefs(context: Context) =
        context.getSharedPreferences(FICHIER, Context.MODE_PRIVATE)

    fun surveillanceActive(context: Context): Boolean =
        prefs(context).getBoolean(CLE_SURVEILLANCE, true)

    fun definirSurveillance(context: Context, active: Boolean) {
        prefs(context).edit().putBoolean(CLE_SURVEILLANCE, active).apply()
    }

    fun surveillanceAppels(context: Context): Boolean =
        prefs(context).getBoolean(CLE_APPELS, true)

    fun definirSurveillanceAppels(context: Context, active: Boolean) {
        prefs(context).edit().putBoolean(CLE_APPELS, active).apply()
    }

    fun expediteurAutorise(context: Context, expediteur: String): Boolean =
        autorises(context).contains(normaliser(expediteur))

    fun autorises(context: Context): Set<String> =
        prefs(context).getStringSet(CLE_AUTORISES, emptySet()) ?: emptySet()

    fun autoriser(context: Context, expediteur: String) {
        val liste = autorises(context).toMutableSet()
        liste.add(normaliser(expediteur))
        prefs(context).edit().putStringSet(CLE_AUTORISES, liste).apply()
    }

    fun retirerAutorisation(context: Context, expediteur: String) {
        val liste = autorises(context).toMutableSet()
        liste.remove(normaliser(expediteur))
        prefs(context).edit().putStringSet(CLE_AUTORISES, liste).apply()
    }

    fun analysesEffectuees(context: Context): Int =
        prefs(context).getInt(CLE_COMPTEUR, 0)

    fun incrementerAnalyses(context: Context) {
        prefs(context).edit().putInt(CLE_COMPTEUR, analysesEffectuees(context) + 1).apply()
    }

    private fun normaliser(expediteur: String): String =
        expediteur.filter { it.isLetterOrDigit() || it == '+' }.lowercase()
}
