import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PIOM Sistema Mina", layout="wide")

st.title("⛏️ PIOM - Inteligencia Operacional Sistema Mina")

st.write("Análisis completo del turno: perforación, carguío y transporte")

archivo = st.file_uploader("Subir Excel operacional", type=["xlsx"])

if archivo:

    df = pd.read_excel(archivo)

    st.subheader("Datos del Turno")
    st.dataframe(df)

    columnas = [
        "Hora","Equipo_perforacion","Metros_plan","Metros_real",
        "Pala_activa","Camiones_activos","Plan","Real",
        "Tiempo_carguio_min","Espera","Distancia_km",
        "Mant_prog","Mant_no_prog"
    ]

    if all(col in df.columns for col in columnas):

        # -------------------------
        # EFICIENCIA PERFORACION
        # -------------------------

        df["Eficiencia_perforacion"] = df["Metros_real"] / df["Metros_plan"] * 100

        perf_equipo = df.groupby("Equipo_perforacion")["Metros_real"].sum()
        perf_plan = df.groupby("Equipo_perforacion")["Metros_plan"].sum()

        eficiencia_perf = perf_equipo / perf_plan * 100

        peor_perforadora = eficiencia_perf.idxmin()

        # -------------------------
        # EFICIENCIA CARGUIO
        # -------------------------

        prod_pala = df.groupby("Pala_activa")["Real"].sum()
        prod_plan = df.groupby("Pala_activa")["Plan"].sum()

        eficiencia_pala = prod_pala / prod_plan * 100

        peor_pala = eficiencia_pala.idxmin()

        # -------------------------
        # TRANSPORTE
        # -------------------------

        espera_prom = df["Espera"].mean()

        # -------------------------
        # MANTENCION
        # -------------------------

        mant_prog = df["Mant_prog"].sum()
        mant_no_prog = df["Mant_no_prog"].sum()

        # -------------------------
        # RENDIMIENTO DEL TURNO
        # -------------------------

        perf_turno = df["Metros_real"].sum() / df["Metros_plan"].sum() * 100
        prod_turno = df["Real"].sum() / df["Plan"].sum() * 100

        rendimiento_total = (perf_turno + prod_turno) / 2

        st.subheader("📊 Rendimiento del Turno Completo")

        st.metric("Perforación %", round(perf_turno,1))
        st.metric("Producción %", round(prod_turno,1))
        st.metric("Rendimiento Sistema %", round(rendimiento_total,1))

        # -------------------------
        # DETECTOR CUELLO BOTELLA
        # -------------------------

        indicadores = {
            "Perforacion": 100 - perf_turno,
            "Carguio": 100 - prod_turno,
            "Transporte": espera_prom,
            "Mantencion": mant_no_prog
        }

        cuello_botella = max(indicadores, key=indicadores.get)

        st.subheader("🚨 Cuello de Botella Detectado")

        st.error(cuello_botella)

        # -------------------------
        # EQUIPO CON PROBLEMA
        # -------------------------

        st.subheader("⚠️ Equipos Críticos")

        st.write(f"Perforadora con menor rendimiento: **{peor_perforadora}**")
        st.write(f"Pala con menor rendimiento: **{peor_pala}**")

        # -------------------------
        # RECOMENDACIONES
        # -------------------------

        st.subheader("💡 Recomendación Operacional")

        if cuello_botella == "Perforacion":
            st.info("Aumentar disponibilidad de perforadoras o revisar tiempos de cambio de barra.")

        elif cuello_botella == "Carguio":
            st.info("Optimizar tiempos de carguío o redistribuir flota.")

        elif cuello_botella == "Transporte":
            st.info("Reducir congestión de camiones o optimizar rutas.")

        elif cuello_botella == "Mantencion":
            st.info("Revisar plan de mantenimiento para reducir fallas no programadas.")

        # -------------------------
        # GRAFICOS
        # -------------------------

        st.subheader("📈 Producción Real vs Plan")

        fig1 = px.line(df, y=["Plan","Real"], title="Producción")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("🚚 Espera de Camiones")

        fig2 = px.line(df, y="Espera", title="Tiempo de Espera")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("⛏️ Metros Perforados")

        fig3 = px.line(df, y=["Metros_plan","Metros_real"], title="Perforación")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("⚙️ Producción por Pala")

        fig4 = px.bar(df.groupby("Pala_activa")["Real"].sum().reset_index(),
                      x="Pala_activa",
                      y="Real",
                      title="Producción por Pala")

        st.plotly_chart(fig4, use_container_width=True)

    else:

        st.error("El Excel no tiene las columnas necesarias.")
        import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("PIOM - Plataforma Inteligente de Optimización Minera")

uploaded_file = st.file_uploader("Subir archivo Excel del turno", type=["xlsx"])

# -----------------------------
# FUNCIONES PIOM
# -----------------------------

def calcular_indicadores(data):

    ef_perforacion = data["metros_perforados"][0] / data["metros_planificados"][0]

    ef_carguio = data["toneladas_cargadas"][0] / data["capacidad_pala_turno"][0]

    ef_transporte = data["toneladas_transportadas"][0] / data["capacidad_transporte_turno"][0]

    disponibilidad = data["horas_operativas"][0] / data["horas_programadas"][0]

    flota = data["camiones_disponibles"][0] / data["camiones_totales"][0]

    indicadores = {
        "Perforación": ef_perforacion,
        "Carguío": ef_carguio,
        "Transporte": ef_transporte,
        "Disponibilidad equipos": disponibilidad,
        "Disponibilidad camiones": flota
    }

    return indicadores


def detectar_cuello_botella(indicadores):

    cuello = min(indicadores, key=indicadores.get)

    return cuello


def generar_recomendacion(cuello):

    if cuello == "Transporte":
        return "Aumentar camiones o reducir tiempo de ciclo."

    elif cuello == "Carguío":
        return "Revisar eficiencia pala o tiempos de carguío."

    elif cuello == "Perforación":
        return "Revisar rendimiento de perforadora."

    elif cuello == "Disponibilidad equipos":
        return "Revisar mantenciones programadas y no programadas."

    else:
        return "Optimizar gestión de flota."

# -----------------------------
# APP PRINCIPAL
# -----------------------------

if uploaded_file is not None:

    data = pd.read_excel(uploaded_file)

    st.subheader("Datos del turno")
    st.dataframe(data)

    indicadores = calcular_indicadores(data)

    st.subheader("Indicadores de eficiencia")

    for k,v in indicadores.items():

        st.write(f"{k}: {round(v*100,2)} %")

    cuello = detectar_cuello_botella(indicadores)

    st.subheader("Cuello de botella del sistema")

    st.error(cuello)

    recomendacion = generar_recomendacion(cuello)

    st.subheader("Recomendación PIOM")

    st.success(recomendacion)

    # -----------------------------
    # GRAFICO
    # -----------------------------

    nombres = list(indicadores.keys())
    valores = [v*100 for v in indicadores.values()]

    fig, ax = plt.subplots()

    ax.bar(nombres,valores)

    ax.set_ylabel("Eficiencia (%)")
    ax.set_title("Indicadores operacionales turno")

    st.pyplot(fig)
