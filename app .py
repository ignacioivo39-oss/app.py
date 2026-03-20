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

# ---------------- ESTILO SALA CONTROL ----------------

st.markdown("""
<style>
body {background-color: #0E1117;}
.block-container {padding-top: 1rem;}
h1, h2, h3 {color: white;}
</style>
""", unsafe_allow_html=True)

st.title("⛏️ PIOM PRO - Sala de Control Minera")
st.write("Sistema inteligente de optimización operacional")

archivo = st.file_uploader("Subir archivo Excel operacional", type=["xlsx"])

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

    perf = (df["metros_real"].sum() / df["metros_plan"].sum() * 100) \
        if "metros_plan" in df and df["metros_plan"].sum() > 0 else 0

    prod = (df["real"].sum() / df["plan"].sum() * 100) \
        if df["plan"].sum() > 0 else 0

    espera = df["espera"].mean() if "espera" in df else 0
    mant = df["mant_no_prog"].sum() if "mant_no_prog" in df else 0

    return {"Perforación": perf, "Producción": prod, "Espera": espera, "Mant": mant}

def estado_mina(ind):
    if ind["Producción"] < 85 and ind["Espera"] > 5:
        return "🔴 SISTEMA SATURADO"
    elif ind["Producción"] < 90:
        return "🟡 RIESGO PRODUCTIVO"
    elif ind["Espera"] > 4:
        return "🟡 CONGESTIÓN"
    return "🟢 OPERACIÓN NORMAL"

def detectar_cuello(ind):
    problema = {
        "Perforación": 100 - ind["Perforación"],
        "Carguío": 100 - ind["Producción"],
        "Transporte": ind["Espera"],
        "Mantención": ind["Mant"]
    }
    return max(problema, key=problema.get)

# ---------------- APP ----------------

if not archivo:
    st.info("Sube un archivo Excel para comenzar")
    st.stop()

df = cargar_excel(archivo)

if "real" not in df.columns or "plan" not in df.columns:
    st.error("El Excel debe contener columnas: real y plan")
    st.stop()

indicadores = calcular_indicadores(df)

# ---------------- KPI SALA CONTROL ----------------

st.subheader("🎛️ Sala de Control Operacional")

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
c4.metric("Mantención", indicadores["Mant"])

# ---------------- ESTADO ----------------

st.subheader("🚨 Estado Global")

estado = estado_mina(indicadores)

if "🔴" in estado:
    st.error(estado)
elif "🟡" in estado:
    st.warning(estado)
else:
    st.success(estado)

# ---------------- CUELLO ----------------

cuello = detectar_cuello(indicadores)
st.subheader("🚨 Cuello de Botella")
st.error(cuello)

# ---------------- DECISIONES ----------------

st.subheader("🧠 Decisiones Automáticas")

acciones = []

if indicadores["Perforación"] < 85:
    acciones.append("Aumentar perforación")

if indicadores["Espera"] > 5:
    acciones.append("Reducir flota")

if indicadores["Producción"] < 90:
    acciones.append("Optimizar carguío")

for a in acciones:
    st.warning(f"➡ {a}")

if not acciones:
    st.success("Sistema optimizado")

# ---------------- IMPACTO ----------------

st.subheader("💰 Impacto Económico")

precio = st.number_input("Precio tonelada ($)", value=100)
perdida = df["plan"].sum() - df["real"].sum()

if perdida > 0:
    st.error(f"Pérdida estimada: ${int(perdida * precio):,}")
else:
    st.success("Sin pérdidas")

# ---------------- IA ----------------

st.subheader("🤖 IA Predictiva")

if IA_OK:
    hist = pd.read_csv("historico.csv")

    if len(hist) > 3:
        X = hist[["plan","espera"]]
        y = hist["real"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        pred = modelo.predict([[df["plan"].sum(), df["espera"].mean()]])[0]

        st.metric("Producción estimada", int(pred))
    else:
        st.info("Faltan datos históricos")
else:
    st.warning("IA no disponible")

# ---------------- GRÁFICOS ----------------

st.subheader("📊 Monitoreo Operacional")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(px.line(df, y=["plan","real"], title="Producción"), use_container_width=True)

with col2:
    st.plotly_chart(px.bar(df, y="espera", title="Espera Camiones"), use_container_width=True)

# ---------------- DISPATCH ----------------

st.subheader("🚚 Control de Flota")

if "pala_activa" in df.columns:

    colas = df.groupby("pala_activa")["espera"].mean()
    mejor = colas.idxmin()

    st.success(f"Enviar camiones a: {mejor}")
    st.dataframe(colas)
    # --------------------------------
# IA DESPACHO AUTOMÁTICO
# --------------------------------

st.subheader("🤖 IA Despacho Automático")

if "pala_activa" in df.columns and "espera" in df.columns:

    # estado actual del sistema
    colas = df.groupby("pala_activa")["espera"].mean()
    produccion = df.groupby("pala_activa")["real"].sum()

    # función de decisión inteligente
    def score_pala(p):
        return colas[p] * 0.6 - produccion[p] * 0.0005

    # elegir mejor pala
    mejor_pala = min(colas.index, key=score_pala)

    st.success(f"Asignación automática: enviar próximo camión a {mejor_pala}")

    # mostrar evaluación
    decision_df = pd.DataFrame({
        "Pala": colas.index,
        "Cola": colas.values,
        "Producción": produccion.values,
        "Score": [score_pala(p) for p in colas.index]
    })

    st.dataframe(decision_df)
st.subheader("🚚 Simulación Decisiones Automáticas")

n_camiones = st.slider("Simular camiones", 1, 20, 5)

asignaciones = []

for i in range(n_camiones):
    mejor_pala = min(colas.index, key=score_pala)
    asignaciones.append(mejor_pala)
    colas[mejor_pala] += 0.5  # simula llegada
t.write("Asignaciones automáticas:")
st.write(asignaciones)
def score_pala(p):
    return (
        colas[p] * 0.5 +
        (100 - produccion[p] / max(produccion)) * 50
    )
# ---------------- BALANCE ----------------

st.subheader("⚖️ Balance Sistema")

balance_df = pd.DataFrame({
    "Proceso": ["Perforación","Carguío","Transporte"],
    "Valor": [
        indicadores["Perforación"],
        indicadores["Producción"],
        100 - indicadores["Espera"] * 10
    ]
})

st.plotly_chart(
    px.bar(balance_df, x="Proceso", y="Valor", color="Valor"),
    use_container_width=True
)
