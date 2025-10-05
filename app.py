# ================================
#  app.py — versión con Plotly choropleth
# ================================

import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json

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
    """)

    st.metric("Número de registros", len(df))
    st.subheader("Vista previa del dataset")
    st.dataframe(df.head(10))

# =========================
# Página 2: Descriptivos
# =========================
elif page == "Descriptivos":
    st.title("📊 Análisis descriptivo")

    st.write("### Conteo de pacientes por diagnóstico")
    st.write(df["Diagnóstico"].value_counts())

    st.write("### Promedio de edad por diagnóstico")
    st.write(df.groupby("Diagnóstico")["Edad"].mean())

    st.write("### Promedio de frecuencia de visitas por diagnóstico")
    st.write(df.groupby("Diagnóstico")["Frecuencia_Visitas"].mean())

# =========================
# Página 3: Gráficos
# =========================
elif page == "Gráficos":
    st.title("📈 Visualizaciones")

    diag_counts = df["Diagnóstico"].value_counts().reset_index()
    diag_counts.columns = ["Diagnóstico", "Pacientes"]
    fig_bar = px.bar(diag_counts, x="Diagnóstico", y="Pacientes", color="Diagnóstico", title="Distribución de diagnósticos")
    st.plotly_chart(fig_bar)

    fig_box = px.box(df, x="Diagnóstico", y="Edad", color="Diagnóstico", title="Distribución de edad por diagnóstico")
    st.plotly_chart(fig_box)

    fig_hist = px.histogram(df, x="Edad", nbins=20, color="Diagnóstico", title="Histograma de edades")
    st.plotly_chart(fig_hist)

    fig_scatter = px.scatter(df, x="Edad", y="Frecuencia_Visitas", color="Diagnóstico", title="Edad vs Frecuencia de visitas")
    st.plotly_chart(fig_scatter)

# =========================
# Página 4: Mapas (con Plotly)
# =========================
elif page == "Mapas":
    st.title("🗺️ Mapa de pacientes por departamento (Plotly)")

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        diagnosticos_unicos = sorted(df["Diagnóstico"].dropna().unique())
        diagnostico_sel = st.selectbox("Seleccionar diagnóstico", ["Todos"] + list(diagnosticos_unicos))
    with col2:
        generos_unicos = sorted(df["Genero"].dropna().unique())
        genero_sel = st.selectbox("Filtrar por género", ["Todos"] + list(generos_unicos))
    with col3:
        metrica_sel = st.selectbox(
            "Métrica para colorear",
            ["Num_Pacientes", "Edad", "Frecuencia_Visitas"],
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

    # Agrupar datos
    df_grouped = df_filtrado.groupby("Departamento").agg({
        "ID": "count",
        "Edad": "mean",
        "Frecuencia_Visitas": "mean"
    }).reset_index().rename(columns={"ID": "Num_Pacientes"})

    # Unir con shapefile
    gdf_merge = gdf.merge(df_grouped, left_on="dpto_cnmbr", right_on="Departamento", how="left")

    # Convertir a geojson
    geojson = json.loads(gdf_merge.to_json())

    # Crear mapa Plotly
    fig = px.choropleth(
        gdf_merge,
        geojson=geojson,
        locations="dpto_cnmbr",
        featureidkey="properties.dpto_cnmbr",
        color=metrica_sel,
        color_continuous_scale="RdYlBu",
        title=f"Distribución de {metrica_sel.lower()} por departamento"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)
