package cm.scamguard.scamguard_app.sentinelle

data class Signal(val code: String, val message: String, val poids: Int)

object ReglesLocales {

    private val REGLES = listOf(
        Signal("R1", "On vous demande un code secret", 30) to
            Regex("\\b(code|pin|mot de passe|password|otp)\\b.{0,40}\\b(\\d{4,8})\\b", RegexOption.IGNORE_CASE),
        Signal("R2", "Le message imite un operateur ou une banque", 25) to
            Regex("\\b(mtn|orange money|momo|om|afriland|ecobank|uba|sgbc|bicec)\\b.{0,60}\\b(compte|bloque|suspendu|verifier|confirmer)\\b", RegexOption.IGNORE_CASE),
        Signal("R3", "Le message vous met sous pression", 20) to
            Regex("\\b(urgent|immediatement|sous 24 ?h|maintenant|dernier avertissement|expire)\\b", RegexOption.IGNORE_CASE),
        Signal("R4", "On vous annonce un gain", 28) to
            Regex("\\b(felicitation\\w*|gagn\\w+|gain|tirage|heureux gagnant|winner|prize)\\b", RegexOption.IGNORE_CASE),
        Signal("R5", "On vous demande de payer pour recevoir de l argent", 32) to
            Regex("\\b(frais|caution|avance|deblocage|activation)\\b.{0,50}\\b(\\d{3,7})\\b", RegexOption.IGNORE_CASE),
        Signal("R6", "Le message contient un lien raccourci ou douteux", 22) to
            Regex("(bit\\.ly|tinyurl|t\\.me|cutt\\.ly|is\\.gd|rb\\.gy|shorturl|\\.tk/|\\.ml/|\\.ga/|\\.cf/|\\.xyz/)", RegexOption.IGNORE_CASE),
        Signal("R8", "On vous demande un transfert d argent urgent", 15) to
            Regex("\\b(envoy\\w+|transfer\\w+|depos\\w+)\\b.{0,40}\\b(\\d{4,8})\\s?(fcfa|xaf|f)?\\b", RegexOption.IGNORE_CASE),
        Signal("R9", "Le message vous menace de poursuites", 20) to
            Regex("\\b(poursuite|justice|police|tribunal|amende|arrestation|huissier)\\b", RegexOption.IGNORE_CASE),
        Signal("R10", "On vous promet un rendement irrealiste", 16) to
            Regex("\\b(investi\\w+|placement|crypto|forex|doubl\\w+)\\b.{0,50}\\b(\\d{2,3}\\s?%|rendement|benefice)\\b", RegexOption.IGNORE_CASE)
    )

    private val LIEN = Regex("(https?://\\S+|www\\.\\S+|\\b[a-z0-9-]+\\.(com|net|org|info|xyz|tk|ml|ga|cf|top|icu|cm)\\b\\S*)", RegexOption.IGNORE_CASE)

    fun evaluer(texte: String): Pair<Int, List<Signal>> {
        val trouves = ArrayList<Signal>()
        var total = 0

        for ((signal, motif) in REGLES) {
            if (motif.containsMatchIn(texte)) {
                trouves.add(signal)
                total += signal.poids
            }
        }
        return Pair(total.coerceAtMost(100), trouves)
    }

    fun liens(texte: String): List<String> =
        LIEN.findAll(texte).map { it.value.trimEnd('.', ',', ')') }.distinct().toList()
}
