import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import folium
import geopandas as gpd
from streamlit.components.v1 import html

# =========================
# Configuración general
# =========================
st.set_page_config(page_title="Análisis Salud", layout="wide")

# Rutas de archivos
DATA_PATH = "salud_pacientes.csv"
SHAPEFILE_PATH = "shapefile_departamental/MGN_ADM_DPTO_POLITICO.shp"

# =========================
# Cargar datos
# =========================
df = pd.read_csv(DATA_PATH)

# Shapefile
gdf = gpd.read_file(SHAPEFILE_PATH)
gdf["dpto_cnmbr"] = gdf["dpto_cnmbr"].str.upper()
df["Departamento"] = df["Departamento"].str.upper()

# =========================
# Navegación
# =========================
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a:", ["Contexto", "Descriptivos", "Gráficos", "Mapas"])

# =========================
# Página 1: Contexto
# =========================
if page == "Contexto":
    st.title("📑 Contexto de los datos")

    st.markdown("""
    Esta aplicación analiza datos ficticios de **pacientes de salud en Colombia**.  
    El objetivo es **explorar patrones de diagnóstico, género, edad y frecuencia de visitas médicas**, 
    además de identificar cómo se distribuyen las enfermedades en los departamentos.

    **Variables principales:**
    - 🆔 **ID**: identificador único de paciente.  
    - 🗺️ **Departamento**: ubicación geográfica.  
    - 📍 **Latitud y Longitud**: coordenadas de localización.  
    - 🎂 **Edad** del paciente.  
    - 👩‍⚕️ **Género** (Masculino, Femenino, Otro).  
    - 🏥 **Diagnóstico** (diabetes, hipertensión, asma, etc.).  
    - 📊 **Frecuencia de visitas** médicas.

    El análisis incluye estadísticas descriptivas, visualizaciones gráficas y un mapa interactivo.
    """)

    st.metric("Número de registros", len(df))

    st.subheader("Vista previa del dataset")
    st.dataframe(df.head(10))

# =========================
# Página 2: Descriptivos
# =========================
elif page == "Descriptivos":
    st.title("📊 Análisis descriptivo")

    st.markdown("### Conteo de pacientes por diagnóstico")
    st.write(df["Diagnóstico"].value_counts())

    st.markdown("### Promedio de edad por diagnóstico")
    st.write(df.groupby("Diagnóstico")["Edad"].mean())

    st.markdown("### Promedio de frecuencia de visitas por diagnóstico")
    st.write(df.groupby("Diagnóstico")["Frecuencia_Visitas"].mean())

# =========================
# Página 3: Gráficos
# =========================
elif page == "Gráficos":
    st.title("📈 Visualizaciones")

    # Barras diagnósticos
    diag_counts = df["Diagnóstico"].value_counts().reset_index()
    diag_counts.columns = ["Diagnóstico", "Pacientes"]
    fig_bar = px.bar(diag_counts, x="Diagnóstico", y="Pacientes", color="Diagnóstico",
                     title="Distribución de diagnósticos")
    st.plotly_chart(fig_bar)

    # Boxplot
    fig_box = px.box(df, x="Diagnóstico", y="Edad", color="Diagnóstico",
                     title="Distribución de edad por diagnóstico")
    st.plotly_chart(fig_box)

    # Histograma
    fig_hist = px.histogram(df, x="Edad", nbins=20, color="Diagnóstico",
                            title="Histograma de edades")
    st.plotly_chart(fig_hist)

    # Dispersión
    fig_scatter = px.scatter(df, x="Edad", y="Frecuencia_Visitas", color="Diagnóstico",
                             title="Edad vs Frecuencia de visitas")
    st.plotly_chart(fig_scatter)

    # Barras apiladas
    fig_stack = px.histogram(df, x="Diagnóstico", color="Genero", barmode="stack",
                             title="Distribución género vs diagnóstico")
    st.plotly_chart(fig_stack)

# =========================
# Página 4: Mapas
# =========================
elif page == "Mapas":
    st.title("🗺️ Mapa de pacientes")

    # Filtros en el centro
    col1, col2, col3 = st.columns(3)
    with col1:
        diagnosticos_unicos = sorted(df["Diagnóstico"].dropna().unique())
        diagnostico_sel = st.selectbox("Seleccionar diagnóstico", options=["Todos"] + list(diagnosticos_unicos))
    with col2:
        generos_unicos = sorted(df["Genero"].dropna().unique())
        genero_sel = st.selectbox("Filtrar por género", options=["Todos"] + list(generos_unicos))
    with col3:
        metrica_sel = st.selectbox(
            "Métrica para colorear",
            options=["Num_Pacientes", "Edad", "Frecuencia_Visitas"],
            format_func=lambda x: {
                "Num_Pacientes": "Número de pacientes",
                "Edad": "Edad promedio",
                "Frecuencia_Visitas": "Visitas promedio"
            }[x]
        )

    # Filtrado
    df_filtrado = df.copy()
    if diagnostico_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Diagnóstico"] == diagnostico_sel]
    if genero_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Genero"] == genero_sel]

    # Agrupación
    df_grouped_filt = df_filtrado.groupby("Departamento").agg({
        "ID": "count",
        "Edad": "mean",
        "Frecuencia_Visitas": "mean"
    }).reset_index().rename(columns={"ID": "Num_Pacientes"})

    gdf_merge_filt = gdf.merge(df_grouped_filt, left_on="dpto_cnmbr", right_on="Departamento", how="left")

    # Selección de paleta por métrica
    palette_dict = {
        "Num_Pacientes": "Reds",
        "Edad": "Blues",
        "Frecuencia_Visitas": "Greens"
    }
    palette = palette_dict[metrica_sel]

    st.markdown(f"### Distribución de pacientes ({diagnostico_sel}, {genero_sel}) - {metrica_sel}")

    # Crear mapa
    m1 = folium.Map(location=[4.5709, -74.2973], zoom_start=5, tiles="CartoDB positron")

    # Choropleth
    folium.Choropleth(
        geo_data=gdf_merge_filt,
        data=gdf_merge_filt,
        columns=["dpto_cnmbr", metrica_sel],
        key_on="feature.properties.dpto_cnmbr",
        fill_color=palette,
        fill_opacity=0.7,
        line_opacity=0.5,
        nan_fill_color="lightgrey",
        legend_name={
            "Num_Pacientes": "Número de pacientes",
            "Edad": "Edad promedio",
            "Frecuencia_Visitas": "Visitas promedio"
        }[metrica_sel]
    ).add_to(m1)

    # Tooltip con todas las métricas
    folium.GeoJson(
        gdf_merge_filt,
        style_function=lambda feature: {"color": "transparent", "weight": 0},
        tooltip=folium.GeoJsonTooltip(
            fields=["dpto_cnmbr", "Num_Pacientes", "Edad", "Frecuencia_Visitas"],
            aliases=["Departamento", "Pacientes", "Edad Promedio", "Visitas Promedio"],
            localize=True
        )
    ).add_to(m1)

    # ✅ Renderizar el mapa como HTML estático (sin streamlit-folium)
    map_html = m1._repr_html_()
    html(map_html, height=600, width=900)
