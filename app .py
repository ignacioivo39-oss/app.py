import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PIOM Dashboard", layout="wide")

st.title("🚀 PIOM - Plataforma de Inteligencia Operacional Minera")

st.markdown("## 🔥 Índice de Riesgo PIOM")

# Simulación simple
np.random.seed(42)
riesgo = np.random.randint(40, 90)

st.metric(label="IR PIOM", value=f"{riesgo}/100")

if riesgo < 50:
    st.success("Estado: Riesgo Bajo")
elif riesgo < 70:
    st.warning("Estado: Riesgo Medio")
else:
    st.error("Estado: Riesgo Alto")

# Gráfico simple
data = pd.DataFrame({
    "Hora": range(1, 13),
    "Desviación (%)": np.random.normal(5, 2, 12)
})

fig = px.line(data, x="Hora", y="Desviación (%)", title="Desviación Plan vs Real")
st.plotly_chart(fig, use_container_width=True)
