import streamlit as st
import pandas as pd
import plotly.express as px
import time
import random

st.set_page_config(page_title="PIOM ENTERPRISE", layout="wide")

st.title("PIOM - Plataforma Inteligente de Operación Minera")
st.markdown("### Control • Diagnóstico • Optimización • Predicción • IA")

archivo = st.file_uploader("Cargar datos operacionales", type=["xlsx"])

# --------------------------------
# 🔧 VALIDACIÓN
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
    return df.fillna(0)

def indicadores(df):
    return {
        "prod": df["Real"].sum()/df["Plan"].sum()*100 if df["Plan"].sum()>0 else 0,
        "perf": df["Metros_real"].sum()/df["Metros_plan"].sum()*100 if df["Metros_plan"].sum()>0 else 0,
        "espera": df["Espera"].mean(),
        "mant": df["Mant_no_prog"].sum()
    }

def diagnostico(ind):
    problemas = []
    if ind["prod"] < 90: problemas.append("Baja producción")
    if ind["espera"] > 5: problemas.append("Congestión flota")
    if ind["perf"] < 85: problemas.append("Baja perforación")
    if ind["mant"] > 20: problemas.append("Fallas equipos")
    return problemas

# --------------------------------
# 🧠 FUNCIONES PRO
# --------------------------------

def formatear(valor, u):
    if u == "%": return f"{valor:.1f} %"
    if u == "min": return f"{valor:.1f} min"
    if u == "$": return f"${valor:,.0f}"
    if u == "eventos": return f"{int(valor)}"
    return valor

def estado(prod, espera, fallas):
    if prod >= 95 and espera < 5 and fallas < 1000:
        return "🟢 Estable"
    elif prod >= 85:
        return "🟡 Alerta"
    return "🔴 Crítico"

def dispatch(df):
    colas = df.groupby("Pala_activa")["Espera"].mean()
    prod = df.groupby("Pala_activa")["Real"].sum()
    maxp = prod.max() if len(prod)>0 else 1

    def score(p):
        return colas[p]*0.6 + (1 - prod[p]/maxp)*20

    ranking = sorted(colas.index, key=score)
    return ranking, colas, prod

# --------------------------------
# 🚀 APP
# --------------------------------

if not archivo:
    st.warning("Sube archivo para comenzar")
    st.stop()

df = cargar(archivo)

faltantes = [c for c in columnas_necesarias if c not in df.columns]
if faltantes:
    st.error(f"Faltan columnas: {faltantes}")
    st.stop()

ind = indicadores(df)

# --------------------------------
# 🖥️ SALA DE CONTROL
# --------------------------------

st.subheader("📊 Sala de Control")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Producción", formatear(ind["prod"], "%"))
c2.metric("Perforación", formatear(ind["perf"], "%"))
c3.metric("Espera", formatear(ind["espera"], "min"))
c4.metric("Fallas", formatear(ind["mant"], "eventos"))

# --------------------------------
# 🟢 ESTADO
# --------------------------------

st.subheader("Estado Operacional")
e = estado(ind["prod"], ind["espera"], ind["mant"])

if "Estable" in e: st.success(e)
elif "Alerta" in e: st.warning(e)
else: st.error(e)

# --------------------------------
# 🔍 DIAGNÓSTICO
# --------------------------------

st.subheader("Diagnóstico")
prob = diagnostico(ind)

if prob:
    for p in prob:
        st.warning(p)
else:
    st.success("Operación balanceada")

# --------------------------------
# 💰 IMPACTO
# --------------------------------

st.subheader("Impacto Económico")

precio = st.number_input("Precio tonelada", 100)
perdida = max(df["Plan"].sum()-df["Real"].sum(),0)
st.metric("Pérdida", formatear(perdida*precio,"$"))

# --------------------------------
# 🚛 MOTOR DISPATCH
# --------------------------------

ranking, colas, prod = dispatch(df)

st.subheader("Motor de Despacho")

if ranking:
    st.success(f"Enviar a: {ranking[0]}")
    st.info(f"Siguiente: {ranking[1] if len(ranking)>1 else ranking[0]}")

# --------------------------------
# ⚙️ DECISIÓN
# --------------------------------

st.subheader("Decisión por Equipo")

for p in ranking:
    c1,c2 = st.columns(2)
    c1.success(f"{p} Prioridad")
    c2.info(f"{p} Flujo óptimo")

# --------------------------------
# 🔄 SIMULACIÓN
# --------------------------------

st.subheader("Simulación Dispatch")

if len(colas)>0:
    n = st.slider("Camiones",1,30,10)
    sim = colas.copy()
    asign=[]

    for i in range(n):
        m = min(sim.index, key=lambda p: sim[p])
        asign.append(m)
        sim[m]+=0.7

    st.dataframe(pd.DataFrame({"Camión":range(1,n+1),"Destino":asign}))

# --------------------------------
# ⏱️ TIEMPO REAL
# --------------------------------

st.subheader("Simulación Tiempo Real")

if st.button("Iniciar"):

    palas = list(colas.index)
    colas_rt = {p: random.uniform(1,4) for p in palas}
    prod_rt = {p: random.randint(1000,3000) for p in palas}

    for i in range(20):

        mejor = min(palas, key=lambda p: colas_rt[p])

        colas_rt[mejor]+=0.5
        salida = random.choice(palas)

        if colas_rt[salida]>0:
            colas_rt[salida]-=0.4
            prod_rt[salida]+=200

        st.write(f"Ciclo {i+1} → enviar a {mejor}")
        st.dataframe(pd.DataFrame({
            "Pala":palas,
            "Cola":[round(colas_rt[p],2) for p in palas],
            "Prod":[prod_rt[p] for p in palas]
        }))

        time.sleep(0.5)

# --------------------------------
# 🧠 OPTIMIZACIÓN
# --------------------------------

st.subheader("Optimización PIOM")

if len(colas)>0:

    n = st.slider("Optimizar camiones",1,50,15)
    carga = {p:0 for p in colas.index}
    asign=[]

    maxp = prod.max() if prod.max()>0 else 1

    def costo(p):
        return colas[p]*0.5 + (1-prod[p]/maxp)*30 + (carga[p]/6)*20

    for i in range(n):
        m = min(colas.index, key=costo)
        asign.append(m)
        carga[m]+=1

    st.dataframe(pd.DataFrame({
        "Camión":[f"CA-{i+1}" for i in range(n)],
        "Destino":asign
    }))

    st.bar_chart(pd.Series(asign).value_counts())

# --------------------------------
# 🤖 IA
# --------------------------------

st.subheader("Decisión Inteligente")

if ranking:
    mejor = ranking[0]
    st.success(f"Enviar a {mejor}")

    st.subheader("Explicación IA")

    if colas[mejor]>5:
        st.warning("Alta congestión")
    elif prod[mejor]<prod.max()*0.7:
        st.warning("Baja producción")
    else:
        st.success("Óptima")

# --------------------------------
# 🔮 PREDICCIÓN
# --------------------------------

st.subheader("Predicción Operacional")

if ranking:
    futura = colas[ranking[0]]+2

    if futura>6:
        st.error("Riesgo de congestión")
    else:
        st.success("Sistema estable")

# --------------------------------
# 🚨 ALERTAS
# --------------------------------

st.subheader("Alertas Inteligentes")

hay=False

for p in colas.index:

    if colas[p]>5:
        st.error(f"{p} saturada")
        hay=True

    elif colas[p]>3:
        st.warning(f"{p} en riesgo")
        hay=True

if not hay:
    st.success("Sin alertas críticas")
# --------------------------------
# 📊 RESUMEN EJECUTIVO
# --------------------------------

st.subheader("Resumen Ejecutivo")

# estado general
estado_general = estado(ind["prod"], ind["espera"], ind["mant"])

# principales problemas
problemas = diagnostico(ind)

# pala crítica
pala_critica = None
if len(colas) > 0:
    pala_critica = max(colas.index, key=lambda p: colas[p])

# producción total
produccion_total = df["Real"].sum()

# --------------------------------
# TEXTO EJECUTIVO
# --------------------------------

st.markdown("### Estado General de la Operación")

if "Estable" in estado_general:
    st.success(f"La operación se encuentra en condición ESTABLE, con una producción de {formatear(ind['prod'],'%')} y tiempos de espera controlados ({formatear(ind['espera'],'min')}).")

elif "Alerta" in estado_general:
    st.warning(f"La operación presenta condiciones de ALERTA. Producción: {formatear(ind['prod'],'%')} y tiempos de espera de {formatear(ind['espera'],'min')}.")

else:
    st.error(f"La operación se encuentra en estado CRÍTICO. Producción bajo objetivo ({formatear(ind['prod'],'%')}).")

# --------------------------------
# PROBLEMAS CLAVE
# --------------------------------

st.markdown("### Principales Desviaciones")

if problemas:
    for p in problemas:
        st.write(f"- {p}")
else:
    st.write("No se detectan desviaciones relevantes.")

# --------------------------------
# IMPACTO ECONÓMICO
# --------------------------------

st.markdown("### Impacto Económico")

st.write(f"Pérdida estimada: **{formatear(perdida * precio, '$')}**")

# --------------------------------
# ANÁLISIS OPERACIONAL
# --------------------------------

st.markdown("### Análisis Operacional")

if pala_critica:
    st.write(f"La mayor congestión se presenta en **{pala_critica}**, lo que puede impactar la continuidad operacional.")

if ranking:
    st.write(f"El sistema recomienda priorizar la operación en **{ranking[0]}** para mejorar la eficiencia global.")

# --------------------------------
# PROYECCIÓN
# --------------------------------

st.markdown("### Proyección")
 
if ranking:
    futura = colas[ranking[0]] + 2

    if futura > 6:
        st.warning("Se proyecta riesgo de congestión en los próximos ciclos.")
    else:
        st.success("Se proyecta una operación estable en el corto plazo.")

# --------------------------------
# CONCLUSIÓN
# --------------------------------

st.markdown("### Conclusión")

if "Crítico" in estado_general:
    st.error("Se requiere intervención inmediata en la operación para recuperar niveles de producción.")

elif "Alerta" in estado_general:
    st.warning("Se recomienda ajuste en la asignación de flota y control de congestión.")

else:
    st.success("La operación se encuentra bajo control y en condiciones óptimas.")
# --------------------------------
# 📄 GENERAR REPORTE PDF
# --------------------------------
# --------------------------------
# 📄 GENERAR REPORTE PDF (CORREGIDO)
# --------------------------------

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

def generar_pdf(ind, problemas, perdida, precio, ranking, colas):

    # ✅ ruta segura (SOLUCIÓN AL ERROR)
    ruta = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

    doc = SimpleDocTemplate(ruta)
    styles = getSampleStyleSheet()

    contenido = []

    # TÍTULO
    contenido.append(Paragraph("PIOM - REPORTE OPERACIONAL", styles["Title"]))
    contenido.append(Spacer(1, 12))

    # ESTADO
    contenido.append(Paragraph("Estado General:", styles["Heading2"]))
    contenido.append(Paragraph(estado(ind["prod"], ind["espera"], ind["mant"]), styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # KPIs
    contenido.append(Paragraph("Indicadores:", styles["Heading2"]))
    contenido.append(Paragraph(f"Producción: {formatear(ind['prod'],'%')}", styles["Normal"]))
    contenido.append(Paragraph(f"Perforación: {formatear(ind['perf'],'%')}", styles["Normal"]))
    contenido.append(Paragraph(f"Espera: {formatear(ind['espera'],'min')}", styles["Normal"]))
    contenido.append(Paragraph(f"Fallas: {formatear(ind['mant'],'eventos')}", styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # PROBLEMAS
    contenido.append(Paragraph("Problemas Detectados:", styles["Heading2"]))
    if problemas:
        for p in problemas:
            contenido.append(Paragraph(f"- {p}", styles["Normal"]))
    else:
        contenido.append(Paragraph("Sin desviaciones críticas", styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # IMPACTO
    contenido.append(Paragraph("Impacto Económico:", styles["Heading2"]))
    contenido.append(Paragraph(f"Pérdida: {formatear(perdida*precio,'$')}", styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # RECOMENDACIÓN
    contenido.append(Paragraph("Recomendación Operacional:", styles["Heading2"]))
    if ranking:
        contenido.append(Paragraph(f"Priorizar: {ranking[0]}", styles["Normal"]))
    contenido.append(Spacer(1, 10))

    # ALERTA FUTURA
    if ranking:
        futura = colas[ranking[0]] + 2
        if futura > 6:
            contenido.append(Paragraph("Riesgo de congestión futura", styles["Normal"]))
        else:
            contenido.append(Paragraph("Operación estable proyectada", styles["Normal"]))

    doc.build(contenido)

    return ruta


# --------------------------------
# 📥 BOTÓN DESCARGA PDF (CORREGIDO)
# --------------------------------

if st.button("📄 Generar Reporte PDF"):

    with st.spinner("Generando reporte..."):
        ruta = generar_pdf(ind, problemas, perdida, precio, ranking, colas)

    with open(ruta, "rb") as f:
        st.download_button(
            "⬇️ Descargar Reporte",
            f,
            file_name="reporte_PIOM.pdf"
        )
