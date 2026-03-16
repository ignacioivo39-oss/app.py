import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PIOM - Inteligencia Operacional Minera", layout="wide")

st.title("⛏️ PIOM - Plataforma de Inteligencia Operacional Minera")

st.write("Sube datos operacionales del turno para detectar desviaciones, problemas y recomendaciones.")

archivo = st.file_uploader("Subir archivo Excel", type=["xlsx"])

if archivo is not None:

    df = pd.read_excel(archivo)

    st.subheader("Vista de Datos Operacionales")
    st.dataframe(df)

    columnas_necesarias = [
        "Hora","Pala_activa","Camiones_activos","Plan","Real",
        "Tiempo_carguio_min","Espera","Distancia_km","Mant_prog","Mant_no_prog"
    ]

    if all(col in df.columns for col in columnas_necesarias):

        # ------------------------
        # Calcular desviación
        # ------------------------

        df["Desviacion_%"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100

        desviacion_prom = abs(df["Desviacion_%"]).mean()
        espera_prom = df["Espera"].mean()
        mant_prog_total = df["Mant_prog"].sum()
        mant_no_prog_total = df["Mant_no_prog"].sum()

        # ------------------------
        # Índice PIOM
        # ------------------------

        IR_PIOM = (
            0.4 * desviacion_prom +
            0.3 * espera_prom +
            0.2 * mant_no_prog_total +
            0.1 * mant_prog_total
        )

        st.subheader("📊 Índice de Riesgo PIOM")

        st.metric("IR PIOM", round(IR_PIOM,1))

        if IR_PIOM < 20:
            st.success("Riesgo Bajo")
        elif IR_PIOM < 40:
            st.warning("Riesgo Medio")
        else:
            st.error("Riesgo Alto")

        # ------------------------
        # Detectar equipo con problema
        # ------------------------

        pala_produccion = df.groupby("Pala_activa")["Real"].sum()
        pala_plan = df.groupby("Pala_activa")["Plan"].sum()

        eficiencia_pala = (pala_produccion / pala_plan) * 100

        pala_peor = eficiencia_pala.idxmin()

        st.subheader("⚠️ Equipo con menor rendimiento")

        st.write(f"La pala con menor eficiencia es: **{pala_peor}**")
        st.write(f"Eficiencia: {round(eficiencia_pala.min(),1)} %")

        # ------------------------
        # Identificar causa principal
        # ------------------------

        causas = {
            "Tiempo de espera camiones": espera_prom,
            "Mantención no programada": mant_no_prog_total,
            "Mantención programada": mant_prog_total,
            "Desviación producción": desviacion_prom
        }

        causa_principal = max(causas, key=causas.get)

        st.subheader("🔎 Problema Detectado")

        st.write(causa_principal)

        # ------------------------
        # Recomendaciones
        # ------------------------

        st.subheader("💡 Recomendación Operacional")

        if causa_principal == "Tiempo de espera camiones":
            st.info("Redistribuir camiones entre palas para reducir cola de espera.")

        elif causa_principal == "Mantención no programada":
            st.info("Revisar disponibilidad de equipos y activar plan de mantenimiento correctivo.")

        elif causa_principal == "Mantención programada":
            st.info("Ajustar planificación del turno considerando paradas programadas.")

        else:
            st.info("Revisar estrategia de carguío y asignación de flota.")

        # ------------------------
        # GRÁFICOS
        # ------------------------

        st.subheader("📈 Desviación Plan vs Real")

        fig1 = px.line(df, y="Desviacion_%", title="Desviación de Producción (%)")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("🚚 Tiempo de Espera de Camiones")

        fig2 = px.line(df, y="Espera", title="Tiempo de Espera")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("⛏️ Producción por Pala")

        fig3 = px.bar(
            df.groupby("Pala_activa")["Real"].sum().reset_index(),
            x="Pala_activa",
            y="Real",
            title="Producción por Equipo"
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.error("El Excel no contiene las columnas necesarias.")
