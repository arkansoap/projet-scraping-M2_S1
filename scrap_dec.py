"""
Scraping main 
"""

from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from dataclasses import dataclass
import time
import numpy as np
from selenium.common.exceptions import WebDriverException 
from bs4 import BeautifulSoup as BS
from serde import serialize, deserialize
from serde.json import to_json, from_json

nav = webdriver.Chrome()

class PageElem:

    def __init__(self, adresse : str, bouton_accept : str, bouton_affichage : str):
        self.adresse = adresse
        self.bouton_accept = bouton_accept
        self.bouton_affichage = bouton_affichage

    def __repr__(self) -> str:
        pass

    def open_site(self):   
        nav.get(self.adresse)
        bouton = nav.find_element(By.XPATH, self.bouton_accept)
        bouton.click()

    def affichage_all_item(self):
        bouton = nav.find_element(By.XPATH, self.bouton_affichage)
        while bouton.is_displayed():
            try:
                bouton.click()
            except WebDriverException:
                print("Element is not clickable")

    def recup_cellule(self):
        code = nav.page_source
        soupe = BS(code, "lxml")
        cells = soupe.find_all( name= "article")
        # penser à génraliser pour les trois sites 
        return cells

@serialize
@deserialize
@dataclass
class Sejour:
    description : str
    prix : int
    lieux : str
    duree : int
    diff : str
    theme : str 

class CellElem_or_Re:

    def __init__(self, re_desc):
        self.re_desc = re_desc
        ...

    def catch_info():
        results = list()
        cells = ...
        for cell in cells:
            description = ...
            prix = ...
            lieu = ...
            duree = ...
            diff = ...
            theme = ...
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
            
            

    


    
    
