package cm.scamguard.scamguard_app.sentinelle

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

data class Element(
    val id: Long,
    val expediteur: String,
    val texte: String,
    val score: Int,
    val niveau: String,
    val motifs: List<String>,
    val recu: Long,
    var lu: Boolean = false
)

object Quarantaine {

    private const val FICHIER = "scamguard_quarantaine"
    private const val CLE = "elements"
    private const val MAXIMUM = 200

    private fun prefs(context: Context) =
        context.getSharedPreferences(FICHIER, Context.MODE_PRIVATE)

    @Synchronized
    fun ajouter(context: Context, element: Element) {
        val liste = lire(context).toMutableList()
        if (liste.any { it.expediteur == element.expediteur && it.texte == element.texte }) return

        liste.add(0, element)
        while (liste.size > MAXIMUM) liste.removeAt(liste.size - 1)
        ecrire(context, liste)
    }

    @Synchronized
    fun lire(context: Context): List<Element> {
        val brut = prefs(context).getString(CLE, null) ?: return emptyList()
        return try {
            val tableau = JSONArray(brut)
            (0 until tableau.length()).map { index ->
                val objet = tableau.getJSONObject(index)
                val motifs = objet.optJSONArray("motifs") ?: JSONArray()
                Element(
                    id = objet.getLong("id"),
                    expediteur = objet.getString("expediteur"),
                    texte = objet.getString("texte"),
                    score = objet.getInt("score"),
                    niveau = objet.getString("niveau"),
                    motifs = (0 until motifs.length()).map { motifs.getString(it) },
                    recu = objet.getLong("recu"),
                    lu = objet.optBoolean("lu", false)
                )
            }
        } catch (erreur: Exception) {
            emptyList()
        }
    }

    @Synchronized
    fun supprimer(context: Context, id: Long) {
        ecrire(context, lire(context).filterNot { it.id == id })
    }

    @Synchronized
    fun marquerLu(context: Context, id: Long) {
        val liste = lire(context)
        liste.firstOrNull { it.id == id }?.lu = true
        ecrire(context, liste)
    }

    @Synchronized
    fun vider(context: Context) {
        prefs(context).edit().remove(CLE).apply()
    }

    fun enJson(element: Element): Map<String, Any> = mapOf(
        "id" to element.id,
        "expediteur" to element.expediteur,
        "texte" to element.texte,
        "score" to element.score,
        "niveau" to element.niveau,
        "motifs" to element.motifs,
        "recu" to element.recu,
        "lu" to element.lu
    )

    private fun ecrire(context: Context, liste: List<Element>) {
        val tableau = JSONArray()
        for (element in liste) {
            tableau.put(
                JSONObject().apply {
                    put("id", element.id)
                    put("expediteur", element.expediteur)
                    put("texte", element.texte)
                    put("score", element.score)
                    put("niveau", element.niveau)
                    put("motifs", JSONArray(element.motifs))
                    put("recu", element.recu)
                    put("lu", element.lu)
                }
            )
        }
        prefs(context).edit().putString(CLE, tableau.toString()).apply()
    }
}
