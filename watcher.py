import requests
import time
import os
from selectolax.parser import HTMLParser

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORD = "assioma"
SEEN_FILE = "seen_ads.txt"

# Charger les annonces déjà vues
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(f.read().splitlines())
else:
    seen = set()

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def scrape_leboncoin():
    url = f"https://www.leboncoin.fr/recherche?text={KEYWORD}&category=16"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = HTMLParser(r.text)
    ads = []
    for item in html.css("li[data-qa-id='aditem_container'] a"):
        title = item.text(strip=True)
        link = "https://www.leboncoin.fr" + item.attributes.get("href", "")
        ad_id = link.split("/")[-1]
        if ad_id not in seen and KEYWORD.lower() in title.lower():
            ads.append((ad_id, f"💥 Leboncoin: {title}\n{link}"))
    return ads

def scrape_trocvelo():
    url = f"https://www.troc-velo.com/annonces?searchtext={KEYWORD}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = HTMLParser(r.text)
    ads = []
    for item in html.css("li.annonce"):
        title_el = item.css_first("h2 a")
        price_el = item.css_first(".price")
        if not title_el:
            continue
        title = title_el.text(strip=True)
        link = "https://www.troc-velo.com" + title_el.attributes.get("href", "")
        ad_id = link.split("-")[-1]
        if ad_id not in seen and KEYWORD.lower() in title.lower():
            price = price_el.text(strip=True) if price_el else ""
            ads.append((ad_id, f"💥 Troc-Vélo: {title} {price}\n{link}"))
    return ads

if __name__ == "__main__":
    print("Bot vélo démarré 🚴")
    while True:
        try:
            annonces = scrape_leboncoin() + scrape_trocvelo()
            for ad_id, message in annonces:
                send_telegram(message)
                seen.add(ad_id)
            with open(SEEN_FILE, "w") as f:
                f.write("\n".join(seen))
        except Exception as e:
            print("Erreur:", e)
        time.sleep(60)
