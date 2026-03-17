import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIGURACIÓN APP
# -----------------------------

st.set_page_config(
    page_title="PIOM - Plataforma Inteligencia Operacional Mina",
    layout="wide"
)

st.title("⛏️ PIOM - Plataforma Inteligente de Optimización Minera")
st.write("Análisis operacional completo del turno mina")

# -----------------------------
# SUBIR EXCEL
# -----------------------------

archivo = st.file_uploader(
    "Subir archivo Excel operacional del turno",
    type=["xlsx"]
)

# -----------------------------
# FUNCIONES PIOM
# -----------------------------

def calcular_indicadores(df):

    perf_turno = df["Metros_real"].sum() / df["Metros_plan"].sum() * 100

    prod_turno = df["Real"].sum() / df["Plan"].sum() * 100

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

    cuello = max(problema, key=problema.get)

    return cuello


def detectar_equipos(df):

    eficiencia_perf = df.groupby("Equipo_perforacion").apply(
        lambda x: x["Metros_real"].sum() / x["Metros_plan"].sum()
    ) * 100

    peor_perforadora = eficiencia_perf.idxmin()

    eficiencia_pala = df.groupby("Pala_activa").apply(
        lambda x: x["Real"].sum() / x["Plan"].sum()
    ) * 100

    peor_pala = eficiencia_pala.idxmin()

    return peor_perforadora, peor_pala


def generar_recomendacion(cuello):

    if cuello == "Perforación":
        return "Revisar disponibilidad de perforadoras o tiempos de cambio de barra."

    elif cuello == "Carguío":
        return "Optimizar tiempos de carguío o redistribuir camiones."

    elif cuello == "Transporte":
        return "Reducir congestión de flota o aumentar número de camiones."

    elif cuello == "Mantención":
        return "Revisar plan de mantenimiento para reducir fallas no programadas."

    else:
        return "Optimizar balance del sistema mina."

# -----------------------------
# APP PRINCIPAL
# -----------------------------

if archivo:

    df = pd.read_excel(archivo)

    st.subheader("Datos Operacionales del Turno")
    st.dataframe(df)

    # -----------------------------
    # INDICADORES
    # -----------------------------

    indicadores = calcular_indicadores(df)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Eficiencia Perforación %",
        round(indicadores["Perforación"],1)
    )

    col2.metric(
        "Producción %",
        round(indicadores["Producción"],1)
    )

    col3.metric(
        "Espera Camiones (min)",
        round(indicadores["Espera Camiones"],1)
    )

    # -----------------------------
    # CUELLO DE BOTELLA
    # -----------------------------

    cuello = detectar_cuello_botella(indicadores)

    st.subheader("🚨 Cuello de Botella Detectado")

    st.error(cuello)

    # -----------------------------
    # EQUIPOS CRÍTICOS
    # -----------------------------

    peor_perf, peor_pala = detectar_equipos(df)

    st.subheader("⚠️ Equipos Críticos")

    st.write(f"Perforadora con menor rendimiento: **{peor_perf}**")

    st.write(f"Pala con menor rendimiento: **{peor_pala}**")

    # -----------------------------
    # RECOMENDACIÓN
    # -----------------------------

    recomendacion = generar_recomendacion(cuello)

    st.subheader("💡 Recomendación Operacional PIOM")

    st.success(recomendacion)

    # -----------------------------
    # GRAFICOS
    # -----------------------------

    st.subheader("📊 Producción Real vs Plan")

    fig1 = px.line(
        df,
        y=["Plan","Real"],
        title="Producción"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("⛏️ Metros Perforados")

    fig2 = px.line(
        df,
        y=["Metros_plan","Metros_real"],
        title="Perforación"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🚚 Espera de Camiones")

    fig3 = px.line(
        df,
        y="Espera",
        title="Tiempo de Espera Camiones"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("⚙️ Producción por Pala")

    fig4 = px.bar(
        df.groupby("Pala_activa")["Real"].sum().reset_index(),
        x="Pala_activa",
        y="Real",
        title="Producción por Pala"
    )

    st.plotly_chart(fig4, use_container_width=True)

else:

    st.info("Sube el archivo Excel del turno para iniciar el análisis.")
# -----------------------------
# SIMULADOR SISTEMA MINA
# -----------------------------

st.subheader("🧠 Simulación Sistema Mina")

camiones = st.slider("Número de camiones",1,20,8)

capacidad_camion = st.number_input("Capacidad camión (ton)",200)

tiempo_carguio = st.number_input("Tiempo carguío (min)",3)

viaje_cargado = st.number_input("Viaje cargado (min)",10)

descarga = st.number_input("Tiempo descarga (min)",2)

viaje_vacio = st.number_input("Viaje vacío (min)",8)

espera = st.number_input("Espera promedio (min)",2)

horas_turno = 12

tiempo_ciclo = tiempo_carguio + viaje_cargado + descarga + viaje_vacio + espera

produccion_turno = (camiones * capacidad_camion * horas_turno * 60) / tiempo_ciclo

st.metric("Producción estimada turno (ton)", int(produccion_turno))
# -----------------------------
# OPTIMIZADOR DE FLOTA
# -----------------------------

st.subheader("🚚 Optimización de Flota")

resultados = []

for n in range(1,25):

    prod = (n * capacidad_camion * horas_turno * 60) / tiempo_ciclo

    resultados.append(prod)

sim = pd.DataFrame({
    "Camiones": range(1,25),
    "Produccion": resultados
})

fig = px.line(sim, x="Camiones", y="Produccion",
              title="Producción vs Número de Camiones")

st.plotly_chart(fig,use_container_width=True)
# -----------------------------
# OPTIMIZADOR DE FLOTA
# -----------------------------

st.subheader("🚚 Optimización de Flota")

resultados = []

for n in range(1,25):

    prod = (n * capacidad_camion * horas_turno * 60) / tiempo_ciclo

    resultados.append(prod)

sim = pd.DataFrame({
    "Camiones": range(1,25),
    "Produccion": resultados
})

fig = px.line(sim, x="Camiones", y="Produccion",
              title="Producción vs Número de Camiones")

st.plotly_chart(fig,use_container_width=True)
