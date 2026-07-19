import os
import sys
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

# Garante suporte a caracteres UTF-8 no terminal Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Carrega as senhas do arquivo .env
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY nao configuradas no arquivo .env!")

supabase: Client = create_client(url, key) if url and key else None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

def pegar_preco_mercadolivre(url_produto):
    """Le uma pagina de um produto especifico do Mercado Livre e retorna o preco."""
    try:
        response = requests.get(url_produto, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tentativa 1: Meta tag de preco
        meta_preco = soup.find("meta", itemprop="price")
        if meta_preco and meta_preco.get("content"):
            try:
                return float(meta_preco["content"])
            except ValueError:
                pass

        # Tentativa 2: Seletor padrao
        preco_elemento = soup.find("span", class_="andes-money-amount__fraction")
        if preco_elemento:
            preco = float(preco_elemento.text.replace('.', '').replace(',', '.'))
            return preco
        return None
    except Exception as e:
        print(f"[ERRO] Erro ao ler pagina do produto: {e}")
        return None

def atualizar_precos():
    """Busca todos os produtos no banco e atualiza os precos um por um."""
    print("Buscando produtos no banco Supabase...")
    try:
        resposta = supabase.table("produtos").select("*").execute()
        produtos = resposta.data
    except Exception as e:
        print(f"[ERRO] Falha ao consultar Supabase: {e}")
        return

    if not produtos:
        print("[AVISO] Nenhum produto cadastrado no banco de dados do Supabase ainda.")
        print("[DICA] Para popular o banco automaticamente com uma pesquisa do Mercado Livre, use a funcao varrer_pagina_mercadolivre('URL_DA_BUSCA_DO_ML').")
        return

    print(f"[INFO] {len(produtos)} produto(s) encontrado(s).")
    for prod in produtos:
        loja = str(prod.get('loja', '')).lower()
        if 'mercado' in loja or 'ml' in loja:
            novo_preco = pegar_preco_mercadolivre(prod['url_produto'])
            
            if novo_preco:
                print(f"[OK] Atualizando {prod['nome']}: R$ {novo_preco}")
                supabase.table("produtos").update({"preco_atual": novo_preco}).eq("id", prod['id']).execute()
            else:
                print(f"[AVISO] Nao foi possivel obter novo preco para {prod.get('nome')}")
    
    print("Atualizacao concluida!")

def varrer_pagina_mercadolivre(url_pesquisa):
    """Le uma pagina inteira de resultados do Mercado Livre e cadastra todos no banco."""
    print(f"\n--- INICIANDO VARREDURA ---")
    print(f"Lendo URL: {url_pesquisa}")
    
    try:
        response = requests.get(url_pesquisa, headers=HEADERS, timeout=15)
        print(f"Status da resposta: {response.status_code}")
        if response.status_code != 200:
            print("[ERRO] O Mercado Livre bloqueou a conexao (Status diferente de 200).")
            return 0
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Suporta múltiplos layouts do Mercado Livre (ex: lista legada e cards novos poly-card)
        itens = soup.select("li.ui-search-layout__item, div.ui-search-result, div.poly-card, .ui-search-result__wrapper")
        if not itens:
            itens = soup.find_all("li", class_=lambda x: x and "search" in str(x))
            
        print(f"[INFO] Encontrei {len(itens)} itens na tela do HTML.")
        
        produtos_adicionados = 0
        
        for item in itens:
            try:
                titulo_elemento = item.select_one(".ui-search-item__title, .poly-component__title, h2, a.poly-component__title")
                nome = titulo_elemento.text.strip() if titulo_elemento else "Sem nome"
                
                link_elemento = item.select_one("a.ui-search-link, a.poly-component__title, a[href*='mercadolivre.com']")
                url_produto = link_elemento["href"] if link_elemento and "href" in link_elemento.attrs else ""
                
                preco_elemento = item.select_one(".andes-money-amount__fraction")
                preco = float(preco_elemento.text.replace('.', '').replace(',', '.')) if preco_elemento and preco_elemento.text else 0.0
                
                img_elemento = item.select_one("img")
                imagem_url = ""
                if img_elemento:
                    imagem_url = img_elemento.get("data-src") or img_elemento.get("src") or ""

                if url_produto and nome != "Sem nome" and preco > 0:
                    url_limpa = url_produto.split('#')[0]
                    
                    novo_dado = {
                        "nome": nome,
                        "loja": "Mercado Livre",
                        "url_produto": url_limpa,
                        "url_afiliado": url_limpa, 
                        "preco_atual": preco,
                        "imagem_url": imagem_url
                    }
                    
                    supabase.table("produtos").insert(novo_dado).execute()
                    produtos_adicionados += 1
                    print(f"[OK] Adicionado: {nome[:45]}... (R$ {preco})")
                    
            except Exception as e:
                print(f"[ERRO] Erro ao extrair item: {e}")
                
        print(f"--- FIM DA VARREDURA: {produtos_adicionados} PRODUTOS ADICIONADOS ---")
        return produtos_adicionados
        
    except Exception as e:
        print(f"[ERRO] Erro fatal ao tentar varrer a pagina principal: {e}")
        return 0

if __name__ == "__main__":
    urls_varredura = [
        "https://lista.mercadolivre.com.br/smartphone",
        "https://lista.mercadolivre.com.br/tv",
        "https://lista.mercadolivre.com.br/video-games"
    ]
    print("Iniciando varredura automatica de smartphones, tvs e video games...")
    total = 0
    for url_busca in urls_varredura:
        total += varrer_pagina_mercadolivre(url_busca)
    print(f"\n[SUCESSO] Varredura completa! Total de {total} produtos adicionados ao Supabase.")