import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# CONFIGURACIÓN
# --------------------------------

st.set_page_config(page_title="PIOM", layout="wide")

st.title("⛏️ PIOM - Plataforma Inteligente de Optimización Minera")
st.write("Análisis operacional del turno mina")

archivo = st.file_uploader("Subir Excel", type=["xlsx"])

# --------------------------------
# FUNCIONES
# --------------------------------

@st.cache_data
def cargar_excel(file):
    df = pd.read_excel(file)
    return df.fillna(0)


def calcular_indicadores(df):

    return {
        "Perforación": (df["Metros_real"].sum() / df["Metros_plan"].sum() * 100) if df["Metros_plan"].sum() else 0,
        "Producción": (df["Real"].sum() / df["Plan"].sum() * 100) if df["Plan"].sum() else 0,
        "Espera Camiones": df["Espera"].mean(),
        "Mantención": df["Mant_no_prog"].sum()
    }


def detectar_cuello(ind):
    problema = {
        "Perforación": 100 - ind["Perforación"],
        "Carguío": 100 - ind["Producción"],
        "Transporte": ind["Espera Camiones"],
        "Mantención": ind["Mantención"]
    }
    return max(problema, key=problema.get)


def estado_mina(ind):

    if ind["Producción"] < 85 and ind["Espera Camiones"] > 5:
        return "🔴 Sistema Saturado"
    elif ind["Producción"] < 90:
        return "🟡 Riesgo Productivo"
    elif ind["Espera Camiones"] > 4:
        return "🟡 Congestión Transporte"
    elif ind["Perforación"] < 90:
        return "🟡 Baja Perforación"
    return "🟢 Operación Normal"


def analisis_inteligente(df):

    alertas = []

    if df["Real"].sum() < df["Plan"].sum() * 0.9:
        alertas.append("🔴 Baja producción")

    if df["Espera"].mean() > 5:
        alertas.append("🟡 Congestión camiones")

    if df["Mant_no_prog"].sum() > 20:
        alertas.append("🔴 Fallas no programadas")

    return alertas


# --------------------------------
# APP PRINCIPAL
# --------------------------------

if archivo:

    df = cargar_excel(archivo)

    columnas = [
        "Metros_real","Metros_plan","Real","Plan",
        "Espera","Mant_no_prog","Equipo_perforacion","Pala_activa"
    ]

    faltantes = [c for c in columnas if c not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas: {faltantes}")
        st.stop()

    # ---------------- INDICADORES ----------------

    ind = calcular_indicadores(df)

    c1, c2, c3 = st.columns(3)

    c1.metric("Perforación %", round(ind["Perforación"],1))
    c2.metric("Producción %", round(ind["Producción"],1))
    c3.metric("Espera (min)", round(ind["Espera Camiones"],1))

    # ---------------- ESTADO ----------------

    st.subheader("📡 Estado Sistema Mina")
    st.markdown(f"### {estado_mina(ind)}")

    # ---------------- CUELLO ----------------

    cuello = detectar_cuello(ind)

    st.subheader("🚨 Cuello de Botella")
    st.error(cuello)

    # ---------------- RECOMENDACIÓN ----------------

    recomendaciones = {
        "Perforación": "Revisar perforadoras",
        "Carguío": "Optimizar carguío",
        "Transporte": "Reducir tiempos de espera",
        "Mantención": "Mejorar mantenimiento"
    }

    st.success(recomendaciones.get(cuello, ""))

    # ---------------- GRÁFICOS ----------------

    st.subheader("📊 Producción vs Plan")

    df["Desv_%"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100

    st.plotly_chart(
        px.line(df, y=["Plan","Real"], markers=True),
        use_container_width=True,
        key="prod"
    )

    st.subheader("📉 Desviación")

    st.plotly_chart(
        px.bar(df, y="Desv_%", color="Desv_%"),
        use_container_width=True,
        key="desv"
    )

    st.subheader("🚚 Espera Camiones")

    st.plotly_chart(
        px.line(df, y="Espera"),
        use_container_width=True,
        key="espera"
    )

    # ---------------- RANKING ----------------

    st.subheader("🏆 Ranking Palas")

    ranking = df.groupby("Pala_activa")[["Real","Plan"]].sum()
    ranking["Eficiencia"] = ranking["Real"]/ranking["Plan"]*100

    st.dataframe(ranking.sort_values("Eficiencia", ascending=False))

    # ---------------- PERDIDA ----------------

    perdida = df["Plan"].sum() - df["Real"].sum()

    st.subheader("📉 Pérdida Producción")

    if perdida > 0:
        st.error(f"Se perdieron {int(perdida)} ton")
    else:
        st.success("Producción cumplida")

    # ---------------- IA ----------------

    st.subheader("🧠 Inteligencia PIOM")

    alertas = analisis_inteligente(df)

    for a in alertas:
        st.warning(a)

    if not alertas:
        st.success("Operación estable")

    # ---------------- REPORTE ----------------

    st.subheader("📄 Reporte")

    rep = f"""
Producción: {int(df["Real"].sum())} / {int(df["Plan"].sum())}
Cuello: {cuello}
Estado: {estado_mina(ind)}
"""

    st.text_area("Reporte", rep, height=150)

else:
    st.info("Sube un archivo para comenzar")
