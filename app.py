# 🧮 Multiplication Table — Stable Deluxe

import streamlit as st
import pandas as pd
import numpy as np

# ---- Page config FIRST (must be before any output) ----
st.set_page_config(page_title="Multiplication Table • Stable", page_icon="🧮", layout="wide")

# ---- Sidebar controls ----
with st.sidebar:
    st.title("🎛️ Controls")
    n = st.slider("Table size (n × n)", 5, 50, 12)
    cmap = st.selectbox("Color palette", ["viridis", "plasma", "magma", "cividis", "coolwarm", "rainbow"], index=0)
    show_heatmap = st.checkbox("Show heatmap (Altair)", value=True)
    show_rowcol_sums = st.checkbox("Show row/column totals", value=True)
    highlight_multiples = st.selectbox("Highlight multiples of…", ["None", "2", "3", "5", "7", "10"], index=0)
    precision = st.slider("Decimals", 0, 3, 0)

st.title("🌈 Colorful Multiplication Table — Stable Edition")
st.caption("If anything fails, features will auto-disable with a friendly note instead of crashing.")

# ---- Data ----
rows = np.arange(1, n + 1, dtype=int)
cols = np.arange(1, n + 1, dtype=int)
data = np.outer(rows, cols).astype(float)  # float so styling/formatting never chokes

df = pd.DataFrame(data, index=[f"{i}" for i in rows], columns=[f"{j}" for j in cols])

# Optional totals
df_display = df.copy()
if show_rowcol_sums:
    try:
        df_display["Σ row"] = df_display.sum(axis=1)
        total_row = pd.DataFrame([list(df_display.sum(axis=0))], columns=df_display.columns, index=["Σ col"])
        df_display = pd.concat([df_display, total_row], axis=0)
    except Exception as e:
        st.warning(f"Could not add totals (disabled). Reason: {e}")

# ---- Quick stats ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Size", f"{n} × {n}")
c2.metric("Min", f"{df.values.min():.{precision}f}")
c3.metric("Max", f"{df.values.max():.{precision}f}")
c4.metric("Sum", f"{int(df.values.sum()):,}")

# ---- Styling (robust) ----
st.subheader("📋 Table")
try:
    styler = (
        df_display.style
        .format(f"{{:.{precision}f}}")
        .background_gradient(cmap=cmap, axis=None)
    )

    # highlight multiples if requested (skip last totals row/col automatically by trying/except)
    if highlight_multiples != "None":
        k = int(highlight_multiples)

        def highlight_row(v):
            out = []
            for i, x in enumerate(v):
                try:
                    # if it's the totals column/row header, leave blank
                    if isinstance(x, (int, float, np.floating)) and not pd.isna(x) and (x % k == 0):
                        out.append("background-color: rgba(255,165,0,0.22);")
                    else:
                        out.append("")
                except Exception:
                    out.append("")
            return out

        styler = styler.apply(highlight_row, axis=1)

    st.dataframe(styler, use_container_width=True, height=520)
except Exception as e:
    st.error(f"Table styling failed, showing plain table. Reason: {e}")
    st.dataframe(df_display, use_container_width=True, height=520)

# ---- Heatmap (Altair) ----
if show_heatmap:
    try:
        import altair as alt

        st.subheader("🔥 Heatmap")
        df_heat = (
            pd.DataFrame(df.values, index=rows, columns=cols)
            .reset_index()
            .melt(id_vars="index", var_name="Column", value_name="Value")
            .rename(columns={"index": "Row"})
        )
        chart = alt.Chart(df_heat).mark_rect().encode(
            x=alt.X('Column:O', title='×'),
            y=alt.Y('Row:O', title='='),
            color=alt.Color('Value:Q', title='Product'),
            tooltip=['Row:O', 'Column:O', alt.Tooltip('Value:Q', format=f'.{precision}f')]
        ).properties(height=500, width='container')
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.warning(f"Heatmap disabled. Install Altair or check data. Reason: {e}")

# ---- Download ----
csv = df.to_csv(index=True)
st.download_button(
    "⬇️ Download Base Table (CSV)",
    data=csv,
    file_name=f"multiplication_table_{n}x_{n}.csv",
    mime="text/csv",
)

with st.expander("💡 Fun patterns"):
    st.markdown("""
- Diagonal are perfect squares: 1, 4, 9, 16, …
- Multiples of a chosen number form stripes (use the sidebar).
- Symmetry across the diagonal: `i×j = j×i`.
""")
