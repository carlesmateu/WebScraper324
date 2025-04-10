"""
Mòdul d'utilitats: Funcions auxiliars per netejar text, parsejar dates i calcular atributs addicionals.
"""
import time
from datetime import datetime

# Diccionari per convertir l'índex del dia de la setmana (0 = dilluns, …)
DIES_SETMANA = {0: "Dilluns", 1: "Dimarts", 2: "Dimecres", 3: "Dijous", 4: "Divendres", 5: "Dissabte", 6: "Diumenge"}

def esperar(segons: float) -> None:
    """
    Posa en pausa l'execució durant el nombre de segons especificat.
    
    :param segons: Segons d'espera.
    """
    try:
        time.sleep(segons)
    except Exception as e:
        print(f"Advertència: pausa interrompuda - {e}")

def neteja_text(text: str) -> str:
    """
    Neteja el text eliminant espais innecessaris i salts de línia repetits.
    
    :param text: Text original.
    :return: Text netejat.
    """
    if not text:
        return ""
    text_net = text.strip()
    while "\n\n" in text_net:
        text_net = text_net.replace("\n\n", "\n")
    return text_net

def dia_setmana_desde_data(data_obj: datetime) -> str:
    """
    Retorna el nom del dia de la setmana a partir d'un objecte datetime.
    
    :param data_obj: Objecte datetime.
    :return: Nom del dia de la setmana 
    """
    if not data_obj:
        return ""
    dia_index = data_obj.weekday()  # 0 = dilluns
    return DIES_SETMANA.get(dia_index, "")
