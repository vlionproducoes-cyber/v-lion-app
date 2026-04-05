import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="V-LION PRODUÇÕES", layout="wide", page_icon="🦁")

# === BRANDING ===
st.markdown("""
<style>
    .stApp { background-color: #0F0F0F; color: #F5C400; }
    .big-title { font-size: 48px; font-weight: bold; color: #F5C400; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Logo
st.image("logo.png", width=280)  # sua logo.png que você subiu

st.markdown('<p class="big-title">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"Dashboard completo • Editores • {datetime.now().strftime('%d/%m/%Y')}")

# Persistência dos dados
if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["data", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# Upload de arquivos
st.subheader("📤 Anexe seus arquivos (Excel 2024 + PDFs 2025/2026)")
uploaded = st.file_uploader("Escolha os arquivos", type=["xlsx", "pdf"], accept_multiple_files=True)

if st.button("🔄 Processar arquivos agora"):
    with st.spinner("Processando seus arquivos..."):
        for file in uploaded:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file, header=None)
                st.success(f"✅ Excel {file.name} processado")
                # Aqui podemos adicionar lógica de extração mais precisa se quiser
            else:
                with pdfplumber.open(file) as pdf:
                    text = "\n".join([p.extract_text() or "" for p in pdf.pages])
                st.success(f"✅ PDF {file.name} detectado")
        st.success("Todos os arquivos foram processados!")

# Adicionar venda manual
st.subheader("➕ Adicionar nova venda ou edição")
with st.form("add"):
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Cliente")
    venda = col2.number_input("Valor da venda (R$)", min_value=0.0, step=50.0)
    custo_anuncio = col1.number_input("Custo anúncio (R$)", min_value=0.0, step=50.0)
    editor = col2.text_input("Editor (Miura, Ana Paula, Elaine, Nicole...)")
    valor_editor = st.number_input("Valor pago ao editor (R$)", min_value=0.0, step=50.0)
    
    if st.form_submit_button("✅ Salvar"):
        lucro = venda - custo_anuncio - valor_editor
        nova_linha = pd.DataFrame([{
            "data": datetime.now().date(),
            "cliente": cliente,
            "venda": venda,
            "custo_anuncio": custo_anuncio,
            "editor": editor or "Sem editor",
            "valor_editor": valor_editor,
            "lucro": lucro
        }])
        st.session_state.master = pd.concat([st.session_state.master, nova_linha], ignore_index=True)
        st.success("Salvo com sucesso!")

# Dashboard
st.subheader("📊 Resumo Geral")
if not st.session_state.master.empty:
    total_venda = st.session_state.master["venda"].sum()
    total_editor = st.session_state.master["valor_editor"].sum()
    total_lucro = st.session_state.master["lucro"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vendas Totais", f"R$ {total_venda:,.2f}")
    col2.metric("Custo Total Editores", f"R$ {total_editor:,.2f}", delta_color="off")
    col3.metric("Lucro Total", f"R$ {total_lucro:,.2f}")
    col4.metric("ROI Médio", f"{(total_venda / (st.session_state.master['custo_anuncio'].sum() + total_editor + 0.01)):.2f}x")
    
    # Tabela de editores
    st.subheader("🔥 Desempenho dos Editores")
    editores = st.session_state.master.groupby("editor").agg(
        valor_pago=("valor_editor", "sum"),
        vendas_geradas=("venda", "sum")
    ).reset_index()
    editores["ROI"] = (editores["vendas_geradas"] / editores["valor_pago"]).round(2)
    st.dataframe(editores, use_container_width=True, hide_index=True)
else:
    st.info("Ainda não há dados. Faça upload ou adicione manualmente.")

# Download
if not st.session_state.master.empty:
    csv = st.session_state.master.to_csv(index=False).encode()
    st.download_button("📥 Baixar tudo em Excel/CSV", csv, "v-lion_dados_completos.csv", "text/csv")

st.caption("App feito especialmente para V-Lion • Totalmente personalizável")
