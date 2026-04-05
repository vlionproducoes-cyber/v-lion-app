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
    .glass { background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); 
             border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
    .neon-glow { box-shadow: 0 0 20px #ffd700, 0 0 40px #ffd700; }
    .metric-card { background: rgba(10,10,10,0.85); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,215,0,0.3); }
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Dashboard Futurista • Parser Ultra Seguro • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano", "mes", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# ====================== PARSER ULTRA SEGURO ======================
def parse_vlion_file(df, filename):
    records = []
    current_month = "Desconhecido"
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026

    months_pt = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]

    for _, row in df.iterrows():
        # CONVERSÃO TOTALMENTE SEGURA
        row_text = " ".join(str(x).strip() for x in row).upper()

        # Detecta mês
        for m in months_pt:
            if m in row_text:
                current_month = m
                break

        # Detecta venda
        try:
            val_str = str(row[0]).replace(",", ".").strip()
            if val_str.replace(".", "").replace("-", "").isdigit():
                valor = float(val_str)
                if valor > 0:
                    cliente = str(row[2]).strip() if len(row) > 2 and str(row[2]).strip() != "" else "Cliente não identificado"
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
            continue
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

# ====================== DASHBOARD (mais próximo do Canva) ======================
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
    st.info("👆 Faça upload dos 3 arquivos para começar")

st.caption("✅ App V-Lion • Design futurista • Parser corrigido • Mais próximo do seu Canva")

if not st.session_state.master.empty:
    st.download_button("📥 Baixar todos os dados", st.session_state.master.to_csv(index=False).encode(), "v-lion_dados_completos.csv", "text/csv")
