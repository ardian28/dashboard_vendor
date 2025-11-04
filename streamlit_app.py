import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import io

# Mock data generators
@st.cache_data
def generate_vendor_data():
    vendors = ["PT PMS", "PT KARYA JAYA", "PT MANDIRI SEJAHTERA", 
               "PT SUKSES BERSAMA", "PT MAKMUR ABADI", "PT MITRA USAHA"]
    months = pd.date_range('2023-06-01', '2023-08-01', freq='MS')
    
    data = []
    for vendor in vendors:
        base_score = np.random.randint(75, 90)
        for month in months:
            score = base_score + np.random.randint(-5, 8)
            data.append({
                'vendor': vendor,
                'bulan': month,
                'skor_evaluasi': min(100, max(60, score)),
                'jumlah_pekerja': np.random.randint(80, 150),
                'waktu_thp': np.random.randint(85, 100),
                'kehadiran': np.random.randint(85, 100),
                'thr': np.random.randint(80, 100),
                'bpjs_tk': np.random.randint(75, 100),
                'bpjs_kes': np.random.randint(75, 100),
                'dpslk': np.random.randint(70, 100)
            })
    return pd.DataFrame(data)

def generate_worker_data(vendor, month, num_workers=10):
    np.random.seed(hash(vendor + str(month)) % 2**32)
    workers = [f"Pekerja {i+1}" for i in range(num_workers)]
    scores = np.random.randint(70, 100, num_workers)
    return pd.DataFrame({'pekerja': workers, 'skor': scores})

def predict_future_scores(df, vendor, months=3):
    vendor_data = df[df['vendor'] == vendor].sort_values('bulan')
    if len(vendor_data) < 2:
        return []
    
    last_score = vendor_data['skor_evaluasi'].iloc[-1]
    last_month = vendor_data['bulan'].iloc[-1]
    scores = vendor_data['skor_evaluasi'].values
    trend = (scores[-1] - scores[0]) / len(scores)
    
    predictions = []
    for i in range(1, months + 1):
        next_month = last_month + pd.DateOffset(months=i)
        predicted_score = last_score + (trend * i) + np.random.randint(-2, 3)
        predicted_score = min(100, max(60, int(predicted_score)))
        variance = np.var(scores)
        confidence = max(70, min(95, int(90 - variance)))
        
        predictions.append({
            'bulan': next_month,
            'skor_prediksi': predicted_score,
            'confidence': confidence
        })
    return predictions

def get_risk_status(score):
    if score >= 85:
        return "Low Risk", "#10b981"
    elif score >= 70:
        return "Medium Risk", "#f59e0b"
    else:
        return "High Risk", "#ef4444"

# Page Config
st.set_page_config(
    page_title="VendorPro Dashboard",
    page_icon="VP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = True
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Dashboard"

dark_mode = st.session_state['dark_mode']

# Color scheme
if dark_mode:
    bg_main = "#1a1d29"
    bg_card = "#232734"
    text_primary = "#ffffff"
    text_secondary = "#8b92b0"
    border_color = "#2d3348"
    sidebar_bg = "#1e2130"
    accent = "#5b7cfa"
    chart_text = "#ffffff"
else:
    bg_main = "#f5f7fa"
    bg_card = "#ffffff"
    text_primary = "#2d3748"
    text_secondary = "#718096"
    border_color = "#e2e8f0"
    sidebar_bg = "#ffffff"
    accent = "#5b7cfa"
    chart_text = "#2d3748"

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: {bg_main};
    }}
    
    .block-container {{
        padding: 2rem 3rem;
        max-width: 100%;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding: 1.5rem 1rem;
    }}
    
    .sidebar-title {{
        color: {text_primary};
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 2rem;
        padding: 0 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        position: relative;
    }}
    
    .sidebar-logo {{
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, {accent}, #3b82f6);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 12px rgba(91, 124, 250, 0.3);
    }}
    
    .nav-section {{
        margin-bottom: 2rem;
    }}
    
    .nav-label {{
        color: {text_secondary};
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0 0.5rem;
        margin-bottom: 0.5rem;
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        background: transparent;
        color: {text_secondary};
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.125rem 0;
        text-align: left;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: {border_color};
        color: {text_primary};
    }}
    
    .menu-icon {{
        font-size: 1.1rem;
        width: 20px;
        text-align: center;
    }}
    
    /* Main content */
    .page-header {{
        margin-bottom: 2rem;
        background: linear-gradient(135deg, {accent} 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(91, 124, 250, 0.2);
    }}
    
    .page-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        background-size: 20px 20px;
    }}
    
    .page-header-content {{
        position: relative;
        z-index: 1;
    }}
    
    .page-title {{
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(135deg, white 0%, rgba(255,255,255,0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }}
    
    .page-subtitle {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
        font-weight: 400;
        max-width: 600px;
    }}
    
    /* Cards */
    .metric-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
    }}
    
    .metric-label {{
        color: {text_secondary};
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }}
    
    .metric-value {{
        color: {text_primary};
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .metric-change {{
        display: inline-flex;
        align-items: center;
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
    }}
    
    .metric-change.positive {{
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }}
    
    .metric-change.negative {{
        color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }}
    
    /* Chart Card */
    .chart-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }}
    
    /* White Header (Single row, fixed height, no bottom line) */
    .chart-header {{
        background: #ffffff;
        color: #1f2937;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin: -1.5rem -1.5rem 0 -1.5rem; /* Pull header up into card */
        height: 70px; /* Fixed height for all headers */
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 1px 0 {border_color}; /* Subtle top separator only */
    }}
    
    .chart-header-title {{
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        color: #1f2937;
    }}
    
    .chart-header-subtitle {{
        font-size: 0.8rem;
        color: #6b7280;
        margin: 0;
        opacity: 0.9;
    }}
    
    /* Hide Streamlit elements */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# Load Data
df = generate_vendor_data()
if 'uploaded_data' in st.session_state:
    df = st.session_state['uploaded_data']

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div class='sidebar-title'>
        <div class='sidebar-logo'>VP</div>
        VendorPro
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section'>", unsafe_allow_html=True)
    st.markdown("<div class='nav-label'>Menu</div>", unsafe_allow_html=True)
    
    pages = [
        ("Dashboard", "Dashboard"),
        ("Multi Vendor", "Multi Vendor"),
        ("Prediksi", "Predictions"),
        ("Pekerja", "Workers"),
        ("Laporan", "Reports"),
        ("Settings", "Settings")
    ]
    
    for page_key, label in pages:
        if st.button(label, key=f"nav_{page_key}"):
            st.session_state['current_page'] = page_key
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='nav-section'>", unsafe_allow_html=True)
    st.markdown("<div class='nav-label'>Preferences</div>", unsafe_allow_html=True)
    
    if st.button(f"{'Dark Mode' if not dark_mode else 'Light Mode'}", key="theme_toggle"):
        st.session_state['dark_mode'] = not st.session_state['dark_mode']
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main Content
page = st.session_state['current_page']

# Page Header
st.markdown(f"""
<div class='page-header'>
    <div class='page-header-content'>
        <h1 class='page-title'>{page}</h1>
        <p class='page-subtitle'>{'Vendor Monitoring System' if page == 'Dashboard' else f'{page} Management'}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper: Render chart with white header
def render_chart(title, subtitle, content_func):
    st.markdown(f"""
    <div class='chart-card'>
        <div class='chart-header'>
            <div class='chart-header-title'>{title}</div>
            <div class='chart-header-subtitle'>{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)
    content_func()
    st.markdown("</div></div>", unsafe_allow_html=True)

if page == "Dashboard":
    # Filters
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        selected_vendor = st.selectbox("Vendor", df['vendor'].unique(), key="dash_vendor")
    with col2:
        selected_month = st.selectbox("Period", df['bulan'].dt.strftime('%B %Y').unique(), index=2, key="dash_month")
    
    month_date = pd.to_datetime(selected_month, format='%B %Y')
    filtered_df = df[(df['bulan'] == month_date) & (df['vendor'] == selected_vendor)]
    
    if not filtered_df.empty:
        row = filtered_df.iloc[0]
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            {"label": "Total Workers", "value": f"{row['jumlah_pekerja']}", "change": "+12%", "positive": True},
            {"label": "Evaluation Score", "value": f"{row['skor_evaluasi']}", "change": "+5%", "positive": True},
            {"label": "BPJS Compliance", "value": f"{int((row['bpjs_tk']+row['bpjs_kes'])/2)}%", "change": "+8%", "positive": True},
            {"label": "Risk Status", "value": get_risk_status(row['skor_evaluasi'])[0], "change": "-2%", "positive": False}
        ]
        
        for col, metric in zip([col1, col2, col3, col4], metrics):
            with col:
                change_class = "positive" if metric['positive'] else "negative"
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-label'>{metric['label']}</div>
                    <div class='metric-value'>{metric['value']}</div>
                    <div class='metric-change {change_class}'>{metric['change']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts Row 1
        col1, col2 = st.columns([2, 1])
        
        with col1:
            def trend_chart():
                vendor_trend = df[df['vendor'] == selected_vendor].sort_values('bulan')
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=vendor_trend['bulan'],
                    y=vendor_trend['skor_evaluasi'],
                    mode='lines',
                    line=dict(color=accent, width=3, shape='spline'),
                    fill='tonexty',
                    fillcolor=f'rgba(91, 124, 250, 0.1)',
                    hovertemplate='<b>%{x|%B %Y}</b><br>Score: %{y}<extra></extra>'
                ))
                fig_trend.update_layout(
                    height=300,
                    margin=dict(t=10, b=30, l=40, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', size=11, color=chart_text),
                    xaxis=dict(showgrid=False, showline=True, linecolor=border_color, tickformat='%b %Y'),
                    yaxis=dict(showgrid=True, gridcolor=border_color, range=[0, 100]),
                    hovermode='x unified',
                    showlegend=False
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            render_chart(
                "Performance Trend",
                "Monitor your vendor's evaluation score over time to identify trends and improvements",
                trend_chart
            )
        
        with col2:
            def bpjs_chart():
                bpjs_data = [
                    {"label": "BPJS TK", "value": row['bpjs_tk'], "color": accent},
                    {"label": "BPJS KES", "value": row['bpjs_kes'], "color": "#10b981"},
                ]
                for item in bpjs_data:
                    st.markdown(f"""
                    <div style='margin-bottom: 1.5rem;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                            <span style='color: {text_secondary}; font-size: 0.875rem; font-weight: 500;'>{item['label']}</span>
                            <span style='color: {text_primary}; font-size: 0.875rem; font-weight: 600;'>{item['value']}%</span>
                        </div>
                        <div style='background: {border_color}; border-radius: 8px; height: 8px; overflow: hidden;'>
                            <div style='background: {item["color"]}; width: {item["value"]}%; height: 100%; border-radius: 8px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            render_chart(
                "BPJS Compliance",
                "Visualize compliance rates for BPJS TK and KES to ensure regulatory adherence",
                bpjs_chart
            )
        
        # Charts Row 2
        col1, col2 = st.columns([1, 2])
        
        with col1:
            def compliance_chart():
                categories = ['THP', 'Attendance', 'THR', 'DPSLK']
                values = [row['waktu_thp'], row['kehadiran'], row['thr'], row['dpslk']]
                colors = [accent, '#10b981', '#f59e0b', '#ef4444']
                for cat, val, color in zip(categories, values, colors):
                    st.markdown(f"""
                    <div style='margin-bottom: 1rem;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                            <span style='color: {text_secondary}; font-size: 0.875rem; font-weight: 500;'>{cat}</span>
                            <span style='color: {color}; font-size: 0.875rem; font-weight: 600;'>{val}%</span>
                        </div>
                        <div style='background: {border_color}; border-radius: 6px; height: 6px; overflow: hidden;'>
                            <div style='background: {color}; width: {val}%; height: 100%; border-radius: 6px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            render_chart(
                "Compliance Metrics",
                "Quick overview of key compliance indicators like THP, attendance, and more",
                compliance_chart
            )
        
        with col2:
            def top_workers_chart():
                worker_df = generate_worker_data(selected_vendor, month_date)
                worker_df = worker_df.sort_values('skor', ascending=False).head(10)
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=worker_df['pekerja'],
                    x=worker_df['skor'],
                    orientation='h',
                    marker=dict(color=accent, line=dict(width=0)),
                    text=worker_df['skor'],
                    textposition='outside',
                    textfont=dict(size=11, color=text_primary, family='Inter'),
                    hovertemplate='<b>%{y}</b><br>Score: %{x}<extra></extra>'
                ))
                fig_bar.update_layout(
                    height=300,
                    margin=dict(t=10, b=30, l=100, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', size=10, color=chart_text),
                    xaxis=dict(showgrid=True, gridcolor=border_color, showline=False, range=[0, 110]),
                    yaxis=dict(showgrid=False, showline=False),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            render_chart(
                "Top 10 Workers",
                "Ranked by performance score – celebrate top performers and coach others",
                top_workers_chart
            )

elif page == "Multi Vendor":
    view_mode = st.radio("", ["Combined View", "Card View"], horizontal=True)
    
    if view_mode == "Combined View":
        def combined_view_chart():
            fig = go.Figure()
            colors = [accent, '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            for idx, vendor in enumerate(df['vendor'].unique()):
                vendor_data = df[df['vendor'] == vendor].sort_values('bulan')
                fig.add_trace(go.Scatter(
                    x=vendor_data['bulan'],
                    y=vendor_data['skor_evaluasi'],
                    mode='lines+markers',
                    name=vendor,
                    line=dict(color=colors[idx % len(colors)], width=3),
                    marker=dict(size=8),
                    hovertemplate=f'<b>{vendor}</b><br>%{{x|%b %Y}}<br>Score: %{{y}}<extra></extra>'
                ))
            fig.update_layout(
                height=450,
                margin=dict(t=20, b=40, l=40, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12, color=chart_text),
                xaxis=dict(showgrid=True, gridcolor=border_color, tickformat='%b %Y'),
                yaxis=dict(showgrid=True, gridcolor=border_color, title="Score", range=[50, 100]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        render_chart(
            "All Vendors Performance",
            "Compare evaluation scores across all vendors to benchmark and identify leaders",
            combined_view_chart
        )
    
    else:
        latest_month = df['bulan'].max()
        for i in range(0, len(df['vendor'].unique()), 3):
            cols = st.columns(3)
            vendors_batch = list(df['vendor'].unique())[i:i+3]
            for idx, vendor in enumerate(vendors_batch):
                with cols[idx]:
                    vendor_data = df[df['vendor'] == vendor].sort_values('bulan')
                    latest = vendor_data[vendor_data['bulan'] == latest_month].iloc[0]
                    status, color = get_risk_status(latest['skor_evaluasi'])
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
                            <div>
                                <h4 style='color: {text_primary}; font-size: 1rem; font-weight: 600; margin: 0 0 0.25rem 0;'>{vendor}</h4>
                                <p style='color: {text_secondary}; font-size: 0.75rem; margin: 0;'>{latest['jumlah_pekerja']} Workers</p>
                            </div>
                            <div style='background: {color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;'>{status}</div>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-top: 1rem;'>
                            <div>
                                <div style='color: {text_secondary}; font-size: 0.75rem; margin-bottom: 0.25rem; font-weight: 500;'>SCORE</div>
                                <div style='color: {color}; font-size: 1.5rem; font-weight: 700;'>{latest['skor_evaluasi']}</div>
                            </div>
                            <div>
                                <div style='color: {text_secondary}; font-size: 0.75rem; margin-bottom: 0.25rem; font-weight: 500;'>BPJS</div>
                                <div style='color: {text_primary}; font-size: 1.5rem; font-weight: 700;'>{int((latest['bpjs_tk']+latest['bpjs_kes'])/2)}%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif page == "Prediksi":
    selected_vendor = st.selectbox("Select Vendor", df['vendor'].unique(), key="pred_vendor")
    
    vendor_data = df[df['vendor'] == selected_vendor].sort_values('bulan')
    predictions = predict_future_scores(df, selected_vendor, 3)
    
    if predictions:
        col1, col2, col3 = st.columns(3)
        
        current_score = vendor_data['skor_evaluasi'].iloc[-1]
        next_pred = predictions[0]
        trend = next_pred['skor_prediksi'] - current_score
        
        with col1:
            status, color = get_risk_status(current_score)
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color: {text_secondary}; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;'>Current Score</div>
                <div style='color: {color}; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>{current_score}</div>
                <div style='background: {color}; color: white; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; font-size: 0.875rem; font-weight: 500;'>{status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            trend_icon = "↑" if trend > 0 else "↓" if trend < 0 else "→"
            trend_color = "#10b981" if trend > 0 else "#ef4444" if trend < 0 else text_secondary
            trend_text = "Increasing" if trend > 0 else "Decreasing" if trend < 0 else "Stable"
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color: {text_secondary}; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;'>Trend</div>
                <div style='color: {trend_color}; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>{trend_icon} {abs(trend)}</div>
                <div style='background: {trend_color}; color: white; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; font-size: 0.875rem; font-weight: 500;'>{trend_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        def prediction_chart():
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=vendor_data['bulan'],
                y=vendor_data['skor_evaluasi'],
                mode='lines+markers',
                name='Actual',
                line=dict(color=accent, width=3),
                marker=dict(size=10, color=accent),
                hovertemplate='<b>Actual</b><br>%{x|%B %Y}<br>Score: %{y}<extra></extra>'
            ))
            pred_dates = [p['bulan'] for p in predictions]
            pred_scores = [p['skor_prediksi'] for p in predictions]
            fig_pred.add_trace(go.Scatter(
                x=[vendor_data['bulan'].iloc[-1]] + pred_dates,
                y=[vendor_data['skor_evaluasi'].iloc[-1]] + pred_scores,
                mode='lines+markers',
                name='Prediction',
                line=dict(color='#10b981', width=3, dash='dot'),
                marker=dict(size=10, color='#10b981'),
                hovertemplate='<b>Prediction</b><br>%{x|%B %Y}<br>Score: %{y}<extra></extra>'
            ))
            fig_pred.update_layout(
                height=350,
                margin=dict(t=20, b=40, l=40, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12, color=text_primary),
                xaxis=dict(showgrid=True, gridcolor=border_color, tickformat='%b %Y'),
                yaxis=dict(showgrid=True, gridcolor=border_color, title="Score"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pred, use_container_width=True, config={'displayModeBar': False})
        render_chart(
            "3 Months Prediction",
            "AI-powered forecast based on historical trends – plan ahead with confidence intervals",
            prediction_chart
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, pred in enumerate(predictions):
            with cols[idx]:
                pred_month = pred['bulan'].strftime('%B %Y')
                status, color = get_risk_status(pred['skor_prediksi'])
                st.markdown(f"""
                <div class='metric-card' style='text-align: center;'>
                    <div style='color: {text_secondary}; font-size: 0.75rem; font-weight: 500; margin-bottom: 1rem;'>{pred_month}</div>
                    <div style='color: {color}; font-size: 3rem; font-weight: 700; margin-bottom: 1rem;'>{pred['skor_prediksi']}</div>
                    <div style='color: {text_secondary}; font-size: 0.875rem; margin-bottom: 1rem;'>Confidence: {pred['confidence']}%</div>
                    <div style='background: {color}; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; display: inline-block;'>{status}</div>
                </div>
                """, unsafe_allow_html=True)

elif page == "Pekerja":
    col1, col2 = st.columns(2)
    with col1:
        selected_vendor = st.selectbox("Select Vendor", df['vendor'].unique(), key="worker_vendor")
    with col2:
        selected_month = st.selectbox("Select Period", df['bulan'].dt.strftime('%B %Y').unique(), index=2, key="worker_month")
    
    month_date = pd.to_datetime(selected_month, format='%B %Y')
    worker_df = generate_worker_data(selected_vendor, month_date)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        ("Total Workers", len(worker_df), accent),
        ("Average", f"{worker_df['skor'].mean():.1f}", "#10b981"),
        ("Highest", worker_df['skor'].max(), "#f59e0b"),
        ("Lowest", worker_df['skor'].min(), "#ef4444")
    ]
    
    for col, (label, value, color) in zip([col1, col2, col3, col4], metrics_data):
        with col:
            st.markdown(f"""
            <div class='metric-card' style='text-align: center;'>
                <div style='color: {text_secondary}; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;'>{label}</div>
                <div style='color: {color}; font-size: 2.5rem; font-weight: 700;'>{value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        def workers_table():
            st.dataframe(
                worker_df.style.background_gradient(subset=['skor'], cmap='RdYlGn', vmin=70, vmax=100),
                use_container_width=True,
                hide_index=True,
                height=400
            )
        render_chart(
            "Workers List",
            "Detailed view of individual worker scores – sort, filter, and export as needed",
            workers_table
        )
    
    with col2:
        def hist_chart():
            fig_hist = go.Figure(data=[go.Histogram(
                x=worker_df['skor'],
                nbinsx=10,
                marker_color=accent,
                marker_line_color='white',
                marker_line_width=1.5
            )])
            fig_hist.update_layout(
                height=400,
                margin=dict(t=10, b=30, l=40, r=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=11, color=text_primary),
                xaxis=dict(showgrid=False, title="Score", showline=True, linecolor=border_color),
                yaxis=dict(showgrid=True, gridcolor=border_color, title="Count"),
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})
        render_chart(
            "Score Distribution",
            "Histogram showing the spread of scores across your workforce – spot patterns and outliers",
            hist_chart
        )

elif page == "Laporan":
    # Compute dataframes outside tabs
    summary_data = []
    for vendor in df['vendor'].unique():
        vendor_data = df[df['vendor'] == vendor]
        latest = vendor_data.sort_values('bulan').iloc[-1]
        avg_score = vendor_data['skor_evaluasi'].mean()
        status, _ = get_risk_status(avg_score)
        summary_data.append({
            'Vendor': vendor,
            'Total Workers': latest['jumlah_pekerja'],
            'Avg Score': round(avg_score, 1),
            'Current Score': latest['skor_evaluasi'],
            'Status': status,
            'BPJS TK': f"{latest['bpjs_tk']}%",
            'BPJS KES': f"{latest['bpjs_kes']}%"
        })
    summary_df = pd.DataFrame(summary_data)
    
    display_df = df.copy()
    display_df['bulan'] = display_df['bulan'].dt.strftime('%B %Y')
    display_df = display_df.rename(columns={
        'vendor': 'Vendor',
        'bulan': 'Month',
        'skor_evaluasi': 'Score',
        'jumlah_pekerja': 'Workers',
        'waktu_thp': 'THP %',
        'kehadiran': 'Attendance %',
        'thr': 'THR %',
        'bpjs_tk': 'BPJS TK %',
        'bpjs_kes': 'BPJS KES %',
        'dpslk': 'DPSLK %'
    })
    
    tab1, tab2 = st.tabs(["View Data", "Export"])
    
    with tab1:
        def summary_table():
            st.dataframe(summary_df, use_container_width=True, hide_index=True, height=300)
        render_chart(
            "Vendor Summary",
            "High-level overview of all vendors – average scores, current status, and compliance highlights",
            summary_table
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        def detail_table():
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
        render_chart(
            "Monthly Detail Data",
            "Granular breakdown by vendor and month – drill down for actionable insights",
            detail_table
        )
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
            summary_excel = output.getvalue()
            st.download_button(
                label="Download Summary Excel",
                data=summary_excel,
                file_name='vendor_summary.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        with col2:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                display_df.to_excel(writer, index=False, sheet_name='Details')
            detail_excel = output.getvalue()
            st.download_button(
                label="Download Detail Excel",
                data=detail_excel,
                file_name='vendor_detail.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )

elif page == "Settings":
    tab1, tab2 = st.tabs(["Upload Data", "Preferences"])
    
    with tab1:
        def upload_section():
            st.info("""
            **Required Format:**
            - Columns: vendor, bulan, skor_evaluasi, jumlah_pekerja, waktu_thp, kehadiran, thr, bpjs_tk, bpjs_kes, dpslk
            - Date format: YYYY-MM-DD
            - Score values: 0-100
            """)
            uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
            if uploaded_file is not None:
                try:
                    uploaded_df = pd.read_excel(uploaded_file)
                    st.markdown("#### Data Preview")
                    st.dataframe(uploaded_df.head(10), use_container_width=True, hide_index=True)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.metric("Rows", len(uploaded_df))
                    with col2: st.metric("Columns", len(uploaded_df.columns))
                    with col3: st.metric("Vendors", uploaded_df['vendor'].nunique() if 'vendor' in uploaded_df.columns else 0)
                    with col4: st.metric("Months", uploaded_df['bulan'].nunique() if 'bulan' in uploaded_df.columns else 0)
                    if st.button("Use This Data", type="primary"):
                        if 'bulan' in uploaded_df.columns:
                            uploaded_df['bulan'] = pd.to_datetime(uploaded_df['bulan'])
                        st.session_state['uploaded_data'] = uploaded_df
                        st.success("Data successfully uploaded!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        render_chart(
            "Upload Excel File",
            "Import custom data in the required format to override mock datasets",
            upload_section
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Reset to Default Data"):
            if 'uploaded_data' in st.session_state:
                del st.session_state['uploaded_data']
            st.success("Data reset to default!")
            st.rerun()

    with tab2:
        def preferences_section():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**<span style='color: {text_primary};'>Display</span>**", unsafe_allow_html=True)
                dark_mode_checkbox = st.checkbox("Dark mode", value=dark_mode, key="dark_mode_checkbox")
                if dark_mode_checkbox != dark_mode:
                    st.session_state['dark_mode'] = dark_mode_checkbox
                    st.rerun()
                st.checkbox("Chart animations", value=True)
            with col2:
                st.markdown(f"**<span style='color: {text_primary};'>Notifications</span>**", unsafe_allow_html=True)
                st.checkbox("Weekly email report", value=False)
                st.checkbox("High risk vendor alert", value=True)
            if st.button("Save Preferences", use_container_width=True):
                st.success("Settings saved successfully!")
        render_chart(
            "Dashboard Preferences",
            "Customize your experience with theme and notification settings",
            preferences_section
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='chart-card'>
            <div class='chart-header'>
                <div class='chart-header-title'>About</div>
                <div class='chart-header-subtitle'>VendorPro Analytics Platform details</div>
            </div>
            <div style='color: {text_secondary}; line-height: 1.8; padding-top: 1rem;'>
                <p><strong style='color: {text_primary};'>VendorPro Analytics Platform v2.0</strong></p>
                <p>Integrated vendor monitoring and evaluation system with AI prediction features.</p>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1.5rem;'>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: #10b981; font-size: 1.25rem;'>✓</span>
                        <span>Real-time monitoring</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: #10b981; font-size: 1.25rm;'>✓</span>
                        <span>AI-powered predictions</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: #10b981; font-size: 1.25rem;'>✓</span>
                        <span>Multi-vendor comparison</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: #10b981; font-size: 1.25rem;'>✓</span>
                        <span>Export to Excel</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)