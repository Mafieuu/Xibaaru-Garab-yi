## Activer l'environnement virtuel Conda 

doc : https://gist.github.com/atifraza/b1a92ae7c549dd011590209f188ed2a0
1. Se placer dans anaconda promp puis dans la racine du projet
2. Utilisez le fichier conda_env.yaml pour créer votre environnement conda : (l'autre env sera venv_env)

```bash
    conda env create -f conda_env.yaml
 ```
 Le nom de l'environnement qui sera créé sera hackaton_ensae_env
3. activez l\'environnement
```bash
    conda activate hackaton_ensae_env
```
4. configuration du kernel

```bash
    python -m ipykernel install --user --name hackaton_ensae_env --display-name "Python (hackaton_ensae)"
```
5. Lancer JupyterLab (ou Jupyter) et sélectionnez le kernel "Python (hackaton_ensae)"

---
pour exporter le conda_env.yaml :
```bash
conda env export --name hackaton_ensae_env --no-builds > conda_env.yml

Conda enregistre, par défaut, les numéros de build des packages (ex. ).En supprimant ces informations avec , le fichier est plus générique et portable : il permet à d'autres utilisateurs d'installer les mêmes packages sans être bloqués par une version spécifique de build.
les builds correspondent aux versions spécifiques des paquets qui tiennent compte de la manière dont ils ont été compilés pour une plateforme donnée. Chaque build peut inclure des optimisations et des dépendances spécifiques à l’architecture du système (Windows, macOS, Linux) ou à certaines configurations.
pour lancer jupyterlab depuis conda prompt : jupyter lab
```


    