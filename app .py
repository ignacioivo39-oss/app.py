import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración página
st.set_page_config(page_title="PIOM Dashboard", layout="wide")
st.title("🚀 PIOM - Plataforma de Inteligencia Operacional Minera")
st.markdown("## 📂 Cargar Datos Operacionales (Excel)")

# Carga de archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    st.write("### Vista previa de datos")
    st.dataframe(df.head())

    # Validación columnas
    required_cols = ["Plan", "Real", "Turno"]
    if all(col in df.columns for col in required_cols):
        
        # Cálculo de desviación
        df["Desviacion_%"] = (df["Real"] - df["Plan"]) / df["Plan"] * 100
        
        # Cálculo por turno
        turno_summary = df.groupby("Turno")["Desviacion_%"].mean().reset_index()
        turno_summary["Indice_PIOM"] = turno_summary["Desviacion_%"].abs() * 2
        
        # Índice PIOM global
        riesgo_total = np.mean(abs(df["Desviacion_%"])) * 2
        st.metric("🔥 Índice PIOM Total", f"{round(riesgo_total,1)}/100")
        
        # Alertas globales
        if riesgo_total < 20:
            st.success("Estado: Riesgo Bajo")
        elif riesgo_total < 40:
            st.warning("Estado: Riesgo Medio")
        else:
            st.error("Estado: Riesgo Alto")
        
        # Gráfico general
        fig1 = px.line(df, x=df.index, y="Desviacion_%", title="Desviación Plan vs Real (%)")
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico por turno
        fig2 = px.bar(turno_summary, x="Turno", y="Indice_PIOM",
                      title="Índice PIOM por Turno", text="Indice_PIOM")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabla resumen por turno
        st.write("### Resumen por Turno")
        st.dataframe(turno_summary)
        
    else:
        st.warning(f"El Excel debe contener las columnas: {', '.join(required_cols)}")
