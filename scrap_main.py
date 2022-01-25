"""Scraping Main

Cette librairie a pour but d'automatiser le scraping de sites proposant des séjours itinérant basés sur la 
randonnée. Cette librairie est encore largement perfectible, elle est surtout adaptée -à l'heure actuelle- au 3 sites (decathlon,
explora, et terre d'avenir). Des améliorations sont à apporter. L'utilisateur doit savoir rechercher certains
éléments dans le code source de la page afin d'identifier les éléments. La maitrise des Xpath et des expressions
régulière est donc requise. 

"""

from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from dataclasses import dataclass
import time
import numpy as np
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException, StaleElementReferenceException 
from bs4 import BeautifulSoup as BS
from serde import serialize, deserialize
from serde.json import to_json, from_json
import re
from requests import get 

nav = webdriver.Chrome()

class PageElem:
    """Eléments permettant de récupérer sur un site les cellules correspondant à la liste des séjours 
    
    Exemple:
    >>> import scrap_main
    >>> elemedecat = scrap_main.PageElem(
    ...     nom_site= "Decathlon",
    ...     adresse = "https://www.decathlontravel.com/voyages/sport-rando-nature",
    ...     bouton_accept = '//*[@id="didomi-notice-agree-button"]',
    ...     bouton_affichage = '//*[@id="travel-search-engine-results"]/div[3]/a'
    ... )
    )
    >>> print(elemedecat)
    (site web = decathlon, 
    adresse = https://www.decathlontravel.com/voyages/sport-rando-nature, 
    xpath pour bouton cookies =  //*[@id="didomi-notice-agree-button"], 
    xpath pour affichage = //*[@id="travel-search-engine-results"]/div[3]/a)
    >>> elemedecat.open_site()
    >>> elemedecat.affichage_all_item()
    >>> cellsdecat = elemedecat.recup_cellule()
    >>> len(cellsdecat)
    134
    """
    def __init__(self, adresse:str, bouton_accept:str, bouton_affichage:str, nom_site:str):
        """initialise les éléments propre à un site"""
        self.nom_site = nom_site
        self.adresse = adresse
        self.bouton_accept = bouton_accept
        self.bouton_affichage = bouton_affichage

    def __repr__(self) -> str:
        """Renvoie la liste des éléments propres à un site"""
        return f"(site web={self.nom_site}, adresse = {self.adresse}, xpath pour bouton cookies =  {self.bouton_accept}, xpath pour affichage = {self.bouton_affichage})"

    def __str__(self) -> str:
        """Affiche les éléments par ligne"""
        return f"(site web = {self.nom_site}, \nadresse = {self.adresse}, \nxpath pour bouton cookies =  {self.bouton_accept}, \nxpath pour affichage = {self.bouton_affichage})"
    
    def __call__(self):
        """permet d'appeler une instance de classe"""
        return self

    def open_site(self):
        """ouverture de la page web"""   
        nav.get(self.adresse)
        time.sleep(10)
        if self.bouton_accept is not None:
            bouton = nav.find_element(By.XPATH, self.bouton_accept)
            bouton.click()

    def affichage_all_item(self):
        """affichage de toutes les cellules"""
        bouton = nav.find_element(By.XPATH, self.bouton_affichage)
        #compteur = 0
        while  bouton.is_displayed() and bouton.is_enabled():
            try:
                bouton.click()
            except (StaleElementReferenceException, WebDriverException, ElementClickInterceptedException):
                 print("Element is not clickable")
                 pass

    def recup_cellule(self)->list:
        """récupération des cellules dans une liste"""
        code = nav.page_source
        soupe = BS(code, "lxml")
        if "decathlon" in self.adresse:
            cells = soupe.find_all(name= "article")
        elif "explora" in self.adresse:
            cells = soupe.find_all(class_= "tablink-home-adventures w-inline-block w-tab-link")
        elif "terdav" in self.adresse:
            cells = soupe.find_all(name="article", attrs={"class":"circuit item"})
        return cells

@serialize
@deserialize
@dataclass
class Sejour:
    """Représente les donnée d'un séjour"""
    description : str
    prix : int
    lieux : str
    duree : int
    diff : str
    theme : str 

class CellElem:
    """récupère les items voulus dans une cellule à l'aide d'expression régulière
    
    Exemple:
    ...
    """
    def __init__(self, re_desc, re_prix, re_lieu, re_duree, re_diff, re_theme):
        self.re_desc = re_desc
        self.re_prix = re_prix
        self.re_lieu = re_lieu
        self.re_duree = re_duree
        self.re_diff = re_diff
        self.re_theme = re_theme

    def __call__(self):
        """permet d'appeler une instance de classe"""
        return self

    def __repr__(self) -> str:
        """Renvoie la liste des éléments propres à un site"""
        pass

    def catch_info(self, pageElem:PageElem)->list:
        """récupère les items d'un séjour"""
        # modification requises pour être fonctionnel
        results = list()
        cells = pageElem.recup_cellule()
        for cell in cells:
            texte = str(cell)
            texte.replace("&#231;", "ç").replace("&#224;", "à").replace("&#39", "'").replace("&#233;", "é")
            texte = texte.replace("\n", " ")
            motif = re.compile(self.re_desc)
            description = motif.findall(texte)[0]
            motif = re.compile(self.re_prix)
            prix = motif.findall(texte)[0]
            prix = int(prix.replace("\u202f",""))
            motif = re.compile(self.re_lieu)
            lieu = motif.findall(texte)[0]
            lieu = lieu.replace(" ", "")
            motif = re.compile(self.re_duree)
            duree = motif.findall(texte)[0]
            duree = int(duree)
            motif = re.compile(self.re_diff)
            diff = motif.findall(texte)[0]
            if pageElem.nom_site == "Explora1":
                    adresse="https://www.explora-project.com" + cell.attrs["href"]
                    full_page = get(adresse)
                    code = full_page.content.decode("utf8")
                    texte = str(code)
                    motif = re.compile("data-flag(.*?)div")
                    liste = motif.findall(texte)
                    theme = liste[-1][2:-2] 
            else:
                motif = re.compile(self.re_theme)
                theme = motif.findall(texte)[0]
            results.append(
                Sejour(
                    description,
                    prix,
                    lieu,
                    duree,
                    diff,
                    theme
                )
            )
        return results

    def save_sejours_to_Json(self,pageElem:PageElem):
        """sauvegarde de la liste des séjours au format JSON"""
        results = self.catch_info(pageElem)
        with open(f"backup_{pageElem.nom_site}.json", "w") as fichier:
            fichier.write(to_json(results))

def scraping(pageElem:PageElem, cellsElem:CellElem):
    """synthétise le processus de scraping dans une seule fonction destinée à l'utlisateur"""
    pageElem.open_site()
    pageElem.affichage_all_item()
    cellsElem.save_sejours_to_Json(pageElem)
    nav.quit()
            
            

    


    
    
