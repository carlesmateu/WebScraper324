"""
Script principal: Coordina tot el procés de web scraping des de la navegació per seccions 
fins a l'exportació del dataset CSV, processant totes les notícies sense restricció de data.
"""
import os
import logging
import csv
from datetime import datetime
import pandas as pd
import urllib.robotparser

import scraper, utils

# Definició de seccions del portal 324.cat
SECCIONS = {
    "Ultimes Notícies": "https://www.3cat.cat/324/",
    "Societat": "https://www.3cat.cat/324/societat/",
    "Política": "https://www.3cat.cat/324/politica/",
    "Món": "https://www.3cat.cat/324/mon/",
    "Economia": "https://www.3cat.cat/324/economia/",
    "Cultura": "https://www.3cat.cat/324/cultura/",
    "Anàlisi": "https://www.3cat.cat/324/analisi/",
    "Comarques": "https://www.3cat.cat/324/comarques/"
}

def comprova_robots_txt(base_url: str, user_agent: str) -> None:
    """
    Comprova el fitxer robots.txt del domini per assegurar que podem fer scraping.
    
    :param base_url: URL base del lloc.
    :param user_agent: User-Agent que utilitzem.
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url + "/robots.txt")
    try:
        rp.read()
        if not rp.can_fetch(user_agent, base_url + "/"):
            logging.warning("El fitxer robots.txt pot restringir l'accés amb el nostre User-Agent.")
    except Exception as e:
        logging.warning(f"No s'ha pogut llegir robots.txt: {e}")

def main():
    comprova_robots_txt("https://www.3cat.cat", scraper.CUSTOM_USER_AGENT)
    
    # Crear directori per al dataset si no existeix
    os.makedirs("dataset", exist_ok=True)
    output_csv_path = os.path.join("../dataset", "noticies_324.csv")
    
    # Inicialitzar el WebDriver
    driver = scraper.init_driver(headless=True)
    articles_data = []
    processed_urls = set()
    
    try:
        for seccio, url in SECCIONS.items():
            print(f"Processant secció: {seccio} - {url}")
            logging.info(f"Processant secció: {seccio}")
            article_links = scraper.get_article_links_from_section(driver, url)
            print(f"Articles trobats en la secció '{seccio}': {len(article_links)}")
            for link in article_links:
                if link in processed_urls:
                    continue
                print("Processant article: " + link)
                article_data = scraper.parse_article(driver, link)
                if not article_data:
                    print("No s'ha pogut extreure la informació de l'article.")
                    continue
                
                # No es fa cap filtratge per data; s'afegeix l'article tal com es troba.
                article_data["seccio"] = seccio
                # Intentem parsejar la data, però encara que falli, afegim l'article.
                data_pub = article_data.get("data_publicacio", "")
                try:
                    dt = datetime.strptime(data_pub, "%d/%m/%Y - %H.%M") if data_pub else None
                except Exception:
                    dt = None
                article_data["datetime"] = dt
                processed_urls.add(link)
                articles_data.append(article_data)
                print(f"Article afegit. Total processats fins ara: {len(articles_data)}")
                utils.esperar(0.5)
            utils.esperar(2.0)
    finally:
        driver.quit()
        logging.info("Tancat el WebDriver.")
        print("WebDriver tancat.")
    
    if not articles_data:
        logging.error("El dataset està buit. No s'han recopilat notícies.")
        print("Error: No s'han recopilat notícies.")
        return

    # Convertir les dades a DataFrame i afegir columnes derivades
    df = pd.DataFrame(articles_data)
    # Afegir dia de la setmana si la data està disponible (en cas contrari assigna una cadena buida)
    df['dia_setmana'] = df['datetime'].apply(lambda dt: utils.dia_setmana_desde_data(dt) if dt is not None else "")
    # Eliminar la columna 'datetime' per al CSV final si no es necessita
    df.drop(columns=["datetime"], inplace=True)
    # Reordenar columnes (mantenint la mateixa estructura)
    columnes = ["seccio", "titol", "subtitol", "autor", "autor_afiliacio", "data_publicacio", "dia_setmana", "num_paraules", "num_caracters", "text"]
    df = df.reindex(columns=columnes)
    
    df.to_csv(output_csv_path, index=False, encoding="utf-8")
    logging.info(f"Dataset CSV generat correctament: {output_csv_path} (Total: {len(df)} notícies)")
    print(f"Dataset CSV generat: {output_csv_path} (Total: {len(df)} notícies)")

if __name__ == "__main__":
    main()
