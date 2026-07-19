import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    st.error("As variáveis de ambiente do Supabase não foram encontradas. Verifique seu arquivo .env.")
    st.stop()

supabase = create_client(url, key)

st.set_page_config(page_title="Painel Central - Malucão das Promoções", layout="wide", page_icon="🚨")

# ==========================================
# BARRA LATERAL: CADASTRO DE PRODUTOS
# ==========================================
st.sidebar.title("➕ Cadastrar Produtos")
with st.sidebar.form("form_cadastro_unico"):
    nome = st.text_input("Nome do Produto")
    loja = st.selectbox("Loja", ["Mercado Livre", "Amazon", "Kabum", "Shopee", "Magalu"])
    url_produto = st.text_input("Link do Produto")
    preco_inicial = st.number_input("Preço Atual (R$)", min_value=0.0, step=10.0)
    imagem_url = st.text_input("URL da Imagem (Opcional)")
    url_afiliado = st.text_input("Seu Link de Afiliado (Opcional)")
    
    botao_salvar = st.form_submit_button("💾 Salvar Produto")
    
    if botao_salvar:
        if nome and url_produto:
            dados = {
                "nome": nome,
                "loja": loja,
                "url_produto": url_produto,
                "preco_atual": preco_inicial,
                "imagem_url": imagem_url or "",
                "url_afiliado": url_afiliado or url_produto
            }
            try:
                supabase.table("produtos").insert(dados).execute()
                st.success("✅ Produto cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        else:
            st.warning("Preencha ao menos o Nome e o Link do Produto.")

# ==========================================
# CONTEÚDO PRINCIPAL
# ==========================================
st.title("🚨 Painel Central - Malucão das Promoções")
st.write("Monitore os preços dos produtos e gere os posts com links de afiliado em um clique.")

@st.cache_data(ttl=15)
def carregar_produtos():
    try:
        resposta = supabase.table("produtos").select("*").order("id", desc=True).execute()
        return resposta.data
    except Exception as e:
        st.error(f"Erro ao conectar com o Supabase: {e}")
        return []

produtos = carregar_produtos()

if not produtos:
    st.info("Nenhum produto cadastrado ainda. Use a barra lateral para cadastrar seu primeiro item!")
else:
    st.write(f"### 📦 Catálogo de Promoções ({len(produtos)} itens)")
    
    for prod in produtos:
        with st.container():
            col_img, col_info, col_acao = st.columns([1.5, 3.5, 3])
            
            with col_img:
                img_path = prod.get('imagem_url')
                if img_path and len(img_path) > 10:
                    st.image(img_path, use_container_width=True)
                else:
                    st.markdown("🖼️ *Sem imagem*")

            with col_info:
                st.markdown(f"#### {prod.get('nome')}")
                st.markdown(f"**Loja:** `{prod.get('loja')}`")
                st.markdown(f"**Preço Atual:** <h3 style='color:#00c853; margin:0;'>R$ {prod.get('preco_atual', 0):,.2f}</h3>", unsafe_allow_html=True)
                if prod.get('url_produto'):
                    st.markdown(f"[🔗 Abrir link da loja]({prod.get('url_produto')})")

            with col_acao:
                with st.expander("📱 Gerar Post para WhatsApp / Telegram", expanded=True):
                    link_final = prod.get('url_afiliado') or prod.get('url_produto') or '#'
                    texto_post = f"""🔥 *ALERTA DE PREÇO BAIXO!* 🔥

O preço caiu! 😱
📦 *{prod.get('nome')}*
💳 Por apenas: *R$ {prod.get('preco_atual', 0):,.2f}*

🛒 *Compre aqui antes que acabe:* 
{link_final}

🏃‍♂️ Corre que o estoque acaba rápido!
_Preço sujeito a alteração no site da loja._"""
                    
                    st.code(texto_post, language="")
            
            st.divider()