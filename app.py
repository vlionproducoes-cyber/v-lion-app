import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

# CSS 100% inspirado no seu Canva (glassmorphism + neon dourado + Orbitron)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at top, #0a0a0a 0%, #111111 50%, #000000 100%); color: #f5c400; }
    .big-title { font-family: 'Orbitron', monospace; font-size: 52px; font-weight: 900; 
                 background: linear-gradient(90deg, #ffd700, #ffed4e, #d4af37); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                 text-shadow: 0 0 30px rgba(255,215,0,0.6); }
    .glass { background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); 
             border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
    .neon-glow { box-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700; }
    .metric-card { background: rgba(10,10,10,0.85); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,215,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Dashboard Futurista • Leitura Completa • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano", "mes", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# ====================== PARSER FORTE (corrigido) ======================
def parse_vlion_file(df, filename):
    records = []
    current_month = "Desconhecido"
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026

    months_pt = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]

    for _, row in df.iterrows():
        # CONVERSÃO SEGURA - isso resolve o erro
        row_str = row.fillna("").astype(str).str.strip()
        row_text = " ".join(row_str).upper()

        # Detecta mês
        for m in months_pt:
            if m in row_text:
                current_month = m
                break

        # Detecta venda (coluna 0 com número positivo)
        try:
            val_str = row_str[0].replace(",", ".").strip()
            if val_str.replace(".", "").replace("-", "").isdigit():
                valor = float(val_str)
                if valor > 0:
                    cliente = row_str[2] if len(row_str) > 2 and row_str[2] != "" else "Cliente não identificado"
                    editor = "Sem editor"
                    for e in ["Miura", "Ana Paula", "Elaine", "Nicole", "Jéssica", "Julia", "João", "Luciane"]:
                        if e.upper() in row_text:
                            editor = e
                            break
                    records.append({
                        "ano": ano, "mes": current_month, "cliente": cliente,
                        "venda": valor, "custo_anuncio": 0, "editor": editor,
                        "valor_editor": 0, "lucro": valor
                    })
        except:
            continue  # ignora linhas problemáticas
    return pd.DataFrame(records)

# ====================== UPLOAD ======================
st.subheader("📤 Upload dos 3 arquivos Excel")
arquivos = st.file_uploader("Arraste V-Lion Produções 2024.xlsx, 2025.xlsx e 2026.xlsx", 
                           type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 CARREGAR TODAS AS PLANILHAS AGORA"):
    with st.spinner("Processando as 3 planilhas..."):
        total = 0
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            parsed = parse_vlion_file(df, arq.name)
            if not parsed.empty:
                st.session_state.master = pd.concat([st.session_state.master, parsed], ignore_index=True)
                st.success(f"✅ {arq.name} → **{len(parsed)} vendas** extraídas")
                total += len(parsed)
            else:
                st.warning(f"⚠️ {arq.name} não encontrou vendas")
        st.balloons()
        st.success(f"🎉 Total de {total} vendas carregadas com sucesso!")

# ====================== TABS (igual ao Canva) ======================
tab1, tab2, tab3 = st.tabs(["📊 INDICADORES", "👥 CLIENTES", "📋 RESUMO"])

with tab1:
    if not st.session_state.master.empty:
        tv = st.session_state.master["venda"].sum()
        te = st.session_state.master["valor_editor"].sum()
        tl = st.session_state.master["lucro"].sum()
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 VENDAS", f"R$ {tv:,.2f}")
        col2.metric("📦 PEDIDOS", len(st.session_state.master))
        col3.metric("🎯 TICKET MÉDIO", f"R$ {tv/len(st.session_state.master):,.2f}" if len(st.session_state.master)>0 else "R$ 0,00")
        col4.metric("💸 CUSTOS EDITORES", f"R$ {te:,.2f}")
        col5.metric("📈 LUCRO", f"R$ {tl:,.2f}", delta=f"R$ {tl:,.2f}")
    else:
        st.info("👆 Carregue as planilhas acima")

with tab2:
    st.subheader("👥 Clientes")
    if not st.session_state.master.empty:
        busca = st.text_input("🔍 Buscar cliente")
        df_cli = st.session_state.master.copy()
        if busca:
            df_cli = df_cli[df_cli["cliente"].str.contains(busca, case=False)]
        st.dataframe(df_cli[["cliente","venda","mes","ano"]], use_container_width=True)
    else:
        st.info("Nenhum cliente ainda")

with tab3:
    st.subheader("📋 Resumo por Mês")
    if not st.session_state.master.empty:
        resumo = st.session_state.master.groupby(["ano","mes"])["venda"].sum().unstack(fill_value=0)
        st.dataframe(resumo, use_container_width=True)
    else:
        st.info("Carregue as planilhas")

# Adicionar manual + download
st.subheader("➕ Adicionar nova venda")
with st.form("nova"):
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Cliente")
    venda = col2.number_input("Valor da venda R$", min_value=0.0, step=10.0)
    if st.form_submit_button("🚀 SALVAR"):
        nova = pd.DataFrame([{"ano": datetime.now().year, "mes": datetime.now().strftime("%B"), "cliente": cliente,
                              "venda": venda, "custo_anuncio": 0, "editor": "Manual", "valor_editor": 0, "lucro": venda}])
        st.session_state.master = pd.concat([st.session_state.master, nova], ignore_index=True)
        st.success("✅ Salvo!")

if not st.session_state.master.empty:
    st.download_button("📥 Baixar todos os dados", st.session_state.master.to_csv(index=False).encode(), "v-lion_dados.csv", "text/csv")

st.caption("✅ App V-Lion • Design igual ao Canva • Parser corrigido")
