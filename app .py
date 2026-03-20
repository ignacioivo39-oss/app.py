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
