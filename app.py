# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from PIL import Image
from data_sc import CROP_PARAMS, get_sc_dataframe, calculate_potentials
from mas_engine_v5 import MultiAgentSystemEngineSBCE

# Configurações da página Streamlit
st.set_page_config(
    page_title="Sistema Multiagente - SBCE & Biomassa SC",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização segura do session_state para persistência entre abas
if 'linha_selecionada' not in st.session_state:
    st.session_state['linha_selecionada'] = "BNDES Fundo Clima"
if 'capex_financiado' not in st.session_state:
    st.session_state['capex_financiado'] = 3000000
if 'prazo_comercial' not in st.session_state:
    st.session_state['prazo_comercial'] = 15.0


# Função para carregar imagem de forma segura (Local -> URL Fallback -> SVG Fallback)
def get_udesc_logo_image():
    local_paths = ["Udesc_Logo.jpg", "Marca UDESC.jpg", "Marca PPGEEL UDESC.jpg", "Udesc_Logo.png"]
    for path in local_paths:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                target_height = 96
                aspect_ratio = img.width / img.height
                target_width = int(target_height * aspect_ratio)
                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                return img_resized
            except Exception:
                return path
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Logotipo_da_UDESC.svg/320px-Logotipo_da_UDESC.svg.png"

def get_sc_flag_image():
    local_paths = ["Bandeira do Estado de Santa Catarina.jpg", "Bandeira.png"]
    for path in local_paths:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                target_height = 96
                aspect_ratio = img.width / img.height
                target_width = int(target_height * aspect_ratio)
                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                return img_resized
            except Exception:
                return path
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Bandeira_de_Santa_Catarina.svg/320px-Bandeira_de_Santa_Catarina.svg.png"

def get_local_map_base64():
    import base64
    local_filenames = [
        "mapa-municípal-do-estado-de-santa-catarina-nome dos municipios.webp",
        "mapa_municipal_sc.webp",
        "mapa.webp",
        "mapa-municípal-do-estado-de-santa-catarina-nome dos municipios.jpg",
        "mapa_municipal_sc.jpg",
        "mapa.jpg",
        "mapa-municípal-do-estado-de-santa-catarina-nome dos municipios.png"
    ]
    for filename in local_filenames:
        if os.path.exists(filename):
            try:
                with open(filename, "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode("utf-8")
                ext = os.path.splitext(filename)[1].lower()
                mime = "image/webp" if ext == ".webp" else ("image/png" if ext == ".png" else "image/jpeg")
                return f"data:{mime};base64,{encoded}"
            except Exception:
                pass
    return None

def get_pdf_map_base64():
    import base64
    import subprocess
    local_filenames = [
        "Mapa_Rodoviário_Santa_Catarina.pdf",
        "mapa_rodoviario_santa_catarina.pdf",
        "Mapa_Rodoviario_Santa_Catarina.pdf",
        "mapa_rodoviário_santa_catarina.pdf"
    ]
    for filename in local_filenames:
        if os.path.exists(filename):
            try:
                out_prefix = "temp_pdf_map_page"
                if os.path.exists(out_prefix + "-1.png"):
                    os.remove(out_prefix + "-1.png")
                cmd = ["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", filename, out_prefix]
                subprocess.run(cmd, check=True, capture_output=True)
                png_path = out_prefix + "-1.png"
                if os.path.exists(png_path):
                    with open(png_path, "rb") as f:
                        data = f.read()
                    encoded = base64.b64encode(data).decode("utf-8")
                    try:
                        os.remove(png_path)
                    except Exception:
                        pass
                    return f"data:image/png;base64,{encoded}"
            except Exception:
                pass
    return None





# Imagens embarcadas via Base64 SVG (100% de confiabilidade offline)
UDESC_TEXT_BASE64 = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAgNDAiIHdpZHRoPSIxMjAiIGhlaWdodD0iNDAiPgogIDx0ZXh0IHg9IjYwIiB5PSIyOCIgZm9udC1mYW1pbHk9IidNb250c2VycmF0JywgJ0hlbHZldGljYScsICdBcmlhbCcsIHNhbnMtc2VyaWYiIGZvbnQtd2VpZ2h0PSI5MDAiIGZvbnQtc2l6ZT0iMjgiIGZpbGw9IiMwNDZBMzgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGxldHRlci1zcGFjaW5nPSIxIj5VREVTQzwvdGV4dD4KPC9zdmc+'
PPGEEL_LOGO_BASE64 = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAgMTIwIiB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCI+CiAgPGNpcmNsZSBjeD0iNjAiIGN5PSI2MCIgcj0iNTIiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzA0NkEzOCIgc3Ryb2tlLXdpZHRoPSI0Ii8+CiAgPGNpcmNsZSBjeD0iNjAiIGN5PSI2MCIgcj0iNDQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0RBMjkxQyIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSI0LDQiLz4KICA8cGF0aCBkPSJNIDM1IDYwIEwgNTAgNDUgTCA3MCA0NSBMIDg1IDYwIEwgNzAgNzUgTCA1MCA3NSBaIiBmaWxsPSJub25lIiBzdHJva2U9IiMwNDZBMzgiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iNDUiIHI9IjQiIGZpbGw9IiNEQTI5MUMiLz4KICA8Y2lyY2xlIGN4PSI3MCIgY3k9IjQ1IiByPSI0IiBmaWxsPSIjMDQ2QTM4Ii8+CiAgPGNpcmNsZSBjeD0iMzUiIGN5PSI2MCIgcj0iNCIgZmlsbD0iIzA0NkEzOCIvPgogIDxjaXJjbGUgY3g9Ijg1IiBjeT0iNjAiIHI9IjQiIGZpbGw9IiNEQTI5MUMiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9Ijc1IiByPSI0IiBmaWxsPSIjMDQ2QTM4Ii8+CiAgPGNpcmNsZSBjeD0iNzAiIGN5PSI3NSIgcj0iI0RBMjkxQyIvPgogIDx0ZXh0IHg9IjYwIiB5PSI2MiIgZm9udC1mYW1pbHk9IidNb250c2VycmF0JywgJ0hlbHZldGljYScsIHNhbnMtc2VyaWYiIGZvbnQtd2VpZ2h0PSJib2xkIiBmb250LXNpemU9IjExIiBmaWxsPSIjMDAwMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5QUEdFRUw8L3RleHQ+CiAgPHRleHQgeD0iNjAiIHk9IjcwIiBmb250LWZhbWlseT0iJ01vbnRzZXJyYXQnLCAnSGVsdmV0aWNhJywgc2Fucy1zZXJpZiIgZm9udC1zaXplPSI2IiBmaWxsPSIjNjY2NjY2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5MSUMgLSBVREVTQzwvdGV4dD4KPC9zdmc+'
UDESC_LOGO_BASE64 = UDESC_TEXT_BASE64 # fallback
SC_FLAG_BASE64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNTAgMTAwIiB3aWR0aD0iMTUwIiBoZWlnaHQ9IjEwMCI+CiAgPCEtLSBCYWNrZ3JvdW5kIFN0cmlwZXMgKFJlZC1XaGl0ZS1SZWQpIC0tPgogIDxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSIxNTAiIGhlaWdodD0iMzMuMyIgZmlsbD0iI0RBMjkxQyIvPgogIDxyZWN0IHg9IjAiIHk9IjMzLjMiIHdpZHRoPSIxNTAiIGhlaWdodD0iMzMuNCIgZmlsbD0iI0ZGRkZGRiIvPgogIDxyZWN0IHg9IjAiIHk9IjY2LjciIHdpZHRoPSIxNTAiIGhlaWdodD0iMzMuMyIgZmlsbD0iI0RBMjkxQyIvPgogIAogIDwhLS0gR3JlZW4gUmhvbWJ1cyBpbiB0aGUgY2VudGVyIC0tPgogIDxwb2x5Z29uIHBvaW50cz0iNzUsMTIgMTM1LDUwIDc1LDg4IDE1LDUwIiBmaWxsPSIjODRCRDAwIi8+CiAgCiAgPCEtLSBTaW1wbGlmaWVkIENvYXQgb2YgQXJtcyBpbiB0aGUgY2VudGVyIC0tPgogIDxwb2x5Z29uIHBvaW50cz0iNzUsMzIgNzgsNDIgODgsNDIgODAsNDggODMsNTggNzUsNTIgNjcsNTggNzAsNDggNjIsNDIgNzIsNDIiIGZpbGw9IiNFQUFBMDAiIHN0cm9rZT0iI0ZGRkZGRiIgc3Ryb2tlLXdpZHRoPSIxIi8+CiAgPHBhdGggZD0iTSA3MywzMSBDIDczLDI2IDc3LDI2IDc3LDMxIFoiIGZpbGw9IiNEQTI5MUMiLz4KICA8Y2lyY2xlIGN4PSI3NSIgY3k9IjUwIiByPSI4IiBmaWxsPSIjNUM3NjhEIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMC43Ii8+CiAgPHBhdGggZD0iTSA1NSw2MiBRIDc1LDY4IDk1LDYyIEwgOTIsNjYgUSA3NSw3MSA1OCw2NiBaIiBmaWxsPSIjREEyOTFDIi8+CiAgPHRleHQgeD0iNzUiIHk9IjY1LjUiIGZvbnQtZmFtaWx5PSJIZWx2ZXRpY2EsIEFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIzIiBmaWxsPSIjRkZGRkZGIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5TQU5UQSBDQVRBUklOQTwvdGV4dD4KPC9zdmc+"

# Cabeçalho Institucional - Destaque das Marcas com Alinhamento Vertical Perfeito de 96px
col_logo_udesc, col_logo_ppgeel, col_logo_sc, col_title = st.columns([1.1, 1.2, 1.3, 7.0])

with col_logo_udesc:
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 96px; border: 2px solid #046A38; border-radius: 6px; padding: 4px; background-color: #F8F9FA; width: 110px;">
        <span style="font-family: 'Montserrat', 'Helvetica', 'Arial', sans-serif; font-weight: 900; font-size: 26px; color: #046A38; letter-spacing: 1px; line-height: 1;">UDESC</span>
        <span style="font-family: 'Montserrat', 'Helvetica', sans-serif; font-weight: 700; font-size: 8px; color: #DA291C; text-align: center; line-height: 1.1; margin-top: 2px;">JOINVILLE</span>
    </div>
    """, unsafe_allow_html=True)

with col_logo_ppgeel:
    st.image(PPGEEL_LOGO_BASE64, width=100)

with col_logo_sc:
    st.image(SC_FLAG_BASE64, width=130)

with col_title:
    st.title("🌱 Sistema Multiagente para Descarbonização e Geração de Eletricidade em Santa Catarina")
    st.markdown("🏛️ **PPGEEL - Laboratório de Inteligência Computacional (LIC) | campus Joinville**")

st.markdown("""
Esta plataforma computacional simula um **Sistema Multiagente (MAS)** que integra dados de produtividade agrícola do IBGE, 
potencial elétrico, de descarbonização por pirólise de resíduos agrícolas e a regulação do **SBCE (Sistema Brasileiro de Comércio de Emissões)**.
""")

# Barra Lateral - Parâmetros da Simulação e do Mercado
st.sidebar.header("⚙️ Parâmetros da Simulação")

collect_rate = st.sidebar.slider(
    "Taxa de Coleta/Aproveitamento de Resíduos",
    min_value=0.05, max_value=1.00, value=0.20, step=0.05,
    help="Fração dos resíduos agrícolas que podem ser coletados e transportados para as usinas."
)

st.sidebar.header("💰 Preços de Mercado")
biomass_price = st.sidebar.slider(
    "Preço da Biomassa (R$/tonelada)",
    min_value=50.0, max_value=300.0, value=150.0, step=10.0,
    help="Preço pago aos agricultores/cooperativas pelos resíduos agrícolas."
)

electricity_price = st.sidebar.slider(
    "Preço de Venda da Energia (R$/MWh)",
    min_value=300.0, max_value=800.0, value=550.0, step=25.0,
    help="Tarifa de venda da energia elétrica renovável gerada pelas usinas."
)

st.sidebar.header("🏛️ Regulação do Mercado SBCE")
sbce_mode = st.sidebar.selectbox(
    "Fase de Regulação do SBCE",
    ["Alocação Gratuita", "Leilão por Consignação", "Leilão Tradicional"],
    index=1,
    help="Seleciona as regras e o preço de mercado associados ao Sistema Brasileiro de Comércio de Emissões."
)

# Inicializa o motor multiagente com o modo SBCE ativo
@st.cache_data
def run_mas_engine(collect_rate, biomass_price, electricity_price, sbce_mode):
    engine = MultiAgentSystemEngineSBCE(
        collect_rate=collect_rate,
        biomass_price=biomass_price,
        electricity_price=electricity_price,
        sbce_mode=sbce_mode
    )
    engine.run_simulation()
    return engine

engine = run_mas_engine(collect_rate, biomass_price, electricity_price, sbce_mode)
df_plants, df_industries = engine.get_summary_df()

# Preço do carbono dinâmico baseado na regulação selecionada
carbon_price_display = engine.carbon_price

# Obtenção de dados de SC para os mapas
df_sc = get_sc_dataframe()
df_sc_potentials = calculate_potentials(df_sc, collect_rate=collect_rate)

# Layout de Abas principais
(tab_dashboard, tab_mapping, tab_historical, tab_siting, tab_logistics, tab_mas, 
 tab_sbce, tab_advantages, tab_financing, tab_whirlpool, tab_calculator, tab_articles) = st.tabs([
    "📊 Dashboard Geral SC", 
    "🗺️ Mapeamento de Potenciais", 
    "📈 Análise Histórica 2020-2024",
    "📍 Localização Ótima de Usinas",
    "🚚 Rotas Logísticas & Escoamento",
    "🤖 Mercado Multiagente (MAS)", 
    "🏛️ Regulação SBCE & Leilão",
    "💰 Vantagens Financeiras",
    "🏦 Modelos de Financiamento",
    "🏭 Caso Whirlpool & Captura",
    "🏭 Calculadora Industrial", 
    "📚 Grounding Científico (Artigos)"
])

# ==================== ABA 1: DASHBOARD GERAL ====================
with tab_dashboard:
    st.header("📈 Panorama Geral de Santa Catarina")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total de Resíduos Gerados",
            value=f"{df_sc_potentials['Residuo_Total_t'].sum() / 1000:.1f} mil toneladas"
        )
    with col2:
        st.metric(
            label="Resíduos Aproveitados",
            value=f"{df_sc_potentials['Residuo_Coletado_t'].sum() / 1000:.1f} mil toneladas",
            delta=f"{collect_rate*100:.0f}% de taxa de coleta"
        )
    with col3:
        st.metric(
            label="Potencial Elétrico Total",
            value=f"{df_sc_potentials['PE_Total_MWh'].sum() / 1000:.1f} GWh/ano"
        )
    with col4:
        st.metric(
            label="Capacidade de Descarbonização",
            value=f"{df_sc_potentials['PD_Total_tCO2eq'].sum():,.0f} tCO2eq/ano"
        )

    st.subheader("🌾 Distribuição do Potencial de Resíduos por Cultura Agrícola")
    res_crop_totals = {}
    pe_crop_totals = {}
    pd_crop_totals = {}
    
    for crop in CROP_PARAMS:
        res_crop_totals[crop] = df_sc_potentials[f"{crop}_Residuo_Coletado"].sum()
        pe_crop_totals[crop] = df_sc_potentials[f"{crop}_PE_MWh"].sum()
        pd_crop_totals[crop] = df_sc_potentials[f"{crop}_PD_tCO2eq"].sum()
        
    df_totals = pd.DataFrame({
        "Cultura": list(CROP_PARAMS.keys()),
        "Resíduo Coletado (t)": list(res_crop_totals.values()),
        "Potencial Elétrico (MWh)": list(pe_crop_totals.values()),
        "Descarbonização (tCO2eq)": list(pd_crop_totals.values())
    })
    
    fig_res = px.bar(
        df_totals, x="Cultura", y="Resíduo Coletado (t)", 
        title="Volume de Resíduos Disponíveis para Pirólise",
        color="Cultura", color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_res, use_container_width=True)
    
    st.subheader("🏆 Maiores Municípios Produtores de Biomassa e Seus Potenciais")
    df_top_sc = df_sc_potentials.sort_values(by="Residuo_Total_t", ascending=False)[
        ["municipio", "regiao", "Residuo_Total_t", "PE_Total_MWh", "PD_Total_tCO2eq"]
    ].rename(columns={
        "municipio": "Município",
        "regiao": "Região",
        "Residuo_Total_t": "Produção de Resíduos (t)",
        "PE_Total_MWh": "Potencial Elétrico (MWh)",
        "PD_Total_tCO2eq": "Descarbonização (tCO2eq)"
    })
    st.dataframe(df_top_sc, use_container_width=True, hide_index=True)


# ==================== ABA 2: MAPEAMENTO DE POTENCIAIS ====================
with tab_mapping:
    st.header("🗺️ Mapeamento Espacial de Santa Catarina")
    st.markdown("""
    Os mapas de calor abaixo mostram a distribuição espacial de produtividade, resíduos, 
    potencial elétrico e potencial de descarbonização em SC por município, condizendo com os mapas de referência anexados.
    """)
    
    selected_crop = st.selectbox("Escolha a Cultura Agrícola para Mapeamento", list(CROP_PARAMS.keys()))
    col_map1, col_map2 = st.columns(2)
    
    with col_map1:
        st.subheader(f"⚡ Potencial Elétrico - {selected_crop} (MWh)")
        fig_map_pe = px.scatter(
            df_sc_potentials, x="lon", y="lat",
            size=f"{selected_crop}_PE_MWh" if df_sc_potentials[f"{selected_crop}_PE_MWh"].sum() > 0 else None,
            color=f"{selected_crop}_PE_MWh",
            hover_name="municipio",
            hover_data=["regiao", f"{selected_crop}_Residuo_Coletado", f"{selected_crop}_PE_MWh"],
            color_continuous_scale="Viridis",
            labels={f"{selected_crop}_PE_MWh": "Potencial Elétrico (MWh)"}
        )
        fig_map_pe.update_layout(xaxis_title="Longitude", yaxis_title="Latitude")
        st.plotly_chart(fig_map_pe, use_container_width=True)
        
    with col_map2:
        st.subheader(f"🍃 Potencial de Descarbonização - {selected_crop} (tCO2eq)")
        fig_map_pd = px.scatter(
            df_sc_potentials, x="lon", y="lat",
            size=f"{selected_crop}_PD_tCO2eq" if df_sc_potentials[f"{selected_crop}_PD_tCO2eq"].sum() > 0 else None,
            color=f"{selected_crop}_PD_tCO2eq",
            hover_name="municipio",
            hover_data=["regiao", f"{selected_crop}_Residuo_Coletado", f"{selected_crop}_PD_tCO2eq"],
            color_continuous_scale="Greens",
            labels={f"{selected_crop}_PD_tCO2eq": "Capacidade de Captura (tCO2eq)"}
        )
        fig_map_pd.update_layout(xaxis_title="Longitude", yaxis_title="Latitude")
        st.plotly_chart(fig_map_pd, use_container_width=True)


# ==================== ABA 3: LOCALIZAÇÃO ÓTIMA ====================

# ==================== ABA 3: ANÁLISE HISTÓRICA 2020-2024 (NOVA ABA) ====================
with tab_historical:
    st.header("📈 Análise Histórica do Potencial de Descarbonização (2020 - 2024)")
    st.markdown("""
    Esta seção analisa a evolução temporal do potencial de descarbonização em Santa Catarina, 
    de acordo com os mapeamentos secretos de 2020 a 2024 das diferentes culturas agrícolas: **Arroz, Soja, Milho e Trigo** [120, 133].
    Observe como a expansão das culturas e as flutuações anuais impactam diretamente a capacidade de captura estável de carbono.
    """)

    # Banco de dados histórico (PAM/IBGE correspondente aos mapas anexados)
    years = [2020, 2021, 2022, 2023, 2024]
    hist_data = {
        "Ano": years,
        "Arroz": [259000, 270000, 255000, 274000, 248000],
        "Soja": [379000, 402000, 363000, 426000, 450000],
        "Milho": [326000, 307000, 314000, 295000, 264000],
        "Trigo": [32000, 60000, 69000, 62000, 73000]
    }
    df_hist = pd.DataFrame(hist_data)
    df_melted = df_hist.melt(id_vars=["Ano"], var_name="Cultura", value_name="Potencial (tCO2eq/ano)")

    # Layout de Gráficos
    col_hist_chart1, col_hist_chart2 = st.columns(2)
    
    with col_hist_chart1:
        st.subheader("📊 Trajetória Anual do Potencial por Cultura")
        fig_hist_line = px.line(
            df_melted, x="Ano", y="Potencial (tCO2eq/ano)", color="Cultura", markers=True,
            title="Evolução Temporal do Potencial de Descarbonização (tCO2eq/ano)",
            color_discrete_sequence=px.colors.qualitative.Dark2,
            labels={"Ano": "Ano de Safra", "Potencial (tCO2eq/ano)": "Redução (tCO2eq/ano)"}
        )
        fig_hist_line.update_layout(xaxis=dict(type='linear', tickmode='linear', tick0=2020, dtick=1))
        st.plotly_chart(fig_hist_line, use_container_width=True)

    with col_hist_chart2:
        st.subheader("⛰️ Potencial de Descarbonização Acumulado (SC)")
        fig_hist_area = px.area(
            df_melted, x="Ano", y="Potencial (tCO2eq/ano)", color="Cultura",
            title="Capacidade Total de Captura de Carbono em Solo por Ano em SC",
            color_discrete_sequence=px.colors.qualitative.Dark2,
            labels={"Ano": "Ano de Safra", "Potencial (tCO2eq/ano)": "Redução Total (tCO2eq/ano)"}
        )
        fig_hist_area.update_layout(xaxis=dict(type='linear', tickmode='linear', tick0=2020, dtick=1))
        st.plotly_chart(fig_hist_area, use_container_width=True)

    # Painel de Detalhes e Grounding das Culturas
    st.subheader("🔍 Detalhamento Científico por Cultura Agrícola")
    selected_hist_crop = st.selectbox("Selecione uma cultura para análise detalhada", ["Todas", "Arroz", "Soja", "Milho", "Trigo"])

    if selected_hist_crop == "Todas":
        total_captured = df_hist[["Arroz", "Soja", "Milho", "Trigo"]].sum().sum()
        avg_annual = df_hist[["Arroz", "Soja", "Milho", "Trigo"]].sum(axis=1).mean()
        
        st.info(f"""
        - **Total Acumulado Mitigado (2020-2024):** {total_captured:,.0f} tCO2eq evitadas no solo catarinense.
        - **Potencial Médio Anual do Estado:** {avg_annual:,.0f} tCO2eq/ano [133, 139].
        - **Dinâmica Temporal:** A soja consolidou-se como o principal pilar de captura, crescendo de forma expressiva e compensando as quedas do milho causadas por substituição de safra e seca na região Oeste [140].
        """)
    else:
        crop_series = df_hist[selected_hist_crop]
        total_captured = crop_series.sum()
        avg_annual = crop_series.mean()
        max_year = df_hist.loc[crop_series.idxmax(), "Ano"]
        max_val = crop_series.max()
        
        # Grounding text based on the sources
        grounding_text = ""
        if selected_hist_crop == "Arroz":
            grounding_text = "Historicamente concentrado nas regiões Norte e Sul do estado [133, 139]. O biocarvão de arroz possui altíssima estabilidade térmica e teor de silício benéfico para o solo [125]. Os mapas mostram que o potencial permaneceu estável ao redor de 260.000 tCO2eq/ano devido à estabilidade das bacias hidrográficas [125, 133]."
        elif selected_hist_crop == "Soja":
            grounding_text = "Representa o maior volume absoluto de resíduos do estado [140]. Em 2024, atingiu seu pico histórico devido à grande produtividade na região de Campos Novos, onde 73% do peso total da planta no setor agrícola é considerado resíduo energético e processável via pirólise [140]."
        elif selected_hist_crop == "Milho":
            grounding_text = "Concentra-se prioritariamente no Oeste Catarinense [133, 139]. Os resíduos de palha e sabugo representam aproximadamente 58% do peso de grãos produzidos [140]. O declínio observado deve-se ao aumento de rotações de cultura no inverno e clima adverso que reduziu as safras gerais do estado [140]."
        elif selected_hist_crop == "Trigo":
            grounding_text = "Representa a cultura de inverno com maior taxa de crescimento percentual no período, impulsionando a participação de biocombustíveis na entressafra e gerando renda extra para cooperativas agrícolas regionais [109, 114]."

        st.success(f"""
        **Análise de {selected_hist_crop}:**
        - **Total Mitigado (2020-2024):** {total_captured:,.0f} tCO2eq.
        - **Potencial Médio Anual:** {avg_annual:,.0f} tCO2eq/ano.
        - **Ano de Maior Impacto:** {max_year} ({max_val:,.0f} tCO2eq).
        - **Parecer Técnico-Espacial:** {grounding_text}
        """)

with tab_siting:
    st.header("📍 Otimizador de Localização para Novas Usinas de Pirólise")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        w_carbon = st.slider("Importância do Potencial de Carbono (Sequestro)", 0.0, 1.0, 0.5, 0.05)
    with col_w2:
        w_finance = st.slider("Importância do Potencial Elétrico (Financeiro)", 0.0, 1.0, 0.3, 0.05)
    with col_w3:
        w_logistics = st.slider("Importância da Proximidade Industrial (Logística)", 0.0, 1.0, 0.2, 0.05)
        
    sum_w = w_carbon + w_finance + w_logistics
    w_carbon_n, w_finance_n, w_logistics_n = (w_carbon/sum_w, w_finance/sum_w, w_logistics/sum_w) if sum_w > 0 else (0.33, 0.33, 0.33)

    INDUSTRIAL_HUBS = [
        {"municipio": "Joinville", "lat": -26.30, "lon": -48.84},
        {"municipio": "Florianópolis", "lat": -27.59, "lon": -48.54},
        {"municipio": "Chapecó", "lat": -27.10, "lon": -52.61},
        {"municipio": "Criciúma", "lat": -28.67, "lon": -49.37}
    ]

    def get_logistics_factor(row):
        min_dist = float('inf')
        for hub in INDUSTRIAL_HUBS:
            dist = ((row["lat"] - hub["lat"])**2 + (row["lon"] - hub["lon"])**2)**0.5
            if dist < min_dist: min_dist = dist
        return 1.0 / (1.0 + min_dist)

    df_siting = df_sc_potentials.copy()
    df_siting["Fator_Logistica"] = df_siting.apply(get_logistics_factor, axis=1)
    
    df_siting["Score_Carbono"] = (df_siting["PD_Total_tCO2eq"] / df_siting["PD_Total_tCO2eq"].max()) * 100
    df_siting["Score_Financeiro"] = (df_siting["PE_Total_MWh"] / df_siting["PE_Total_MWh"].max()) * 100
    df_siting["Score_Logistica"] = (df_siting["Fator_Logistica"] / df_siting["Fator_Logistica"].max()) * 100
    
    df_siting["Siting_Score"] = (
        (df_siting["Score_Carbono"] * w_carbon_n) + 
        (df_siting["Score_Financeiro"] * w_finance_n) + 
        (df_siting["Score_Logistica"] * w_logistics_n)
    )
    
    df_siting_sorted = df_siting.sort_values(by="Siting_Score", ascending=False)
    col_sit_map, col_sit_data = st.columns([3, 2])
    
    with col_sit_map:
        st.markdown("🌐 **Ajustes Geográficos de Alinhamento do Mapa**")
        with st.expander("🛠️ Ajuste Fino de Calibração do Mapa de Santa Catarina"):
            col_adj1, col_adj2, col_adj3 = st.columns(3)
            with col_adj1:
                map_x = st.slider("Alinhamento Horizontal (Longitude Oeste)", -55.5, -52.0, -54.08, 0.01)
                map_y = st.slider("Alinhamento Vertical (Latitude Norte)", -26.5, -24.5, -25.75, 0.01)
            with col_adj2:
                map_w = st.slider("Largura Horizontal do Mapa (Graus)", 4.0, 7.5, 5.75, 0.01)
                map_h = st.slider("Altura Vertical do Mapa (Graus)", 2.5, 5.5, 3.82, 0.01)
            with col_adj3:
                map_opacity = st.slider("Opacidade da Imagem de Fundo", 0.1, 1.0, 0.85, 0.05)
                map_source_type = st.radio("Selecione o Mapa Base de SC", ["Vetorizado (Wikimedia)", "Mapa Anexado (Local - WebP)", "Sem Mapa de Fundo"], index=0)

        # Determinar imagem de fundo para o Plotly
        local_map_base64 = get_local_map_base64()
        if map_source_type == "Mapa Anexado (Local - WebP)" and local_map_base64:
            bg_source = local_map_base64
        elif map_source_type == "Sem Mapa de Fundo":
            bg_source = None
        else:
            bg_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/SantaCatarina_MesoMicroMunicip.svg/800px-SantaCatarina_MesoMicroMunicip.svg.png"

        fig_siting_map = px.scatter(
            df_siting_sorted, x="lon", y="lat",
            size="Siting_Score", color="Siting_Score",
            hover_name="municipio",
            hover_data=["regiao", "Residuo_Total_t", "PD_Total_tCO2eq", "PE_Total_MWh", "Siting_Score"],
            color_continuous_scale="Jet",
            labels={"Siting_Score": "Pontuação Ótima (0-100)"},
            range_x=[-54.2, -48.0],
            range_y=[-29.6, -25.6],
            title="Localização Ótima de Usinas no Mapa Municipal de SC"
        )

        if bg_source:
            fig_siting_map.add_layout_image(
                dict(
                    source=bg_source,
                    xref="x",
                    yref="y",
                    x=map_x,
                    y=map_y,
                    sizex=map_w,
                    sizey=map_h,
                    sizing="stretch",
                    opacity=map_opacity,
                    layer="below"
                )
            )

        fig_siting_map.update_layout(
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title="",
                range=[-54.2, -48.0]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title="",
                range=[-29.6, -25.6]
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )

        st.plotly_chart(fig_siting_map, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗺️ Visualizador Otimizado de Mapas Municipais (Cores Reais de Alta Resolução)")
        st.markdown("""
        Para uma visualização ultra-fiel dos limites municipais e dos potenciais de Santa Catarina (como os mapas oficiais de referência), 
        utilize o seletor abaixo. Ele renderiza a imagem real mapeada de forma instantânea e otimizada para computadores e celulares:
        """)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_crop = st.selectbox("Selecione a Cultura para o Mapa de Alta Resolução", ["Arroz", "Soja", "Milho", "Trigo"])
        with col_m2:
            sel_year = st.selectbox("Selecione o Ano para o Mapa de Alta Resolução", [2020, 2021, 2022, 2023, 2024], index=4)
            
        # Determina o nome do arquivo com base na cultura e ano
        img_filename = f"analise PD{sel_crop}{sel_year}.png"
        img_fallback_url = f"https://raw.githubusercontent.com/UDESC-Joinville-LIC/biomassa-sc/main/images/analise_PD{sel_crop.lower()}{sel_year}.png"
        
        if os.path.exists(img_filename):
            st.image(img_filename, caption=f"Mapa Municipal Oficial de SC - Potencial de {sel_crop} ({sel_year})", use_container_width=True)
        else:
            st.warning(f"⚠️ Imagem local '{img_filename}' não encontrada no diretório do VS Code.")
            st.markdown(f"""
            **Como visualizar o Mapa Municipal com Cores Reais:**
            1. Baixe o arquivo **`analise PD{sel_crop}{sel_year}.png`** do painel de **Fontes** à esquerda no Gemini Notebook.
            2. Cole-o na **mesma pasta** onde estão salvos o `app-v13.py` e os outros arquivos.
            3. Recarregue esta página no seu navegador para ver o mapa original de alta resolução abrir de forma **100% offline e imediata**!
            """)


        if map_source_type == "Mapa Anexado (Local - WebP)" and not local_map_base64:
            st.warning("⚠️ Arquivo local 'mapa-municípal-do-estado-de-santa-catarina-nome dos municipios.webp' não encontrado no diretório. Carregado o mapa vetorizado como fallback. Baixe a imagem das suas fontes do Notebook e coloque-a na mesma pasta do script para ativação completa.")
        
    with col_sit_data:
        df_ranking_display = df_siting_sorted[
            ["municipio", "regiao", "Score_Carbono", "Score_Financeiro", "Score_Logistica", "Siting_Score"]
        ].head(10).rename(columns={
            "municipio": "Município", "regiao": "Região",
            "Score_Carbono": "Nota Carbono", "Score_Financeiro": "Nota Financeira",
            "Score_Logistica": "Nota Logística", "Siting_Score": "Nota Final"
        })
        st.dataframe(df_ranking_display.style.format("{:.1f}", subset=["Nota Carbono", "Nota Financeira", "Nota Logística", "Nota Final"]), use_container_width=True, hide_index=True)


# ==================== ABA 5: ROTAS LOGÍSTICAS & ESCOAMENTO (NOVA ABA) ====================
with tab_logistics:
    st.header("🚚 Rotas Logísticas e Escoamento de Biocarvão (Biochar)")
    st.markdown("""
    Esta seção apresenta o modelo de **planejamento e simulação logística de escoamento do biocarvão** produzido pelas usinas de pirólise 
    até os polos de solo agrícola em Santa Catarina para sequestro permanente de carbono [RELATORIO_SEMESTRAL_POS_DOUTORADO_28.08.2026_assinado.pdf].
    
    O sistema calcula a distância de transporte pelas rodovias federais e estaduais catarinenses de acordo com o **Mapa Rodoviário de Santa Catarina** [97] 
    e computa os custos financeiros de transporte, pedágios, queima de combustível e as emissões resultantes de CO2 para caminhões tradicionais, 
    bem como para frotas elétricas (EV) e de hidrogênio (H2), em conformidade com as diretrizes metodológicas de **Tang et al. (2025)** [1-s2.0-S0306261925006051-main.pdf] 
    e planejamento multienergético de **Apata (2025)** [1-s2.0-S2352484725002410-main.pdf].
    """)

    import networkx as nx
    import math

    # Criação do Grafo de Rodovias de SC
    G = nx.Graph()
    nodes = {
        "Joinville": (-48.84, -26.30),
        "Massaranduba": (-49.00, -26.61),
        "Itajaí": (-48.66, -26.90),
        "Florianópolis": (-48.54, -27.59),
        "Tubarão": (-48.97, -28.47),
        "Criciúma": (-49.37, -28.67),
        "Turvo": (-49.67, -28.92),
        "Lages": (-50.32, -27.81),
        "Campos Novos": (-51.22, -27.40),
        "Joaçaba": (-51.50, -27.17),
        "Chapecó": (-52.61, -27.10),
        "São Miguel do Oeste": (-53.52, -26.87),
        "Blumenau": (-49.06, -26.91),
        "Rio do Sul": (-49.64, -27.21),
        "Curitibanos": (-50.58, -27.28),
        "Canoinhas": (-50.38, -26.17),
        "Mafra": (-49.80, -26.11),
        "Papanduva": (-50.14, -26.27)
    }

    # Edges representing highway routes with distances in km (based on road map and geographic reality of SC)
    G.add_edge("Joinville", "Massaranduba", weight=35)
    G.add_edge("Massaranduba", "Itajaí", weight=60)
    G.add_edge("Itajaí", "Florianópolis", weight=95)
    G.add_edge("Florianópolis", "Tubarão", weight=135)
    G.add_edge("Tubarão", "Criciúma", weight=50)
    G.add_edge("Criciúma", "Turvo", weight=40)
    
    G.add_edge("Florianópolis", "Lages", weight=220)
    G.add_edge("Lages", "Campos Novos", weight=120)
    G.add_edge("Campos Novos", "Joaçaba", weight=45)
    G.add_edge("Joaçaba", "Chapecó", weight=125)
    G.add_edge("Chapecó", "São Miguel do Oeste", weight=130)
    
    G.add_edge("Itajaí", "Blumenau", weight=55)
    G.add_edge("Blumenau", "Rio do Sul", weight=90)
    G.add_edge("Rio do Sul", "Curitibanos", weight=110)
    G.add_edge("Curitibanos", "Campos Novos", weight=65)
    
    G.add_edge("Mafra", "Papanduva", weight=60)
    G.add_edge("Papanduva", "Curitibanos", weight=140)
    G.add_edge("Curitibanos", "Lages", weight=80)
    G.add_edge("Mafra", "Canoinhas", weight=55)
    G.add_edge("Canoinhas", "Papanduva", weight=45)

    log_col1, log_col2 = st.columns([1.0, 1.2])

    with log_col1:
        # Destaque patriótico com a bandeira de Santa Catarina e subheader unificado
        col_log_h1, col_log_h2 = st.columns([3.2, 1.0])
        with col_log_h1:
            st.subheader("📋 Parâmetros Logísticos")
        with col_log_h2:
            st.image(SC_FLAG_BASE64, width=120, caption="Bandeira de SC")
        
        # Origin usina mapping
        plant_names_map = {
            "Usina_Joinville_Pir": "Joinville",
            "Usina_CamposNovos_Pir": "Campos Novos",
            "Usina_Turvo_Pir": "Turvo",
            "Usina_Massaranduba_Pir": "Massaranduba",
            "Usina_Chapeco_Pir": "Chapecó"
        }
        sel_plant_log = st.selectbox("Usina Produtora de Origem (Biocarvão)", list(plant_names_map.keys()))
        origin_node = plant_names_map[sel_plant_log]

        # Destination soil hubs mapping
        dest_names_map = {
            "Planalto Serrano (Lages - Solo Florestal)": "Lages",
            "Oeste (São Miguel do Oeste - Cultivos de Milho/Soja)": "São Miguel do Oeste",
            "Sul (Turvo / Araranguá - Cultivos de Arroz)": "Turvo",
            "Planalto Norte (Canoinhas - Cultivos de Trigo/Soja)": "Canoinhas",
            "Vale do Itajaí (Rio do Sul - Solo Agrícola Diverso)": "Rio do Sul"
        }
        sel_dest_log = st.selectbox("Polo Agrícola de Destino (Solo)", list(dest_names_map.keys()))
        dest_node = dest_names_map[sel_dest_log]

        # Truck configuration
        log_truck = st.selectbox("Tecnologia da Frota de Caminhões", [
            "Caminhão Médio (Diesel - Euro V)", 
            "Caminhão Pesado (Diesel - Euro VI)", 
            "Caminhão Pesado Elétrico (EV - Zero Local)", 
            "Caminhão Pesado Hidrogênio (H2 - Emissão Zero)"
        ], index=1)

        # Biochar amount
        biochar_t = st.slider("Volume de Biocarvão Escoado (Toneladas/ano)", min_value=100, max_value=25000, value=5000, step=100)

        # Calculando Rota
        path = nx.shortest_path(G, source=origin_node, target=dest_node, weight="weight")
        distance = nx.shortest_path_length(G, source=origin_node, target=dest_node, weight="weight")

        # Configurações físicas do tipo de caminhão selecionado
        truck_params = {
            "Caminhão Médio (Diesel - Euro V)": {"payload": 10.0, "consumption": 4.0, "fuel_price": 6.10, "co2_rate": 1.10, "label": "Diesel"},
            "Caminhão Pesado (Diesel - Euro VI)": {"payload": 25.0, "consumption": 2.5, "fuel_price": 6.10, "co2_rate": 1.60, "label": "Diesel"},
            "Caminhão Pesado Elétrico (EV - Zero Local)": {"payload": 20.0, "consumption": 1.4, "fuel_price": 0.55, "co2_rate": 0.14, "label": "Eletricidade"},
            "Caminhão Pesado Hidrogênio (H2 - Emissão Zero)": {"payload": 22.0, "consumption": 0.08, "fuel_price": 32.00, "co2_rate": 0.00, "label": "Hidrogênio"}
        }

        tp = truck_params[log_truck]
        payload = tp["payload"]
        consumption = tp["consumption"]
        fuel_price = tp["fuel_price"]
        co2_rate = tp["co2_rate"]

        num_trips = math.ceil(biochar_t / payload)
        total_dist_km = distance * 2 * num_trips

        # Cálculos de consumo e custos
        if tp["label"] == "Diesel":
            energy_consumed = total_dist_km / consumption
            energy_unit = "litros de Diesel S10"
            fuel_cost = energy_consumed * fuel_price
        elif tp["label"] == "Eletricidade":
            energy_consumed = total_dist_km * consumption
            energy_unit = "kWh de energia limpa"
            fuel_cost = energy_consumed * fuel_price
        else:
            energy_consumed = total_dist_km * consumption
            energy_unit = "kg de Hidrogênio Verde"
            fuel_cost = energy_consumed * fuel_price

        # Pedágios e manutenção
        toll_rate_per_segment = 16.50
        num_segments = len(path) - 1
        total_tolls = num_segments * num_trips * 2 * toll_rate_per_segment
        driver_maint_cost = total_dist_km * 1.35
        total_transport_cost = fuel_cost + total_tolls + driver_maint_cost

        # Emissões e Sequestro Líquido (Baseado no Relatório de Pós-Doutorado [110, 113])
        # 1 tonelada de biochar com 58.92% de carbono sequestra estável:
        # CO2eq = biochar_t * 0.5892 * (44/12) = biochar_t * 2.1604 tCO2eq
        gross_captured_t = biochar_t * 2.1604
        transport_emissions_t = (total_dist_km * co2_rate) / 1000.0
        net_captured_t = gross_captured_t - transport_emissions_t
        logistics_efficiency = (net_captured_t / gross_captured_t) * 100 if gross_captured_t > 0 else 0.0

        st.markdown("---")
        st.subheader("📊 Indicadores Físico-Financeiros")
        kpi_l1, kpi_l2 = st.columns(2)
        with kpi_l1:
            st.metric("🛣️ Distância do Trajeto de Ida", f"{distance:.1f} km", help="Distância calculada sobre a malha de estradas reais de Santa Catarina.")
            st.metric("🚛 Total de Viagens Requeridas", f"{num_trips} viagens", delta=f"{payload}t de carga útil/caminhão")
        with kpi_l2:
            st.metric("⚡ Energia Consumida", f"{energy_consumed:,.1f} {energy_unit}")
            st.metric("💸 Custo de Transporte Total", f"R$ {total_transport_cost:,.2f}", delta="Combustível, Pedágios e Mão de obra")

    with log_col2:
        st.subheader("🗺️ Traçado da Rota Logística no Mapa de SC")
        
        st.markdown("🌐 **Ajustes Geográficos de Alinhamento do Mapa**")
        with st.expander("🛠️ Ajuste Fino de Calibração do Mapa de Santa Catarina (Logística)"):
            col_adj_log1, col_adj_log2, col_adj_log3 = st.columns(3)
            with col_adj_log1:
                log_map_x = st.slider("Alinhamento Horizontal (Logística)", -55.5, -52.0, -54.08, 0.01, key="log_slider_x")
                log_map_y = st.slider("Alinhamento Vertical (Logística)", -26.5, -24.5, -25.75, 0.01, key="log_slider_y")
            with col_adj_log2:
                log_map_w = st.slider("Largura Horizontal do Mapa (Logística)", 4.0, 7.5, 5.75, 0.01, key="log_slider_w")
                log_map_h = st.slider("Altura Vertical do Mapa (Logística)", 2.5, 5.5, 3.82, 0.01, key="log_slider_h")
            with col_adj_log3:
                log_map_opacity = st.slider("Opacidade da Imagem de Fundo (Logística)", 0.1, 1.0, 0.85, 0.05, key="log_slider_opacity")
                log_map_source_type = st.radio("Selecione o Mapa Base de SC (Logística)", ["Mapa Anexado (Local - WebP)", "Mapa Rodoviário Anexado (Local - PDF)", "Vetorizado (Wikimedia)", "Sem Mapa de Fundo"], index=0, key="log_radio_source")

        # Plotly Map Visualization
        fig_log_map = go.Figure()

        # 1. Desenhar a malha de rodovias de SC em cinza claro
        for edge in G.edges():
            n1, n2 = edge
            x_coords = [nodes[n1][0], nodes[n2][0]]
            y_coords = [nodes[n1][1], nodes[n2][1]]
            fig_log_map.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode="lines",
                line=dict(color="#D3D3D3", width=2, dash="dash"),
                hoverinfo="none",
                showlegend=False
            ))

        # 2. Destacar a Rota Ativa calculada em azul cobalto
        path_x = [nodes[node][0] for node in path]
        path_y = [nodes[node][1] for node in path]
        fig_log_map.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode="lines+markers",
            line=dict(color="#0056b3", width=5),
            marker=dict(size=8, color="#003366"),
            name="Rota Rodoviária de Escoamento",
            hoverinfo="text",
            hovertext=" -> ".join(path)
        ))

        # 3. Marcadores de Origem e Destino com ícones e textos
        fig_log_map.add_trace(go.Scatter(
            x=[nodes[origin_node][0]], y=[nodes[origin_node][1]],
            mode="markers+text",
            marker=dict(symbol="star", size=16, color="#DA291C", line=dict(color="white", width=1.5)),
            text=[f"Usina Origem: {origin_node}"],
            textposition="top center",
            name="Usina de Pirólise"
        ))

        fig_log_map.add_trace(go.Scatter(
            x=[nodes[dest_node][0]], y=[nodes[dest_node][1]],
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=16, color="#046A38", line=dict(color="white", width=1.5)),
            text=[f"Solo Sequestro: {dest_node}"],
            textposition="bottom center",
            name="Disposição no Solo"
        ))

        # Configurações do layout do mapa para sobreposição correta
        local_map_base64 = get_local_map_base64()
        pdf_map_base64 = get_pdf_map_base64()
        if log_map_source_type == "Mapa Anexado (Local - WebP)" and local_map_base64:
            bg_source_log = local_map_base64
        elif log_map_source_type == "Mapa Rodoviário Anexado (Local - PDF)" and pdf_map_base64:
            bg_source_log = pdf_map_base64
        elif log_map_source_type == "Mapa Rodoviário Anexado (Local - PDF)" and local_map_base64:
            bg_source_log = local_map_base64 # fallback
        elif log_map_source_type == "Sem Mapa de Fundo":
            bg_source_log = None
        else:
            bg_source_log = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/SantaCatarina_MesoMicroMunicip.svg/800px-SantaCatarina_MesoMicroMunicip.svg.png"

        # Slider values are dynamically mapped/calibrated for the road network background
        if bg_source_log:
            fig_log_map.add_layout_image(
                dict(
                    source=bg_source_log,
                    xref="x", yref="y",
                    x=log_map_x, y=log_map_y,
                    sizex=log_map_w, sizey=log_map_h,
                    sizing="stretch",
                    opacity=log_map_opacity,
                    layer="below"
                )
            )

        fig_log_map.update_layout(
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title="",
                range=[-54.2, -48.0]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title="",
                range=[-29.6, -25.6]
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_log_map, use_container_width=True)

        # KPIs de Balanço de Carbono Líquido
        st.markdown("#### 🍃 Balanço de Descarbonização Líquida (*Net Carbon Sequestration*)")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("🌱 Sequestro Bruto (Biochar no Solo)", f"{gross_captured_t:,.1f} tCO2eq", help="Quantidade total de carbono retido fisicamente pelo biocarvão de forma permanente.")
        with col_c2:
            st.metric("🚛 Emissões do Transporte", f"{transport_emissions_t:,.2f} tCO2eq", delta="- Emissões Fiscais do Caminhão" if transport_emissions_t > 0 else "Zero Emissão", delta_color="inverse")
        with col_c3:
            st.metric("🎯 Sequestro Líquido Real", f"{net_captured_t:,.1f} tCO2eq", delta=f"{logistics_efficiency:.2f}% de Ecoeficiência")

        if tp["label"] == "Eletricidade":
            st.success("💡 **Acoplamento Setorial Inteligente (Apata, 2025):** Como você está utilizando frotas elétricas (EV), você pode utilizar a própria eletricidade limpa de cogeração gerada em tempo real pelas usinas para recarregar as baterias dos caminhões, operando um ciclo fechado de descarbonização de 100% de ecoeficiência!")
        elif tp["label"] == "Diesel":
            st.warning("⚠️ **Atenção:** O uso de caminhões a diesel reduz a eficiência líquida do sequestro devido à queima de combustíveis fósseis nas rodovias. Considere apoiar políticas públicas de incentivo a frotas elétricas ou hidrogênio para acelerar o Net Zero 2030 das indústrias.")

    # Seção para o Relatório Técnico Integrado (Download e Leitura)
    st.markdown("---")
    st.subheader("📥 Relatório Técnico de Viabilidade Logística (PDF)")
    st.markdown("""
    Disponibilizamos abaixo o documento científico oficializado de viabilidade e planejamento do projeto de pós-doutorado, 
    focado no escoamento de biocarvão para a **Whirlpool Joinville** e conformidade perante o **SBCE**. 
    Você pode baixá-lo ou ler suas seções diretamente na tela:
    """)
    
    # Busca segura pelo arquivo PDF do relatório nas fontes e no ambiente
    pdf_paths = [
        "relatorio-logistica-biocarvao-v2.pdf",
        "artifacts/relatorio-logistica-biocarvao-v2.pdf",
        "/workspace/artifacts/relatorio-logistica-biocarvao-v2.pdf"
    ]
    pdf_data = None
    for p_path in pdf_paths:
        if os.path.exists(p_path):
            try:
                with open(p_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                break
            except Exception:
                pass
                
    if pdf_data:
        st.download_button(
            label="📥 Baixar Relatório Técnico de Viabilidade Logística Completo (PDF)",
            data=pdf_data,
            file_name="relatorio-logistica-biocarvao-v2.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ O arquivo do relatório 'relatorio-logistica-biocarvao-v2.pdf' não foi encontrado localmente. Certifique-se de baixá-lo no painel de Fontes ou Studio e colocá-lo na pasta de execução local.")

    # Exposição das Seções do Relatório para Leitura Rápida
    with st.expander("📖 Ler o Relatório Técnico na Tela (Estrutura Completa Verificada)"):
        st.markdown("""
        ### **PLANEJAMENTO LOGÍSTICO MULTIECOEFICIENTE PARA O ESCOAMENTO DE BIOCARVÃO E SEQUESTRO DE CARBONO EM SANTA CATARINA**
        *Relatório Técnico de Viabilidade das Rotas de Descarbonização e Integração com o SBCE para a Whirlpool Joinville*
        
        ---
        
        #### **1. Fundamentação Científica do Biocarvão no Solo**
        O acoplamento setorial entre o resíduo agrícola e o solo por de pirólise térmica distribuída representa uma solução de vanguarda no contexto de Sistemas Multienergia (MES), conforme proposto por Apata (2025). A conversão de resíduos abundantes no campo (palha, casca e sabugo) em um reator de pirólise gera gás de síntese (para cogeração elétrica) e biocarvão (biochar). O biocarvão produzido apresenta alta estabilidade térmica e um teor de carbono puro em massa de 58,92%, o qual se mantém inalterável e estável por mais de 500 anos quando incorporado ao solo agrícola catarinense, operando como uma tecnologia altamente confiável de remoção direta de dióxido de carbono (CDR).
        
        Além do sequestro físico permanente, a disposição final do biocarvão no solo promove co-benefícios agronômicos indispensáveis à agricultura do estado. O material atua como um condicionador estrutural, aumentando a porosidade, a capacidade de retenção de água (umidade) e a fixação de nutrientes no solo de cultivos. Essa dinâmica eleva o rendimento médio das lavouras das cooperativas fornecedoras de biomassa e reduz a dependência de fertilizantes químicos importados, gerando valor econômico direto e reduzindo custos na cadeia agrícola estadual.
        
        ---
        
        #### **2. Alinhamento de Metas de Descarbonização: Whirlpool Joinville**
        A Whirlpool Corporation estabeleceu em seu Relatório de Sustentabilidade de 2024 o compromisso global de alcançar emissões líquidas zero (Net Zero) nos Escopos 1 e 2 de suas fábricas e operações até 2030. No cenário brasileiro, a unidade fabril de Joinville alcançou um marco histórico em 2024: compensou 100% de seu consumo elétrico (Escopo 2) por meio de Certificados de Energia Renovável (RECs) e geração solar local. Diante disso, o desafio tecnológico e regulatório central para o compliance sob o SBCE (Sistema Brasileiro de Comércio de Emissões) reside no abatimento ou compensação de suas emissões diretas de Escopo 1, originadas predominantemente pela queima de gás natural em fornos de cura de pintura e processos térmicos.
        
        O biocarvão gerado a partir de resíduos de Santa Catarina apresenta um perfil de permanência extrema e risco quase nulo de re-emissão perante alternativas tradicionais como o plantio de árvores, o qual é vulnerável a incêndios e secas (como os incêndios florestais de Coahuila descritos no apêndice do relatório). Para neutralizar a meta residual de Escopo 1 da Whirlpool Joinville, estimada em 10.000 tCO2eq/ano, o sistema multiagente do LIC/UDESC demonstra que o processamento e escoamento planejado de cerca de 46.300 t/ano de resíduos agrícolas locais é fisicamente suficiente para suprir de forma sustentável e barata toda a necessidade de remoção biológica.
        
        ---
        
        #### **3. Metodologia de Mapeamento de Rotas e Resíduos por Região**
        Para calcular o traçado real do escoamento, modelamos a infraestrutura viária de Santa Catarina por meio de um grafo computacional complexo (BR-101, BR-282, BR-470, BR-116). Foram mapeadas quatro rotas estratégicas focando na proximidade e no aproveitamento do resíduo de cultura agrícola dominante de cada região geográfica, em conformidade com os dados municipais de produtividade do IBGE/SIDRA:
        
        *   **3.1. Rota Região Sul (Resíduo Dominante: Arroz):**
            A cultura do arroz irrigado é altamente concentrada no Sul catarinense (regiões de Turvo, Araranguá e Tubarão). Mapeamos o fluxo logístico ligando a bacia agrícola até a usina regional de Turvo (BR-101), escoando o biocarvão produzido diretamente para incorporação nos solos das lavouras de arroz locais. Esta rota caracteriza-se por curtíssimas distâncias médias (40 km ida e volta), minimizando os custos de queima de diesel e o frete por tonelada.
        *   **3.2. Rota Região Norte (Resíduo Dominante: Arroz / Soja):**
            O Norte catarinense (região de Joinville, Guaramirim e Massaranduba) apresenta expressivos volumes de casca de arroz e palha de soja. O escoamento do biocarvão é planejado de Joinville até Massaranduba via BR-101 e SC-108, permitindo o tratamento de resíduos industriais locais e a devolução de nutrientes aos cultivos adjacentes. Distância de trajeto estipulada em 35 km (ida).
        *   **3.3. Rota Região Planalto Serrano (Resíduo Dominante: Soja / Trigo):**
            Campos Novos destaca-se historicamente com o maior volume bruto de resíduos agrícolas do estado (municípios com até 355 mil toneladas anuais no PAM/IBGE de 2024), onde 73% do peso total da colheita de soja é considerado resíduo. Mapeamos a rota de escoamento de Campos Novos a Lages via BR-282 (120 km), aproveitando os resíduos para gerar biocarvão e incorporá-lo na vasta bacia de reflorestamento e solos silviculturais do Planalto Serrano catarinense.
        *   **3.4. Rota Região Oeste (Resíduo Dominante: Milho / Soja):**
            O Oeste de Santa Catarina é o principal cinturão de produção de milho (onde palha e sabugo equivalem a 58% do peso de grãos). Mapeamos a rota logística ligando a Usina de Chapecó aos polos agrícolas de São Miguel do Oeste via BR-282 (130 km). A modelagem foca no uso de frotas de Caminhões Elétricos (EV) para escoamento, acoplando a energia limpa de cogeração gerada pelas usinas para as estações de recarga rápida de baterias, resultando em ecoeficiência logística de 99,73%.
            
        ---
        
        #### **4. Mapeamento das Melhores Rotas Logísticas por Região de Santa Catarina**
        O mapa dinâmico Plotly acima ilustra graficamente os trajetos rodoviários ótimos calculados em tempo real, sobrepondo as rotas sobre a cartografia municipal real e permitindo um ajuste milimétrico para fins de apresentação e relatórios.
        
        ---
        
        #### **5. Resultados das Simulações de Ecoeficiência Logística**
        Para validar e quantificar cientificamente as emissões, o motor multiagente (mas_engine_v5.py) realizou o cálculo do balanço de carbono líquido de cada trajeto rodoviário real. O balanço subtrai as emissões dos escapamentos dos caminhões pesados da carga de sequestro bruto proporcionada pelo biocarvão retido permanentemente no solo:
        
        *   **Rota Norte (Arroz):** Joinville -> Massaranduba | 35.0 km | Sequestro Líquido: **10.795,5 tCO2 | Ecoeficiência: 99,94%**
        *   **Rota Sul (Arroz):** Turvo -> Criciúma | 40.0 km | Sequestro Líquido: **25.485,2 tCO2 | Ecoeficiência: 99,92%**
        *   **Rota Planalto (Soja):** Campos Novos -> Lages | 120.0 km | Sequestro Líquido: **10.539,6 tCO2 | Ecoeficiência: 97,57%**
        *   **Rota Oeste (Milho):** Chapecó -> S.M. Oeste | 130.0 km | Sequestro Líquido: **75.391,3 tCO2 | Ecoeficiência: 99,99%**
        
        ---
        
        #### **6. Discussão e Acoplamento Setorial Inteligente**
        Os resultados provam que a eficiência de sequestro do biocarvão no solo permanece extremamente alta (superior a 97.5% em todas as rotas), inclusive em trajetos de longa distância rodoviária. Isso decorre da alta densidade e do excepcional fator de fixação de carbono do biocarvão por tonelada (2,1604 tCO2eq/t) perante as baixas emissões dos caminhões de transporte.
        Conforme as premissas de Apata (2025), o acoplamento setorial do sistema elétrico e de transporte atinge seu ótimo ao adotar frotas de Caminhões Elétricos (EV) carregadas diretamente com a eletricidade excedente de cogeração térmica da usina de pirólise. Esse ciclo de realimentação energética circular elimina por completo as emissões de combustível fóssil (elevando a eficiência logística para 99,99%) e blinda os custos operacionais das usinas e cooperativas contra as flutuações de preços internacionais de derivados de petróleo, fornecendo uma transição viável, rentável e segura.
        """)

    st.markdown("---")


# ==================== ABA 4: MERCADO MULTIAGENTE ====================
with tab_mas:
    st.header("🤖 Interação do Sistema Multiagente (MAS)")
    st.markdown(f"**Modo de Regulação Ativo:** `{sbce_mode}` (Preço do crédito de carbono: **R$ {carbon_price_display:.2f}/tCO2eq**)")
    
    st.subheader("🏢 Resultados dos Agentes Usinas de Pirólise")
    st.dataframe(
        df_plants.style.format({
            "Biomassa Processada (t)": "{:,.1f}",
            "Eletricidade (MWh)": "{:,.1f}",
            "Créditos Carbono (tCO2eq)": "{:,.1f}",
            "Investimento CAPEX": "R$ {:,.2f}",
            "Lucro Líquido (R$/ano)": "R$ {:,.2f}",
            "Payback (Anos)": lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
        }),
        use_container_width=True, hide_index=True
    )
    
    st.subheader("🏭 Resultados dos Agentes Indústrias")
    st.dataframe(
        df_industries.style.format({
            "Demanda (MWh)": "{:,.0f}",
            "Meta CO2 (tCO2)": "{:,.0f}",
            "Eletricidade Contratada (MWh)": "{:,.1f}",
            "Créditos Comprados (tCO2eq)": "{:,.1f}",
            "Descarbonização (%)": "{:,.1f}%",
            "Custos SBCE (R$)": "R$ {:,.2f}",
            "Reembolso SBCE (R$)": "R$ {:,.2f}",
            "Economia Financeira Líquida (R$/ano)": "R$ {:,.2f}"
        }),
        use_container_width=True, hide_index=True
    )

    st.write("---")
    st.subheader("💡 Análise do Payback Computacional e Integração de Financiamento ESG")
    
    # 1. Explicação técnica de por que o payback é rápido ou longo
    st.markdown("""
    ### ⚡ Por que o Tempo de Retorno (Payback) é Tão Rápido (< 1 Ano)?
    Conforme observado nos resultados computacionais acima, a maioria das usinas de pirólise catarinenses apresenta um tempo de retorno extremamente rápido (frequentemente **menor que 1 ano**). Isso ocorre devido ao efeito sinérgico de várias variáveis macro e microeconômicas modeladas pelo sistema multiagente:
    
    * **Dupla Rota de Monetização (Dual Revenues):** Ao contrário de usinas térmicas tradicionais que vendem apenas eletricidade, o reator de pirólise fatura em duas frentes de alta margem:
        1. **Venda de Eletricidade Limpa (MWh):** Deslocando a energia convencional do grid por uma tarifa de fomento garantida (R$ 550,00/MWh).
        2. **Venda de Créditos de Remoção de Carbono (Biochar):** O biocarvão seco permanente estocado no solo agrícola de Santa Catarina gera créditos valiosos comercializados no mercado secundário do SBCE (variando de **R$ 80,00 a R$ 200,00/tCO2eq**).
    * **Resíduos de Baixo Custo (Baixo OPEX Variável):** A biomassa catarinense é um resíduo agrícola abundante (casca de arroz, palha de soja, palha de milho). Como o preço de compra pago ao produtor é baixo (R$ 150,00/tonelada), o custo operacional de insumos é rapidamente amortizado.
    * **Subsídio Estrutural de CAPEX (Leilão por Consignação):** Sob as regras do **Leilão por Consignação do SBCE** (Guo et al., 2024), 15% do investimento inicial (CAPEX) das usinas de pirólise é subsidiado de forma não reembolsável direto dos fundos de transição climática arrecadados pelo leilão do governo, encolhendo drasticamente o payback técnico.
    * **Altíssimo Volume e Eficiência Física:** Cada tonelada de casca de arroz gera cerca de **0,95 MWh de energia real** (eficiência elétrica de 25% e LHV de 13,75 MJ/kg) e neutraliza **0,2160 tCO2eq** permanentes no solo (teor de carbono de 58,92% em massa), otimizando a escala.
    
    #### ⚠️ Quando o Payback se Torna Longo ou Inviável?
    * **Preço Excessivo de Matéria-Prima:** Se o preço pago aos agricultores/cooperativas pela biomassa ultrapassar R$ 250,00/tonelada, a margem de lucro operacional é comprimida.
    * **Baixa Escala de Operação (Taxa de Coleta Insuficiente):** Se a taxa de aproveitamento e logística de coleta na região for menor que 10%, a usina opera abaixo do ponto de equilíbrio técnico, sendo incapaz de cobrir o OPEX fixo (calculado como 5% do CAPEX anual).
    * **Baixo Preço de Carbono (Alocação Gratuita):** Se a regulação do SBCE for ineficiente e mantiver o preço do carbono abaixo de R$ 80,00/tCO2eq, a rota de créditos voluntários não cobre o custo de transporte intermunicipal.
    """)

    st.markdown("""
    ### 🏦 Simulação de Payback Alavancado por Financiamento
    Nesta seção, integramos de forma dinâmica o **banco escolhido** e a **linha de crédito verde** selecionados na aba **`🏦 Modelos de Financiamento`** para avaliar o payback sob o ponto de vista do proprietário da usina.
    """)
    
    # Dicionário de parâmetros de financiamento
    fin_params_lookup = {
        "BNDES Fundo Clima": {"juros": 5.0, "prazo": 144, "carencia": 36, "banco": "BNDES (Fundo Clima)", "foco": "Aquisição de reatores de pirólise"},
        "Banco do Brasil - Agro Verde": {"juros": 7.5, "prazo": 96, "carencia": 24, "banco": "Banco do Brasil (Agro Verde)", "foco": "Logística e fomento de resíduos agrícolas"},
        "Caixa ESG Infraestrutura": {"juros": 9.25, "prazo": 120, "carencia": 24, "banco": "Caixa Econômica Federal", "foco": "Cogeração e tratamento de lodo/resíduos"},
        "Desenvolve SC Sustentável": {"juros": 8.25, "prazo": 72, "carencia": 18, "banco": "Desenvolve SC (Agência de Fomento SC)", "foco": "Minigeração térmica distribuída"}
    }
    
    # Busca segura dos parâmetros a partir da aba de financiamento
    linha_ativa = st.session_state.get('linha_selecionada', "BNDES Fundo Clima")
    params_ativo = fin_params_lookup[linha_ativa]
    juros_ativo = params_ativo["juros"]
    prazo_meses_ativo = params_ativo["prazo"]
    carencia_meses_ativo = params_ativo["carencia"]
    banco_ativo = params_ativo["banco"]
    
    st.info(f"🏛️ **Linha Ativa do Simulador:** **{linha_ativa}** operada pelo **{banco_ativo}** | Juros: **{juros_ativo:.2f}% a.a.** | Prazo: **{prazo_meses_ativo} meses ({prazo_meses_ativo/12:.1f} anos)** com **{carencia_meses_ativo} meses ({carencia_meses_ativo/12:.1f} anos) de carência**.")
    
    col_mas_f1, col_mas_f2 = st.columns(2)
    with col_mas_f1:
        proprietario_ativo = st.selectbox(
            "Selecione o Perfil do Proprietário (Agente Investidor):",
            ["Investidores Independentes (Foco em Retorno de Capital Próprio / Equity)", 
             "A Própria Indústria (Autoprodução / Descarbonização Integrada de Joinville)"]
        )
    with col_mas_f2:
        fin_pct_slider = st.slider(
            "Proporção do Investimento Financiado (% do CAPEX):",
            min_value=0, max_value=100, value=80, step=5,
            help="Qual a porcentagem do Investimento CAPEX de cada usina que será coberta por financiamento bancário.",
            key="fin_pct_slider_mas"
        )
        
    fin_pct = fin_pct_slider / 100.0
    prazo_anos = prazo_meses_ativo / 12.0
    
    fin_results = []
    for _, row in df_plants.iterrows():
        usina_name = row["Usina"]
        capex_total = row["Investimento CAPEX"]
        lucro_anual = row["Lucro Líquido (R$/ano)"]
        
        # Investimento
        capex_financiado_usina = capex_total * fin_pct
        equity_usina = capex_total * (1.0 - fin_pct)
        
        # Serviço da dívida anual (PMT)
        if capex_financiado_usina > 0:
            if juros_ativo > 0:
                i = juros_ativo / 100.0
                pmt_anual = capex_financiado_usina * (i / (1 - (1 + i) ** (-prazo_anos)))
            else:
                pmt_anual = capex_financiado_usina / prazo_anos if prazo_anos > 0 else 0.0
        else:
            pmt_anual = 0.0
            
        if proprietario_ativo == "Investidores Independentes (Foco em Retorno de Capital Próprio / Equity)":
            # Caixa livre dos acionistas (FCFE)
            fluxo_liquido = lucro_anual - pmt_anual
            
            if equity_usina <= 0:
                payback_fin = 0.0
            elif fluxo_liquido > 0:
                payback_fin = equity_usina / fluxo_liquido
            else:
                payback_fin = "Inviável (FCFE <= 0)"
                
            fin_results.append({
                "Usina": usina_name,
                "CAPEX Total": capex_total,
                "CAPEX Financiado": capex_financiado_usina,
                "Capital Próprio (Equity)": equity_usina,
                "Prestação Anual (Juros+Amort)": pmt_anual,
                "Fluxo de Caixa Livre (FCFE)": fluxo_liquido,
                "Payback Alavancado (Anos)": payback_fin
            })
            
        else: # "A Própria Indústria (Autoprodução / Descarbonização Integrada de Joinville)"
            # Se for a própria indústria, vamos calcular o ganho integrado de Joinville!
            wh_row = df_industries[df_industries["Indústria"] == "Whirlpool_Joinville_Plant"]
            
            if len(wh_row) > 0 and usina_name == "Usina_Joinville_Pir":
                wh_data = wh_row.iloc[0]
                elec_contratada = wh_data["Eletricidade Contratada (MWh)"]
                creditos_comprados = wh_data["Créditos Comprados (tCO2eq)"]
                
                # Ganhos Integrados da Indústria Whirlpool:
                # 1. Economia de Energia: paga electricity_price (R$ 550) vs R$ 680 do grid
                economia_energia = elec_contratada * (680.0 - electricity_price)
                # 2. Economia de Créditos: evita pagar multa do SBCE (auction_price)
                economia_carbono = creditos_comprados * engine.auction_price
                # 3. Lucro Líquido da Usina que agora pertence à Indústria
                lucro_usina = lucro_anual
                
                ganho_integrado_anual = lucro_usina + economia_energia + economia_carbono
                fluxo_liquido = ganho_integrado_anual - pmt_anual
                
                if equity_usina <= 0:
                    payback_fin = 0.0
                elif fluxo_liquido > 0:
                    payback_fin = equity_usina / fluxo_liquido
                else:
                    payback_fin = "Inviável (Fluxo Integrado <= 0)"
                    
                fin_results.append({
                    "Usina": f"{usina_name} (Parceria Whirlpool Joinville)",
                    "CAPEX Total": capex_total,
                    "CAPEX Financiado": capex_financiado_usina,
                    "Capital Próprio (Equity)": equity_usina,
                    "Prestação Anual": pmt_anual,
                    "Ganhos Integrados (R$/ano)": ganho_integrado_anual,
                    "Payback Integrado (Anos)": payback_fin
                })
            else:
                # Outras usinas e indústrias associadas pelo motor
                paired_ind_savings = 0.0
                if usina_name == "Usina_CamposNovos_Pir":
                    paired_ind = df_industries[df_industries["Indústria"] == "Agro_Oeste_Alimentos"]
                elif usina_name == "Usina_Turvo_Pir":
                    paired_ind = df_industries[df_industries["Indústria"] == "Cerâmica_Sul_Revestimentos"]
                elif usina_name == "Usina_Chapeco_Pir":
                    paired_ind = df_industries[df_industries["Indústria"] == "Tech_Floripa_Eletro"]
                else:
                    paired_ind = pd.DataFrame()
                    
                if len(paired_ind) > 0:
                    wh_data = paired_ind.iloc[0]
                    elec_contratada = wh_data["Eletricidade Contratada (MWh)"]
                    creditos_comprados = wh_data["Créditos Comprados (tCO2eq)"]
                    economia_energia = elec_contratada * (680.0 - electricity_price)
                    economia_carbono = creditos_comprados * engine.auction_price
                    lucro_usina = lucro_anual
                    ganho_integrado_anual = lucro_usina + economia_energia + economia_carbono
                else:
                    ganho_integrado_anual = lucro_anual
                    
                fluxo_liquido = ganho_integrado_anual - pmt_anual
                
                if equity_usina <= 0:
                    payback_fin = 0.0
                elif fluxo_liquido > 0:
                    payback_fin = equity_usina / fluxo_liquido
                else:
                    payback_fin = "Inviável"
                    
                fin_results.append({
                    "Usina": usina_name,
                    "CAPEX Total": capex_total,
                    "CAPEX Financiado": capex_financiado_usina,
                    "Capital Próprio (Equity)": equity_usina,
                    "Prestação Anual": pmt_anual,
                    "Ganhos Integrados (R$/ano)": ganho_integrado_anual,
                    "Payback Integrado (Anos)": payback_fin
                })
                
    df_fin = pd.DataFrame(fin_results)
    
    st.markdown("**📊 Detalhamento de Fluxo de Caixa e Retorno Alavancado**")
    if proprietario_ativo == "Investidores Independentes (Foco em Retorno de Capital Próprio / Equity)":
        st.dataframe(
            df_fin.style.format({
                "CAPEX Total": "R$ {:,.2f}",
                "CAPEX Financiado": "R$ {:,.2f}",
                "Capital Próprio (Equity)": "R$ {:,.2f}",
                "Prestação Anual (Juros+Amort)": "R$ {:,.2f}",
                "Fluxo de Caixa Livre (FCFE)": "R$ {:,.2f}",
                "Payback Alavancado (Anos)": lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
            }),
            use_container_width=True, hide_index=True
        )
    else:
        st.dataframe(
            df_fin.style.format({
                "CAPEX Total": "R$ {:,.2f}",
                "CAPEX Financiado": "R$ {:,.2f}",
                "Capital Próprio (Equity)": "R$ {:,.2f}",
                "Prestação Anual": "R$ {:,.2f}",
                "Ganhos Integrados (R$/ano)": "R$ {:,.2f}",
                "Payback Integrado (Anos)": lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
            }),
            use_container_width=True, hide_index=True
        )
        
    st.markdown(f"""
    ### 🎯 Quando é Viável que a Indústria Financie e Adquira a Usina?
    Com base nas simulações integradas acima, a aquisição e o financiamento verticalizado da usina de pirólise por parte da **própria indústria** (como a **Whirlpool** em Joinville) se mostram extremamente viáveis e estratégicos sob as seguintes condições técnicas e regulatórias:
    
    1. **Efeito Alavancagem com Juros Subsidiados (Arbitragem de Juros):**
       Ao utilizar as linhas de crédito verde brasileiras (mapeadas pela *Climate Policy Initiative*), como o **BNDES Fundo Clima (taxa de {juros_ativo:.2f}% a.a.)** em vez de capital comercial tradicional, a indústria capta recursos a um custo de capital significativamente abaixo da Taxa Interna de Retorno (TIR) do reator de pirólise. Isso gera um **efeito alavanca positivo**, reduzindo o payback integrado da indústria para níveis altamente competitivos.
    2. **Mitigação Direta de Custos de Conformidade do SBCE:**
       Com a transição para as fases reguladas de leilão (Leilão por Consignação ou Tradicional), cada tonelada de CO2 de emissões diretas inevitáveis de **Escopo 1** (como a queima de gás natural em Joinville) atrai pesadas multas do governo (R$ 100,00 a R$ 180,00/ton). Ao possuir sua própria usina de biocarvão local, a indústria **evita integralmente estes custos** ao certificar créditos de remoção a um custo interno estável de produção, blindando seu balanço.
    3. **Previsibilidade e Hedge de Custos de Energia:**
       A indústria garante o fornecimento de eletricidade renovável a um preço previsível e contratado (R$ {electricity_price:.2f}/MWh), economizando **R$ {680.0 - electricity_price:.2f} por MWh** em relação às tarifas do grid convencional de mercado livre (PLD / R$ 680,00/MWh). Isso elimina riscos de volatilidade energética e garante estabilidade operacional de longo prazo.
    4. **Aproveitamento de Períodos de Carência:**
       A carência oferecida pelas linhas verdes (ex: **{carencia_meses_ativo} meses no {banco_ativo}**) permite que a indústria instale o reator, comece a processar a biomassa agrícola, e fature receitas antes de pagar o principal da dívida, aliviando integralmente a pressão sobre o fluxo de caixa inicial.
    """)

# ==================== ABA 5: REGULAÇÃO SBCE & LEILÃO ====================
with tab_sbce:
    st.header("🏛️ Avaliação do Sistema Brasileiro de Comércio de Emissões (SBCE)")
    st.markdown(f"""
    O **SBCE** estabelecerá limites de emissões (cap-and-trade) para grandes indústrias no Brasil. 
    Esta simulação avalia o comportamento de agentes e mercado sob **três modos de alocação de quotas de carbono** extraídos da literatura hibridizada de IA (*Guo et al., 2024*):
    """)
    
    sbce_cols = st.columns(3)
    with sbce_cols[0]:
        st.info("""
        **1. Alocação Gratuita (Compliance Suave)**
        - **Quotas Gratuitas:** 90% das metas históricas.
        - **Preço de Leilão:** R$ 0,00/ton.
        - **Preço do Crédito de Biocarvão:** R$ 80,00/tCO2eq.
        - **Objetivo:** Evitar vazamento de carbono e choques de custo iniciais na indústria catarinense.
        """)
    with sbce_cols[1]:
        st.warning("""
        **2. Leilão por Consignação (Fase de Transição)**
        - **Quotas Gratuitas:** 50% das metas.
        - **Preço de Leilão:** R$ 100,00/ton.
        - **Preço do Crédito de Biocarvão:** R$ 120,00/tCO2eq.
        - **Reembolso:** 50% da receita arrecadada retorna para as indústrias como fomento, e usinas recebem 15% de subsídio no CAPEX.
        """)
    with sbce_cols[2]:
        st.error("""
        **3. Leilão Tradicional (Fase Neutra Estrita)**
        - **Quotas Gratuitas:** 0% (compra total).
        - **Preço de Leilão:** R$ 180,00/ton.
        - **Preço do Crédito de Biocarvão:** R$ 200,00/tCO2eq.
        - **Objetivo:** Garantir a descarbonização profunda em longo prazo, gerando receita governamental para políticas macro ambientais.
        """)

    st.subheader("📊 Análise de Impacto das Fases do SBCE nos Agentes")
    
    # Gerar dados dos 3 cenários para exibir gráficos comparativos
    modes = ["Alocação Gratuita", "Leilão por Consignação", "Leilão Tradicional"]
    payback_comparison = []
    savings_comparison = []
    compliance_comparison = []
    
    for m in modes:
        sim_engine = MultiAgentSystemEngineSBCE(
            collect_rate=collect_rate, 
            biomass_price=biomass_price, 
            electricity_price=electricity_price, 
            sbce_mode=m
        )
        sim_engine.run_simulation()
        p_df, i_df = sim_engine.get_summary_df()
        
        for _, row in p_df.iterrows():
            payback_comparison.append({"Cenário SBCE": m, "Usina": row["Usina"], "Payback (Anos)": row["Payback (Anos)"]})
        for _, row in i_df.iterrows():
            savings_comparison.append({"Cenário SBCE": m, "Indústria": row["Indústria"], "Economia Líquida (R$)": row["Economia Financeira Líquida (R$/ano)"]})
            compliance_comparison.append({"Cenário SBCE": m, "Indústria": row["Indústria"], "Custo SBCE (R$)": row["Custos SBCE (R$)"]})
            
    df_pay_comp = pd.DataFrame(payback_comparison)
    df_sav_comp = pd.DataFrame(savings_comparison)
    df_com_comp = pd.DataFrame(compliance_comparison)
    
    fig_cols = st.columns(2)
    with fig_cols[0]:
        fig_pay = px.bar(
            df_pay_comp, x="Usina", y="Payback (Anos)", color="Cenário SBCE", barmode="group",
            title="Tempo de Retorno (Payback) das Usinas por Fase do SBCE",
            color_discrete_sequence=px.colors.qualitative.T10
        )
        st.plotly_chart(fig_pay, use_container_width=True)
    with fig_cols[1]:
        fig_sav = px.bar(
            df_sav_comp, x="Indústria", y="Economia Líquida (R$)", color="Cenário SBCE", barmode="group",
            title="Economia Financeira Líquida das Indústrias por Fase do SBCE",
            color_discrete_sequence=px.colors.qualitative.T10
        )
        st.plotly_chart(fig_sav, use_container_width=True)
        
    st.info("""
    💡 **Análise de Jogo e Políticas Públicas (Grounding Científico):**
    - **A Consignação como Sucesso:** Observe que o **Leilão por Consignação** atinge o menor tempo de payback para as usinas (cerca de 0,41 a 0,49 anos) porque reverte 15% de subsídio de CAPEX direto das receitas tributárias do carbono. 
    - **O Custo de Transição:** Sob o **Leilão Tradicional**, a economia líquida das indústrias cai por conta da alta despesa de leilão, porém a valorização do biocarvão para **R$ 200,00/tCO2eq** impede a insolvência das usinas de pirólise catarinenses, mantendo-as estáveis e lucrativas.
    """)


# ==================== ABA 6: VANTAGENS FINANCEIRAS DAS INDÚSTRIAS ====================
with tab_advantages:
    st.header("💰 Análise de Viabilidade & Vantagens Financeiras para Indústrias em SC")
    st.markdown("""
    A transição para matrizes energéticas limpas, como a energia gerada a partir da **pirólise de resíduos de biomassa**, 
    não é apenas um imperativo ecológico, mas uma decisão de **alta rentabilidade e resiliência estratégica** para as indústrias de Santa Catarina.
    """)
    
    # Grid de KPIs principais das Vantagens
    adv_col1, adv_col2, adv_col3 = st.columns(3)
    with adv_col1:
        st.metric(
            label="⚡ Redução de Custos de Energia",
            value="R$ 130,00/MWh Economizados",
            delta="Tarifa de R$ 550 vs R$ 680 do Grid"
        )
    with adv_col2:
        st.metric(
            label="🏛️ Isenção e Blindagem de Multas SBCE",
            value="Até R$ 180,00/tCO2 Evitado",
            delta="Evitação de Imposto/Quota Carbono"
        )
    with adv_col3:
        st.metric(
            label="💵 Retorno via Reembolso por Consignação",
            value="50% de Repasse de Carbono",
            delta="Mecanismo de Fomento Industrial"
        )
        
    st.write("---")
    
    # Seção Interativa de Demonstração de Economia
    st.subheader("🧮 Simulador Dinâmico de Economia e Payback Corporativo")
    st.markdown("Ajuste os parâmetros abaixo para ver em tempo real a diferença de custos e o ganho anual da sua empresa:")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        demanda_usuario = st.slider("Sua Demanda de Energia Elétrica (MWh/ano)", min_value=1000, max_value=50000, value=10000, step=1000)
        emissoes_usuario = st.slider("Emissões Associadas de Carbono (tCO2eq/ano)", min_value=500, max_value=20000, value=3000, step=500)
        preco_grid_val = st.number_input("Preço Médio da Energia Convencional/Grid (R$/MWh)", value=680.0, step=10.0)
    
    # Cálculos
    custo_energia_conv = demanda_usuario * preco_grid_val
    custo_compliance_conv = emissoes_usuario * 180.0
    custo_total_conv = custo_energia_conv + custo_compliance_conv
    
    co2_evitado_grid = demanda_usuario * 0.1
    co2_restante = max(0.0, emissoes_usuario - co2_evitado_grid)
    
    custo_energia_renov = demanda_usuario * electricity_price
    custo_creditos_carbono = co2_restante * carbon_price_display
    custo_total_renov = custo_energia_renov + custo_creditos_carbono
    
    economia_anual = custo_total_conv - custo_total_renov
    percentual_reducao_custo = (economia_anual / custo_total_conv) * 100 if custo_total_conv > 0 else 0.0
    
    with sim_col2:
        st.markdown("**Comparativo Econômico de Custos Operacionais**")
        df_comp_chart = pd.DataFrame({
            "Categoria": ["Energia", "Carbono / Conformidade", "Total Geral", "Energia", "Carbono / Conformidade", "Total Geral"],
            "Custo Anual (R$)": [custo_energia_conv, custo_compliance_conv, custo_total_conv, custo_energia_renov, custo_creditos_carbono, custo_total_renov],
            "Modelo": ["Matriz Convencional (Cinza)", "Matriz Convencional (Cinza)", "Matriz Convencional (Cinza)", "Matriz Renovável (Biomassa)", "Matriz Renovável (Biomassa)", "Matriz Renovável (Biomassa)"]
        })
        
        fig_adv_comp = px.bar(
            df_comp_chart, x="Categoria", y="Custo Anual (R$)", color="Modelo", barmode="group",
            title="Comparativo de Custos: Convencional vs. Renovável de SC",
            color_discrete_sequence=["#8B0000", "#2E8B57"]
        )
        st.plotly_chart(fig_adv_comp, use_container_width=True)
        
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.success(f"🚀 **Economia Anual Estimada para sua Indústria:** R$ {economia_anual:,.2f}/ano")
    with col_metric2:
        st.info(f"📈 **Redução Total de Custos de Energia & Carbono:** {percentual_reducao_custo:.1f}%")
        
    st.markdown("""
    ### 🛡️ Os 4 Pilares da Vantagem Financeira da Biomassa de Pirólise em SC
    
    1. **Arbitragem e Redução de Tarifa de Energia**:
       A energia convencional proveniente de fontes fósseis marginais ou adquirida no mercado livre apresenta custos elevados (R$ 680,00/MWh). A energia termoelétrica renovável gerada a partir da **pirólise distribuída** utiliza resíduos abundantes locais de Santa Catarina, permitindo contratos bilaterais previsíveis de longo prazo fora da volatilidade do mercado de curto prazo (PLD).
       
    2. **Evitação do Custo de Conformidade do Carbono (SBCE)**:
       Com o mercado regulado de cap-and-trade no Brasil, cada tonelada de CO2eq emitida sem abatimento incorrerá em penalidades significativas ou na obrigação de adquirir quotas caras. A pirólise de resíduos agrícolas gera eletricidade (reduzindo Escopo 2 ao deslocar 0,1 tCO2eq/MWh do grid) e produz **biocarvão (biochar)**, um sumidouro permanente de carbono. Adquirir esses créditos de biochar de usinas locais de Santa Catarina sai **até 55% mais barato** do que disputar quotas em leilões tradicionais do governo.
       
    3. **Aproveitamento de Incentivos e Isenção de Custos SBCE**:
       Sob o modelo de **Leilão por Consignação** que o simulador avalia, as indústrias recebem restituição de 50% das receitas arrecadadas pelo leilão do governo como fomento de transição, enquanto as usinas recebem 15% de subsídio direto em seu CAPEX, estabilizando as tarifas.
       
    4. **Segurança e Estabilidade de Preços (Hedge Fóssil)**:
       A flutuação de combustíveis fósseis como diesel e gás natural importados afeta severamente a indústria de processos (cerâmico, metalúrgico, alimentos). A biomassa de Santa Catarina (como casca de arroz e palha de soja) é um recurso **local, renovável e descorrelacionado** de instabilidades geopolíticas externas, reduzindo custos de transporte e logística.
    """)



# ==================== ABA 7: ESTUDO DE CASO WHIRLPOOL & COMPARAÇÃO DE CAPTURA ====================

# ==================== ABA 8: MODELOS DE FINANCIAMENTO ESG (CPI) ====================
with tab_financing:
    st.header("🏦 Modelos de Financiamento Sustentável no Brasil (CPI)")
    st.markdown("""
    Esta seção apresenta as principais **linhas de crédito verde e sustentável** mapeadas de acordo com a 
    **Plataforma de Linhas de Crédito Sustentável no Brasil** da *Climate Policy Initiative (CPI)*. 
    
    Indústrias catarinenses podem utilizar estes mecanismos para financiar a transição para a biomassa de pirólise com taxas subsidiadas,
    maximizando as vantagens financeiras e garantindo o compliance sob o SBCE.
    """ )
    
    # Cards de Linhas de Crédito
    card_cols = st.columns(4)
    with card_cols[0]:
        st.info("""
        **🏛️ BNDES Fundo Clima**
        * **Taxa de Juros:** 4,0% a 6,15% ao ano (Taxa Verde)
        * **Prazo Total:** Até 144 meses (12 anos)
        * **Carência:** Até 36 meses (3 anos)
        * **Foco:** Aquisição de reatores de pirólise e equipamentos termoelétricos de biomassa.
        """)
    with card_cols[1]:
        st.warning("""
        **🌾 Banco do Brasil - Agro Verde**
        * **Taxa de Juros:** 6,5% a 8,5% ao ano
        * **Prazo Total:** Até 96 meses (8 anos)
        * **Carência:** Até 24 meses (2 anos)
        * **Foco:** Logística, fomento e colheita de resíduos de arroz e soja junto a cooperativas agrícolas de SC.
        """)
    with card_cols[2]:
        st.success("""
        **🏢 Caixa ESG Infraestrutura**
        * **Taxa de Juros:** 8,5% a 10,0% ao ano
        * **Prazo Total:** Até 120 meses (10 anos)
        * **Carência:** Até 24 meses (2 anos)
        * **Foco:** Cogeração térmica e tratamento térmico acoplado de lodo de esgoto (SS).
        """)
    with card_cols[3]:
        st.error("""
        **🗺️ Desenvolve SC Sustentável**
        * **Taxa de Juros:** 7,0% a 9,5% ao ano
        * **Prazo Total:** Até 72 meses (6 anos)
        * **Carência:** Até 18 meses (1,5 ano)
        * **Foco:** Agência de Fomento Estadual para projetos de micro/minigeração térmica distribuída em Santa Catarina.
        """)
        
    st.write("---")
    
    # Novo simulador dinâmico de juros e ganhos
    st.subheader("🧮 Simulador Dinâmico de Linhas de Crédito Verde (CPI)")
    st.markdown("Selecione uma das linhas de crédito verde brasileiras para simular o financiamento do CAPEX da sua usina:")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        linha_selecionada = st.selectbox(
            "Selecione a Linha de Crédito Verde",
            ["BNDES Fundo Clima", "Banco do Brasil - Agro Verde", "Caixa ESG Infraestrutura", "Desenvolve SC Sustentável"],
            key="linha_selecionada"
        )
        capex_financiado = st.slider("Valor do Investimento a Financiar (R$)", min_value=500000, max_value=25000000, value=st.session_state['capex_financiado'], step=500000, key="capex_financiado")
        prazo_comercial = st.number_input("Taxa de Juros de Linhas Comerciais Tradicionais (% a.a.)", value=st.session_state['prazo_comercial'], step=0.5, key="prazo_comercial")
        
    fin_params = {
        "BNDES Fundo Clima": {"juros": 5.0, "prazo": 144, "carencia": 36, "foco": "Aquisição de reatores de pirólise"},
        "Banco do Brasil - Agro Verde": {"juros": 7.5, "prazo": 96, "carencia": 24, "foco": "Logística e fomento de resíduos agrícolas"},
        "Caixa ESG Infraestrutura": {"juros": 9.25, "prazo": 120, "carencia": 24, "foco": "Cogeração e tratamento de resíduos urbanos/lodo"},
        "Desenvolve SC Sustentável": {"juros": 8.25, "prazo": 72, "carencia": 18, "foco": "Projetos estaduais de geração distribuída"}
    }
    
    p_sel = fin_params[linha_selecionada]
    juros_linha = p_sel["juros"]
    prazo_meses = p_sel["prazo"]
    carencia_meses = p_sel["carencia"]
    
    custo_juros_sust = capex_financiado * (juros_linha / 100.0)
    custo_juros_com = capex_financiado * (prazo_comercial / 100.0)
    economia_juros_anual = custo_juros_com - custo_juros_sust
    
    capacidade_estimada_t = (capex_financiado / 2500000.0) * 10000.0
    co2_evitado_estimado = capacidade_estimada_t * 0.2160 + (capacidade_estimada_t * 0.9548 * 0.1)
    
    with col_f2:
        st.markdown(f"### 📊 Relatório Financeiro e Ambiental: **{linha_selecionada}**")
        st.write(f"🎯 **Foco Principal:** {p_sel['foco']}.")
        st.write(f"⏳ **Prazo de Amortização:** {prazo_meses} meses ({prazo_meses/12:.1f} anos) com **{carencia_meses} meses de carência**.")
        
        f_cols = st.columns(2)
        with f_cols[0]:
            st.metric(
                label="📉 Economia Anual de Juros",
                value=f"R$ {economia_juros_anual:,.2f}/ano",
                delta=f"Taxa de {juros_linha:.2f}% a.a."
            )
        with f_cols[1]:
            st.metric(
                label="🌿 Descarbonização Estimada Viabilizada",
                value=f"{co2_evitado_estimado:,.0f} tCO2eq/ano",
                delta="Sequestro via Biocarvão no Solo"
            )
            
        st.markdown(f"""
        * **Custo de Juros Anual Sustentável:** R$ {custo_juros_sust:,.2f}/ano  
        * **Custo de Juros Anual Comercial:** R$ {custo_juros_com:,.2f}/ano  
        * **Prazo de Carência:** Durante os primeiros {carencia_meses/12:.1f} anos, a usina já opera faturando energia elétrica e créditos de carbono antes do início do pagamento do principal!
        """)
        
    st.write("---")
    
    # Ganhos Econômicos e Ambientais detalhados
    st.subheader("📈 Análise Comparativa de Ganhos Econômicos e Ambientais")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("""
        ### 💵 Ganhos Financeiros da Indústria
        * **Redução no Custo de Capital (Arbitragem de Juros):**
          Financiar com o **Fundo Clima** ou linhas ESG a juros de **4% a 8% a.a.** em vez de linhas comerciais tradicionais (taxas de **15% a 20% a.a.** no mercado brasileiro) economiza milhões em despesas financeiras ao longo do projeto.
        * **Amortização e Caixa Flexível:**
          A carência de até 3 anos permite que o reator de pirólise local seja instalado, comece a gerar energia elétrica (MWh) e gere biocarvão para créditos de carbono antes do pagamento da primeira parcela do financiamento.
        * **CAPEX 100% Financiável:**
          Possibilidade de cobrir até 100% do investimento inicial em equipamentos sustentáveis de bioenergia.
        """)
    with col_g2:
        st.markdown("""
        ### 🍃 Ganhos Ambientais da Indústria
        * **Abatimento Imediato de Escopo 1 e 2:**
          O financiamento viabiliza a substituição do gás natural fóssil por gás de síntese e calor renovável da pirólise (Escopo 1), reduzindo a dependência da rede elétrica fóssil (Escopo 2).
        * **Geração de Créditos de Remoção de Alta Permanência (CDR):**
          Garante a posse de créditos de biocarvão (biochar) que retêm o carbono no solo por **mais de 500 anos**, o que atesta conformidade científica sólida perante o mercado e agências regulatórias.
        * **Proteção contra Mudanças de Regulação:**
          Blindagem financeira completa contra a escalada de preços de quotas de leilões tradicionais do SBCE.
        """)
        
    st.write("---")
    st.subheader("🎯 Alinhamento de Metas de Descarbonização: Whirlpool Corporation (NetZero 2030)")
    
    col_wh1, col_wh2 = st.columns(2)
    with col_wh1:
        st.markdown("""
        #### 📈 Metas Globais e Nível Brasil (Whirlpool)
        Com base no **Relatório de Sustentabilidade 2024 da Whirlpool**:
        * **Meta Net Zero 2030 (Escopos 1 e 2):** Compromisso global de zerar emissões em todas as fábricas e operações.
        * **Sucesso Elétrico no Brasil:** A Whirlpool atingiu **100% de correspondência renovável (Escopo 2)** no Brasil em 2024 via RECs e usina solar própria na fábrica de Joinville.
        * **A Meta Brasil para Net Zero 2030:** Com a eletricidade (Escopo 2) já 100% renovável, o desafio central do Brasil é **eliminar ou compensar o Escopo 1 (Direct Emissions)**, associado à queima de gás natural em processos térmicos e cura de pintura.
        """)
    with col_wh2:
        st.markdown("""
        #### 💎 Demanda de Créditos de Carbono Necessários para Net Zero
        Para compensar emissões diretas inevitáveis de Escopo 1 até 2030:
        * **Meta Global de Créditos:** A Whirlpool necessita neutralizar **121.002 tCO₂eq/ano** (emissão total de Escopo 1 de 2024).
        * **Meta Brasil (Unidade Joinville):** A fábrica de Joinville requer cerca de **10.000 tCO₂eq/ano** de créditos de remoção duráveis para atingir o Net Zero 2030 de forma local.
        * **Viabilidade Física da Rota de Biocarvão de SC:** O sequestro de biocarvão gerado nas usinas próximas neutraliza **0,2160 tCO₂eq por tonelada de resíduo**. Para suprir 100% da necessidade de créditos da Whirlpool Joinville, basta processar **~46.300 t/ano** de resíduos agrícolas de arroz, soja e milho da região, gerando um equilíbrio de mercado perfeito via sistema multiagente!
        """)


with tab_whirlpool:
    st.header("🏭 Estudo de Caso Whirlpool (Joinville) & Comparativo de Captura de Carbono")
    st.markdown("""
    Este painel avalia a estratégia de descarbonização da **Whirlpool (Unidade Joinville)**, uma das maiores fabricantes de eletrodomésticos da América Latina,
    com base nas metas e dados reais descritos em seu **Relatório de Sustentabilidade 2024**.
    
    A Whirlpool Corporation assumiu o compromisso global de **alcançar emissões líquidas zero (Net Zero) nos Escopos 1 e 2 de suas fábricas e operações até 2030**.
    - **Escopo 1 (Gás Natural e Combustíveis):** Representa emissões diretas de processos de manufatura (como fornos de cura de tinta e queima direta).
    - **Escopo 2 (Consumo de Eletricidade):** Representa o consumo de energia elétrica. No Brasil, em 2024, a Whirlpool já correspondia **100% de seu consumo com eletricidade renovável (RECs)** e opera uma usina solar na fábrica de Joinville.
    """)
    
    # KPIs específicos da Whirlpool baseados no relatório
    wh_col1, wh_col2, wh_col3 = st.columns(3)
    with wh_col1:
        st.metric(
            label="🌍 Meta Real Whirlpool (Joinville)",
            value="Net Zero 2030",
            delta="Fábricas e Operações Globais"
        )
    with wh_col2:
        st.metric(
            label="⚡ Consumo Global de Energia 2024",
            value="5.056.948 Gigajoules (GJ)",
            delta="41,3% de Fontes Renováveis no Mix"
        )
    with wh_col3:
        st.metric(
            label="📉 Redução de Emissões Globais",
            value="-36% nos Escopos 1 e 2 (2024)",
            delta="3º ano consecutivo com queda de 2 dígitos"
        )
        
    st.write("---")
    
    # Seção Comparativa de Métodos de Captura/Offset
    st.subheader("🌲 Comparativo de Rotas Tecnológicas para Compensação de Emissões")
    st.markdown("""
    Para neutralizar as emissões inevitáveis de seu **Escopo 1 (Joinville)**, estimadas em uma meta de **10.000 tCO2eq/ano** para compensação residual,
    a Whirlpool pode adotar diferentes rotas tecnológicas. Abaixo, comparamos a viabilidade técnica, econômica e a permanência de cada método:
    """)
    
    # Tabela comparativa de métodos
    df_compare_capture = pd.DataFrame({
        "Mecanismo de Captura": [
            "Biocarvão (Biochar - Pirólise de Biomassa SC)",
            "Plantio de Árvores (Reflorestamento Local de Nativas)",
            "Captura Direta de Ar (DAC - Tecnologia de Absorção)",
            "Créditos de Mercado Geral (REDD+ / Evitação de Desmatamento)"
        ],
        "Custo Médio (R$/tCO2eq)": [150.00, 400.00, 4200.00, 60.00],
        "Permanência do Carbono": ["Extrema (> 500 anos)", "Moderada-Baixa (~ 30 anos)", "Extrema (> 1000 anos)", "Muito Baixa (~ 10 anos)"],
        "Tempo de Absorção": ["Imediato (Estocado de forma inerte)", "Lento (Leva 15-20 anos para crescer)", "Imediato (Injeção Geológica Profunda)", "Retrospectivo (Baseado em projetos históricos)"],
        "Riscos de Re-emissão": ["Quase Nulo (Fisicamente inalterável no solo)", "Alto (Incêndios florestais, Pragas, Secas)", "Nulo", "Alto (Falta de adicionalidade ou vazamento)"],
        "Co-benefícios Regionais": [
            "Melhora física do solo, retenção de água e nutrientes na agricultura catarinense",
            "Recuperação de biodiversidade e bacias hidrográficas locais em SC",
            "Nenhum (Apenas captura concentrada em planta de alta escala)",
            "Nenhum impacto físico na região de Joinville"
        ]
    })
    st.dataframe(df_compare_capture, use_container_width=True, hide_index=True)
    
    st.write("---")
    
    # Simulador Dinâmico da Carteira de Compensação da Whirlpool
    st.subheader("🎛️ Simulador de Carteira de Descarbonização Whirlpool Joinville")
    st.markdown("Crie uma estratégia de descarbonização combinando as tecnologias e veja o custo total e o perfil de risco resultante:")
    
    sim_wh_col1, sim_wh_col2 = st.columns([1, 1.2])
    
    with sim_wh_col1:
        st.markdown("**1. Defina a Meta e Alocação dos Recursos**")
        meta_wh = st.slider("Meta de Abatimento Anual (tCO2eq/ano)", min_value=1000, max_value=20000, value=10000, step=1000)
        
        # Alocações (Sliders robustos à prova de colapsos de min_value/max_value)
        p_biochar = st.slider("% Alocação em Biocarvão (Pirólise de Biomassa Local)", 0, 100, 60, step=5)
        
        # Para p_trees:
        max_trees = 100 - p_biochar
        if max_trees > 0:
            p_trees = st.slider("% Alocação em Plantio de Árvores (Reflorestamento de Nativas)", 0, max_trees, min(40, max_trees), step=5)
        else:
            st.text("🌳 % Alocação em Plantio de Árvores: 0% (Esgotado)")
            p_trees = 0
            
        # Para p_market:
        max_market = 100 - p_biochar - p_trees
        if max_market > 0:
            p_market = st.slider("% Alocação em Créditos de Mercado Geral (REDD+)", 0, max_market, max_market, step=5)
        else:
            st.text("🌍 % Alocação em Créditos de Mercado (REDD+): 0% (Esgotado)")
            p_market = 0
            
        # Para p_dac:
        max_dac = 100 - p_biochar - p_trees - p_market
        if max_dac > 0:
            p_dac = st.slider("% Alocação em Captura Direta de Ar (DAC)", 0, max_dac, max_dac, step=5)
        else:
            st.text("🌬️ % Alocação em Captura Direta de Ar (DAC): 0% (Esgotado)")
            p_dac = 0
        
        total_p = p_biochar + p_trees + p_market + p_dac
        if total_p != 100:
            st.error(f"⚠️ A soma das alocações deve ser exatamente 100%. Soma atual: {total_p}%")
            
    with sim_wh_col2:
        st.markdown("**2. Resultados da Simulação da Carteira**")
        
        # Valores de custos unitários
        c_biochar = 150.00
        c_trees = 400.00
        c_market = 60.00
        c_dac = 4200.00
        
        # Custos da alocação
        custo_biochar = (meta_wh * (p_biochar/100.0)) * c_biochar
        custo_trees = (meta_wh * (p_trees/100.0)) * c_trees
        custo_market = (meta_wh * (p_market/100.0)) * c_market
        custo_dac = (meta_wh * (p_dac/100.0)) * c_dac
        custo_total_carteira = custo_biochar + custo_trees + custo_market + custo_dac
        
        # Outras métricas
        arvores_plantadas = (meta_wh * (p_trees/100.0)) / 0.02 # assume 20kg de CO2/arvore/ano (0.02 t)
        biomassa_processada = (meta_wh * (p_biochar/100.0)) / 0.2160 # assume 0.2160 tCO2eq/ton resíduo
        
        # Permanência média ponderada
        perm_biochar = 500
        perm_trees = 30
        perm_market = 10
        perm_dac = 1000
        permanencia_media = (
            (p_biochar * perm_biochar) + 
            (p_trees * perm_trees) + 
            (p_market * perm_market) + 
            (p_dac * perm_dac)
        ) / 100.0
        
        # Economia em relação a focar apenas em Plantio de Árvores
        custo_100_reflorestamento = meta_wh * c_trees
        economia_gerada = custo_100_reflorestamento - custo_total_carteira
        
        # Métricas de Resultado
        res_cols = st.columns(2)
        with res_cols[0]:
            st.metric(
                label="💰 Custo Total Anual da Carteira",
                value=f"R$ {custo_total_carteira:,.2f}/ano"
            )
        with res_cols[1]:
            st.metric(
                label="⏳ Permanência Média do Carbono",
                value=f"{permanencia_media:.1f} anos",
                help="Tempo médio estimado de retenção do CO2 de forma segura."
            )
            
        st.write("📈 *Composição e Requisitos Físicos da Carteira:*")
        st.progress(min(1.0, max(0.0, total_p / 100.0)))
        
        # Exibe os requisitos físicos
        if p_biochar > 0:
            st.write(f"🌾 **Biomassa Requerida:** {biomassa_processada:,.1f} toneladas de resíduos agrícolas processados anualmente em SC para gerar o biocarvão necessário.")
        if p_trees > 0:
            st.write(f"🌳 **Árvores Necessárias:** {arvores_plantadas:,.0f} mudas plantadas e ativamente monitoradas para garantir a taxa de captura anual.")
        if p_dac > 0:
            st.write(f"🧪 **Energia para DAC:** Alto consumo elétrico local de matriz limpa requerido para processamento.")
            
        if economia_gerada > 0:
            st.success(f"🎉 **Vantagem Econômica:** Esta carteira diversificada economiza **R$ {economia_gerada:,.2f}/ano** em comparação a uma estratégia focada exclusivamente em plantio de árvores (reflorestamento).")
        elif economia_gerada < 0:
            st.warning(f"⚠️ **Atenção:** Esta carteira custa **R$ {abs(economia_gerada):,.2f}/ano** a mais do que o reflorestamento convencional devido ao alto custo das tecnologias selecionadas.")
            
    st.info("""
    💡 **Análise de Viabilidade Técnica e Logística para Whirlpool Joinville:**
    - **O Biocarvão como Aliado de Escopo 1:** O Relatório de Sustentabilidade destaca que mitigar emissões de Escopo 1 (gás natural) é o maior desafio regulatório da empresa. O biocarvão gerado nas usinas de pirólise próximas (como Joinville e Massaranduba) representa a solução ideal: fornece créditos de carbono premium com estabilidade permanente e apoia de forma direta a economia agrícola catarinense.
    - **A Fragilidade do Reflorestamento Isolado:** Embora plantar árvores seja essencial para a biodiversidade (como o projeto voluntário da Whirlpool no México que plantou 850 árvores em Coahuila), focar unicamente em reflorestamento exige extensões massivas de terra (Hectares) e possui alto risco de reversão por incêndios, o que expõe a empresa a passivos ambientais e não garante o compliance estrito sob o SBCE.
    """)


# ==================== ABA 8: CALCULADORA INDUSTRIAL ====================
with tab_calculator:
    st.header("🏭 Verificação de Descarbonização Individual para Sua Indústria")
    st.markdown("""
    Se você representa uma indústria em Santa Catarina, utilize esta interface para verificar a viabilidade técnica e financeira 
    de descarbonizar seus processos com base no reator de pirólise mais próximo.
    """)
    
    col_ind1, col_ind2 = st.columns(2)
    with col_ind1:
        st.subheader("📋 Dados da Sua Indústria")
        ind_name = st.text_input("Nome da Indústria", "Whirlpool Joinville Plant")
        ind_city = st.selectbox("Cidade da Sua Operação", df_sc["municipio"].tolist(), index=4) # default Joinville
        
        city_coords = df_sc[df_sc["municipio"] == ind_city].iloc[0]
        ind_lat, ind_lon = city_coords["lat"], city_coords["lon"]
        
        energy_demand = st.number_input("Demanda de Energia Elétrica Anual (MWh/ano)", min_value=500, max_value=100000, value=8000, step=500)
        co2_emissions = st.number_input("Emissões Anuais de Escopo 1 e 2 (tCO2eq/ano)", min_value=100, max_value=50000, value=2500, step=100)
        btn_calc = st.button("🚀 Executar Pareamento Multiagente")
        
    with col_ind2:
        st.subheader("🎯 Resultado do Pareamento Computacional")
        if btn_calc or ind_name:
            sorted_plants = sorted(
                engine.plants, 
                key=lambda p: ((ind_lat - p.lat)**2 + (ind_lon - p.lon)**2)**0.5
            )
            nearest_plant = sorted_plants[0]
            dist_plant = ((ind_lat - nearest_plant.lat)**2 + (ind_lon - nearest_plant.lon)**2)**0.5 * 110 # km
            
            original_cost = energy_demand * 680.0
            
            purchased_elec = min(energy_demand, nearest_plant.electricity_generated_mwh)
            purchased_credits = min(co2_emissions, nearest_plant.co2_captured_t)
            
            decarbonization_achieved = (purchased_elec * 0.1) + purchased_credits
            decarb_pct = min(100.0, (decarbonization_achieved / co2_emissions) * 100)
            
            new_cost = (purchased_elec * electricity_price) + ((energy_demand - purchased_elec) * 680.0)
            credits_cost = purchased_credits * carbon_price_display
            
            # Cálculo de conformidade individual para o SBCE do usuário
            unabated_co2 = max(0.0, co2_emissions - decarbonization_achieved)
            if sbce_mode == "Alocação Gratuita":
                free_quotas = co2_emissions * 0.90
                uncovered = max(0.0, unabated_co2 - free_quotas)
                compliance_cost = uncovered * 150.0
            elif sbce_mode == "Leilão por Consignação":
                free_quotas = co2_emissions * 0.50
                uncovered = max(0.0, unabated_co2 - free_quotas)
                compliance_cost = (uncovered * 100.0) * (1.0 - 0.50)
            else:
                free_quotas = 0.0
                uncovered = unabated_co2
                compliance_cost = uncovered * 180.0
                
            savings = (original_cost + (co2_emissions * 0.1 * 300.0)) - (new_cost + credits_cost + compliance_cost)
            
            st.markdown(f"**Usinas Compatíveis Próximas:**")
            st.write(f"📍 Usina mais próxima identificada: **{nearest_plant.name}** ({nearest_plant.municipality})")
            st.write(f"🗺️ Distância estimada de transporte/linha: **{dist_plant:.1f} km**")
            
            st.metric(label="Descarbonização Viável Obtida", value=f"{decarb_pct:.1f}%", delta=f"{decarbonization_achieved:,.1f} tCO2eq/ano")
            st.metric(label="Economia Líquida Sob {0}".format(sbce_mode), value=f"R$ {savings:,.2f} /ano")
            st.write(f"- Custo de Aquisição de Eletricidade: **R$ {new_cost:,.2f}/ano**")
            st.write(f"- Custo dos Créditos de Biocarvão (Carbon): **R$ {credits_cost:,.2f}/ano**")
            st.write(f"- Custos de Conformidade do SBCE: **R$ {compliance_cost:,.2f}/ano**")


# ==================== ABA 7: GROUNDING CIENTÍFICO ====================
with tab_articles:
    st.header("📚 Referências Científicas e Fórmulas Verificadas")
    st.markdown("""
    Todo o modelo matemático de simulação multiagente, o de potenciais de descarbonização em Santa Catarina, e a regulação de leilão de carbono 
    estão fundamentados de forma estrita nas referências de artigos anexadas ao projeto de pós-doutorado:
    """)
    
    st.markdown("""
    1. **Mecanismos de Leilão de Carbono Regulado**  
       *Fonte: Guo, Zhang & Zhang (2024) - Applied Energy 357*  
       - **Leilão por Consignação (Consignment Auction):** Mecanismo de transição onde o governo estabelece uma taxa de devolução para as indústrias de modo a manter a estabilidade do mercado e do preço da eletricidade.
       - **Leilão Tradicional:** Recomendado sob metas de longo prazo (neutralidade) para aumentar o custo explícito das emissões e acelerar o investimento em descarbonização profunda.
       
    2. **Parâmetros da Pirólise e Rendimento do Biocarvão**  
       *Fonte: RELATORIO_SEMESTRAL_POS_DOUTORADO_28.08.2026_assinado.pdf*  
       - O reator gera **10% em massa de biocarvão** e 47% de bio-óleo.  
       - O biocarvão seco apresenta **58,92% de teor de carbono em massa**.  
       - Fórmula de Sequestro Estável de CO2eq no solo: $\\text{CO2eq} = \\text{Resíduo} \\times 0.10 \\times 0.5892 \\times \\frac{44}{12} = \\text{Resíduo} \\times 0.2160$ tCO2eq por tonelada.

    3. **Abordagem Integrada de Planejamento de Sistemas Multienergia (MES)**  
       *Fonte: Apata (2025) - Energy Reports 13*  
       - Estudo sobre integração multivetorial de energia e políticas adaptativas para a modelagem dinâmica de resiliência e descarbonização em longo prazo.
    """)
