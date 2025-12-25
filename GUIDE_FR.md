# Guide d'utilisation BouabidTransfer - Étape par étape

## Vue d'ensemble

BouabidTransfer est une application pour transférer des données de l'iPhone vers un ordinateur Windows avec une vitesse et une fiabilité maximales.

## Prérequis

- Windows 10 ou Windows 11
- iPhone (iPhone 6 ou plus récent)
- Câble USB
- Python 3.9 ou plus récent (déjà installé)

## Comment lancer l'application

### Étape 1: Lancer l'application

**Méthode 1: Double-clic**
- Ouvrez le dossier du projet
- Double-cliquez sur le fichier `RUN_APP.bat`
- L'application s'ouvrira automatiquement

**Méthode 2: Ligne de commande**
```bash
cd C:\Users\achra\Documents\dc\BouabidTransfer
python src/main.py
```

### Étape 2: Connecter l'iPhone

1. **Utilisez un câble USB**
   - Connectez l'iPhone à l'ordinateur avec un câble USB
   - Assurez-vous que le câble est bien branché

2. **Déverrouillez l'iPhone**
   - Déverrouillez l'iPhone
   - Assurez-vous que l'écran est allumé

3. **Faire confiance à l'ordinateur**
   - Lorsque le message "Trust This Computer?" apparaît sur l'iPhone
   - Appuyez sur **"Trust"** (Faire confiance)
   - Entrez le code d'accès si demandé
   - C'est une étape unique pour chaque ordinateur

### Étape 3: Sélectionner l'iPhone dans l'application

1. **Ouvrez BouabidTransfer**
   - L'iPhone devrait apparaître dans la liste "Connected Devices" (Appareils connectés)
   - S'il n'apparaît pas, cliquez sur le bouton **"Refresh"** (Actualiser)

2. **Sélectionnez l'iPhone**
   - Cliquez sur l'iPhone dans la liste
   - Le nom de l'iPhone s'affichera (par exemple "iPhone d'Ahmed")
   - Un message "Selected: [nom iPhone]" apparaîtra dans la barre d'état

### Étape 4: Ajouter les fichiers à transférer

**Ajouter des fichiers individuels:**
1. Cliquez sur le bouton **"Add Files"** (Ajouter des fichiers)
2. Parcourez et sélectionnez les fichiers de l'iPhone
3. Cliquez sur "OK" ou "Select"

**Ajouter un dossier:**
1. Cliquez sur le bouton **"Add Folder"** (Ajouter un dossier)
2. Sélectionnez un dossier de l'iPhone
3. Tous les fichiers de ce dossier seront ajoutés

**Note:** Actuellement, l'application nécessite une intégration complète avec l'appareil pour afficher les fichiers. Vous pouvez:
- Entrer manuellement les chemins des fichiers (si vous les connaissez)
- Ou attendre l'intégration complète avec l'appareil

### Étape 5: Choisir le dossier de destination

1. **Cliquez sur "Browse..."** à côté de "Destination"
2. **Sélectionnez un dossier** sur l'ordinateur où vous voulez sauvegarder les fichiers
   - Vous pouvez choisir:
     - Le dossier Documents
     - Le Bureau
     - Un disque dur USB externe
     - N'importe quel dossier
3. **Cliquez sur "Select Folder"** (Sélectionner le dossier)

### Étape 6: Démarrer le transfert

1. **Cliquez sur le bouton "Start Transfer"** (Démarrer le transfert)
2. **Surveillez la progression**
   - La barre de progression globale montre la progression totale
   - La progression des fichiers individuels montre chaque fichier
   - L'indicateur de vitesse montre la vitesse de transfert
   - ETA montre le temps restant estimé

### Étape 7: Attendre la fin

1. **Laissez le transfert se terminer**
   - Les fichiers sont vérifiés automatiquement
   - Un message "Transfer Complete" apparaîtra à la fin
2. **Vérifiez le dossier de destination**
   - Tous les fichiers devraient être là
   - L'intégrité des fichiers a été vérifiée

## Méthodes de connexion

### Méthode principale: USB uniquement

**Prérequis:**
- Câble USB uniquement
- Pas besoin de Wi-Fi

**Comment ça fonctionne:**
- Connexion directe via USB
- Le plus rapide et le plus fiable
- Fonctionne sans réseau

**Étapes:**
1. Connectez l'iPhone à l'ordinateur avec un câble USB
2. Déverrouillez l'iPhone et appuyez sur "Trust This Computer"
3. Ouvrez BouabidTransfer
4. L'iPhone apparaîtra dans la liste des appareils
5. Commencez le transfert!

### Méthode avancée: USB + Wi-Fi (vitesse maximale)

**Prérequis:**
- Câble USB
- iPhone et ordinateur sur le même réseau Wi-Fi

**Comment ça fonctionne:**
- USB pour la connexion principale
- Wi-Fi pour le transfert parallèle (vitesse supplémentaire)
- Les deux fonctionnent ensemble pour une vitesse maximale

**Étapes:**
1. Connectez l'iPhone à l'ordinateur via USB
2. Assurez-vous que l'iPhone et l'ordinateur sont sur le même réseau Wi-Fi
3. Appuyez sur "Trust This Computer" sur l'iPhone
4. Ouvrez BouabidTransfer
5. L'application utilisera USB + Wi-Fi ensemble
6. Commencez le transfert pour une vitesse maximale!

## Résolution des problèmes

### L'application ne démarre pas

**Problème:** Erreur lors de l'exécution de `python src/main.py`

**Solutions:**
1. Vérifiez que Python est installé:
   ```bash
   python --version
   ```
   Devrait afficher Python 3.9 ou plus récent

2. Installez les bibliothèques requises:
   ```bash
   pip install PyQt5 pyyaml colorlog psutil
   ```

3. Vérifiez que vous êtes dans le bon dossier:
   ```bash
   cd C:\Users\achra\Documents\dc\BouabidTransfer
   ```

### iPhone non détecté

**Problème:** L'iPhone n'apparaît pas dans la liste des appareils

**Solutions:**
1. **Vérifiez la connexion USB**
   - Assurez-vous que le câble est bien branché
   - Essayez un autre port USB
   - Essayez un autre câble USB

2. **Faire confiance à l'ordinateur**
   - Déverrouillez l'iPhone
   - Cherchez le message "Trust This Computer?"
   - Appuyez sur "Trust" et entrez le code d'accès

3. **Vérifiez les paramètres de l'iPhone**
   - Réglages → Général → À propos
   - Assurez-vous que Windows reconnaît l'iPhone

4. **Installez les pilotes iOS**
   - Windows devrait installer les pilotes automatiquement
   - Sinon, installez iTunes (inclut les pilotes)

5. **Cliquez sur le bouton Actualiser**
   - Dans BouabidTransfer, cliquez sur le bouton "Refresh"
   - Attendez quelques secondes pour la détection

### Échec du transfert

**Problème:** Le transfert s'arrête ou échoue

**Solutions:**
1. **Vérifiez l'espace de stockage**
   - Assurez-vous que le disque de destination a suffisamment d'espace
   - Libérez de l'espace si nécessaire

2. **Vérifiez la connexion**
   - Assurez-vous que l'iPhone reste connecté
   - Ne débranchez pas le câble pendant le transfert

3. **Réessayez**
   - Cliquez sur "Cancel" si le transfert est bloqué
   - Cliquez sur "Start Transfer" à nouveau
   - L'application peut reprendre les transferts interrompus

4. **Vérifiez les journaux**
   - Regardez dans le fichier `logs/bouabidtransfer.log`
   - Affiche des informations d'erreur détaillées

## Résumé rapide

1. **Lancez l'application** → Double-cliquez sur `RUN_APP.bat`
2. **Connectez l'iPhone** → Utilisez un câble USB
3. **Faites confiance à l'ordinateur** → Appuyez sur "Trust" sur l'iPhone
4. **Sélectionnez l'iPhone** → Dans la liste des appareils
5. **Ajoutez les fichiers** → Sélectionnez les fichiers à transférer
6. **Choisissez la destination** → Sélectionnez le dossier de sauvegarde
7. **Démarrez le transfert** → Cliquez sur "Start Transfer"
8. **Attendez** → Laissez le transfert se terminer

## Conseils importants

- ✅ Utilisez un câble USB de haute qualité pour une vitesse maximale
- ✅ Assurez-vous que l'iPhone reste déverrouillé pendant le transfert
- ✅ Ne débranchez pas le câble pendant le transfert
- ✅ Vérifiez l'espace de stockage avant de commencer
- ✅ Utilisez Wi-Fi pour une vitesse supplémentaire (optionnel)

## Support

Si vous rencontrez des problèmes:
1. Vérifiez les journaux dans `logs/bouabidtransfer.log`
2. Lisez les autres documentations
3. Vérifiez les messages d'erreur (faciles à comprendre)
4. Consultez la section Résolution des problèmes ci-dessus

---

**Bonne chance pour transférer vos données! 🚀**


