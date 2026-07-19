import os
import sys
import time
import requests
import cloudscraper
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY nao configuradas no .env")
    sys.exit(1)

supabase: Client = create_client(url, key)

def enviar_alerta_telegram(nome, preco_antigo, preco_novo, url_afiliado):
    """Envia um alerta automatico no Telegram quando o preco de um produto cai."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
        
    desconto_porcentagem = round(((preco_antigo - preco_novo) / preco_antigo) * 100, 1)
    
    mensagem = f"""🔥 *ALERTA DE QUEDA DE PREÇO!* 🔥

📉 *{nome}*
💰 *De:* R$ {preco_antigo:,.2f}
✅ *Por:* R$ {preco_novo:,.2f} (-{desconto_porcentagem}%)

🛒 *Compre com desconto:*
{url_afiliado}

🏃‍♂️ *Aproveite antes que o estoque acabe!*"""

    try:
        api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(api_url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem,
            "parse_mode": "Markdown"
        }, timeout=5)
        print(f"  [TELEGRAM] Alerta de queda enviado para '{nome}'!")
    except Exception as e:
        print(f"  [ERRO TELEGRAM] {e}")

def raspar_e_verificar_ofertas(url_ofertas="https://www.mercadolivre.com.br/ofertas"):
    print(f"\n[{time.strftime('%H:%M:%S')}] --- Lendo ofertas do Mercado Livre ---")
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url_ofertas)
    
    if response.status_code != 200:
        print(f"[ERRO] Status HTTP: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    itens = soup.select(".promotion-item, .promotions-item, div.promotion-item__container, .poly-card, li.ui-search-layout__item")
    if not itens:
        itens = [p.find_parent(['li', 'div', 'article']) for p in soup.select('.andes-money-amount__fraction') if p.find_parent(['li', 'div', 'article'])]
        
    itens_unicos = []
    seen = set()
    for item in itens:
        if item and id(item) not in seen:
            seen.add(id(item))
            itens_unicos.append(item)

    print(f"[INFO] Encontrei {len(itens_unicos)} itens na pagina de ofertas.")
    
    # Carrega produtos existentes do banco para comparacao rápida
    existentes = {}
    try:
        resp = supabase.table("produtos").select("*").execute()
        for p in resp.data:
            if p.get("url_produto"):
                existentes[p["url_produto"]] = p
    except Exception as e:
        print(f"[ERRO] Falha ao carregar banco: {e}")

    novos_inseridos = 0
    precos_atualizados = 0

    for item in itens_unicos:
        try:
            titulo_elem = item.select_one('.promotion-item__title, .poly-component__title, .ui-search-item__title, p.promotion-item__title, .promotion-item__description, h2, h3')
            nome = titulo_elem.text.strip() if titulo_elem else ""
            
            link_elem = item.select_one('a')
            url_prod = link_elem.get('href', '').split('#')[0] if link_elem else ""
            
            preco_elem = item.select_one('.andes-money-amount__fraction')
            preco = 0.0
            if preco_elem and preco_elem.text:
                try:
                    preco = float(preco_elem.text.replace('.', '').replace(',', '.').strip())
                except ValueError:
                    preco = 0.0
            
            img_elem = item.select_one('img')
            imagem_url = (img_elem.get('data-src') or img_elem.get('src') or "") if img_elem else ""

            if nome and url_prod and preco > 0:
                if url_prod in existentes:
                    prod_banco = existentes[url_prod]
                    preco_antigo = float(prod_banco.get("preco_atual", 0))
                    
                    # Queda de preco detectada!
                    if preco < preco_antigo and preco_antigo > 0:
                        print(f"[QUEDA DE PRECO] {nome}: R$ {preco_antigo} -> R$ {preco}")
                        supabase.table("produtos").update({"preco_atual": preco}).eq("id", prod_banco["id"]).execute()
                        precos_atualizados += 1
                        
                        # Dispara o alerta para o Telegram
                        enviar_alerta_telegram(nome, preco_antigo, preco, prod_banco.get("url_afiliado") or url_prod)
                    elif preco != preco_antigo:
                        # Preco subiu ou mudou
                        supabase.table("produtos").update({"preco_atual": preco}).eq("id", prod_banco["id"]).execute()
                        precos_atualizados += 1
                else:
                    # Novo produto! Inserir no banco
                    dados = {
                        "nome": nome,
                        "loja": "Mercado Livre",
                        "url_produto": url_prod,
                        "url_afiliado": url_prod,
                        "preco_atual": preco,
                        "imagem_url": imagem_url
                    }
                    supabase.table("produtos").insert(dados).execute()
                    novos_inseridos += 1
                    print(f"[NOVO OK] {nome[:45]}... (R$ {preco})")
                    
        except Exception:
            pass

    print(f"[FIM] {novos_inseridos} novos adicionados | {precos_atualizados} precos verificados/atualizados.")

if __name__ == "__main__":
    raspar_e_verificar_ofertas()
