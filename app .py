import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PIOM Dashboard", layout="wide")

st.title("🚀 PIOM - Plataforma de Inteligencia Operacional Minera")

st.markdown("## 📂 Cargar Datos Operacionales (Excel)")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    
    df = pd.read_excel(uploaded_file)

    st.write("### Vista previa de datos")
    st.dataframe(df.head())

    if "Plan" in df.columns and "Real" in df.columns:
        
        df["Desviacion_%"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100
        
        riesgo = np.mean(abs(df["Desviacion_%"])) * 2
        
        st.metric("🔥 Índice PIOM", f"{round(riesgo,1)}/100")

        if riesgo < 20:
            st.success("Estado: Riesgo Bajo")
        elif riesgo < 40:
            st.warning("Estado: Riesgo Medio")
        else:
            st.error("Estado: Riesgo Alto")

        fig = px.line(df, y="Desviacion_%", title="Desviación Plan vs Real (%)")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("El Excel debe contener columnas llamadas 'Plan' y 'Real'")
