import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("[ERRO] SUPABASE_URL ou SUPABASE_KEY nao configuradas no .env")
    sys.exit(1)

supabase: Client = create_client(url, key)

produtos_iniciais = [
    # Smartphones
    {
        "nome": "Apple iPhone 15 (128 GB) - Preto",
        "loja": "Mercado Livre",
        "preco_atual": 4899.00,
        "url_produto": "https://www.mercadolivre.com.br/apple-iphone-15-128-gb-preto/p/MLB28509355",
        "url_afiliado": "https://www.mercadolivre.com.br/apple-iphone-15-128-gb-preto/p/MLB28509355",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_754129-MLA71783300742_092023-F.webp"
    },
    {
        "nome": "Samsung Galaxy S24 Ultra 5G (512 GB) - Titânio Preto",
        "loja": "Mercado Livre",
        "preco_atual": 6499.00,
        "url_produto": "https://www.mercadolivre.com.br/samsung-galaxy-s24-ultra-5g-512gb/p/MLB31558231",
        "url_afiliado": "https://www.mercadolivre.com.br/samsung-galaxy-s24-ultra-5g-512gb/p/MLB31558231",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_844573-MLU74134954432_012024-F.webp"
    },
    {
        "nome": "Xiaomi Redmi Note 13 Pro 5G (256 GB) - Preto",
        "loja": "Mercado Livre",
        "preco_atual": 1899.00,
        "url_produto": "https://www.mercadolivre.com.br/xiaomi-redmi-note-13-pro-5g-256gb/p/MLB31522049",
        "url_afiliado": "https://www.mercadolivre.com.br/xiaomi-redmi-note-13-pro-5g-256gb/p/MLB31522049",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_914592-MLU74213898275_012024-F.webp"
    },
    # Smart TVs
    {
        "nome": "Smart TV 55\" Samsung 4K UHD Crystal QLED 55Q60D",
        "loja": "Mercado Livre",
        "preco_atual": 2799.00,
        "url_produto": "https://www.mercadolivre.com.br/smart-tv-55-samsung-qled-4k-55q60d/p/MLB34019231",
        "url_afiliado": "https://www.mercadolivre.com.br/smart-tv-55-samsung-qled-4k-55q60d/p/MLB34019231",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_795123-MLU75498102391_042024-F.webp"
    },
    {
        "nome": "Smart TV 65\" LG 4K UHD ThinQ AI 65UT8050",
        "loja": "Mercado Livre",
        "preco_atual": 3299.00,
        "url_produto": "https://www.mercadolivre.com.br/smart-tv-65-lg-4k-65ut8050/p/MLB34021042",
        "url_afiliado": "https://www.mercadolivre.com.br/smart-tv-65-lg-4k-65ut8050/p/MLB34021042",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_812301-MLU75901239102_042024-F.webp"
    },
    # Consoles & Video Games
    {
        "nome": "Console PlayStation 5 Edição Digital (Slim)",
        "loja": "Mercado Livre",
        "preco_atual": 3699.00,
        "url_produto": "https://www.mercadolivre.com.br/console-playstation-5-slim-edicao-digital/p/MLB30920491",
        "url_afiliado": "https://www.mercadolivre.com.br/console-playstation-5-slim-edicao-digital/p/MLB30920491",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_892301-MLU74910293041_032024-F.webp"
    },
    {
        "nome": "Console Nintendo Switch OLED 64GB - Edição Mario Red",
        "loja": "Mercado Livre",
        "preco_atual": 2199.00,
        "url_produto": "https://www.mercadolivre.com.br/nintendo-switch-oled-edicao-mario/p/MLB27591023",
        "url_afiliado": "https://www.mercadolivre.com.br/nintendo-switch-oled-edicao-mario/p/MLB27591023",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_612039-MLU71920391023_092023-F.webp"
    },
    {
        "nome": "Console Xbox Series X 1TB - Preto",
        "loja": "Mercado Livre",
        "preco_atual": 4299.00,
        "url_produto": "https://www.mercadolivre.com.br/console-xbox-series-x-1tb/p/MLB16182902",
        "url_afiliado": "https://www.mercadolivre.com.br/console-xbox-series-x-1tb/p/MLB16182902",
        "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_910239-MLA43912093012_112020-F.webp"
    }
]

def popular_banco():
    print("[INFO] Cadastrando catálogo inicial de Smartphones, TVs e Consoles no Supabase...")
    adicionados = 0
    for p in produtos_iniciais:
        try:
            supabase.table("produtos").insert(p).execute()
            adicionados += 1
            print(f"[OK] Cadastrado: {p['nome']} (R$ {p['preco_atual']})")
        except Exception as e:
            print(f"[ERRO] Falha ao cadastrar {p['nome']}: {e}")
            
    print(f"\n[SUCESSO] Total de {adicionados} produtos inseridos com sucesso no Supabase!")

if __name__ == "__main__":
    popular_banco()
