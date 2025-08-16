# 🌟 Multiplication Table Web App — Deluxe Edition

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ------------------------ Page & Style ------------------------
st.set_page_config(page_title="Multiplication Table • Deluxe", page_icon="🧮", layout="wide")

# Hide Streamlit chrome (optional)
st.markdown("""
<style>
/* Tidy up default chrome */
#MainMenu, header {visibility: hidden;}
footer {visibility: hidden;}
/* Pretty scrollbars for dark/light */
[data-testid="stHorizontalBlock"]::-webkit-scrollbar, .stDataFrame div::-webkit-scrollbar { height: 8px; width: 8px; }
[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb, .stDataFrame div::-webkit-scrollbar-thumb { background: #bbb; border-radius: 6px; }
/* Hover highlight for dataframe cells */
.dataframe tbody tr:hover td, .dataframe tbody tr:hover th { background: rgba(255, 235, 59, 0.18) !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------ Sidebar Controls ------------------------
with st.sidebar:
    st.title("🎛️ Controls")
    n = st.slider("Table size (n × n)", 5, 50, 12, help="Choose how big the table should be.")
    cmap = st.selectbox("Color palette (table)", ["viridis", "plasma", "magma", "cividis", "coolwarm", "rainbow"], index=0)
    show_heatmap = st.checkbox("Show heatmap", value=True)
    show_rowcol_sums = st.checkbox("Show row/column totals", value=True)
    highlight_multiples = st.selectbox("Highlight multiples of…", ["None", "2", "3", "5", "7", "10"], index=0)
    precision = st.slider("Number format (decimal places)", 0, 3, 0)
    st.caption("Tip: Use ⌘/Ctrl + Click to multi-select in the table.")

# ------------------------ Data ------------------------
rows = np.arange(1, n + 1)
cols = np.arange(1, n + 1)
data = np.outer(rows, cols)
df = pd.DataFrame(data, index=[f"{i}" for i in rows], columns=[f"{j}" for j in cols])

# Optional row/column sums
if show_rowcol_sums:
    df["Σ row"] = df.sum(axis=1)
    total_row = pd.DataFrame([list(df.sum(axis=0))], columns=df.columns, index=["Σ col"])
    df_display = pd.concat([df, total_row], axis=0)
else:
    df_display = df.copy()

# ------------------------ Top Section ------------------------
st.title("🌈 Colorful Multiplication Table — Deluxe")
st.caption("Interactive, downloadable, and pretty.")

# Quick stats
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Size", f"{n} × {n}")
with c2:
    st.metric("Min", f"{df.min().min():.{precision}f}")
with c3:
    st.metric("Max", f"{df.max().max():.{precision}f}")
with c4:
    st.metric("Sum", f"{df.values.sum():,}")

# ------------------------ Styling ------------------------
styler = df_display.style.format(f"{{:.{precision}f}}") \
    .background_gradient(cmap=cmap, axis=None) \
    .set_table_styles([
        {"selector": "th", "props": [("position", "sticky"), ("top", "0"), ("z-index", "1"), ("background", "rgba(250,250,250,0.9)")]}
    ])

# Highlight multiples (if chosen)
if highlight_multiples != "None":
    k = int(highlight_multiples)
    def _highlight(v):
        try:
            return ["background-color: rgba(255,165,0,0.22);" if (isinstance(x, (int, float)) and x % k == 0) else "" for x in v]
        except Exception:
            return ["" for _ in v]
    styler = styler.apply(_highlight, axis=1)

# ------------------------ Display Table ------------------------
st.subheader("📋 Table")
st.dataframe(styler, use_container_width=True, height=520)

# ------------------------ Heatmap (Altair) ------------------------
if show_heatmap:
    st.subheader("🔥 Heatmap")
    # Prepare long-form for Altair
    df_heat = pd.DataFrame(df.values, index=rows, columns=cols).reset_index().melt(
        id_vars="index", var_name="Column", value_name="Value"
    ).rename(columns={"index": "Row"})
    # Altair chart
    chart = alt.Chart(df_heat).mark_rect().encode(
        x=alt.X('Column:O', title='×'),
        y=alt.Y('Row:O', title='='),
        color=alt.Color('Value:Q', scale=alt.Scale(scheme='viridis'), title='Product'),
        tooltip=['Row:O', 'Column:O', alt.Tooltip('Value:Q', format=f'.{precision}f')]
    ).properties(height=500, width='container')
    st.altair_chart(chart, use_container_width=True)

# ------------------------ CSV Download ------------------------
csv = df.to_csv(index=True)
st.download_button(
    "⬇️ Download Base Table (CSV)",
    data=csv,
    file_name=f"multiplication_table_{n}x{n}.csv",
    mime="text/csv",
)

# ------------------------ Fun Facts ------------------------
with st.expander("💡 Fun patterns to look for"):
    st.markdown("""
- **Diagonal** from top-left to bottom-right are the perfect squares: 1, 4, 9, 16, …
- Multiples of a chosen number form **regular stripes** (toggle “Highlight multiples” in the sidebar).
- The table is **symmetric** across the diagonal: `i×j = j×i`.
""")
