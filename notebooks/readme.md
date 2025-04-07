# Connexion API
## Prérequis

* Un compte sur https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings est necessaire. Noter que pour un acces gratuit vous disposez que d'un mois.
* Ne pas se servir de  apps.sentinel-hub.com même si le tutoriel demande de le faire : Elle ne reconnais pas les clefs clients
* Se referer à la documentation officielle 

## Configuration

1.  Suivre la documentation https://docs.sentinel-hub.com/api/latest/
2.  Creer un compte sur https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings
3.  Obtenir un "OAuth clients" comme specifie dans la doc
4. Dans le dossier notebooks, créez un fichier .env
4.  Ouvrez le fichier `.env` avec un éditeur de texte et ajoutez les lignes suivantes, en remplaçant les valeurs par vos propres identifiants :

    ```
    Client_ID=votre-id-client
    Client_secret=votre-password-client
    ```

