from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import logging
import time
import logging
import re
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup



CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebScraper324/1.0"

def init_driver(headless: bool = True) -> webdriver.Firefox:
    """
    Inicializa el WebDriver de Firefox con las opciones necesarias.
    
    :param headless: Si es True, se ejecuta en modo headless (sin interfaz gráfica).
    :return: Instancia configurada de WebDriver de Firefox.
    """
    options = FirefoxOptions()
    if headless:
        options.headless = True
    
    options.set_preference("general.useragent.override", CUSTOM_USER_AGENT)
    try:
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options
        )
    except Exception as e:
        logging.error(f"No se pudo iniciar el WebDriver de Firefox: {e}")
        raise
    driver.implicitly_wait(5)
    logging.info("WebDriver de Firefox iniciado correctamente.")
    return driver


BASE_URL = "https://www.3cat.cat/324"


CUSTOM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebScraper324/1.0"







def scroll_to_bottom(driver: webdriver.Chrome, pause: float = 1.0, max_scrolls: int = 100) -> None:
    """
    Desplaça la pàgina cap al peu de la pàgina repetidament per carregar el contingut dinàmic.
    
    :param driver: Instància activa del WebDriver.
    :param pause: Temps d'espera entre cada scroll.
    :param max_scrolls: Nombre màxim d'iteracions per evitar bucles infinits.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1
    logging.info(f"Scroll completat: {scrolls} iteracions.")

def get_article_links_from_section(driver: webdriver.Chrome, section_url: str) -> list:
    """
    Navega a la pàgina d'una secció i retorna una llista d'enllaços únics d'articles.
    
    :param driver: Instància del WebDriver.
    :param section_url: URL de la secció a extreure.
    :return: Llista d'enllaços d'articles.
    """
    logging.info(f"Carregant secció: {section_url}")
    try:
        driver.get(section_url)
    except Exception as e:
        logging.error(f"No s'ha pogut carregar la URL {section_url}: {e}")
        return []
    
    # Realitzar scroll per carregar tot el contingut
    scroll_to_bottom(driver, pause=1.5, max_scrolls=200)
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    
    article_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/324/' in href and 'noticia' in href:
            if href.startswith('/'):
                href = "https://www.3cat.cat" + href
            if href not in article_links:
                article_links.append(href)
    logging.info(f"{len(article_links)} articles trobats a {section_url}.")
    return article_links

def parse_article(driver: webdriver.Chrome, article_url: str) -> dict:
    """
    Accedeix a la pàgina d'un article i extreu les dades rellevants: titol, subtitol, data i contingut.
    
    :param driver: WebDriver actiu.
    :param article_url: URL de l'article.
    :return: Diccionari amb les dades extretes o None si falla.
    """
    logging.info(f"Extrayent article: {article_url}")
    try:
        driver.get(article_url)
    except Exception as e:
        logging.error(f"Error carregant l'article {article_url}: {e}")
        return None
    time.sleep(1)  # Espera per càrrega completa
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = {}
    try:
        # Títol: es busca en l'etiqueta <h1> o <h2>
        title_elem = soup.find('h1') or soup.find('h2')
        data['titol'] = title_elem.get_text().strip() if title_elem else ""
        # Subtítol: intentem buscar algun <h2> diferent o primer paràgraf significatiu
        subtitles = soup.find_all('h2')
        subtitol = ""
        if subtitles and len(subtitles) > 0:
            subtitol = subtitles[0].get_text().strip()
        data['subtitol'] = subtitol
       
        autor_elem = soup.find("span", class_=re.compile(r'author', re.I))
        data['autor'] = autor_elem.get_text().strip() if autor_elem else ""
        # Data de publicació: es busca un patró de data en text (ex: "dd/mm/YYYY - HH.MM")
        date_elem = soup.find(string=re.compile(r'\d{2}/\d{2}/\d{4} - \d{2}\.\d{2}'))
        date_text = date_elem.strip() if date_elem else ""
        original_date_text = date_text.split("Actualitzat")[0].strip() if date_text else ""
        data['data_publicacio'] = original_date_text
        try:
            data_dt = datetime.strptime(original_date_text, "%d/%m/%Y - %H.%M") if original_date_text else None
        except Exception as e:
            logging.warning(f"Problema al parsejar la data '{original_date_text}': {e}")
            data_dt = None
        data['datetime'] = data_dt
        # Contingut textual complet: concatenem tots els paràgrafs rellevants
        contingut = ""
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if not text:
                continue
            # Saltar textos no rellevants
            if text.lower().startswith("compartir") or "font:" in text.lower():
                continue
            contingut += text + "\n"
        contingut = contingut.strip()
        data['text'] = contingut
        # Calcular longitud: número de caràcters i paraules
        data['num_caracters'], data['num_paraules'] = len(contingut), len(contingut.split())
    except Exception as e:
        logging.error(f"Error parsejant l'article {article_url}: {e}")
        return None
    return data
