import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# ---------------- IA SEGURA ----------------

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    IA_OK = True
except:
    IA_OK = False

# ---------------- CONFIG ----------------

st.set_page_config(page_title="PIOM PRO", layout="wide")

# ---------------- ESTILO ----------------

st.markdown("""
<style>
body {background-color: #0E1117;}
.block-container {padding-top: 1rem;}
h1, h2, h3 {color: white;}
</style>
""", unsafe_allow_html=True)

st.title("⛏️ PIOM PRO - Sala de Control Inteligente")
st.write("Sistema autónomo de optimización minera")

archivo = st.file_uploader("Subir Excel", type=["xlsx"])

# ---------------- HISTÓRICO ----------------

if "historico.csv" not in os.listdir():
    pd.DataFrame(columns=["real","plan","espera"]).to_csv("historico.csv", index=False)

# ---------------- FUNCIONES ----------------

@st.cache_data
def cargar_excel(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df.fillna(0)

def calcular_indicadores(df):
    perf = (df["metros_real"].sum() / df["metros_plan"].sum() * 100) if "metros_plan" in df else 0
    prod = (df["real"].sum() / df["plan"].sum() * 100) if df["plan"].sum() > 0 else 0
    espera = df["espera"].mean()
    mant = df["mant_no_prog"].sum() if "mant_no_prog" in df else 0

    return {"Perforación": perf, "Producción": prod, "Espera": espera, "Mant": mant}

def estado_mina(ind):
    if ind["Producción"] < 85 and ind["Espera"] > 5:
        return "🔴 SISTEMA SATURADO"
    elif ind["Producción"] < 90:
        return "🟡 RIESGO"
    elif ind["Espera"] > 4:
        return "🟡 CONGESTIÓN"
    return "🟢 NORMAL"

# ---------------- APP ----------------

if not archivo:
    st.info("Sube archivo Excel")
    st.stop()

df = cargar_excel(archivo)

indicadores = calcular_indicadores(df)

# ---------------- KPI ----------------

st.subheader("🎛️ Sala de Control")

c1, c2, c3, c4 = st.columns(4)

def color(valor, bueno, medio):
    if valor >= bueno:
        return "🟢"
    elif valor >= medio:
        return "🟡"
    return "🔴"

c1.metric("Producción", f"{round(indicadores['Producción'],1)}% {color(indicadores['Producción'],95,85)}")
c2.metric("Perforación", f"{round(indicadores['Perforación'],1)}% {color(indicadores['Perforación'],90,80)}")
c3.metric("Espera", f"{round(indicadores['Espera'],1)} min")
c4.metric("Mant", indicadores["Mant"])

# ---------------- ESTADO ----------------

st.subheader("Estado Sistema")

estado = estado_mina(indicadores)

if "🔴" in estado:
    st.error(estado)
elif "🟡" in estado:
    st.warning(estado)
else:
    st.success(estado)

# ---------------- IA DESPACHO AUTOMÁTICO ----------------

st.subheader("🤖 IA Despacho Automático")

if "pala_activa" in df.columns:

    colas = df.groupby("pala_activa")["espera"].mean()
    produccion = df.groupby("pala_activa")["real"].sum()

    def score_pala(p):
        return colas[p]*0.6 - produccion[p]*0.0005

    mejor_pala = min(colas.index, key=score_pala)

    st.success(f"Enviar próximo camión a: {mejor_pala}")

    decision_df = pd.DataFrame({
        "Pala": colas.index,
        "Cola": colas.values,
        "Producción": produccion.values,
        "Score": [score_pala(p) for p in colas.index]
    })

    st.dataframe(decision_df)

# ---------------- SIMULACIÓN DECISIONES ----------------

st.subheader("🚚 Simulación IA")

n_camiones = st.slider("Simular decisiones", 1, 20, 5)

sim_colas = colas.copy()

asignaciones = []

for i in range(n_camiones):
    mejor = min(sim_colas.index, key=score_pala)
    asignaciones.append(mejor)
    sim_colas[mejor] += 0.5

st.write("Asignaciones IA:", asignaciones)

# ---------------- IA PREDICTIVA ----------------

st.subheader("🤖 Predicción")

if IA_OK:

    hist = pd.read_csv("historico.csv")

    if len(hist) > 3:
        X = hist[["plan","espera"]]
        y = hist["real"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        pred = modelo.predict([[df["plan"].sum(), df["espera"].mean()]])[0]

        st.metric("Producción estimada", int(pred))

# ---------------- GRÁFICOS ----------------

st.subheader("📊 Producción")

st.plotly_chart(px.line(df, y=["plan","real"]), use_container_width=True)

# ---------------- DISPATCH ----------------

st.subheader("🚚 Control Flota")

st.dataframe(colas)

# ---------------- BALANCE ----------------

st.subheader("⚖️ Balance Sistema")

balance = {
    "Perforación": indicadores["Perforación"],
    "Carguío": indicadores["Producción"],
    "Transporte": 100 - indicadores["Espera"] * 10
}

st.write(balance)
