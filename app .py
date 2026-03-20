import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="PIOM ENTERPRISE", layout="wide")

st.title("⛏️ PIOM ENTERPRISE - Sistema Inteligente de Operación Minera")
st.markdown("### Control • Predicción • Optimización • Decisión")

archivo = st.file_uploader("Cargar datos operacionales", type=["xlsx"])

# --------------------------------
# FUNCIONES CORE
# --------------------------------

@st.cache_data
def cargar(file):
    df = pd.read_excel(file)
    df = df.fillna(0)
    return df

def indicadores(df):
    return {
        "prod": df["Real"].sum() / df["Plan"].sum() * 100,
        "perf": df["Metros_real"].sum() / df["Metros_plan"].sum() * 100,
        "espera": df["Espera"].mean(),
        "mant": df["Mant_no_prog"].sum()
    }

def diagnostico(ind):
    problemas = []

    if ind["prod"] < 90:
        problemas.append("Baja producción")

    if ind["espera"] > 5:
        problemas.append("Congestión flota")

    if ind["perf"] < 85:
        problemas.append("Baja perforación")

    if ind["mant"] > 20:
        problemas.append("Fallas equipos")

    return problemas

def motor_dispatch(df):

    colas = df.groupby("Pala_activa")["Espera"].mean()
    prod = df.groupby("Pala_activa")["Real"].sum()

    max_prod = prod.max()

    def score(p):
        return colas[p]*0.6 + (1 - prod[p]/max_prod)*20

    palas = list(colas.index)
    ranking = sorted(palas, key=score)

    return ranking, colas, prod

# --------------------------------
# APP
# --------------------------------

if not archivo:
    st.warning("Cargar archivo")
    st.stop()

df = cargar(archivo)
ind = indicadores(df)

# --------------------------------
# SALA DE CONTROL
# --------------------------------

st.subheader("🎛️ Sala de Control")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Producción %", round(ind["prod"],1))
c2.metric("Perforación %", round(ind["perf"],1))
c3.metric("Espera", round(ind["espera"],1))
c4.metric("Fallas", ind["mant"])

# --------------------------------
# ESTADO GLOBAL
# --------------------------------

st.subheader("📡 Estado Operacional")

if ind["prod"] < 85:
    st.error("🔴 Sistema crítico")
elif ind["espera"] > 5:
    st.warning("🟡 Sistema congestionado")
else:
    st.success("🟢 Sistema estable")

# --------------------------------
# DIAGNÓSTICO
# --------------------------------

st.subheader("🧠 Diagnóstico Inteligente")

problemas = diagnostico(ind)

for p in problemas:
    st.warning(p)

if not problemas:
    st.success("Operación balanceada")

# --------------------------------
# IMPACTO ECONÓMICO
# --------------------------------

st.subheader("💰 Impacto Económico")

precio = st.number_input("Precio tonelada", 100)

perdida = df["Plan"].sum() - df["Real"].sum()

st.metric("Pérdida $", int(perdida * precio))

# --------------------------------
# MOTOR DISPATCH
# --------------------------------

ranking, colas, prod = motor_dispatch(df)

st.subheader("🚚 Motor de Despacho Inteligente")

mejor = ranking[0]
segunda = ranking[1] if len(ranking)>1 else ranking[0]

col1, col2 = st.columns(2)

col1.success(f"Enviar camiones a: {mejor}")
col2.info(f"Próxima asignación: {segunda}")

# --------------------------------
# DECISIÓN POR EQUIPO
# --------------------------------

st.subheader("🏗️ Decisión por Equipo")

for pala in ranking:

    col1, col2 = st.columns(2)

    col1.success(f"{pala} → Prioridad")
    col2.info(f"{pala} → Flujo recomendado")

# --------------------------------
# SIMULADOR DESPACHO
# --------------------------------

st.subheader("🚚 Simulación Dispatch")

n = st.slider("Camiones", 1, 30, 10)

colas_sim = colas.copy()
prod_sim = prod.copy()

asignaciones = []

for i in range(n):
    mejor = min(colas_sim.index, key=lambda p: colas_sim[p])
    asignaciones.append(mejor)
    colas_sim[mejor] += 0.7

st.dataframe(pd.DataFrame({
    "Camión": range(1,n+1),
    "Destino": asignaciones
}))

# --------------------------------
# VISUAL
# --------------------------------

st.subheader("📊 Balance Sistema")

balance = pd.DataFrame({
    "Proceso": ["Perforación","Producción","Transporte"],
    "Valor": [ind["perf"], ind["prod"], 100 - ind["espera"]*10]
})

st.plotly_chart(px.bar(balance, x="Proceso", y="Valor", color="Valor"),
                use_container_width=True)
import time
import random

# --------------------------------
# SIMULACIÓN TIEMPO REAL
# --------------------------------

st.subheader("🚨 Simulación Operacional en Tiempo Real")

if "Pala_activa" in df.columns:

    # estado inicial
    palas = list(df["Pala_activa"].unique())

    colas = {p: random.uniform(1,4) for p in palas}
    produccion = {p: random.randint(1000,3000) for p in palas}

    # control
    iniciar = st.button("▶️ Iniciar Simulación")
    detener = st.button("⛔ Detener")

    placeholder = st.empty()

    if iniciar:

        for ciclo in range(50):  # ciclos simulados

            if detener:
                break

            # lógica IA (decisión)
            def score(p):
                return colas[p]*0.6 + (1 - produccion[p]/max(produccion.values()))*20

            mejor_pala = min(palas, key=score)

            # simular llegada camión
            colas[mejor_pala] += random.uniform(0.3,1)

            # simular salida (descarga)
            salida = random.choice(palas)

            if colas[salida] > 0:
                colas[salida] -= random.uniform(0.2,0.8)
                produccion[salida] += random.randint(150,250)

            # mostrar estado
            with placeholder.container():

                st.markdown(f"### ⏱️ Ciclo {ciclo+1}")

                col1, col2 = st.columns(2)

                col1.success(f"🚚 Enviar camión a: {mejor_pala}")
                col2.info(f"📊 Producción total: {sum(produccion.values())}")

                st.write("### 📊 Estado Palas")

                estado_df = pd.DataFrame({
                    "Pala": palas,
                    "Cola": [round(colas[p],2) for p in palas],
                    "Producción": [produccion[p] for p in palas]
                })

                st.dataframe(estado_df)

            time.sleep(1)
# --------------------------------
# MOTOR DE OPTIMIZACIÓN PIOM (CORE)
# --------------------------------

st.subheader("🧠 Motor de Optimización PIOM (Nivel Profesional)")

if "Pala_activa" in df.columns:

    # estado actual
    colas = df.groupby("Pala_activa")["Espera"].mean().to_dict()
    produccion = df.groupby("Pala_activa")["Real"].sum().to_dict()

    palas = list(colas.keys())

    # parámetros del sistema
    capacidad_pala = {p: 6 for p in palas}  # capacidad máxima camiones
    carga_actual = {p: 0 for p in palas}

    # función de costo
    def costo(p):

        # congestión
        congestion = colas[p]

        # desbalance
        balance = (max(produccion.values()) - produccion[p]) / max(produccion.values())

        # saturación
        saturacion = carga_actual[p] / capacidad_pala[p]

        return (
            congestion * 0.5 +
            balance * 30 +
            saturacion * 20
        )

    # simulación asignación
    n_camiones = st.slider("Camiones a optimizar", 1, 50, 15)

    asignaciones = []

    for i in range(n_camiones):

        mejor = min(palas, key=costo)

        asignaciones.append(mejor)

        # actualizar sistema dinámico
        carga_actual[mejor] += 1
        colas[mejor] += 0.6
        produccion[mejor] += 200

    # resultados
    resultado = pd.DataFrame({
        "Camión": [f"CA-{i+1}" for i in range(n_camiones)],
        "Destino Óptimo": asignaciones
    })

    st.dataframe(resultado)

    # resumen
    st.subheader("📊 Distribución Óptima")

    distribucion = pd.Series(asignaciones).value_counts()

    st.bar_chart(distribucion)
# --------------------------------
# IA AVANZADA PIOM (NIVEL IMPACTO)
# --------------------------------

st.subheader("🧠 IA Operacional Avanzada")

if all(col in df.columns for col in ["Pala_activa","Espera","tiempo_ciclo","Real"]):

    colas = df.groupby("Pala_activa")["Espera"].mean().to_dict()
    ciclos = df.groupby("Pala_activa")["tiempo_ciclo"].mean().to_dict()
    produccion = df.groupby("Pala_activa")["Real"].sum().to_dict()

    palas = list(colas.keys())
    max_prod = max(produccion.values())

    def analizar_pala(p):

        espera = colas[p]
        ciclo = ciclos[p]
        prod = produccion[p]

        problemas = []

        if espera > 5:
            problemas.append("alta congestión")

        if ciclo > 25:
            problemas.append("ciclo lento")

        if prod < max_prod * 0.7:
            problemas.append("baja producción")

        return problemas

    # evaluar todas
    analisis = {p: analizar_pala(p) for p in palas}

    # función costo real
    def costo(p):
        return (
            ciclos[p]*0.4 +
            colas[p]*0.3 +
            (1 - produccion[p]/max_prod)*20
        )

    ranking = sorted(palas, key=costo)

    mejor = ranking[0]
    segunda = ranking[1] if len(ranking) > 1 else mejor

    # ---------------- RESULTADO ----------------

    st.subheader("🚚 Decisión Inteligente")

    st.success(f"Enviar camiones a: {mejor}")
    st.info(f"Asignación automática: enviar próximo camión a {segunda}")

    # ---------------- EXPLICACIÓN ----------------

    st.subheader("📡 Explicación IA")

    problemas = analisis[mejor]

    if problemas:
        st.warning(f"{mejor} optimiza el sistema porque tiene: {', '.join(problemas)}")
    else:
        st.success(f"{mejor} es la pala más eficiente del sistema")

    # ---------------- PREDICCIÓN ----------------

    st.subheader("🔮 Predicción Operacional")

    futura_espera = colas[mejor] + 2

    if futura_espera > 6:
        st.error("Riesgo de congestión en los próximos ciclos")
    else:
        st.success("Sistema estable en los próximos ciclos")

    # ---------------- ALERTAS ----------------

    st.subheader("🚨 Alertas Inteligentes")

    for p in palas:
        if colas[p] > 6:
            st.error(f"{p} saturada")
        elif produccion[p] < max_prod * 0.6:
            st.warning(f"{p} bajo rendimiento")
