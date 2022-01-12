"""build dataframe
Construction du dataframe à partir des backups de séjours en JSON
"""

from serde import se, serialize, deserialize
from serde.json import to_json, from_json
import pandas as pd
from scrap_main import Sejour, PageElem, CellElem


liste_backup = ["backup_decathlon.json", "backup_explora.json", "backup_terdav.json", "backup_terdav2.json"]
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

def build_df():
    """construction du dataframe"""
    columns = ['description', 'prix', 'lieux', 'duree', 'diff', 'theme']
    df = pd.DataFrame(data=assemblage_liste_sejour(), columns= columns)
    return df 

def make_lower(df):
    df["theme"] = df["theme"].str.lower()
    df["description"] = df["description"].str.lower()
    df["lieux"] = df["lieux"].str.lower()

def theme_with_desc(df):
    for i in range(0, len(df)):
        if "ski" in df.iloc[i]["description"]:
            df.loc[i,"theme"] = "activités nordique"
    # possibilité d'en rajouter

def level_diff(df):
    df.loc[(df["diff"] ==1)|(df["diff"] ==2)|(df["diff"] =="niveau 1"), "diff"] = "Découverte"
    df.loc[(df["diff"] ==3)|(df["diff"] =="niveau 2"), "diff"] = "Initié"
    df.loc[(df["diff"] ==4)|(df["diff"] ==5)|(df["diff"] == "niveau 3")|(df["diff"] == "niveau 4"), "diff"] = "Confirmé"

def level_theme(df):
    df.loc[(df["theme"] =="randonnée")|(df["theme"] =="trek")|(df["theme"] =="auberge")|(df["theme"] =="hôtel")|(df["theme"] =="refuge")|(df["theme"] =="découverte"), "theme"] = "rando nature"
    df.loc[(df["theme"] == "vélo")|(df["theme"] == "vtt")|(df["theme"] == "vélo de route"), "theme"] = "cyclo"
    df.loc[(df["theme"] == "randonnée avec âne")|(df["theme"] == "chiens de traîneau")|(df["theme"] == "cani rando"), "theme"] = "ani-rando"
    df.loc[(df["theme"] =="raquettes à neige")|(df["theme"] =="ski de randonnée")|(df["theme"] =="ski nordique")|(df["theme"] =="chalet")|(df["theme"] =="alpinisme")|(df["theme"] =="cascade de glace")|(df["theme"] =="raquette")|(df["theme"] =="logement privé"), "theme"] = "activités nordique"
    for i in range(0, len(df)):
        if "rando nature" not in df.iloc[i]["theme"] and "cyclo" not in df.iloc[i]["theme"] and "activités nordique" not in df.iloc[i]["theme"] and "multi-activités" not in df.iloc[i]["theme"] and "ani-rando" not in df.iloc[i]["theme"]: 
            df.loc[i,"theme"] = "multi-activités"

def level_lieu(df):
    for i in range(0, len(df)):
        for str in region:
            if str in df.loc[i,"lieux"]:
                df.loc[i, "lieux"] = "metropole"
        for str in pays_proche:
            if str in df.loc[i, "lieux"]:
                df.loc[i, "lieux"] = "dest_proche"
    for i in range(0, len(df)):
        if df.loc[i, "lieux"] != "metropole" and df.loc[i, "lieux"] != "dest_proche" and df.loc[i, "lieux"] != "" :
            df.loc[i, "lieux"] = "dest_éloignée"

def nettoyage(df):
    df.drop(df[df["prix"]==0].index, axis = 0, inplace=True)
    df.drop(df[df["lieux"]==""].index, axis = 0, inplace=True)
    df = df.reset_index(drop=True)

def transfo_var(df):
    df["lieux"] = df["lieux"].astype("category")
    df["diff"] = df["diff"].astype("category")
    df["theme"] = df["theme"].astype("category")

def save_dataframe(df):
    df.to_pickle("my_df.pkl")


