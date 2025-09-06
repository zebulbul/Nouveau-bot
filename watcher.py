import os
import time
import requests
from selectolax.parser import HTMLParser
import httpx

# ⚠️ Récupération directe depuis les variables d'environnement Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("Il manque TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID dans les variables d'environnement !")

# Fonction pour envoyer un message sur Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=data)
        if r.status_code != 200:
            print("Erreur Telegram :", r.text)
    except Exception as e:
        print("Erreur lors de l'envoi Telegram :", e)

# Envoi d'un message de démarrage
send_telegram_message("🚴 Bot vélo démarré et en ligne !")

# Liste pour mémoriser les annonces déjà vues
seen_ads = set()

# Fonction pour scraper Leboncoin
def scrape_leboncoin():
    url = "https://www.leboncoin.fr/recherche"
    params = {"text": "assioma", "category": "2"}  # Ajuste la catégorie si besoin
    try:
        response = httpx.get(url, params=params, timeout=10)
        html = HTMLParser(response.text)
        ads = html.css("a[data-qa-id='aditem-container']")
        for ad in ads:
            link = ad.attributes.get("href")
            if link and link not in seen_ads:
                seen_ads.add(link)
                send_telegram_message(f"Nouvelle annonce Leboncoin : {link}")
    except Exception as e:
        print("Erreur Leboncoin :", e)

# Fonction pour scraper Troc-Vélo
def scrape_trocvelo():
    url = "https://www.troc-velo.com/recherche.php"
    params = {"recherche": "assioma"}
    try:
        response = httpx.get(url, params=params, timeout=10)
        html = HTMLParser(response.text)
        ads = html.css("div.listing_item a")
        for ad in ads:
            link = ad.attributes.get("href")
            if link and link not in seen_ads:
                seen_ads.add(link)
                send_telegram_message(f"Nouvelle annonce Troc-Vélo : {link}")
    except Exception as e:
        print("Erreur Troc-Vélo :", e)

# Boucle principale
while True:
    scrape_leboncoin()
    scrape_trocvelo()
    time.sleep(60)  # Scraping toutes les 60 secondes
