import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# --------------------------------
# CONFIG
# --------------------------------

st.set_page_config(page_title="PIOM", layout="wide")

st.title("⛏️ PIOM - Inteligencia Operacional Minera")
st.write("Sistema inteligente con aprendizaje automático")

archivo = st.file_uploader("Subir Excel", type=["xlsx"])

# --------------------------------
# HISTÓRICO IA
# --------------------------------

if "historico.csv" not in os.listdir():
    pd.DataFrame(columns=["real","plan","espera"]).to_csv("historico.csv", index=False)

# --------------------------------
# FUNCIONES
# --------------------------------

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


# --------------------------------
# APP
# --------------------------------

if archivo:

    df = cargar_excel(archivo)

    if "real" not in df.columns or "plan" not in df.columns:
        st.error("❌ El Excel debe tener columnas: real y plan")
        st.stop()

    indicadores = calcular_indicadores(df)

    # ---------------- KPIs ----------------

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

    # ---------------- IMPACTO ECONÓMICO ----------------

    st.subheader("💰 Impacto Económico")

    precio = st.number_input("Precio por tonelada ($)", value=100)

    perdida = df["plan"].sum() - df["real"].sum()
    impacto = perdida * precio

    if perdida > 0:
        st.error(f"Pérdida: ${int(impacto):,}")
    else:
        st.success("Sin pérdidas")

    # ---------------- GUARDAR HISTÓRICO ----------------

    st.subheader("💾 Aprendizaje IA")

    if st.button("Guardar turno para IA"):

        nuevo = pd.DataFrame({
            "real": [df["real"].sum()],
            "plan": [df["plan"].sum()],
            "espera": [df["espera"].mean() if "espera" in df else 0]
        })

        hist = pd.read_csv("historico.csv")
        hist = pd.concat([hist, nuevo], ignore_index=True)
        hist.to_csv("historico.csv", index=False)

        st.success("Turno guardado")

    # ---------------- IA ----------------

    st.subheader("🤖 IA Predictiva")

    hist = pd.read_csv("historico.csv")

    if len(hist) > 3:

        X = hist[["plan","espera"]]
        y = hist["real"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        pred = modelo.predict([[df["plan"].sum(), df["espera"].mean()]])[0]

        st.metric("Predicción IA Producción", int(pred))

        # riesgo
        st.subheader("⚠️ Riesgo IA")

        error = abs(pred - df["real"].sum())

        if error > df["plan"].sum() * 0.1:
            st.error("Riesgo alto")
        else:
            st.success("Riesgo bajo")

    else:
        st.info("Necesitas al menos 4 turnos para IA")

    # ---------------- GRÁFICOS ----------------

    st.subheader("📊 Producción")

    st.plotly_chart(
        px.line(df, y=["plan","real"], markers=True),
        use_container_width=True,
        key="g1"
    )

    df["desv"] = ((df["real"] - df["plan"]) / df["plan"].replace(0,1)) * 100

    st.subheader("📉 Desviación")

    st.plotly_chart(
        px.bar(df, y="desv", color="desv"),
        use_container_width=True,
        key="g2"
    )

    # ---------------- RANKING ----------------

    if "pala_activa" in df.columns:
        st.subheader("🏆 Ranking Palas")

        rank = df.groupby("pala_activa")[["real","plan"]].sum()
        rank["Eficiencia"] = (rank["real"] / rank["plan"]) * 100

        st.dataframe(rank.sort_values("Eficiencia", ascending=False))

    # ---------------- REPORTE ----------------

    st.subheader("📄 Reporte")

    rep = f"""
Producción: {int(df["real"].sum())}
Plan: {int(df["plan"].sum())}
Estado: {estado_mina(indicadores)}
Cuello: {cuello}
"""

    st.text_area("Reporte Ejecutivo", rep, height=150)

else:
    st.info("Sube un archivo Excel para comenzar")
    st.subheader("🚚 IA Optimización de Flota")

capacidad = st.number_input("Capacidad camión (ton)", 200)
tiempo_ciclo = st.number_input("Tiempo ciclo (min)", 25)

mejor_prod = 0
mejor_n = 0

for n in range(1, 25):
    prod = (n * capacidad * 12 * 60) / tiempo_ciclo

    if prod > mejor_prod:
        mejor_prod = prod
        mejor_n = n

st.success(f"Flota óptima recomendada: {mejor_n} camiones")

# Comparación real
prod_actual = (8 * capacidad * 12 * 60) / tiempo_ciclo

st.write(f"Producción actual estimada: {int(prod_actual)} ton")
st.write(f"Producción óptima estimada: {int(mejor_prod)} ton")
st.subheader("🔧 IA Mantenimiento Predictivo")

if indicadores["Mant"] > 20:
    st.error("Alta tasa de fallas detectada")

    if indicadores["Producción"] < 90:
        st.warning("Impacto directo en producción")

    st.info("Recomendación: aumentar mantenimiento preventivo")

else:
    st.success("Nivel de mantenimiento controlado")
    st.subheader("⛏️ IA Optimización Perforación")

if "metros_real" in df.columns and "metros_plan" in df.columns:

    perf = indicadores["Perforación"]

    if perf < 85:
        st.error("Baja eficiencia de perforación")

        st.info("Acciones sugeridas:")
        st.write("- Revisar tiempos de cambio de barra")
        st.write("- Evaluar disponibilidad de equipos")
        st.write("- Capacitación operador")

    else:
        st.success("Perforación eficiente")
        st.subheader("🧠 Diagnóstico Inteligente")

if indicadores["Espera"] > 5:
    causa = "Transporte saturado"
elif indicadores["Mant"] > 20:
    causa = "Fallas de equipos"
elif indicadores["Perforación"] < 90:
    causa = "Perforación deficiente"
else:
    causa = "Sistema balanceado"

st.warning(f"Problema raíz detectado: {causa}")
# --------------------------------
# IA POR EQUIPO
# --------------------------------

st.subheader("🧠 IA por Equipo (Análisis Avanzado)")

# ---- PALAS ----
if "pala_activa" in df.columns:

    pala = df.groupby("pala_activa")[["real","plan"]].sum()
    pala["eficiencia"] = (pala["real"] / pala["plan"]) * 100

    peor_pala = pala["eficiencia"].idxmin()
    mejor_pala = pala["eficiencia"].idxmax()

    st.write(f"🔻 Peor pala: **{peor_pala}** ({round(pala.loc[peor_pala,'eficiencia'],1)}%)")
    st.write(f"🔺 Mejor pala: **{mejor_pala}** ({round(pala.loc[mejor_pala,'eficiencia'],1)}%)")

    if pala.loc[peor_pala,"eficiencia"] < 85:
        st.error(f"Pala crítica detectada: {peor_pala}")
        st.info("Acción: redistribuir camiones o revisar operador")

# ---- PERFORADORAS ----
if "equipo_perforacion" in df.columns:

    perf = df.groupby("equipo_perforacion")[["metros_real","metros_plan"]].sum()
    perf["eficiencia"] = (perf["metros_real"] / perf["metros_plan"]) * 100

    peor_perf = perf["eficiencia"].idxmin()

    if perf.loc[peor_perf,"eficiencia"] < 85:
        st.error(f"Perforadora crítica: {peor_perf}")
        st.info("Acción: revisar disponibilidad o tiempos muertos")

# ---- CAMIONES (SI EXISTEN) ----
if "camion" in df.columns:

    cam = df.groupby("camion")["espera"].mean().reset_index()

    peor_camion = cam.sort_values("espera", ascending=False).iloc[0]

    if peor_camion["espera"] > 6:
        st.error(f"Camión con mayor espera: {peor_camion['camion']}")
        st.info("Acción: revisar asignación de flota")
        # --------------------------------
# SALA DE CONTROL MINA
# --------------------------------

st.subheader("🎛️ Sala de Control Operacional")

col1, col2, col3 = st.columns(3)

# Producción
if indicadores["Producción"] >= 95:
    col1.success("Producción 🟢")
elif indicadores["Producción"] >= 85:
    col1.warning("Producción 🟡")
else:
    col1.error("Producción 🔴")

# Transporte
if indicadores["Espera"] <= 3:
    col2.success("Transporte 🟢")
elif indicadores["Espera"] <= 5:
    col2.warning("Transporte 🟡")
else:
    col2.error("Transporte 🔴")

# Mantención
if indicadores["Mant"] <= 10:
    col3.success("Equipos 🟢")
elif indicadores["Mant"] <= 20:
    col3.warning("Equipos 🟡")
else:
    col3.error("Equipos 🔴")
    st.subheader("📊 Mapa de Eficiencia Equipos")

if "pala_activa" in df.columns:

    ef = df.groupby("pala_activa")[["real","plan"]].sum()
    ef["eficiencia"] = (ef["real"] / ef["plan"]) * 100

    fig = px.bar(
        ef.reset_index(),
        x="pala_activa",
        y="eficiencia",
        color="eficiencia",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(fig, use_container_width=True)
# --------------------------------
# MOTOR DE DESPACHO (CORE REAL)
# --------------------------------

st.subheader("🚚 Motor de Despacho Inteligente")

if "pala_activa" in df.columns and "camion" in df.columns:

    # calcular colas (espera promedio por pala)
    colas = df.groupby("pala_activa")["espera"].mean().reset_index()

    # seleccionar pala con menor espera
    mejor_pala = colas.sort_values("espera").iloc[0]["pala_activa"]

    st.success(f"Asignar próximos camiones a: {mejor_pala}")

    st.write("Colas actuales:")
    st.dataframe(colas)
    st.subheader("⚖️ Balance Flota - Palas")

prod = df.groupby("pala_activa")["real"].sum().reset_index()

total = prod["real"].sum()

prod["participacion_%"] = (prod["real"] / total) * 100

st.dataframe(prod)

# detectar desequilibrio
if prod["participacion_%"].max() > 50:
    st.warning("Desbalance detectado: una pala está sobrecargada")
    st.subheader("⏱️ Control de Ciclo")

if "espera" in df.columns:

    ciclo = df["espera"].mean() + 20  # simplificado

    st.metric("Tiempo ciclo estimado (min)", round(ciclo,1))

    if ciclo > 30:
        st.error("Ciclo alto → baja eficiencia")
        from sklearn.ensemble import RandomForestRegressor

st.subheader("🤖 IA por Pala")

if "pala_activa" in df.columns:

    data = df[["pala_activa","plan","espera","real"]]

    # convertir texto a número
    data = pd.get_dummies(data, columns=["pala_activa"])

    X = data.drop("real", axis=1)
    y = data["real"]

    modelo = RandomForestRegressor()
    modelo.fit(X, y)

    pred = modelo.predict(X)

    st.write("Predicción promedio:", int(pred.mean()))
st.subheader("🚨 IA detección equipos deficientes")

df["ratio"] = df["real"] / df["plan"]

bajo = df[df["ratio"] < 0.8]

if not bajo.empty:
    st.error("Equipos bajo rendimiento detectados")
    st.dataframe(bajo)
    st.subheader("🚚 IA recomendación flota")

espera = df["espera"].mean()

if espera > 5:
    st.warning("Reducir camiones → congestión")
elif espera < 2:
    st.success("Aumentar camiones → capacidad disponible")
