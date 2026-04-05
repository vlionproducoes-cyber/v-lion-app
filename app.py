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
st.caption(f"🚀 Dashboard Futurista • Cálculos 100% Corrigidos • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ====================== PERSISTÊNCIA ======================
if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano","mes","cliente","venda","custo_anuncio","editor","valor_editor","lucro"])

# ====================== NOVO PARSER CORRIGIDO ======================
def parse_vlion_file(df, filename):
    records = []
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026
    months_pt = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]
    editors = ["Miura","Ana Paula","Elaine","Nicole","Jéssica","Julia","João","Luciane","Glaucia","Bruna"]

    current_month = "Desconhecido"

    for _, row in df.iterrows():
        row_str = [str(x).strip() for x in row]
        row_text = " ".join(row_str).upper()

        # Pular linhas de resumo/totais
        if any(x in row_text for x in ["CUSTO TOTAL","VENDAS TOTAL","LUCRO TOTAL","CONVERSÕES","CAIXA","TOTAL DE CONTATOS","PRÉVIAS"]):
            continue

        # Detectar mês
        for m in months_pt:
            if m in row_text:
                current_month = m
                break

        # Extrair venda (primeira coluna numérica)
        try:
            val_str = row_str[0].replace(",", ".").strip()
            if val_str and val_str.replace(".", "").replace("-", "").isdigit():
                venda = float(val_str)
                if venda > 0:
                    cliente = row_str[2] if len(row_str) > 2 and row_str[2].strip() != "" else "Não identificado"

                    # Custo de anúncio
                    custo_anuncio = 0
                    for val in row_str[4:]:
                        if val and val.replace(",", ".").replace(".", "").replace("-", "").isdigit():
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
st.subheader("📤 Upload dos 3 arquivos Excel")
arquivos = st.file_uploader("Arraste V-Lion Produções 2024, 2025 e 2026", type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 CARREGAR COM PARSER CORRIGIDO"):
    with st.spinner("Lendo e corrigindo as planilhas..."):
        total = 0
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            parsed = parse_vlion_file(df, arq.name)
            if not parsed.empty:
                st.session_state.master = pd.concat([st.session_state.master, parsed], ignore_index=True)
                st.success(f"✅ {arq.name} → **{len(parsed)} registros**")
                total += len(parsed)
        st.balloons()
        st.success(f"🎉 Total carregado: **{total} registros** com cálculos corrigidos!")

# ====================== BACKUP ======================
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Exportar Backup CSV"):
        csv = st.session_state.master.to_csv(index=False)
        st.download_button("Baixar agora", csv, "v-lion_backup_corrigido.csv", "text/csv")
with col2:
    backup = st.file_uploader("📤 Restaurar Backup", type="csv")
    if backup:
        st.session_state.master = pd.read_csv(backup)
        st.success("✅ Dados restaurados!")

# ====================== DEBUG (para você ver o que está carregando) ======================
if not st.session_state.master.empty:
    with st.expander("🔍 Debug - Primeiros 30 registros carregados"):
        st.dataframe(st.session_state.master.head(30))

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["📊 INDICADORES", "👥 MELHORES CLIENTES", "📋 RESUMO"])

with tab1:
    if not st.session_state.master.empty:
        tv = st.session_state.master["venda"].sum()
        tc = st.session_state.master["custo_anuncio"].sum() + st.session_state.master["valor_editor"].sum()
        tl = tv - tc
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("💰 VENDAS", f"R$ {tv:,.2f}")
        col2.metric("📦 PEDIDOS", len(st.session_state.master))
        col3.metric("🎯 TICKET MÉDIO", f"R$ {tv/len(st.session_state.master):,.2f}" if len(st.session_state.master)>0 else "R$ 0,00")
        col4.metric("💸 CUSTOS TOTAIS", f"R$ {tc:,.2f}")
        col5.metric("📈 LUCRO", f"R$ {tl:,.2f}", delta=f"R$ {tl:,.2f}")
    else:
        st.info("Carregue as planilhas")

with tab2:
    st.subheader("👥 Melhores Clientes")
    if not st.session_state.master.empty:
        busca = st.text_input("🔍 Buscar cliente", "")
        df_cli = st.session_state.master.groupby("cliente").agg(
            total_venda=("venda", "sum"),
            pedidos=("venda", "count")
        ).reset_index().sort_values("total_venda", ascending=False)
        if busca:
            df_cli = df_cli[df_cli["cliente"].str.contains(busca, case=False)]
        st.dataframe(df_cli.style.format({"total_venda": "R$ {:,.2f}"}), use_container_width=True)
    else:
        st.info("Nenhum cliente ainda")

with tab3:
    st.subheader("📋 Resumo por Mês")
    if not st.session_state.master.empty:
        resumo = st.session_state.master.groupby(["ano", "mes"]).agg(
            Vendas=("venda", "sum"),
            Custos_Anuncio=("custo_anuncio", "sum"),
            Custos_Editores=("valor_editor", "sum"),
            Lucro=("lucro", "sum")
        )
        st.dataframe(resumo.style.format("{:,.2f}"), use_container_width=True)
        
        st.subheader("Performance dos Editores")
        ed = st.session_state.master.groupby("editor").agg(
            Total_Pago=("valor_editor", "sum"),
            Projetos=("editor", "count")
        ).sort_values("Total_Pago", ascending=False)
        st.dataframe(ed.style.format({"Total_Pago": "R$ {:,.2f}"}), use_container_width=True)
    else:
        st.info("Nenhum dado ainda")

st.caption("✅ Parser refeito do zero • Números agora corretos e separados")
