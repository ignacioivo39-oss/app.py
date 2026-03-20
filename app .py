import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# CONFIG
# --------------------------------

st.set_page_config(page_title="PIOM PRO", layout="wide")

st.title("⛏️ PIOM PRO - Inteligencia Operacional Minera")
st.write("Sistema inteligente de optimización minera")

archivo = st.file_uploader("Subir Excel", type=["xlsx"])

# --------------------------------
# FUNCIONES
# --------------------------------

@st.cache_data
def cargar_excel(file):
    df = pd.read_excel(file)

    # normalizar columnas (ANTI-ERROR)
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    return df.fillna(0)


def calcular_indicadores(df):

    perf = (df["metros_real"].sum() / df["metros_plan"].sum() * 100) \
        if "metros_plan" in df and df["metros_plan"].sum() > 0 else 0

    prod = (df["real"].sum() / df["plan"].sum() * 100) \
        if df["plan"].sum() > 0 else 0

    espera = df["espera"].mean() if "espera" in df else 0
    mant = df["mant_no_prog"].sum() if "mant_no_prog" in df else 0

    return {
        "Perforación": perf,
        "Producción": prod,
        "Espera": espera,
        "Mant": mant
    }


def estado_mina(ind):

    if ind["Producción"] < 85 and ind["Espera"] > 5:
        return "🔴 Sistema Saturado"
    elif ind["Producción"] < 90:
        return "🟡 Riesgo Productivo"
    elif ind["Espera"] > 4:
        return "🟡 Congestión Transporte"
    elif ind["Perforación"] < 90:
        return "🟡 Baja Perforación"
    return "🟢 Operación Normal"


def detectar_cuello(ind):

    problema = {
        "Perforación": 100 - ind["Perforación"],
        "Carguío": 100 - ind["Producción"],
        "Transporte": ind["Espera"],
        "Mantención": ind["Mant"]
    }

    return max(problema, key=problema.get)


# --------------------------------
# APP
# --------------------------------

if archivo:

    df = cargar_excel(archivo)

    columnas_base = ["real", "plan"]

    faltantes = [c for c in columnas_base if c not in df.columns]

    if faltantes:
        st.error(f"❌ Faltan columnas obligatorias: {faltantes}")
        st.stop()

    # indicadores SIEMPRE definidos antes de usar
    indicadores = calcular_indicadores(df)

    # ---------------- KPIs ----------------

    c1, c2, c3 = st.columns(3)

    c1.metric("Perforación %",
              round(indicadores["Perforación"], 1))

    c2.metric("Producción %",
              round(indicadores["Producción"], 1))

    c3.metric("Espera (min)",
              round(indicadores["Espera"], 1))

    # ---------------- ESTADO ----------------

    st.subheader("📡 Estado del Sistema Mina")
    st.markdown(f"### {estado_mina(indicadores)}")

    # ---------------- CUELLO ----------------

    cuello = detectar_cuello(indicadores)

    st.subheader("🚨 Cuello de Botella")
    st.error(cuello)

    # ---------------- IMPACTO ECONÓMICO ----------------

    st.subheader("💰 Impacto Económico")

    precio = st.number_input("Precio por tonelada ($)", value=100)

    perdida = df["plan"].sum() - df["real"].sum()

    impacto = perdida * precio

    if perdida > 0:
        st.error(f"Pérdida: ${int(impacto):,}")
    else:
        st.success("Sin pérdidas económicas")

    # ---------------- PREDICCIÓN ----------------

    st.subheader("🔮 Predicción Producción")

    df["real_acum"] = df["real"].cumsum()

    tendencia = df["real_acum"].iloc[-1] / len(df)

    pred = tendencia * 12

    st.metric("Producción estimada turno", int(pred))

    # ---------------- ALERTAS ----------------

    st.subheader("🚨 Alertas Inteligentes")

    alertas = []

    if indicadores["Espera"] > 5:
        alertas.append("Congestión en transporte")

    if indicadores["Producción"] < 85:
        alertas.append("Baja producción")

    if indicadores["Mant"] > 20:
        alertas.append("Alta mantención")

    if alertas:
        for a in alertas:
            st.warning(a)
    else:
        st.success("Operación estable")

    # ---------------- GRÁFICOS ----------------

    st.subheader("📊 Producción")

    st.plotly_chart(
        px.line(df, y=["plan", "real"], markers=True),
        use_container_width=True,
        key="prod"
    )

    # desviación segura
    df["desv"] = ((df["real"] - df["plan"]) / df["plan"].replace(0, 1)) * 100

    st.subheader("📉 Desviación")

    st.plotly_chart(
        px.bar(df, y="desv", color="desv"),
        use_container_width=True,
        key="desv"
    )

    if "espera" in df.columns:
        st.subheader("🚚 Espera Camiones")

        st.plotly_chart(
            px.line(df, y="espera"),
            use_container_width=True,
            key="espera"
        )

    # ---------------- RANKING ----------------

    if "pala_activa" in df.columns:
        st.subheader("🏆 Ranking Palas")

        rank = df.groupby("pala_activa")[["real", "plan"]].sum()

        rank["Eficiencia"] = (rank["real"] / rank["plan"]) * 100

        st.dataframe(rank.sort_values("Eficiencia", ascending=False))

    # ---------------- REPORTE ----------------

    st.subheader("📄 Reporte Ejecutivo")

    reporte = f"""
Producción: {int(df["real"].sum())}
Plan: {int(df["plan"].sum())}
Estado: {estado_mina(indicadores)}
Cuello: {cuello}
"""

    st.text_area("Reporte", reporte, height=150)

else:
    st.info("Sube un archivo Excel para comenzar")
