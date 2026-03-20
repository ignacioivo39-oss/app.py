import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# CONFIGURACIÓN
# --------------------------------

st.set_page_config(
    page_title="PIOM PRO",
    layout="wide"
)

st.title("⛏️ PIOM PRO - Sala de Control Minera")
st.write("Optimización operacional y despacho inteligente")

archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"])

# --------------------------------
# FUNCIONES
# --------------------------------

@st.cache_data
def cargar_excel(file):
    df = pd.read_excel(file)
    df = df.fillna(0)
    return df

def calcular_indicadores(df):

    perf = (df["Metros_real"].sum() / df["Metros_plan"].sum() * 100) if df["Metros_plan"].sum() > 0 else 0
    prod = (df["Real"].sum() / df["Plan"].sum() * 100) if df["Plan"].sum() > 0 else 0
    espera = df["Espera"].mean()
    mant = df["Mant_no_prog"].sum()

    return {
        "Perforación": perf,
        "Producción": prod,
        "Espera": espera,
        "Mant": mant
    }

def estado_mina(ind):

    if ind["Producción"] < 85:
        return "🔴 Riesgo Producción"
    elif ind["Espera"] > 5:
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
# APP PRINCIPAL
# --------------------------------

if not archivo:
    st.info("Sube un archivo Excel para comenzar")
    st.stop()

df = cargar_excel(archivo)

columnas = ["Metros_real","Metros_plan","Real","Plan","Espera","Mant_no_prog","Pala_activa"]

faltantes = [c for c in columnas if c not in df.columns]

if faltantes:
    st.error(f"Faltan columnas: {faltantes}")
    st.stop()

indicadores = calcular_indicadores(df)

# --------------------------------
# KPI
# --------------------------------

st.subheader("🎛️ KPIs Operacionales")

c1, c2, c3 = st.columns(3)

c1.metric("Perforación %", round(indicadores["Perforación"],1))
c2.metric("Producción %", round(indicadores["Producción"],1))
c3.metric("Espera (min)", round(indicadores["Espera"],1))

# --------------------------------
# ESTADO Y CUELLO
# --------------------------------

st.subheader("📡 Estado del Sistema")
st.markdown(f"### {estado_mina(indicadores)}")

cuello = detectar_cuello(indicadores)

st.subheader("🚨 Cuello de Botella")
st.error(cuello)

# --------------------------------
# GRÁFICOS
# --------------------------------

st.subheader("📊 Producción")

st.plotly_chart(
    px.line(df, y=["Plan","Real"], markers=True),
    use_container_width=True
)

st.subheader("🚚 Espera Camiones")

st.plotly_chart(
    px.line(df, y="Espera", markers=True),
    use_container_width=True
)

# --------------------------------
# SIMULADOR
# --------------------------------

st.subheader("🧠 Simulación Sistema Mina")

camiones = st.slider("Camiones",1,20,8)
capacidad = st.number_input("Capacidad (ton)",200)
tiempo_ciclo = st.number_input("Tiempo ciclo (min)",25)

if tiempo_ciclo > 0:
    prod = (camiones * capacidad * 12 * 60) / tiempo_ciclo
    st.metric("Producción estimada", int(prod))

# --------------------------------
# IA DESPACHO (MEJORADA)
# --------------------------------

st.subheader("🤖 IA Despacho Inteligente")

colas = df.groupby("Pala_activa")["Espera"].mean()
produccion = df.groupby("Pala_activa")["Real"].sum()

max_prod = produccion.max()

def score(p):
    return (
        colas[p] * 0.5 +
        (1 - produccion[p]/max_prod) * 20
    )

palas = list(colas.index)

ranking = sorted(palas, key=score)

mejor = ranking[0]
segunda = ranking[1] if len(ranking) > 1 else ranking[0]

# ---------------- GLOBAL ----------------

st.subheader("📡 Decisión Global")

col1, col2 = st.columns(2)

col1.success(f"Enviar camiones a: {mejor}")
col2.info(f"Asignación automática: enviar próximo camión a {segunda}")

# ---------------- POR EQUIPO ----------------

st.subheader("🏗️ Decisión por Equipo")

for pala in palas:

    st.markdown(f"### {pala}")

    col1, col2 = st.columns(2)

    col1.success(f"Enviar camiones a: {mejor}")
    col2.info(f"Asignación automática: enviar próximo camión a {segunda}")

# --------------------------------
# RANKING
# --------------------------------

st.subheader("🏆 Ranking Palas")

ranking_df = df.groupby("Pala_activa")[["Real","Plan"]].sum()
ranking_df["Eficiencia"] = (ranking_df["Real"]/ranking_df["Plan"])*100

st.dataframe(ranking_df.sort_values("Eficiencia", ascending=False))

# --------------------------------
# PÉRDIDAS
# --------------------------------

st.subheader("📉 Pérdida Producción")

perdida = df["Plan"].sum() - df["Real"].sum()

if perdida > 0:
    st.error(f"Pérdida: {int(perdida)} ton")
else:
    st.success("Producción cumplida")
