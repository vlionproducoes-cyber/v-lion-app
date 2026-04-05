import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="V-LION", layout="wide", page_icon="🦁")

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0a0a0a, #1a1a2e); color: #f5c400; }
    .big-title { font-size: 52px; font-weight: bold; background: linear-gradient(90deg, #f5c400, #ffd700); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .neon { text-shadow: 0 0 15px #f5c400, 0 0 30px #f5c400; }
    .glass { background: rgba(10,10,10,0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255,215,0,0.3); border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

st.image("logo.png", width=180)
st.markdown('<p class="big-title neon">V-LION PRODUÇÕES</p>', unsafe_allow_html=True)
st.caption(f"🚀 Dashboard Futurista • Processamento Inteligente • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if "master" not in st.session_state:
    st.session_state.master = pd.DataFrame(columns=["ano", "mes", "cliente", "venda", "custo_anuncio", "editor", "valor_editor", "lucro"])

# ====================== PARSER FORTE ======================
def parse_vlion_file(df, filename):
    records = []
    current_month = "Desconhecido"
    ano = 2024 if "2024" in filename else 2025 if "2025" in filename else 2026

    for i, row in df.iterrows():
        row = row.fillna("").astype(str).str.strip()
        row_text = " ".join(row).upper()

        # Detecta mês
        months = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO","JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]
        for m in months:
            if m in row_text:
                current_month = m
                break

        # Linha de venda (coluna 0 tem número > 0)
        try:
            valor_str = str(row[0]).replace(",", ".").strip()
            if valor_str.replace(".", "").isdigit():
                valor = float(valor_str)
                if valor > 0:
                    cliente = str(row[2]) if len(row) > 2 and str(row[2]) != "" else "Cliente não identificado"

                    # Procura editor na linha inteira
                    editor = "Sem editor"
                    editor_list = ["Miura", "Ana Paula", "Elaine", "Nicole", "Jéssica", "Julia", "João", "Luciane"]
                    for e in editor_list:
                        if e.upper() in row_text:
                            editor = e
                            break

                    records.append({
                        "ano": ano,
                        "mes": current_month,
                        "cliente": cliente,
                        "venda": valor,
                        "custo_anuncio": 0,
                        "editor": editor,
                        "valor_editor": 0,
                        "lucro": valor
                    })
        except:
            pass

    return pd.DataFrame(records)

# ====================== UPLOAD ======================
st.subheader("📤 Upload dos 3 arquivos Excel")
arquivos = st.file_uploader("Arraste aqui: V-Lion Produções 2024.xlsx, 2025.xlsx e 2026.xlsx", 
                           type=["xlsx"], accept_multiple_files=True)

if st.button("🔥 Processar todos os arquivos agora"):
    with st.spinner("Lendo e extraindo todas as vendas..."):
        for arq in arquivos:
            df = pd.read_excel(arq, header=None)
            parsed = parse_vlion_file(df, arq.name)
            if not parsed.empty:
                st.session_state.master = pd.concat([st.session_state.master, parsed], ignore_index=True)
                st.success(f"✅ {arq.name} → **{len(parsed)} vendas** extraídas")
            else:
                st.warning(f"⚠️ {arq.name} não encontrou vendas (verifique o arquivo)")

    st.balloons()

# ====================== DASHBOARD ======================
if not st.session_state.master.empty:
    tv = st.session_state.master["venda"].sum()
    te = st.session_state.master["valor_editor"].sum()
    tl = st.session_state.master["lucro"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VENDAS TOTAIS", f"R$ {tv:,.2f}")
    col2.metric("CUSTO TOTAL EDITORES", f"R$ {te:,.2f}")
    col3.metric("LUCRO TOTAL", f"R$ {tl:,.2f}")
    col4.metric("ROI MÉDIO", f"{(tv / (te + 1)):.2f}x")

    st.subheader("🔥 Editores")
    ed = st.session_state.master.groupby("editor").agg(
        pago=("valor_editor","sum"), gerado=("venda","sum")
    ).round(2)
    ed["ROI"] = (ed["gerado"] / ed["pago"]).round(2)
    st.dataframe(ed, use_container_width=True)

else:
    st.info("👆 Faça upload dos 3 arquivos Excel para começar")

# Adicionar manual
st.subheader("➕ Adicionar nova venda")
col1, col2 = st.columns(2)
with st.form("nova"):
    cliente = col1.text_input("Cliente")
    venda = col2.number_input("Valor da venda R$", min_value=0.0, step=10.0)
    custo = col1.number_input("Custo anúncio R$", min_value=0.0, step=10.0)
    editor = col2.text_input("Editor")
    valor_editor = st.number_input("Valor pago ao editor R$", min_value=0.0, step=10.0)
    if st.form_submit_button("🚀 SALVAR"):
        lucro = venda - custo - valor_editor
        nova = pd.DataFrame([{"ano": datetime.now().year, "mes": datetime.now().strftime("%B"), "cliente": cliente,
                              "venda": venda, "custo_anuncio": custo, "editor": editor or "Sem editor",
                              "valor_editor": valor_editor, "lucro": lucro}])
        st.session_state.master = pd.concat([st.session_state.master, nova], ignore_index=True)
        st.success("✅ Salvo!")

# Download
if not st.session_state.master.empty:
    st.download_button("📥 Baixar todos os dados", st.session_state.master.to_csv(index=False).encode(), "v-lion_dados_completos.csv", "text/csv")

st.caption("App V-Lion Futurista • Parser melhorado")
