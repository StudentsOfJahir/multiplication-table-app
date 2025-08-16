# 🌟 Multiplication Table Web App with Streamlit

import streamlit as st
import pandas as pd

# App title
st.title("🌈 Colorful Multiplication Table")

# Slider to choose table size
n = st.slider("Select table size (n × n):", 5, 20, 10)

# Create multiplication table
data = [[i * j for j in range(1, n+1)] for i in range(1, n+1)]

# Convert to DataFrame for nice display
df = pd.DataFrame(data, 
                  index=[f"{i}" for i in range(1, n+1)], 
                  columns=[f"{j}" for j in range(1, n+1)])

# Show table with colorful background
st.write("### Multiplication Table")
st.dataframe(df.style.background_gradient(cmap="rainbow"))
