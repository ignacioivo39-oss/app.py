import streamlit as st
import pandas as pd
import plotly.express as px
import time
import random

st.set_page_config(page_title="PIOM ENTERPRISE", layout="wide")

st.title("PIOM - Sistema Inteligente de Operación Minera")
st.markdown("### Control • Predicción • Optimización • Decisión")

archivo = st.file_uploader("Cargar datos operacionales", type=["xlsx"])

# --------------------------------
# 🔧 VALIDACIÓN COLUMNAS
# --------------------------------

columnas_necesarias = [
    "Real","Plan","Metros_real","Metros_plan",
    "Espera","Mant_no_prog","Pala_activa"
]

# --------------------------------
# 🔧 FUNCIONES BASE
# --------------------------------

@st.cache_data
def cargar(file):
    df = pd.read_excel(file)
    df = df.fillna(0)
    return df

def indicadores(df):
    try:
        prod = df["Real"].sum() / df["Plan"].sum() * 100 if df["Plan"].sum() > 0 else 0
        perf = df["Metros_real"].sum() / df["Metros_plan"].sum() * 100 if df["Metros_plan"].sum() > 0 else 0
        espera = df["Espera"].mean()
        mant = df["Mant_no_prog"].sum()

        return {"prod": prod, "perf": perf, "espera": espera, "mant": mant}
    except:
        return {"prod": 0, "perf": 0, "espera": 0, "mant": 0}

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
# 🧠 FUNCIONES PRO
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
    return str(valor)

def estado_operacional(prod, espera, fallas):
    if prod >= 95 and espera < 5 and fallas < 1000:
        return "🟢 Sistema estable"
    elif prod >= 85:
        return "🟡 Sistema en alerta"
    return "🔴 Sistema crítico"

def motor_dispatch(df):
    colas = df.groupby("Pala_activa")["Espera"].mean()
    prod = df.groupby("Pala_activa")["Real"].sum()

    if len(prod) == 0:
        return [], colas, prod

    max_prod = prod.max() if prod.max() > 0 else 1

    def score(p):
        return colas[p]*0.6 + (1 - prod[p]/max_prod)*20

    ranking = sorted(colas.index, key=score)

    return ranking, colas, prod

# --------------------------------
# 🚀 APP
# --------------------------------

if not archivo:
    st.warning("Cargar archivo")
    st.stop()

df = cargar(archivo)

# validar columnas
faltantes = [c for c in columnas_necesarias if c not in df.columns]

if faltantes:
    st.error(f"Faltan columnas en el Excel: {faltantes}")
    st.stop()

ind = indicadores(df)

# --------------------------------
# 🖥️ SALA DE CONTROL
# --------------------------------

st.subheader("Sala de Control")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Producción (%)", formatear_kpi(ind["prod"], "%"))
c2.metric("Perforación (%)", formatear_kpi(ind["perf"], "%"))
c3.metric("Tiempo Espera (min)", formatear_kpi(ind["espera"], "min"))
c4.metric("Fallas Equipos", formatear_kpi(ind["mant"], "eventos"))

# --------------------------------
# 🟢 ESTADO
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
# 🔍 DIAGNÓSTICO
# --------------------------------

st.subheader("Diagnóstico")

problemas = diagnostico(ind)

for p in problemas:
    st.warning(p)

if not problemas:
    st.success("Operación balanceada")

# --------------------------------
# 💰 IMPACTO
# --------------------------------

st.subheader("Impacto Económico")

precio = st.number_input("Precio por tonelada ($)", 100)

perdida = max(df["Plan"].sum() - df["Real"].sum(), 0)
impacto = perdida * precio

st.metric("Pérdida económica", formatear_kpi(impacto, "$"))

# --------------------------------
# 🚛 DISPATCH
# --------------------------------

ranking, colas, prod = motor_dispatch(df)

st.subheader("Motor de Despacho")

if len(ranking) > 0:

    mejor = ranking[0]
    segunda = ranking[1] if len(ranking)>1 else ranking[0]

    col1, col2 = st.columns(2)
    col1.success(f"Enviar camiones a: {mejor}")
    col2.info(f"Próxima asignación: {segunda}")

# --------------------------------
# ⚙️ EQUIPOS
# --------------------------------

st.subheader("Decisión por Equipo")

for pala in ranking:
    col1, col2 = st.columns(2)
    col1.success(f"{pala} → Prioridad")
    col2.info(f"{pala} → Flujo recomendado")

# --------------------------------
# 🔄 SIMULACIÓN
# --------------------------------

st.subheader("Simulación Dispatch")

if len(colas) > 0:

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
# 📊 VISUAL
# --------------------------------

st.subheader("Balance Sistema")

balance = pd.DataFrame({
    "Proceso": ["Perforación","Producción","Transporte"],
    "Valor": [ind["perf"], ind["prod"], max(0, 100 - ind["espera"]*10)]
})

st.plotly_chart(px.bar(balance, x="Proceso", y="Valor", color="Valor"),
                use_container_width=True)

# --------------------------------
# 🚨 ALERTAS
# --------------------------------

st.subheader("Alertas Inteligentes")

if len(prod) > 0:

    hay_alertas = False
    max_prod = prod.max() if prod.max() > 0 else 1

    for p in colas.index:

        if colas[p] > 5:
            st.error(f"{p} saturada")
            hay_alertas = True

        elif colas[p] > 3:
            st.warning(f"{p} en riesgo de congestión")
            hay_alertas = True

        if prod[p] < max_prod * 0.8:
            st.warning(f"{p} bajo rendimiento")
            hay_alertas = True

    if not hay_alertas:
        st.success("Sistema sin alertas críticas")
