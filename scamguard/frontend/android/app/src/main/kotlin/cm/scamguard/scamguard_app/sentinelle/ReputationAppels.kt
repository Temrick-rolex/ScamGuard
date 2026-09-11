package cm.scamguard.scamguard_app.sentinelle

import android.content.Context
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

data class VerdictAppel(val score: Int, val motifs: List<String>, val signalements: Int)

object ReputationAppels {

    private const val FICHIER = "scamguard_session"
    private const val CLE_URL = "api_base_url"
    private const val CLE_JETON = "access_token"
    private const val DELAI = 4000

    fun enregistrerSession(context: Context, baseUrl: String, jeton: String) {
        context.getSharedPreferences(FICHIER, Context.MODE_PRIVATE)
            .edit()
            .putString(CLE_URL, baseUrl)
            .putString(CLE_JETON, jeton)
            .apply()
    }

    fun effacerSession(context: Context) {
        context.getSharedPreferences(FICHIER, Context.MODE_PRIVATE).edit().clear().apply()
    }

    fun consulter(context: Context, numero: String): VerdictAppel? {
        val prefs = context.getSharedPreferences(FICHIER, Context.MODE_PRIVATE)
        val base = prefs.getString(CLE_URL, null) ?: return null
        val jeton = prefs.getString(CLE_JETON, null) ?: return null

        return try {
            // Convention : "base" contient deja le prefixe /api/v1, on ne
            // colle donc que le chemin de l endpoint. Evite le double
            // /api/v1/api/v1/... de l ancienne convention.
            val connexion = (URL("$base/analyses/phone").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = DELAI
                readTimeout = DELAI
                doOutput = true
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Authorization", "Bearer $jeton")
            }

            connexion.outputStream.use {
                it.write(JSONObject().put("phone", numero).toString().toByteArray())
            }

            if (connexion.responseCode != 200) return null

            val corps = connexion.inputStream.bufferedReader().use { it.readText() }
            val racine = JSONObject(corps)
            val explications = racine.optJSONArray("explanations")
            val motifs = ArrayList<String>()
            if (explications != null) {
                for (index in 0 until explications.length()) {
                    motifs.add(explications.getJSONObject(index).optString("message"))
                }
            }

            VerdictAppel(
                score = racine.optInt("score", 0),
                motifs = motifs,
                signalements = racine.optJSONObject("sources")?.optInt("reports", 0) ?: 0
            )
        } catch (erreur: Exception) {
            null
        }
    }
}
