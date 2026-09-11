package cm.scamguard.scamguard_app

import cm.scamguard.scamguard_app.sentinelle.Alertes
import cm.scamguard.scamguard_app.sentinelle.ModeleLocal
import cm.scamguard.scamguard_app.sentinelle.Quarantaine
import cm.scamguard.scamguard_app.sentinelle.Reglages
import cm.scamguard.scamguard_app.sentinelle.ReputationAppels
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {

    private val canal = "cm.scamguard/sentinelle"

    override fun configureFlutterEngine(engine: FlutterEngine) {
        super.configureFlutterEngine(engine)
        Alertes.creerCanaux(this)

        MethodChannel(engine.dartExecutor.binaryMessenger, canal).setMethodCallHandler { appel, reponse ->
            when (appel.method) {
                "lireQuarantaine" ->
                    reponse.success(Quarantaine.lire(this).map { Quarantaine.enJson(it) })

                "supprimerElement" -> {
                    Quarantaine.supprimer(this, (appel.argument<Any>("id") as Number).toLong())
                    reponse.success(true)
                }

                "marquerLu" -> {
                    Quarantaine.marquerLu(this, (appel.argument<Any>("id") as Number).toLong())
                    reponse.success(true)
                }

                "viderQuarantaine" -> {
                    Quarantaine.vider(this)
                    reponse.success(true)
                }

                "surveillanceActive" -> reponse.success(Reglages.surveillanceActive(this))

                "definirSurveillance" -> {
                    Reglages.definirSurveillance(this, appel.argument<Boolean>("active") ?: true)
                    reponse.success(true)
                }

                "surveillanceAppels" -> reponse.success(Reglages.surveillanceAppels(this))

                "definirSurveillanceAppels" -> {
                    Reglages.definirSurveillanceAppels(this, appel.argument<Boolean>("active") ?: true)
                    reponse.success(true)
                }

                "autoriserExpediteur" -> {
                    Reglages.autoriser(this, appel.argument<String>("expediteur") ?: "")
                    reponse.success(true)
                }

                "retirerAutorisation" -> {
                    Reglages.retirerAutorisation(this, appel.argument<String>("expediteur") ?: "")
                    reponse.success(true)
                }

                "expediteursAutorises" -> reponse.success(Reglages.autorises(this).toList())

                "nombreAnalyses" -> reponse.success(Reglages.analysesEffectuees(this))

                "modeleCharge" -> reponse.success(ModeleLocal.obtenir(this) != null)

                "versionModele" -> reponse.success(ModeleLocal.obtenir(this)?.version ?: "absent")

                "analyserLocalement" -> {
                    val texte = appel.argument<String>("texte") ?: ""
                    reponse.success(ModeleLocal.obtenir(this)?.scorer(texte) ?: -1)
                }

                "enregistrerSession" -> {
                    ReputationAppels.enregistrerSession(
                        this,
                        appel.argument<String>("baseUrl") ?: "",
                        appel.argument<String>("jeton") ?: ""
                    )
                    reponse.success(true)
                }

                "effacerSession" -> {
                    ReputationAppels.effacerSession(this)
                    reponse.success(true)
                }

                else -> reponse.notImplemented()
            }
        }
    }
}
