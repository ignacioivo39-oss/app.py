import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
import random

st.set_page_config(page_title="PIOM ENTERPRISE", layout="wide")

st.title("PIOM - Sistema Inteligente de Operación Minera")
st.markdown("### Control • Predicción • Optimización • Decisión")

archivo = st.file_uploader("Cargar datos operacionales", type=["xlsx"])

# --------------------------------
# FUNCIONES BASE
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

# --------------------------------
# FUNCIONES NUEVAS PRO
# --------------------------------

def formatear_kpi(valor, unidad):
    if unidad == "%":
        return f"{valor:.1f} %"
    elif unidad == "min":
        return f"{valor:.1f} min"
    elif unidad == "$":
        return f"${valor:,.0f}"
    elif unidad == "eventos":
        return f"{int(valor)} eventos"
    else:
        return str(valor)

def estado_operacional(prod, espera, fallas):
    if prod >= 95 and espera < 5 and fallas < 1000:
        return "🟢 Sistema estable"
    elif prod >= 85:
        return "🟡 Sistema en alerta"
    else:
        return "🔴 Sistema crítico"

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
#  APP
# --------------------------------

if not archivo:
    st.warning("Cargar archivo")
    st.stop()

df = cargar(archivo)
ind = indicadores(df)

# --------------------------------
# SALA DE CONTROL (MEJORADA)
# --------------------------------

st.subheader("Sala de Control")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Producción (%)", formatear_kpi(ind["prod"], "%"))
c2.metric("Perforación (%)", formatear_kpi(ind["perf"], "%"))
c3.metric("Tiempo Espera (min)", formatear_kpi(ind["espera"], "min"))
c4.metric("Fallas Equipos", formatear_kpi(ind["mant"], "eventos"))

# --------------------------------
# 🟢 ESTADO OPERACIONAL
# --------------------------------

st.subheader("Estado Operacional")

estado = estado_operacional(ind["prod"], ind["espera"], ind["mant"])

if "estable" in estado:
    st.success(estado)
elif "alerta" in estado:
    st.warning(estado)
else:
    st.error(estado)

# --------------------------------
# DIAGNÓSTICO
# --------------------------------

st.subheader("Diagnóstico")

problemas = diagnostico(ind)

if "Baja producción" in problemas:
    st.warning("⚠️ Producción bajo objetivo")

if "Congestión flota" in problemas:
    st.warning("⚠️ Tiempos de espera elevados")

if "Baja perforación" in problemas:
    st.warning("⚠️ Bajo rendimiento de perforación")

if "Fallas equipos" in problemas:
    st.warning("⚠️ Alta tasa de fallas en equipos")

if not problemas:
    st.success("✅ Operación balanceada")

# --------------------------------
# IMPACTO ECONÓMICO
# --------------------------------

st.subheader("Impacto Económico")

precio = st.number_input("Precio por tonelada ($)", 100)

perdida = df["Plan"].sum() - df["Real"].sum()
impacto = perdida * precio

st.metric("Pérdida económica", formatear_kpi(impacto, "$"))

# --------------------------------
# 🚛 MOTOR DISPATCH
# --------------------------------

ranking, colas, prod = motor_dispatch(df)

st.subheader("Motor de Despacho")

mejor = ranking[0]
segunda = ranking[1] if len(ranking)>1 else ranking[0]

col1, col2 = st.columns(2)

col1.success(f"Enviar camiones a: {mejor}")
col2.info(f"Próxima asignación: {segunda}")

# --------------------------------
# DECISIÓN POR EQUIPO
# --------------------------------

st.subheader("Decisión por Equipo")

for pala in ranking:
    col1, col2 = st.columns(2)
    col1.success(f"{pala} → Prioridad")
    col2.info(f"{pala} → Flujo recomendado")

# --------------------------------
# SIMULACIÓN DISPATCH
# --------------------------------

st.subheader("Simulación Dispatch")

n = st.slider("Camiones", 1, 30, 10)

colas_sim = colas.copy()
asignaciones = []

for i in range(n):
    mejor_sim = min(colas_sim.index, key=lambda p: colas_sim[p])
    asignaciones.append(mejor_sim)
    colas_sim[mejor_sim] += 0.7

st.dataframe(pd.DataFrame({
    "Camión": range(1,n+1),
    "Destino": asignaciones
}))

# --------------------------------
# VISUAL
# --------------------------------

st.subheader("Balance Sistema")

balance = pd.DataFrame({
    "Proceso": ["Perforación","Producción","Transporte"],
    "Valor": [ind["perf"], ind["prod"], 100 - ind["espera"]*10]
})

st.plotly_chart(px.bar(balance, x="Proceso", y="Valor", color="Valor"),
                use_container_width=True)

# --------------------------------
# ALERTAS INTELIGENTES (MEJORADAS)
# --------------------------------

st.subheader("Alertas Inteligentes")

hay_alertas = False
max_prod = max(prod.values())

for p in colas:

    if colas[p] > 5:
        st.error(f"{p} saturada (alta congestión)")
        hay_alertas = True

    elif colas[p] > 3:
        st.warning(f"{p} en riesgo de congestión")
        hay_alertas = True

    if prod[p] < max_prod * 0.8:
        st.warning(f"{p} bajo rendimiento")
        hay_alertas = True

if not hay_alertas:
    st.success("Sistema sin alertas críticas")
