import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PIOM Dashboard", layout="wide")

st.title("🚀 PIOM - Plataforma de Inteligencia Operacional Minera")

st.write("Sube un archivo Excel con datos del turno para analizar desviaciones y detectar problemas.")

# Subir archivo
archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is not None:

    df = pd.read_excel(archivo)

    st.subheader("Vista de datos")
    st.dataframe(df)

    # Verificar columnas necesarias
    columnas = ["Plan", "Real", "Espera", "Mant_prog", "Mant_no_prog"]

    if all(col in df.columns for col in columnas):

        # Desviación producción
        df["Desviacion_%"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100

        desviacion = abs(df["Desviacion_%"]).mean()
        espera = df["Espera"].mean()
        mant_prog = df["Mant_prog"].sum()
        mant_no_prog = df["Mant_no_prog"].sum()

        # Índice PIOM
        IR_PIOM = (
            0.4 * desviacion +
            0.3 * espera +
            0.2 * mant_no_prog +
            0.1 * mant_prog
        )

        st.subheader("Índice de Riesgo Operacional")

        st.metric("IR PIOM", round(IR_PIOM,1))

        if IR_PIOM < 20:
            st.success("Riesgo Bajo")
        elif IR_PIOM < 40:
            st.warning("Riesgo Medio")
        else:
            st.error("Riesgo Alto")

        # Detectar problema principal
        causas = {
            "Tiempo de espera": espera,
            "Mantención no programada": mant_no_prog,
            "Mantención programada": mant_prog,
            "Desviación producción": desviacion
        }

        causa_principal = max(causas, key=causas.get)

        st.subheader("Problema Detectado")
        st.write(causa_principal)

        # Recomendación
        if causa_principal == "Tiempo de espera":
            st.info("Recomendación: redistribuir camiones entre palas para reducir cola.")

        elif causa_principal == "Mantención no programada":
            st.info("Recomendación: revisar disponibilidad de equipos y activar reemplazo.")

        elif causa_principal == "Mantención programada":
            st.info("Recomendación: ajustar planificación del turno.")

        else:
            st.info("Recomendación: revisar estrategia de carguío.")

        # Gráfico desviación
        fig = px.line(df, y="Desviacion_%", title="Desviación Plan vs Real")
        st.plotly_chart(fig)

    else:
        st.warning("El Excel debe tener columnas: Plan, Real, Espera, Mant_prog, Mant_no_prog")
