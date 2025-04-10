 # WebScraper324: Extracció de Notícies de 324.cat

Aquest repositori conté un script de web scraping desenvolupat en Python que permet extreure notícies del portal [324.cat](https://www.3cat.cat/324/). El codi està dissenyat per recórrer diferents seccions del lloc web, extreure dades com el títol, subtítol, autor, data de publicació, contingut i altres atributs derivats, i finalment exportar el resultat en un fitxer CSV per a una anàlisi posterior.

## Característiques

- **Extracció per seccions:** Navega per seccions com "Ultimes Notícies", "Societat", "Política", "Món", "Economia", "Cultura", "Anàlisi" i "Comarques".
- **Recollida d'informació:** Extreu informació rellevant de cada article, com el títol, subtítol, autor, data de publicació i contingut complet.
- **Neteja i processament de dades:** Calcula el nombre de paraules, caràcters i assigna el dia de la setmana a partir de la data de publicació.
- **Exportació en CSV:** Genera un fitxer CSV amb tot el dataset recollit al directori `dataset`.

## Estructura del projecte

- **main.py:** Script principal que coordina tot el procés de web scraping, des de la navegació per seccions fins a la generació del CSV.
- **scraper.py:** Conté les funcions per navegació, extreure enllaços d'articles i processar les pàgines amb Selenium i BeautifulSoup.
- **utils.py:** Inclou funcions auxiliars per a la neteja de text, parseig de dates i càlcul d'atributs addicionals.

## Requisits

El projecte utilitza els següents paquets:

- `selenium`
- `webdriver-manager`
- `pandas`
- `beautifulsoup4`

Per instal·lar tots els paquets necessaris, executeu:

```bash
pip install -r requirements.txt
