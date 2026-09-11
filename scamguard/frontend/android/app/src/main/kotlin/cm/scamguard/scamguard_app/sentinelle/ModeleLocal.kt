package cm.scamguard.scamguard_app.sentinelle

import android.content.Context
import org.json.JSONObject
import kotlin.math.ln
import kotlin.math.sqrt

class ModeleLocal private constructor(
    private val vocabulaire: Map<String, Int>,
    private val idf: DoubleArray,
    private val poids: DoubleArray,
    private val biais: Double,
    private val ngramMax: Int,
    private val sublinear: Boolean,
    val version: String
) {

    fun scorer(texte: String): Int {
        val jetons = decouper(texte)
        if (jetons.isEmpty()) return 0

        val comptes = HashMap<Int, Double>()
        for (jeton in jetons) {
            val index = vocabulaire[jeton] ?: continue
            comptes[index] = (comptes[index] ?: 0.0) + 1.0
        }
        if (comptes.isEmpty()) return 0

        var norme = 0.0
        val pondere = HashMap<Int, Double>(comptes.size)
        for ((index, compte) in comptes) {
            val tf = if (sublinear) 1.0 + ln(compte) else compte
            val valeur = tf * idf[index]
            pondere[index] = valeur
            norme += valeur * valeur
        }
        norme = sqrt(norme)
        if (norme == 0.0) return 0

        var somme = biais
        for ((index, valeur) in pondere) {
            somme += (valeur / norme) * poids[index]
        }

        val probabilite = 1.0 / (1.0 + Math.exp(-somme))
        return Math.round(probabilite * 100).toInt().coerceIn(0, 100)
    }

    private fun decouper(texte: String): List<String> {
        val mots = NON_MOT.split(sansAccent(texte.lowercase()))
            .filter { it.length > 1 }

        if (ngramMax < 2 || mots.size < 2) return mots

        val resultat = ArrayList<String>(mots.size * 2)
        resultat.addAll(mots)
        for (i in 0 until mots.size - 1) {
            resultat.add(mots[i] + " " + mots[i + 1])
        }
        return resultat
    }

    private fun sansAccent(texte: String): String {
        val normalise = java.text.Normalizer.normalize(texte, java.text.Normalizer.Form.NFD)
        return DIACRITIQUES.replace(normalise, "")
    }

    companion object {
        private val NON_MOT = Regex("[^a-z0-9]+")
        private val DIACRITIQUES = Regex("\\p{InCombiningDiacriticalMarks}+")

        @Volatile
        private var instance: ModeleLocal? = null

        fun obtenir(context: Context): ModeleLocal? {
            instance?.let { return it }
            synchronized(this) {
                instance?.let { return it }
                val charge = charger(context)
                instance = charge
                return charge
            }
        }

        private fun charger(context: Context): ModeleLocal? = try {
            val brut = context.assets
                .open("flutter_assets/assets/model_sms_v2.json")
                .bufferedReader()
                .use { it.readText() }

            val racine = JSONObject(brut)
            val vocabJson = racine.getJSONObject("vocabulaire")
            val idfJson = racine.getJSONArray("idf")
            val poidsJson = racine.getJSONArray("poids")

            val vocabulaire = HashMap<String, Int>(vocabJson.length())
            val cles = vocabJson.keys()
            while (cles.hasNext()) {
                val cle = cles.next()
                vocabulaire[cle] = vocabJson.getInt(cle)
            }

            val idf = DoubleArray(idfJson.length()) { idfJson.getDouble(it) }
            val poids = DoubleArray(poidsJson.length()) { poidsJson.getDouble(it) }

            ModeleLocal(
                vocabulaire = vocabulaire,
                idf = idf,
                poids = poids,
                biais = racine.getDouble("biais"),
                ngramMax = racine.optInt("ngram_max", 2),
                sublinear = racine.optBoolean("sublinear_tf", true),
                version = racine.optString("version", "sms")
            )
        } catch (erreur: Exception) {
            null
        }
    }
}
