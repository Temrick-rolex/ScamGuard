# ScamGuard — application multiplateforme

Application Flutter unique produisant trois cibles :

| Cible | Commande | Utilisateur |
|---|---|---|
| Mobile Android | `flutter build apk` | Client |
| Web Client | `flutter build web` | Client |
| Web Admin | `flutter build web --dart-define=ADMIN_BUILD=true` | Administrateur |

## Prérequis

Flutter SDK 3.19 ou plus récent, Android SDK pour l'APK.

```
flutter --version
flutter doctor
```

## Première installation

Le dépôt ne contient que le code source. Les dossiers générés par Flutter
(`android/gradle`, `ios`, `linux`, `windows`, `.dart_tool`) sont produits par
la commande suivante, à lancer une seule fois depuis le dossier parent :

```
flutter create --org cm.scamguard --project-name scamguard_app .
```

Cette commande ne remplace pas les fichiers déjà présents (`lib/`, `pubspec.yaml`,
`web/index.html`, `AndroidManifest.xml`). Ensuite :

```
flutter pub get
```

## Lancer en développement

L'URL du backend est injectée à la compilation, jamais écrite en dur.

```
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
flutter run -d <appareil> --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

`10.0.2.2` est l'adresse de la machine hôte vue depuis l'émulateur Android.
Sur un téléphone physique relié au même Wi-Fi, utilisez l'IP locale du PC
(`http://192.168.x.x:8000/api/v1`).

## Compiler pour la production

```
flutter build apk --release --dart-define=API_BASE_URL=https://<votre-api>/api/v1
flutter build web --release --dart-define=API_BASE_URL=https://<votre-api>/api/v1
flutter build web --release --dart-define=ADMIN_BUILD=true --dart-define=API_BASE_URL=https://<votre-api>/api/v1
```

## Tests

```
flutter test
```

## Structure

```
lib/
  core/        config.dart (URL API, quota), theme.dart (couleurs par niveau)
  models/      miroir exact des schémas Pydantic du backend
  services/    api_client.dart (HTTP + refresh auto), un service par domaine
  state/       providers.dart (Riverpod, session, listes)
  widgets/     risk_gauge, explanation_list, common (chips, cartes, erreurs)
  screens/
    auth/      login, register
    client/    home, analyse, scan_qr, report, history, settings, client_shell
    admin/     dashboard, moderation, users, admin_shell
```

## Correspondance avec le backend

| Écran | Endpoint |
|---|---|
| Connexion | `POST /auth/login`, `POST /auth/refresh` |
| Analyser | `POST /analyses/{message,url,qr,phone}` |
| Historique analyses | `GET /analyses/history` |
| Signaler | `POST /reports` |
| Mes signalements | `GET /reports/mine` |
| Arnaques connues | `GET /reports/history` |
| Accueil, tableau de bord | `GET /reports/stats` |
| Modération | `GET /admin/reports/pending`, `POST .../approve`, `.../reject` |
| Utilisateurs | `GET /admin/users`, `POST .../suspend`, `.../reactivate` |

## Points de conception

Le jeton d'accès expire au bout de 15 minutes. `ApiClient` rejoue automatiquement
la requête après un `401` en utilisant le jeton de rafraîchissement ; si le
rafraîchissement échoue, la session est effacée et l'utilisateur revient à l'écran
de connexion.

Aucun lien n'est ouvert par l'application. Les liens détectés sont affichés en
texte sélectionnable ; c'est l'utilisateur qui décide.

Le scan de QR code n'est pas disponible sur navigateur : l'écran affiche un
message explicite au lieu de planter.

Les interrupteurs SMS et appels sont désactivés sur le web, ces fonctions
n'existant que sur Android.
