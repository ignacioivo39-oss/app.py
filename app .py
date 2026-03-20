import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# CONFIGURACIÓN APP
# --------------------------------

st.set_page_config(
    page_title="PIOM - Plataforma Inteligencia Operacional Mina",
    layout="wide"
)

st.title("⛏️ PIOM - Plataforma Inteligente de Optimización Minera")
st.write("Análisis operacional completo del turno mina")

# --------------------------------
# SUBIR EXCEL
# --------------------------------

archivo = st.file_uploader(
    "Subir archivo Excel operacional del turno",
    type=["xlsx"]
)

# --------------------------------
# FUNCIONES
# --------------------------------

@st.cache_data
def cargar_excel(file):
    df = pd.read_excel(file)
    df = df.fillna(0)
    return df


def calcular_indicadores(df):

    perf_turno = (
        df["Metros_real"].sum() / df["Metros_plan"].sum() * 100
        if df["Metros_plan"].sum() > 0 else 0
    )

    prod_turno = (
        df["Real"].sum() / df["Plan"].sum() * 100
        if df["Plan"].sum() > 0 else 0
    )

    espera_prom = df["Espera"].mean()

    mant_no_prog = df["Mant_no_prog"].sum()

    indicadores = {
        "Perforación": perf_turno,
        "Producción": prod_turno,
        "Espera Camiones": espera_prom,
        "Mantención No Programada": mant_no_prog
    }

    return indicadores


def detectar_cuello_botella(indicadores):

    problema = {
        "Perforación": 100 - indicadores["Perforación"],
        "Carguío": 100 - indicadores["Producción"],
        "Transporte": indicadores["Espera Camiones"],
        "Mantención": indicadores["Mantención No Programada"]
    }

    return max(problema, key=problema.get)


def detectar_equipos(df):

    eficiencia_perf = df.groupby("Equipo_perforacion")[["Metros_real","Metros_plan"]].sum()

    eficiencia_perf["ef"] = (
        eficiencia_perf["Metros_real"] /
        eficiencia_perf["Metros_plan"]
    ) * 100

    peor_perforadora = eficiencia_perf["ef"].idxmin()

    eficiencia_pala = df.groupby("Pala_activa")[["Real","Plan"]].sum()

    eficiencia_pala["ef"] = (
        eficiencia_pala["Real"] /
        eficiencia_pala["Plan"]
    ) * 100

    peor_pala = eficiencia_pala["ef"].idxmin()

    return peor_perforadora, peor_pala


def generar_recomendacion(cuello):

    recomendaciones = {
        "Perforación": "Revisar disponibilidad de perforadoras o tiempos de cambio de barra.",
        "Carguío": "Optimizar tiempos de carguío o redistribuir camiones.",
        "Transporte": "Reducir congestión de flota o mejorar tiempos de ciclo.",
        "Mantención": "Revisar plan de mantenimiento para reducir fallas no programadas."
    }

    return recomendaciones.get(cuello, "Optimizar balance del sistema mina.")


# --------------------------------
# APP PRINCIPAL
# --------------------------------

if archivo:

    df = cargar_excel(archivo)

    columnas_necesarias = [
        "Metros_real","Metros_plan",
        "Real","Plan",
        "Espera","Mant_no_prog",
        "Equipo_perforacion","Pala_activa"
    ]

    faltantes = [c for c in columnas_necesarias if c not in df.columns]

    if faltantes:

        st.error(f"❌ El archivo Excel no contiene estas columnas: {faltantes}")

    else:

        st.subheader("Datos Operacionales del Turno")
        st.dataframe(df)

        indicadores = calcular_indicadores(df)

        col1, col2, col3 = st.columns(3)

        col1.metric("Eficiencia Perforación %",
                    round(indicadores["Perforación"],1))

        col2.metric("Producción %",
                    round(indicadores["Producción"],1))

        col3.metric("Espera Camiones (min)",
                    round(indicadores["Espera Camiones"],1))

        # CUELLO BOTELLA

        cuello = detectar_cuello_botella(indicadores)

        st.subheader("🚨 Cuello de Botella Detectado")
        st.error(cuello)

        # EQUIPOS CRÍTICOS

        peor_perf, peor_pala = detectar_equipos(df)

        st.subheader("⚠️ Equipos Críticos")

        st.write(f"Perforadora con menor rendimiento: **{peor_perf}**")
        st.write(f"Pala con menor rendimiento: **{peor_pala}**")

        # RECOMENDACIÓN

        recomendacion = generar_recomendacion(cuello)

        st.subheader("💡 Recomendación Operacional PIOM")
        st.success(recomendacion)

        # -----------------------------
        # GRÁFICOS
        # -----------------------------

        st.subheader("📊 Producción Real vs Plan")

        fig1 = px.line(df, y=["Plan","Real"], markers=True)

        st.plotly_chart(fig1, use_container_width=True,
                        key="grafico_produccion")

        st.subheader("⛏️ Metros Perforados")

        fig2 = px.line(df, y=["Metros_plan","Metros_real"], markers=True)

        st.plotly_chart(fig2, use_container_width=True,
                        key="grafico_perforacion")

        st.subheader("🚚 Espera de Camiones")

        fig3 = px.line(df, y="Espera", markers=True)

        st.plotly_chart(fig3, use_container_width=True,
                        key="grafico_espera")

        st.subheader("⚙️ Producción por Pala")

        prod_pala = df.groupby("Pala_activa")["Real"].sum().reset_index()

        fig4 = px.bar(prod_pala,
                      x="Pala_activa",
                      y="Real")

        st.plotly_chart(fig4, use_container_width=True,
                        key="grafico_pala")

else:

    st.info("Sube el archivo Excel del turno para iniciar el análisis.")


# --------------------------------
# SIMULADOR SISTEMA MINA
# --------------------------------

st.subheader("🧠 Simulación Sistema Mina")

camiones = st.slider("Número de camiones",1,20,8)

capacidad_camion = st.number_input("Capacidad camión (ton)",200)

tiempo_carguio = st.number_input("Tiempo carguío (min)",3)

viaje_cargado = st.number_input("Viaje cargado (min)",10)

descarga = st.number_input("Tiempo descarga (min)",2)

viaje_vacio = st.number_input("Viaje vacío (min)",8)

espera = st.number_input("Espera promedio (min)",2)

horas_turno = 12

tiempo_ciclo = (
    tiempo_carguio +
    viaje_cargado +
    descarga +
    viaje_vacio +
    espera
)

if tiempo_ciclo > 0:

    produccion_turno = (
        camiones *
        capacidad_camion *
        horas_turno *
        60
    ) / tiempo_ciclo

    st.metric("Producción estimada turno (ton)",
              int(produccion_turno))


# --------------------------------
# OPTIMIZADOR DE FLOTA
# --------------------------------

st.subheader("🚚 Optimización de Flota")

resultados = []

for n in range(1,25):

    prod = (
        n *
        capacidad_camion *
        horas_turno *
        60
    ) / tiempo_ciclo if tiempo_ciclo > 0 else 0

    resultados.append(prod)

sim = pd.DataFrame({
    "Camiones": range(1,25),
    "Produccion": resultados
})

fig = px.line(
    sim,
    x="Camiones",
    y="Produccion",
    markers=True
)

st.plotly_chart(fig, use_container_width=True,
                key="grafico_optimizacion")
# --------------------------------
# ESTADO OPERACIONAL MINA
# --------------------------------

st.subheader("📡 Estado del Sistema Mina")

estado = "🟢 Operación Normal"

if indicadores["Producción"] < 85:
    estado = "🔴 Riesgo Producción"

elif indicadores["Espera Camiones"] > 5:
    estado = "🟡 Congestión Transporte"

elif indicadores["Perforación"] < 90:
    estado = "🟡 Baja Perforación"

st.markdown(f"### {estado}")
# --------------------------------
# RANKING EQUIPOS
# --------------------------------

st.subheader("🏆 Ranking de Equipos")

ranking_palas = df.groupby("Pala_activa")[["Real","Plan"]].sum()

ranking_palas["Eficiencia"] = (
    ranking_palas["Real"] /
    ranking_palas["Plan"]
) * 100

ranking_palas = ranking_palas.sort_values(
    "Eficiencia",
    ascending=False
)

st.dataframe(ranking_palas)
# --------------------------------
# PERDIDA DE PRODUCCIÓN
# --------------------------------

st.subheader("📉 Pérdida de Producción")

produccion_plan = df["Plan"].sum()

produccion_real = df["Real"].sum()

perdida = produccion_plan - produccion_real

if perdida > 0:

    st.error(f"Se perdieron {int(perdida)} toneladas en el turno")

else:

    st.success("Producción cumplida o superada")
# --------------------------------
# MOTOR INTELIGENTE PIOM
# --------------------------------

st.subheader("🧠 Inteligencia Operacional PIOM")

def analisis_inteligente(df):

    alertas = []

    # Producción
    prod_real = df["Real"].sum()
    prod_plan = df["Plan"].sum()

    if prod_real < prod_plan * 0.9:
        alertas.append("🔴 Baja producción general")

    # Esperas
    if df["Espera"].mean() > 5:
        alertas.append("🟡 Alta congestión de camiones")

    # Perforación
    perf = df["Metros_real"].sum() / df["Metros_plan"].sum() * 100

    if perf < 85:
        alertas.append("🟡 Baja eficiencia de perforación")

    # Mantención
    if df["Mant_no_prog"].sum() > 20:
        alertas.append("🔴 Exceso de fallas no programadas")

    return alertas


alertas = analisis_inteligente(df)

if alertas:
    for alerta in alertas:
        st.warning(alerta)
else:
    st.success("Operación estable")
    # --------------------------------
# ANALISIS POR HORA
# --------------------------------

if "Hora" in df.columns:

    st.subheader("⏱️ Análisis por Hora")

    prod_hora = df.groupby("Hora")["Real"].sum().reset_index()

    fig_hora = px.line(prod_hora, x="Hora", y="Real", markers=True)

    st.plotly_chart(fig_hora, use_container_width=True, key="prod_hora")
# --------------------------------
# REPORTE AUTOMATICO
# --------------------------------

st.subheader("📄 Reporte Ejecutivo")

prod_real = df["Real"].sum()
prod_plan = df["Plan"].sum()

cumplimiento = (prod_real / prod_plan) * 100

reporte = f"""
Turno Mina:

Producción Real: {int(prod_real)} ton
Producción Plan: {int(prod_plan)} ton
Cumplimiento: {round(cumplimiento,1)} %

Cuello de botella: {cuello}

Recomendación:
{recomendacion}
"""

st.text_area("Reporte listo para enviar", reporte, height=200)
# --------------------------------
# ESTADO SISTEMA MINA
# --------------------------------

st.subheader("📡 Estado del Sistema Mina")

estado = "🟢 Operación Normal"

if indicadores["Producción"] < 85:
    estado = "🔴 Baja Producción"

elif indicadores["Espera Camiones"] > 5:
    estado = "🟡 Congestión Transporte"

elif indicadores["Perforación"] < 90:
    estado = "🟡 Baja Perforación"

st.markdown(f"### {estado}")
estado = "🟢 Operación Normal"

if indicadores["Producción"] < 85 and indicadores["Espera Camiones"] > 5:
    estado = "🔴 Sistema Saturado"

elif indicadores["Producción"] < 90:
    estado = "🟡 Riesgo Productivo"

elif indicadores["Espera Camiones"] > 4:
    estado = "🟡 Congestión en Transporte"
