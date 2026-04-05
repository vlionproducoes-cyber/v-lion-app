import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

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
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Dashboard Futurista • Dados Persistentes • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ====================== PERSISTÊNCIA ======================
if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano","mes","cliente","venda","custo_anuncio","editor","valor_editor","lucro"])

# ====================== PARSER MELHORADO ======================
def parse_vlion_file(df, filename):
    records = []
    current_month = "Desconhecido"
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026
    months_pt = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]
    editors = ["Miura", "Ana Paula", "Elaine", "Nicole", "Jéssica", "Julia", "João", "Luciane", "Glaucia", "Bruna"]

    for _, row in df.iterrows():
        row_text = " ".join(str(x).strip() for x in row).upper()
        
        # Detectar mês
        for m in months_pt:
            if m in row_text:
                current_month = m
                break
        
        try:
            # Valor principal (venda)
            val_str = str(row[0]).replace(",", ".").strip()
            if val_str.replace(".", "").replace("-", "").isdigit():
                valor = float(val_str)
                if valor > 0:
                    cliente = str(row[2]).strip() if len(row) > 2 and str(row[2]).strip() != "" else "Não identificado"
                    
                    # Detectar editor e custo de edição
                    editor = "Sem editor"
                    valor_editor = 0
                    for e in editors:
                        if e.upper() in row_text:
                            editor = e
                            # Tentar pegar o valor após "Edição"
                            parts = row_text.split(e.upper())
                            if len(parts) > 1:
                                num_part = ''.join(filter(str.isdigit, parts[1][:10]))
                                if num_part:
                                    valor_editor = float(num_part)
                            break
                    
                    # Detectar custo de anúncio
                    custo_anuncio = 0
                    if "VALOR INVESTIDO" in row_text or "INVESTIMENTO" in row_text:
                        try:
                            custo_anuncio = float(str(row[4]).replace(",", ".").strip())
                        except:
                            pass
                    
                    records.append({
                        "ano": ano, "mes": current_month, "cliente": cliente,
                        "venda": valor, "custo_anuncio": custo_anuncio,
                        "editor": editor, "valor_editor": valor_editor,
                        "lucro": valor - custo_anuncio - valor_editor
                    })
        except:
            continue
    return pd.DataFrame(records)

# ====================== UPLOAD + BACKUP ======================
st.subheader("📤 Upload dos 3 arquivos Excel")
arquivos = st.file_uploader("Arraste V-Lion Produções 2024, 2025 e 2026", type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 CARREGAR PLANILHAS"):
    with st.spinner("Processando as 3 planilhas..."):
        total = 0
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            parsed = parse_vlion_file(df, arq.name)
            if not parsed.empty:
                st.session_state.master = pd.concat([st.session_state.master, parsed], ignore_index=True)
                st.success(f"✅ {arq.name} → **{len(parsed)} registros**")
                total += len(parsed)
        st.balloons()

# ====================== BACKUP (para não perder mais os dados) ======================
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Exportar Backup CSV"):
        csv = st.session_state.master.to_csv(index=False)
        st.download_button("Baixar backup agora", csv, "v-lion_backup.csv", "text/csv")
with col2:
    backup_file = st.file_uploader("📤 Restaurar Backup CSV", type="csv")
    if backup_file:
        st.session_state.master = pd.read_csv(backup_file)
        st.success("✅ Dados restaurados com sucesso!")

# ====================== TABS (igual ao Canva) ======================
tab1, tab2, tab3 = st.tabs(["📊 INDICADORES", "👥 CLIENTES", "📋 RESUMO"])

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
        st.info("Carregue as planilhas ou restaure o backup")

with tab2:
    st.subheader("👥 Melhores Clientes")
    if not st.session_state.master.empty:
        busca = st.text_input("🔍 Buscar cliente", "")
        df_cli = st.session_state.master.groupby("cliente").agg(
            total=("venda", "sum"),
            pedidos=("venda", "count"),
            ultima=("ano", "max")
        ).reset_index().sort_values("total", ascending=False)
        
        if busca:
            df_cli = df_cli[df_cli["cliente"].str.contains(busca, case=False)]
        
        st.dataframe(df_cli.style.format({"total": "R$ {:,.2f}"}), use_container_width=True)
        st.caption("🔥 Os melhores clientes estão no topo (ordenado por valor total gasto)")
    else:
        st.info("Nenhum dado ainda")

with tab3:
    st.subheader("📋 Resumo por Mês + Editores")
    if not st.session_state.master.empty:
        resumo = st.session_state.master.groupby(["ano", "mes"]).agg(
            Vendas=("venda", "sum"),
            Custos=("custo_anuncio", "sum"),
            Editores=("valor_editor", "sum"),
            Lucro=("lucro", "sum")
        )
        st.dataframe(resumo, use_container_width=True)
        
        st.subheader("Performance dos Editores")
        editores = st.session_state.master.groupby("editor").agg(
            Total_Pago=("valor_editor", "sum"),
            Qtde_Projetos=("editor", "count")
        ).sort_values("Total_Pago", ascending=False)
        st.dataframe(editores.style.format({"Total_Pago": "R$ {:,.2f}"}), use_container_width=True)
    else:
        st.info("Carregue os arquivos")

st.caption("✅ App V-Lion • Dados persistem com backup • Custos + Editores agora capturados")
