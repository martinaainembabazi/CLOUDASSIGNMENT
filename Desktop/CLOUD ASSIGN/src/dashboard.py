from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    px = None

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
DATA_DB = ROOT / "data" / "patents.db"


st.set_page_config(
    page_title="Global Patent Concentration Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 109, 0, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(0, 184, 217, 0.18), transparent 34%),
            linear-gradient(180deg, #fffaf5 0%, #f8fbff 100%);
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }
    .hero-card {
        background: linear-gradient(135deg, #1f2a44 0%, #193b78 40%, #1ea7a0 100%);
        color: white;
        border-radius: 28px;
        padding: 28px 30px;
        box-shadow: 0 18px 60px rgba(9, 20, 60, 0.22);
        border: 1px solid rgba(255,255,255,0.18);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        max-width: 900px;
    }
    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1rem;
    }
    .pill {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 999px;
        padding: 0.35rem 0.8rem;
        font-size: 0.82rem;
        backdrop-filter: blur(6px);
    }
    .section-title {
        margin-top: 1.2rem;
        margin-bottom: 0.3rem;
        color: #1f2a44;
        font-weight: 800;
    }
    .soft-card {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(31,42,68,0.08);
        border-radius: 22px;
        padding: 18px 18px 8px 18px;
        box-shadow: 0 10px 30px rgba(31,42,68,0.08);
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(245,249,255,0.96));
        border: 1px solid rgba(31,42,68,0.08);
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 8px 26px rgba(31,42,68,0.08);
    }
    .tiny-label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.72rem;
        color: #5b657d;
        margin-bottom: 0.25rem;
        font-weight: 700;
    }
    .tiny-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #1f2a44;
        margin: 0;
    }
    .tiny-note {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.15rem;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff, #f3f8ff);
        border: 1px solid rgba(31,42,68,0.08);
        padding: 14px 16px;
        border-radius: 18px;
        box-shadow: 0 6px 22px rgba(31,42,68,0.07);
    }
    div[data-testid="stMetric"] label {
        color: #5b657d !important;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .stButton button {
        border-radius: 999px;
        border: none;
        background: linear-gradient(90deg, #ff6d00, #ff9f1c);
        color: white;
        font-weight: 700;
        padding: 0.55rem 1rem;
        box-shadow: 0 10px 20px rgba(255, 109, 0, 0.22);
    }
    .stDownloadButton button {
        border-radius: 999px;
        border: none;
        background: linear-gradient(90deg, #193b78, #1ea7a0);
        color: white;
        font-weight: 700;
        padding: 0.55rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.55rem 1rem;
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(31,42,68,0.09);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #193b78, #1ea7a0);
        color: white !important;
        border-color: transparent;
    }
</style>
"""


@st.cache_data
def load_dashboard_data() -> dict[str, object]:
    if not DATA_DB.exists():
        # Fallback to CSV files if database doesn't exist (e.g., on Streamlit Cloud)
        try:
            top_inventors_path = REPORTS / "top_inventors.csv"
            top_companies_path = REPORTS / "top_companies.csv"
            top_countries_path = REPORTS / "top_countries.csv"
            patents_over_time_path = REPORTS / "patents_over_time.csv"
            
            if all([top_inventors_path.exists(), top_companies_path.exists(), 
                    top_countries_path.exists(), patents_over_time_path.exists()]):
                top_inventors = pd.read_csv(top_inventors_path).rename(columns={'name': 'name', 'patent_count': 'patent_count'})
                top_companies = pd.read_csv(top_companies_path)
                top_countries = pd.read_csv(top_countries_path)
                patents_over_time = pd.read_csv(patents_over_time_path)
                total_patents = 9_454_161  # Known total from full pipeline run
                
                return {
                    "total_patents": total_patents,
                    "top_inventors": top_inventors.head(10).to_dict(orient="records"),
                    "top_companies": top_companies.head(10).to_dict(orient="records"),
                    "top_countries": top_countries.head(10).to_dict(orient="records"),
                    "patents_over_time": patents_over_time,
                }
            else:
                st.error("Missing data/patents.db — run src/pipeline.py first")
                st.stop()
        except Exception as e:
            st.error(f"Error loading fallback data: {e}")
            st.stop()

    conn = sqlite3.connect(DATA_DB.as_posix())
    conn.execute("PRAGMA query_only = ON")
    try:
        top_inventors = pd.read_sql_query(
            """
            SELECT i.name, COUNT(DISTINCT pic.patent_id) AS patent_count
            FROM patent_inventor_company pic
            JOIN inventors i ON i.inventor_id = pic.inventor_id
            GROUP BY i.name
            ORDER BY patent_count DESC
            LIMIT 10
            """,
            conn,
        )
        top_companies = pd.read_sql_query(
            """
            SELECT c.name, COUNT(DISTINCT pic.patent_id) AS patent_count
            FROM patent_inventor_company pic
            JOIN companies c ON c.company_id = pic.company_id
            GROUP BY c.name
            ORDER BY patent_count DESC
            LIMIT 10
            """,
            conn,
        )
        top_countries = pd.read_sql_query(
            """
            SELECT i.country, COUNT(DISTINCT pic.patent_id) AS patent_count
            FROM patent_inventor_company pic
            JOIN inventors i ON i.inventor_id = pic.inventor_id
            WHERE i.country IS NOT NULL AND i.country <> ''
            GROUP BY i.country
            ORDER BY patent_count DESC
            LIMIT 10
            """,
            conn,
        )
        patents_over_time = pd.read_sql_query(
            """
            SELECT year, COUNT(DISTINCT patent_id) AS patent_count
            FROM patents
            GROUP BY year
            ORDER BY year
            """,
            conn,
        )
        total_patents = int(
            pd.read_sql_query(
                "SELECT COUNT(DISTINCT patent_id) AS total_patents FROM patents",
                conn,
            ).iloc[0, 0]
        )
    finally:
        conn.close()

    return {
        "total_patents": total_patents,
        "top_inventors": top_inventors.to_dict(orient="records"),
        "top_companies": top_companies.to_dict(orient="records"),
        "top_countries": top_countries.to_dict(orient="records"),
        "patents_over_time": patents_over_time,
    }


def format_int(value: object) -> str:
    try:
        return f"{int(float(value)):,}"
    except Exception:
        return "N/A"


def make_metric_card(label: str, value: str, note: str) -> str:
    return f"""
    <div class='metric-card'>
        <div class='tiny-label'>{label}</div>
        <p class='tiny-value'>{value}</p>
        <div class='tiny-note'>{note}</div>
    </div>
    """


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    summary = load_dashboard_data()
    top_inv = summary.get("top_inventors", [])
    top_comp = summary.get("top_companies", [])
    top_country = summary.get("top_countries", [])

    st.markdown(
        f"""
        <div class='hero-card'>
            <div class='hero-title'>Global Patent Concentration Dashboard</div>
            <div class='hero-subtitle'>
                A visual data story built from PatentsView files. The dashboard shows where patent activity is concentrated,
                who the major inventors and companies are, and how the overall trend changes over time.
            </div>
            <div class='pill-row'>
                <div class='pill'>📌 Concentration by inventor</div>
                <div class='pill'>🏢 Company activity</div>
                <div class='pill'>🌍 Country comparison</div>
                <div class='pill'>📈 Trend over time</div>
                <div class='pill'>3M+ concentration lists</div>
                <div class='pill'>🎨 Presentation-friendly UI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3 class='section-title'>Quick Summary</h3>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total patents", format_int(summary.get("total_patents", 0)))
    with m2:
        st.metric("Top inventor", top_inv[0]["name"] if top_inv else "N/A")
    with m3:
        st.metric("Top company", top_comp[0]["name"] if top_comp else "N/A")
    with m4:
        st.metric("Top country", top_country[0]["country"] if top_country else "N/A")

    st.markdown("<h3 class='section-title'>Highlights</h3>", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    with h1:
        st.info(f"**Total patents:** {format_int(summary.get('total_patents', 0))}\n\nOverall records processed in this run.")
    with h2:
        st.success(f"**Top inventor:** {top_inv[0]['name'] if top_inv else 'N/A'}\n\n{format_int(top_inv[0]['patent_count']) if top_inv else 'N/A'} patents.")
    with h3:
        st.warning(f"**Top company:** {top_comp[0]['name'] if top_comp else 'N/A'}\n\n{format_int(top_comp[0]['patent_count']) if top_comp else 'N/A'} patents.")

    countries = pd.DataFrame(top_country)
    inventors = pd.DataFrame(top_inv)
    companies = pd.DataFrame(top_comp)
    patents_over_time = summary["patents_over_time"]
    findings_path = REPORTS / "findings.md"
    findings_text = findings_path.read_text(encoding="utf-8") if findings_path.exists() else "Run `src/generate_findings.py` after the pipeline to create the write-up."

    tab1, tab2, tab3, tab4 = st.tabs(["Country View", "Inventors", "Companies", "Write-up"])

    with tab1:
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("<h3 class='section-title'>Country Focus</h3>", unsafe_allow_html=True)
            if not countries.empty and HAS_PLOTLY:
                fig = px.bar(
                    countries.head(12).sort_values("patent_count"),
                    x="patent_count",
                    y="country",
                    orientation="h",
                    color="patent_count",
                    color_continuous_scale=["#ffbe0b", "#fb5607", "#3a86ff"],
                    title="Top Countries by Patent Count",
                )
                fig.update_layout(
                    template="plotly_white",
                    height=520,
                    margin=dict(l=10, r=10, t=50, b=10),
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Run the pipeline first so `top_countries.csv` exists.")
        with right:
            st.markdown("<h3 class='section-title'>Top Countries Table</h3>", unsafe_allow_html=True)
            if not countries.empty:
                st.dataframe(countries.head(10), use_container_width=True, height=420)
            else:
                st.info("No country data available yet.")

    with tab2:
        left, right = st.columns([1.1, 0.9])
        with left:
            st.markdown("<h3 class='section-title'>Inventor Concentration</h3>", unsafe_allow_html=True)
            if not inventors.empty and HAS_PLOTLY:
                fig = px.pie(
                    inventors.head(8),
                    names="name",
                    values="patent_count",
                    hole=0.52,
                    color_discrete_sequence=["#ff006e", "#fb5607", "#ffbe0b", "#8338ec", "#3a86ff", "#00b4d8", "#1ea7a0", "#2a9d8f"],
                    title="Share of Top Inventors",
                )
                fig.update_layout(template="plotly_white", height=520, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No inventor data available yet.")
        with right:
            st.markdown("<h3 class='section-title'>Inventor Ranking</h3>", unsafe_allow_html=True)
            if not inventors.empty:
                st.dataframe(inventors.head(12), use_container_width=True, height=420)
            else:
                st.info("Run the pipeline to load inventor data.")

    with tab3:
        st.markdown("<h3 class='section-title'>Company View</h3>", unsafe_allow_html=True)
        if not companies.empty and HAS_PLOTLY:
            fig = px.scatter(
                companies.head(10),
                x="name",
                y="patent_count",
                size="patent_count",
                color="patent_count",
                color_continuous_scale=["#00b4d8", "#1d4ed8", "#0f172a"],
                title="Top Companies by Patent Count",
            )
            fig.update_layout(template="plotly_white", height=500, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="Company", yaxis_title="Patents")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(companies.head(12), use_container_width=True)
        else:
            st.info("No company data available yet.")

    with tab4:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("<h3 class='section-title'>Trend Over Time</h3>", unsafe_allow_html=True)
            if not patents_over_time.empty and HAS_PLOTLY:
                fig = px.line(
                    patents_over_time,
                    x="year",
                    y="patent_count",
                    markers=True,
                    title="Patents Created Each Year",
                    color_discrete_sequence=["#ff6d00"],
                )
                fig.update_traces(line=dict(width=4))
                fig.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Run the pipeline to generate the time trend chart.")
        with c2:
            st.markdown("<h3 class='section-title'>Short Findings</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='soft-card' style='min-height: 430px; line-height: 1.7; font-size: 1rem;'>{findings_text.replace(chr(10), '<br>')}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<h3 class='section-title'>Downloads</h3>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    top_inv_path = REPORTS / "top_inventors.csv"
    top_comp_path = REPORTS / "top_companies.csv"
    top_country_path = REPORTS / "top_countries.csv"
    with d1:
        if top_inv_path.exists():
            st.download_button("Download Inventors CSV", data=top_inv_path.read_bytes(), file_name="top_inventors.csv")
    with d2:
        if top_comp_path.exists():
            st.download_button("Download Companies CSV", data=top_comp_path.read_bytes(), file_name="top_companies.csv")
    with d3:
        if top_country_path.exists():
            st.download_button("Download Countries CSV", data=top_country_path.read_bytes(), file_name="top_countries.csv")

    st.sidebar.markdown("## Presentation Tips")
    st.sidebar.write("Use the tabs like story panels. Open the Country View first, then the Inventors and Companies tabs, and finish with the write-up.")
    st.sidebar.write("This dashboard reads from data/patents.db, which should reflect the latest full pipeline run.")
    st.sidebar.write("If the figures look stale, rerun src/pipeline.py to refresh the database and exports.")


if __name__ == "__main__":
    main()
