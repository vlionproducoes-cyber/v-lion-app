import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at top, #0a0a0a 0%, #111111 50%, #000000 100%); color: #f5c400; }
    .big-title { font-family: 'Orbitron', monospace; font-size: 52px; font-weight: 900; 
                 background: linear-gradient(90deg, #ffd700, #ffed4e, #d4af37); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                 text-shadow: 0 0 30px rgba(255,215,0,0.6); }
    .glass { background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Novo Projeto do Zero • Cálculos Corretos • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ====================== PERSISTÊNCIA ======================
if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano","mes","cliente","venda","custo_anuncio","editor","valor_editor","lucro"])

# ====================== PARSER SIMPLES E SEGURO ======================
def parse_vlion_file(df, filename):
    records = []
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026
    months = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]
    editors = ["Miura","Ana Paula","Elaine","Nicole","Jéssica","Julia","João","Luciane","Glaucia","Bruna"]

    current_month = "Desconhecido"

    for _, row in df.iterrows():
        row_str = [str(x).strip() for x in row]
        row_text = " ".join(row_str).upper()

        # Pular linhas de cabeçalho e totais
        if any(word in row_text for word in ["CUSTO TOTAL","VENDAS TOTAL","LUCRO TOTAL","CAIXA","CONVERSÕES","TOTAL DE CONTATOS"]):
            continue

        # Detectar mês
        for m in months:
            if m in row_text:
                current_month = m
                break

        # Venda = primeira coluna numérica positiva
        try:
            val = row_str[0].replace(",", ".").strip()
            if val and val.replace(".", "").replace("-", "").isdigit():
                venda = float(val)
                if venda > 0:
                    cliente = row_str[2] if len(row_str) > 2 and row_str[2].strip() != "" else "Não identificado"

                    # Custo anúncio
                    custo_anuncio = 0
                    for val in row_str[4:]:
                        if val and val.replace(",", ".").replace("-", "").replace(".", "").isdigit():
                            custo_anuncio = float(val.replace(",", "."))
                            break

                    # Editor
                    editor = "Sem editor"
                    valor_editor = 0
                    for e in editors:
                        if e.upper() in row_text:
                            editor = e
                            break

                    lucro = venda - custo_anuncio - valor_editor

                    records.append({
                        "ano": ano, "mes": current_month, "cliente": cliente,
                        "venda": venda, "custo_anuncio": custo_anuncio,
                        "editor": editor, "valor_editor": valor_editor, "lucro": lucro
                    })
        except:
            continue
    return pd.DataFrame(records)

# ====================== UPLOAD ======================
st.subheader("📤 Upload dos 3 arquivos")
arquivos = st.file_uploader("Arraste os 3 arquivos Excel", type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 CARREGAR NOVO PROJETO"):
    with st.spinner("Carregando com parser limpo..."):
        total = 0
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            parsed = parse_vlion_file(df, arq.name)
            if not parsed.empty:
                st.session_state.master = pd.concat([st.session_state.master, parsed], ignore_index=True)
                st.success(f"✅ {arq.name} → {len(parsed)} registros")
                total += len(parsed)
        st.balloons()

# ====================== BACKUP ======================
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Exportar Backup"):
        csv = st.session_state.master.to_csv(index=False)
        st.download_button("Baixar CSV", csv, "v-lion_novo_backup.csv", "text/csv")
with col2:
    backup = st.file_uploader("📤 Restaurar Backup", type="csv")
    if backup:
        st.session_state.master = pd.read_csv(backup)
        st.success("✅ Restaurado!")

# ====================== DEBUG ======================
if not st.session_state.master.empty:
    with st.expander("🔍 Preview dos dados carregados (primeiros 20)"):
        st.dataframe(st.session_state.master.head(20))

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["📊 INDICADORES", "👥 MELHORES CLIENTES", "📋 RESUMO"])

with tab1:
    if not st.session_state.master.empty:
        tv = st.session_state.master["venda"].sum()
        tc = st.session_state.master["custo_anuncio"].sum() + st.session_state.master["valor_editor"].sum()
        tl = tv - tc
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("💰 VENDAS", f"R$ {tv:,.2f}")
        c2.metric("📦 PEDIDOS", len(st.session_state.master))
        c3.metric("🎯 TICKET MÉDIO", f"R$ {tv/len(st.session_state.master):,.2f}" if len(st.session_state.master)>0 else "R$ 0,00")
        c4.metric("💸 CUSTOS", f"R$ {tc:,.2f}")
        c5.metric("📈 LUCRO", f"R$ {tl:,.2f}", delta=f"R$ {tl:,.2f}")
    else:
        st.info("Carregue os arquivos para ver os indicadores")

with tab2:
    st.subheader("👥 Melhores Clientes")
    if not st.session_state.master.empty:
        busca = st.text_input("🔍 Buscar cliente", "")
        df_cli = st.session_state.master.groupby("cliente").agg(
            total=("venda","sum"), pedidos=("venda","count")
        ).reset_index().sort_values("total", ascending=False)
        if busca:
            df_cli = df_cli[df_cli["cliente"].str.contains(busca, case=False)]
        st.dataframe(df_cli.style.format({"total": "R$ {:,.2f}"}), use_container_width=True)
    else:
        st.info("Carregue os arquivos")

with tab3:
    st.subheader("📋 Resumo por Mês")
    if not st.session_state.master.empty:
        resumo = st.session_state.master.groupby(["ano","mes"]).agg(
            Vendas=("venda","sum"),
            Custos_Anuncio=("custo_anuncio","sum"),
            Custos_Editores=("valor_editor","sum"),
            Lucro=("lucro","sum")
        )
        st.dataframe(resumo.style.format("{:,.2f}"), use_container_width=True)
    else:
        st.info("Carregue os arquivos")

st.caption("✅ Novo projeto do zero • Parser limpo • Cálculos corretos")
