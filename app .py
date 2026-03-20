import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# CONFIG
# --------------------------------

st.set_page_config(page_title="PIOM PRO", layout="wide")

st.title("⛏️ PIOM PRO - Inteligencia Operacional Minera")
st.write("Sistema inteligente de optimización y decisión minera")

archivo = st.file_uploader("Subir Excel", type=["xlsx"])

# --------------------------------
# FUNCIONES
# --------------------------------

@st.cache_data
def cargar_excel(file):
    return pd.read_excel(file).fillna(0)


def indicadores(df):
    return {
        "Perforación": (df["Metros_real"].sum() / df["Metros_plan"].sum() * 100) if df["Metros_plan"].sum() else 0,
        "Producción": (df["Real"].sum() / df["Plan"].sum() * 100) if df["Plan"].sum() else 0,
        "Espera": df["Espera"].mean(),
        "Mant": df["Mant_no_prog"].sum()
    }


def estado(ind):
    if ind["Producción"] < 85 and ind["Espera"] > 5:
        return "🔴 Sistema Saturado"
    elif ind["Producción"] < 90:
        return "🟡 Riesgo Productivo"
    elif ind["Espera"] > 4:
        return "🟡 Congestión Transporte"
    return "🟢 Operación Normal"


def cuello(ind):
    problemas = {
        "Perforación": 100 - ind["Perforación"],
        "Carguío": 100 - ind["Producción"],
        "Transporte": ind["Espera"],
        "Mantención": ind["Mant"]
    }
    return max(problemas, key=problemas.get)


# --------------------------------
# APP
# --------------------------------

if archivo:

    df = cargar_excel(archivo)

    cols = ["Metros_real","Metros_plan","Real","Plan","Espera","Mant_no_prog","Pala_activa"]

    if any(c not in df.columns for c in cols):
        st.error("Archivo incorrecto")
        st.stop()

    ind = indicadores(df)

    # ---------------- KPIs ----------------

    c1,c2,c3 = st.columns(3)

    c1.metric("Perforación %", round(ind["Perforación"],1))
    c2.metric("Producción %", round(ind["Producción"],1))
    c3.metric("Espera", round(ind["Espera"],1))

    # ---------------- ESTADO ----------------

    st.subheader("📡 Estado Sistema")
    st.markdown(f"### {estado(ind)}")

    # ---------------- CUELLO ----------------

    cu = cuello(ind)

    st.subheader("🚨 Cuello de Botella")
    st.error(cu)

    # ---------------- IMPACTO ECONÓMICO ----------------

    st.subheader("💰 Impacto Económico")

    precio = st.number_input("Precio tonelada ($)", value=100)

    perdida = df["Plan"].sum() - df["Real"].sum()

    impacto = perdida * precio

    if perdida > 0:
        st.error(f"Pérdida: ${int(impacto):,}")
    else:
        st.success("Sin pérdidas")

    # ---------------- PREDICCIÓN ----------------

    st.subheader("🔮 Predicción Producción")

    df["Real_acum"] = df["Real"].cumsum()

    tendencia = df["Real_acum"].iloc[-1] / len(df)

    pred = tendencia * 12

    st.metric("Producción estimada turno", int(pred))

    # ---------------- ALERTAS ----------------

    st.subheader("🚨 Alertas Inteligentes")

    alertas = []

    if ind["Espera"] > 5:
        alertas.append("Congestión de transporte")

    if ind["Producción"] < 85:
        alertas.append("Baja producción")

    if ind["Mant"] > 20:
        alertas.append("Alta mantención")

    for a in alertas:
        st.warning(a)

    if not alertas:
        st.success("Operación estable")

    # ---------------- DIAGNÓSTICO ----------------

    st.subheader("🔍 Diagnóstico")

    if ind["Espera"] > 5:
        st.warning("Problema raíz: transporte")

    elif ind["Producción"] < 85:
        st.warning("Problema raíz: producción")

    else:
        st.success("Sistema balanceado")

    # ---------------- GRÁFICOS ----------------

    st.subheader("📊 Producción")

    st.plotly_chart(
        px.line(df, y=["Plan","Real"], markers=True),
        use_container_width=True, key="g1"
    )

    st.subheader("📉 Desviación")

    df["Desv"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100

    st.plotly_chart(
        px.bar(df, y="Desv", color="Desv"),
        use_container_width=True, key="g2"
    )

    st.subheader("🚚 Espera")

    st.plotly_chart(
        px.line(df, y="Espera"),
        use_container_width=True, key="g3"
    )

    # ---------------- OPTIMIZADOR ----------------

    st.subheader("🚚 Optimización Flota")

    camiones = st.slider("Camiones",1,20,8)
    capacidad = st.number_input("Capacidad",200)
    ciclo = st.number_input("Tiempo ciclo",25)

    prod = (camiones * capacidad * 12 * 60) / ciclo

    st.metric("Producción estimada", int(prod))

    mejor = 0
    mejor_n = 0

    for n in range(1,25):
        p = (n * capacidad * 12 * 60) / ciclo
        if p > mejor:
            mejor = p
            mejor_n = n

    st.success(f"Flota óptima: {mejor_n} camiones")

    # ---------------- RANKING ----------------

    st.subheader("🏆 Ranking Palas")

    rank = df.groupby("Pala_activa")[["Real","Plan"]].sum()
    rank["Eficiencia"] = rank["Real"]/rank["Plan"]*100

    st.dataframe(rank.sort_values("Eficiencia", ascending=False))

    # ---------------- REPORTE ----------------

    st.subheader("📄 Reporte Ejecutivo")

    rep = f"""
Producción: {int(df["Real"].sum())}
Plan: {int(df["Plan"].sum())}
Estado: {estado(ind)}
Cuello: {cu}
"""

    st.text_area("Reporte", rep, height=150)

else:
    st.info("Sube archivo Excel")
