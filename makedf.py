"""build dataframe
Construction du dataframe à partir des backups de séjours en JSON
"""

from serde import se, serialize, deserialize
from serde.json import to_json, from_json
import pandas as pd
from scrap_main import Sejour, PageElem, CellElem
from dataclasses import dataclass

liste_backup = ["backup_Decathlon.json", "backup_Explora1.json", "backup_Terdav1.json", "backup_terdav2.json"]
# voir si on peut récup les fichier JSON du dossier ds une liste directement 
# pour ne pas avoir à changer la liste manuellement
region = ["auvergne", "rhone", "alpes", "pyrénées", "massif central", "sud-ouest", "provence", "bourogne", "bretagne", "normandie", "loire", "france", "occitanie", "normandes", "autres régions"]
pays_proche = ["madère", "maroc", "italie", "catalogne", "espagne", "grèce", "suisse", "ecosse", "irlande", "corse"]
# idem , j'ai plusieurs pistes pour ne pas avoir à créer ces listes manuellement

def assemblage_liste_sejour():
    """assemble les backup de séjours en une unique liste"""
    liste_sejours = list()
    for backup in liste_backup:
        with open(backup, "r") as fichier:
            data = fichier.read()
        sejours = from_json(list[Sejour], data)
        for sejour in sejours:
            liste_sejours.append(sejour)
    return liste_sejours

@dataclass
class Df:
    """construction du dataframe"""
    columns = ['description', 'prix', 'lieux', 'duree', 'diff', 'theme']
    df = pd.DataFrame(data=assemblage_liste_sejour(), columns= columns)

    def _make_lower(self):
        """Transforme tous les contenus en minuscule"""
        self.df["theme"] = self.df["theme"].str.lower()
        self.df["description"] = self.df["description"].str.lower()
        self.df["lieux"] = self.df["lieux"].str.lower()

    def _theme_with_desc(self):
        """Utilise la description pour trouver les bonnes modalités des variables catégorielles"""
        for i in range(0, len(self.df)):
            if "ski" in self.df.iloc[i]["description"]:
                self.df.loc[i,"theme"] = "activités nordique"
        # possibilité d'en rajouter

    def _level_diff(self):
        """redéfinit les modalités de la variable diff"""
        self.df.loc[(self.df["diff"] =='1')|(self.df["diff"] =='2')|(self.df["diff"] =="niveau 1"), "diff"] = "Découverte"
        self.df.loc[(self.df["diff"] =='3')|(self.df["diff"] =="niveau 2"), "diff"] = "Initié"
        self.df.loc[(self.df["diff"] =='4')|(self.df["diff"] =='5')|(self.df["diff"] == "niveau 3")|(self.df["diff"] == "niveau 4"), "diff"] = "Confirmé"

    def _level_theme(self):
        """redéfinit les modalités de la variable theme"""
        self.df.loc[(self.df["theme"] =="randonnée")|(self.df["theme"] =="trek")|(self.df["theme"] =="auberge")|(self.df["theme"] =="hôtel")|(self.df["theme"] =="refuge")|(self.df["theme"] =="découverte"), "theme"] = "rando nature"
        self.df.loc[(self.df["theme"] == "vélo")|(self.df["theme"] == "vtt")|(self.df["theme"] == "vélo de route"), "theme"] = "cyclo"
        self.df.loc[(self.df["theme"] == "randonnée avec âne")|(self.df["theme"] == "chiens de traîneau")|(self.df["theme"] == "cani rando"), "theme"] = "ani-rando"
        self.df.loc[(self.df["theme"] =="raquettes à neige")|(self.df["theme"] =="ski de randonnée")|(self.df["theme"] =="ski nordique")|(self.df["theme"] =="chalet")|(self.df["theme"] =="alpinisme")|(self.df["theme"] =="cascade de glace")|(self.df["theme"] =="raquette")|(self.df["theme"] =="logement privé"), "theme"] = "activités nordique"
        for i in range(0, len(self.df)):
            if "rando nature" not in self.df.iloc[i]["theme"] and "cyclo" not in self.df.iloc[i]["theme"] and "activités nordique" not in self.df.iloc[i]["theme"] and "multi-activités" not in self.df.iloc[i]["theme"] and "ani-rando" not in self.df.iloc[i]["theme"]: 
                self.df.loc[i,"theme"] = "multi-activités"

    def _level_lieu(self):
        """redéfinit les modalités de la variable theme"""
        for i in range(0, len(self.df)):
            for str in region:
                if str in self.df.loc[i,"lieux"]:
                    self.df.loc[i, "lieux"] = "metropole"
            for str in pays_proche:
                if str in self.df.loc[i, "lieux"]:
                    self.df.loc[i, "lieux"] = "dest_proche"
        for i in range(0, len(self.df)):
            if self.df.loc[i, "lieux"] != "metropole" and self.df.loc[i, "lieux"] != "dest_proche" and self.df.loc[i, "lieux"] != "" :
                self.df.loc[i, "lieux"] = "dest_éloignée"

    def _nettoyage(self):
        """nettoyage du dataframe"""
        self.df.drop(self.df[self.df["prix"]==0].index, axis = 0, inplace=True)
        self.df.drop(self.df[self.df["lieux"]==""].index, axis = 0, inplace=True)
        self.df = self.df.reset_index(drop=True)

    def _transfo_var(self):
        """transformation des variables de types object à category"""
        self.df["lieux"] = self.df["lieux"].astype("category")
        self.df["diff"] = self.df["diff"].astype("category")
        self.df["theme"] = self.df["theme"].astype("category")

    def _save_dataframe(self):
        "sauvegarde du dataframe en format pkl"
        self.df.to_pickle("my_dataframe.pkl")

    def all_in_one(self):
        """fonction pour l'utilisateur qui réalise toutes les actions nécessaire sur le dataframe"""
        self._make_lower()
        self._theme_with_desc()
        self._level_diff()
        self._level_lieu()
        self._level_theme()
        self._nettoyage()
        self._transfo_var()
        self._save_dataframe()
