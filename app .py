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

st.title("⛏️ PIOM PRO - Inteligencia Operacional Minera")
st.write("Optimización de producción, flota y decisiones en tiempo real")

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
        return "🔴 Sistema Saturado"
    elif ind["Producción"] < 90:
        return "🟡 Riesgo Productivo"
    elif ind["Espera"] > 4:
        return "🟡 Congestión Transporte"
    return "🟢 Operación Normal"

def detectar_cuello(ind):
    problema = {
        "Perforación": 100 - ind["Perforación"],
        "Carguío": 100 - ind["Producción"],
        "Transporte": ind["Espera"],
        "Mantención": ind["Mant"]
    }
    return max(problema, key=problema.get)

# ---------------- APP PRINCIPAL ----------------

if not archivo:
    st.info("Sube un archivo Excel para comenzar")
    st.stop()

df = cargar_excel(archivo)

if "real" not in df.columns or "plan" not in df.columns:
    st.error("El Excel debe contener columnas: real y plan")
    st.stop()

indicadores = calcular_indicadores(df)

# ---------------- KPI ----------------

st.subheader("📊 KPIs Operacionales")

c1, c2, c3 = st.columns(3)
c1.metric("Perforación %", round(indicadores["Perforación"], 1))
c2.metric("Producción %", round(indicadores["Producción"], 1))
c3.metric("Espera (min)", round(indicadores["Espera"], 1))

# ---------------- ESTADO ----------------

st.subheader("📡 Estado Sistema")
st.markdown(f"### {estado_mina(indicadores)}")

# ---------------- CUELLO ----------------

cuello = detectar_cuello(indicadores)
st.subheader("🚨 Cuello de Botella")
st.error(cuello)

# ---------------- IMPACTO ----------------

st.subheader("💰 Impacto Económico")

precio = st.number_input("Precio tonelada ($)", value=100)
perdida = df["plan"].sum() - df["real"].sum()
impacto = perdida * precio

if perdida > 0:
    st.error(f"Pérdida estimada: ${int(impacto):,}")
else:
    st.success("Sin pérdidas")

# ---------------- IA HISTÓRICA ----------------

st.subheader("🧠 Aprendizaje")

if st.button("Guardar turno"):
    nuevo = pd.DataFrame({
        "real": [df["real"].sum()],
        "plan": [df["plan"].sum()],
        "espera": [df["espera"].mean()]
    })
    hist = pd.read_csv("historico.csv")
    hist = pd.concat([hist, nuevo], ignore_index=True)
    hist.to_csv("historico.csv", index=False)
    st.success("Turno guardado")

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
        st.metric("Producción estimada IA", int(pred))

        if abs(pred - df["real"].sum()) > df["plan"].sum() * 0.1:
            st.error("Riesgo alto")
        else:
            st.success("Riesgo bajo")

    else:
        st.info("Se requieren más datos históricos")
else:
    st.warning("IA no disponible")

# ---------------- GRÁFICOS ----------------

st.subheader("📈 Producción")

st.plotly_chart(
    px.line(df, y=["plan","real"], markers=True),
    use_container_width=True
)

df["desv"] = ((df["real"] - df["plan"]) / df["plan"].replace(0,1)) * 100

st.subheader("📉 Desviación")

st.plotly_chart(
    px.bar(df, y="desv", color="desv"),
    use_container_width=True
)

# ---------------- IA POR EQUIPO ----------------

st.subheader("🧠 IA por Equipo")

if IA_OK and "pala_activa" in df.columns:

    data = df[["pala_activa","plan","espera","real"]]
    data = pd.get_dummies(data, columns=["pala_activa"])

    X = data.drop("real", axis=1)
    y = data["real"]

    modelo = RandomForestRegressor()
    modelo.fit(X, y)

    st.metric("Predicción promedio", int(modelo.predict(X).mean()))

# ---------------- MOTOR DISPATCH ----------------

st.subheader("🚚 Motor de Despacho")

if "pala_activa" in df.columns:

    colas = df.groupby("pala_activa")["espera"].mean()
    mejor_pala = colas.idxmin()

    st.success(f"Asignar camiones a: {mejor_pala}")
    st.dataframe(colas)

# ---------------- BALANCE SISTEMA ----------------

st.subheader("⚖️ Balance Sistema")

balance = {
    "Perforación": indicadores["Perforación"],
    "Carguío": indicadores["Producción"],
    "Transporte": 100 - indicadores["Espera"] * 10
}

st.write(balance)
