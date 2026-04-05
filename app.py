import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

# === DESIGN FUTURISTA / NEON ===
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0a0a0a, #1a1a2e); color: #f5c400; }
    .big-title { font-size: 52px; font-weight: bold; background: linear-gradient(90deg, #f5c400, #ffd700); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .neon { text-shadow: 0 0 10px #f5c400, 0 0 20px #f5c400; }
    .metric { background: rgba(245, 196, 0, 0.1); border-radius: 15px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Logo menor e bonita
st.image("logo.png", width=220)

st.markdown('<p class="big-title neon">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Dashboard Futurista • Editores • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Persistência
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["ano", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# Upload
st.subheader("📤 Upload dos arquivos Excel (2024, 2025, 2026)")
arquivos = st.file_uploader("Arraste os 3 arquivos aqui", type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 Processar arquivos agora"):
    with st.spinner("Processando seus arquivos..."):
        for arq in arquivos:
            try:
                df = pd.read_excel(arq, header=None)
                st.success(f"✅ {arq.name} carregado com {len(df)} linhas")
                # Exibe amostra para você ver que carregou
                st.dataframe(df.head(10), use_container_width=True)
            except:
                st.error(f"❌ Erro ao ler {arq.name}")
    st.balloons()

# Adicionar manual (futurista)
st.subheader("➕ Nova venda / edição")
col1, col2 = st.columns(2)
with st.form("form_nova"):
    cliente = col1.text_input("Cliente")
    valor_venda = col2.number_input("Valor da venda R$", min_value=0.0, step=10.0)
    custo_anuncio = col1.number_input("Custo anúncio R$", min_value=0.0, step=10.0)
    editor = col2.text_input("Editor (Miura, Ana Paula, Elaine...)")
    valor_editor = st.number_input("Valor pago ao editor R$", min_value=0.0, step=10.0)
    
    if st.form_submit_button("🚀 SALVAR NO SISTEMA"):
        lucro = valor_venda - custo_anuncio - valor_editor
        nova = pd.DataFrame([{
            "ano": datetime.now().year,
            "cliente": cliente,
            "venda": valor_venda,
            "custo_anuncio": custo_anuncio,
            "editor": editor or "Sem editor",
            "valor_editor": valor_editor,
            "lucro": lucro
        }])
        st.session_state.dados = pd.concat([st.session_state.dados, nova], ignore_index=True)
        st.success("✅ Salvo com sucesso!")

# Dashboard
st.subheader("📊 Resumo Futurista")
if not st.session_state.dados.empty:
    tv = st.session_state.dados["venda"].sum()
    te = st.session_state.dados["valor_editor"].sum()
    tl = st.session_state.dados["lucro"].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VENDAS TOTAIS", f"R$ {tv:,.2f}")
    c2.metric("CUSTO EDITORES", f"R$ {te:,.2f}")
    c3.metric("LUCRO TOTAL", f"R$ {tl:,.2f}", delta_color="normal")
    c4.metric("ROI", f"{(tv/(te+1)):.2f}x")
    
    st.subheader("🔥 Desempenho dos Editores")
    ed = st.session_state.dados.groupby("editor").agg(
        pago=("valor_editor","sum"), gerado=("venda","sum")
    ).round(2)
    ed["ROI"] = (ed["gerado"] / ed["pago"]).round(2)
    st.dataframe(ed, use_container_width=True)
else:
    st.info("Ainda não há dados. Faça upload ou adicione manualmente.")

# Download
if not st.session_state.dados.empty:
    csv = st.session_state.dados.to_csv(index=False).encode()
    st.download_button("📥 Baixar tudo em CSV", csv, "v-lion_dados.csv", "text/csv")

st.caption("App moderno e futurista feito para V-Lion Produções")
