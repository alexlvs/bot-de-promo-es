import requests
import time
import json
import logging
from config import TOKEN, CHAT_APROVACAO, GECKO_API_KEY

# ================= CONFIG =================

ARQUIVO_DB = "database.json"
INTERVALO = 600
MAX_RETRIES = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= DATABASE =================

def carregar_db():
    try:
        with open(ARQUIVO_DB, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()

def salvar_db(db):
    try:
        with open(ARQUIVO_DB, "w") as f:
            json.dump(list(db), f)
    except Exception as e:
        logging.error(f"Erro ao salvar DB: {e}")

postados = carregar_db()

# ================= HTTP =================

HEADERS = {"User-Agent": "Mozilla/5.0"}


# ================= GECKO API =================

def buscar_gecko(url_busca, target):

    url = "https://api.geckoapi.com.br/v1/extract"

    payload = {
        "url": url_busca,
        "target": target,
        "type": "plp"
    }

    headers = {
        "Authorization": f"Bearer {GECKO_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)

        if r.status_code != 200:
            print("STATUS:", r.status_code)
            print("RESPOSTA:", r.text)
            return []

        data = r.json()

        produtos = []

        
        items = data.get("data", {}).get("items", [])

        for item in items:
            nome = item.get("name")
            link = item.get("url")
            imagem = item.get("image")
           

            if nome and link:
                produtos.append({
                    "name": nome,
                    "link": link,
                    "imagem": imagem,

                  
                })

        print(f"{target} retornou {len(produtos)} produtos")
        return produtos

    except Exception as e:
        print("Erro:", e)
        return []

# ================= TELEGRAM =================

def enviar(produto):

    if produto["link"] in postados:
        return

    mensagem = f"""🔥 OFERTA

🛒 {produto['name']}

🔗 {produto['link']}"""

    try:

        # 🔥 SE TEM IMAGEM → ENVIA FOTO
        if produto.get("imagem"):

            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

            r = requests.post(url, data={
                "chat_id": CHAT_APROVACAO,
                "photo": produto["imagem"],
                "caption": mensagem
            }, timeout=15)

        else:
            # 🔥 FALLBACK → TEXTO
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

            r = requests.post(url, data={
                "chat_id": CHAT_APROVACAO,
                "text": mensagem
            }, timeout=10)

        if r.status_code == 200:
            logging.info(f"Enviado: {produto['name']}")
            postados.add(produto["link"])
            salvar_db(postados)
        else:
            logging.error(f"Erro Telegram: {r.text}")

    except Exception as e:
        logging.error(f"Erro envio: {e}")



# ================= BUSCA =================


def buscar_produtos():

    logging.info("🔎 Buscando produtos...")

    produtos = []


    produtos += buscar_gecko(
        "https://lista.mercadolivre.com.br/ofertas",
        "mercadolivre.com.br"
    )

 


    logging.info(f"Total final: {len(produtos)}")
    return produtos
import unicodedata


def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower()

def main():

    logging.info(" BOT INICIADO")

    while True:
        try:
            produtos = buscar_produtos()

            if not produtos:
                logging.warning("Nenhum produto encontrado")

            for produto in produtos[:10]:
                enviar(produto)
                time.sleep(2)

        except Exception as e:
            logging.critical(f"Erro geral: {e}")

        logging.info("⏳ Aguardando 10 minutos...\n")
        time.sleep(INTERVALO)

# ================= START =================

if __name__ == "__main__":
    main()