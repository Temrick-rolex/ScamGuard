package cm.scamguard.scamguard_app.sentinelle

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import cm.scamguard.scamguard_app.MainActivity

object Alertes {

    private const val CANAL_DANGER = "scamguard_danger"
    private const val CANAL_SUSPECT = "scamguard_suspect"

    fun creerCanaux(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val gestionnaire = context.getSystemService(NotificationManager::class.java) ?: return

        val danger = NotificationChannel(
            CANAL_DANGER,
            "Messages dangereux",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "Alerte quand un SMS presente un risque eleve de fraude"
            enableVibration(true)
        }

        val suspect = NotificationChannel(
            CANAL_SUSPECT,
            "Messages suspects",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Signale un SMS douteux sans interrompre votre activite"
            enableVibration(false)
        }

        gestionnaire.createNotificationChannel(danger)
        gestionnaire.createNotificationChannel(suspect)
    }

    fun avertir(context: Context, element: Element) {
        creerCanaux(context)

        val dangereux = element.niveau == "DANGEREUX"
        val canal = if (dangereux) CANAL_DANGER else CANAL_SUSPECT

        val titre = if (dangereux) {
            "Message dangereux mis en quarantaine"
        } else {
            "Message suspect detecte"
        }

        val motif = element.motifs.firstOrNull() ?: "Formulation typique des arnaques"
        val corps = "De ${element.expediteur} : $motif (risque ${element.score} sur 100)"

        val ouverture = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("quarantaine_id", element.id)
        }

        val action = PendingIntent.getActivity(
            context,
            element.id.toInt(),
            ouverture,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, canal)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(titre)
            .setContentText(corps)
            .setStyle(NotificationCompat.BigTextStyle().bigText(corps))
            .setPriority(if (dangereux) NotificationCompat.PRIORITY_HIGH else NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_ERROR)
            .setAutoCancel(true)
            .setContentIntent(action)
            .build()

        try {
            NotificationManagerCompat.from(context).notify(element.id.toInt(), notification)
        } catch (erreur: SecurityException) {
            // permission de notification refusee, la quarantaine reste consultable
        }
    }
}
