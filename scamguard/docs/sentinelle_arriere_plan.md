# La sentinelle en arriere plan

Ce document explique comment ScamGuard analyse les SMS et les appels sans que
l'utilisateur ait besoin d'ouvrir l'application.

## Pourquoi du code natif Kotlin

Flutter ne peut pas recevoir un SMS quand l'application est fermee : le moteur
Dart n'est pas demarre. Android reveille en revanche un `BroadcastReceiver`
declare dans le manifeste. La detection vit donc en Kotlin, et Flutter sert
uniquement a afficher les resultats.

## Chaine complete

1. Un SMS arrive. Android diffuse `SMS_RECEIVED` et reveille `ReceveurSms`.
2. Le receveur passe la main a un fil separe (`goAsync`) pour ne pas bloquer
   le systeme, qui accorde environ dix secondes.
3. `ReglesLocales` cherche neuf motifs de fraude (code secret demande, gain
   annonce, frais de deblocage, menace judiciaire, lien raccourci...).
4. `ModeleLocal` calcule un score avec le modele TF-IDF exporte en JSON.
5. Les deux scores sont fusionnes moitie-moitie.
6. Sous 40 le message est ignore. Au dessus, il part en quarantaine et une
   notification est publiee.

## Le modele qui tourne sur le telephone

Le fichier `assets/model_sms_v2.json` contient le vocabulaire, les valeurs IDF,
les coefficients et le biais du modele entraine sur le serveur. `ModeleLocal.kt`
refait le calcul a la main : TF sous-lineaire, multiplication par l'IDF,
normalisation L2, produit scalaire, sigmoide.

Consequence importante : **aucun SMS ne quitte le telephone**. L'analyse est
entierement locale, ce qui protege la vie privee et fonctionne sans reseau.

Le test `tests/test_parite_modele_mobile.py` rejoue en Python le calcul exact
du Kotlin et verifie que l'ecart avec scikit-learn ne depasse jamais 2 points.
Ce test a permis de detecter une inversion de signe : scikit-learn oriente ses
coefficients vers la classe d'indice 1, or `FRAUDE` est la classe d'indice 0.
L'export applique desormais la correction.

## La quarantaine est logique, pas physique

Depuis Android 4.4, seule l'application SMS par defaut peut supprimer un message
du systeme. ScamGuard ne peut donc pas effacer un SMS frauduleux.

Ce qu'il fait a la place : il conserve une copie dans son espace prive, affiche
le diagnostic et previent l'utilisateur. Le SMS reste visible dans Google
Messages, mais l'utilisateur a ete averti avant de cliquer. C'est la limite du
systeme, pas un choix de conception.

## Les appels

`ServiceAppels` etend `CallScreeningService`. Pendant la sonnerie d'un numero
inconnu, il interroge `/api/v1/analyses/phone` et affiche une notification si le
numero a deja ete signale. L'appel n'est jamais bloque automatiquement : la
decision reste a l'utilisateur.

Sans reseau ou sans session valide, la consultation echoue en silence et
l'appel se deroule normalement.

## Permissions demandees

| Permission | Role | Obligatoire |
|---|---|---|
| `RECEIVE_SMS`, `READ_SMS` | lire le SMS des sa reception | oui |
| `POST_NOTIFICATIONS` | prevenir sans ouvrir l'application | oui |
| `READ_PHONE_STATE` | identifier un appel entrant | non |
| `CAMERA` | scanner un QR code | non |
| `RECEIVE_BOOT_COMPLETED` | reprendre la surveillance apres redemarrage | non |

`PermissionsScreen` explique chaque acces en francais simple avant de le
demander, et propose d'ouvrir les reglages Android si l'utilisateur a refuse
definitivement.

## Reglages disponibles

`Reglages.kt` stocke dans les preferences partagees : surveillance SMS active,
surveillance des appels active, liste des expediteurs de confiance, compteur
d'analyses. Un expediteur marque de confiance n'est plus jamais analyse.

## Limite a annoncer au jury

Flutter et le SDK Android n'etant pas installes dans l'environnement de
developpement utilise, ce code n'a pas ete compile ni execute sur un appareil.
La logique de scoring est en revanche verifiee par le test de parite cote
serveur.
