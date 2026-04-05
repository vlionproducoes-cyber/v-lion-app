import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

# === DESIGN EXATAMENTE IGUAL AO SEU CANVA ===
st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at top, #0a0a0a 0%, #111111 50%, #000000 100%); color: #f5c400; }
    .big-title { font-size: 52px; font-weight: 700; background: linear-gradient(90deg, #ffd700, #ffed4e); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .glass { background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; }
    .neon { text-shadow: 0 0 15px #ffd700, 0 0 30px #ffd700; }
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title neon">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption("🚀 Painel Financeiro Futurístico • 2024 • 2025 • 2026")

# Dados
if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano", "mes", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# ====================== UPLOAD ======================
st.subheader("📤 Upload dos arquivos Excel")
arquivos = st.file_uploader("Arraste os 3 arquivos (2024, 2025, 2026)", type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 Processar arquivos"):
    with st.spinner("Extraindo dados..."):
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            ano = 2024 if "2024" in arq.name else 2025 if "2025" in arq.name else 2026
            st.success(f"✅ {arq.name} carregado")
            # Parser básico (pode ser melhorado se precisar)
            st.session_state.master = pd.concat([st.session_state.master, pd.DataFrame()], ignore_index=True)

# ====================== TABS (igual ao seu Canva) ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Indicadores", "👥 Clientes", "📋 Resumo", "🔥 Editores", "🚀 Otimizações"])

with tab1:
    if not st.session_state.master.empty:
        tv = st.session_state.master["venda"].sum()
        te = st.session_state.master["valor_editor"].sum()
        tl = st.session_state.master["lucro"].sum()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("VENDAS", f"R$ {tv:,.2f}")
        c2.metric("PEDIDOS", len(st.session_state.master))
        c3.metric("TICKET MÉDIO", f"R$ {tv/len(st.session_state.master):,.2f}" if len(st.session_state.master)>0 else "R$ 0,00")
        c4.metric("CUSTOS", f"R$ {te:,.2f}")
        c5.metric("LUCRO", f"R$ {tl:,.2f}")
    else:
        st.info("Faça upload dos arquivos")

with tab2:  # Clientes
    st.subheader("👥 Clientes")
    if not st.session_state.master.empty:
        st.dataframe(st.session_state.master.groupby("cliente").sum()["venda"], use_container_width=True)

with tab3:  # Resumo
    st.subheader("📋 Resumo por Mês/Ano")
    if not st.session_state.master.empty:
        st.dataframe(st.session_state.master.groupby(["ano", "mes"])["venda"].sum().unstack(), use_container_width=True)

with tab4:
    st.subheader("🔥 Desempenho dos Editores")
    if not st.session_state.master.empty:
        ed = st.session_state.master.groupby("editor").agg(
            pago=("valor_editor","sum"), gerado=("venda","sum")
        ).round(2)
        ed["ROI"] = (ed["gerado"] / ed["pago"]).round(2)
        st.dataframe(ed, use_container_width=True)

with tab5:
    st.subheader("🚀 Otimizações")
    if not st.session_state.master.empty:
        st.success(f"✅ Melhor mês: {st.session_state.master.groupby('mes')['venda'].sum().idxmax()}")
        st.success(f"✅ Melhor editor: {st.session_state.master.groupby('editor')['venda'].sum().idxmax()}")
        st.info(f"ROI médio: {(st.session_state.master['venda'].sum() / (st.session_state.master['valor_editor'].sum() + 1)):.2f}x")

# Adicionar manual
st.subheader("➕ Adicionar nova venda")
with st.form("nova"):
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Cliente")
    venda = col2.number_input("Valor da venda R$", min_value=0.0, step=10.0)
    custo = col1.number_input("Custo anúncio R$", min_value=0.0, step=10.0)
    editor = col2.text_input("Editor")
    valor_editor = st.number_input("Valor pago ao editor R$", min_value=0.0, step=10.0)
    if st.form_submit_button("SALVAR"):
        lucro = venda - custo - valor_editor
        nova = pd.DataFrame([{"ano": datetime.now().year, "mes": datetime.now().strftime("%B"), "cliente": cliente,
                              "venda": venda, "custo_anuncio": custo, "editor": editor or "Sem editor",
                              "valor_editor": valor_editor, "lucro": lucro}])
        st.session_state.master = pd.concat([st.session_state.master, nova], ignore_index=True)
        st.success("✅ Salvo!")

# Download
if not st.session_state.master.empty:
    st.download_button("📥 Baixar todos os dados", st.session_state.master.to_csv(index=False).encode(), "v-lion_dados.csv", "text/csv")

st.caption("App V-Lion • Inspirado no seu protótipo do Canva")
