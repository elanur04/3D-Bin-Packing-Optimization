import streamlit as st
import time
import random
import plotly.graph_objects as go
import numpy as np
import os

# Modüllerimizi içe aktaralım
from models import Item, Bin
from packing_solver import evaluate_solution
from algorithms import run_genetic_algorithm, run_whale_optimization_algorithm

# Streamlit sayfa tasarımı ayarları
st.set_page_config(
    page_title="PackOptima — 3D Bin Packing Optimizasyon",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Arayüz ve Görsel Estetik — Emerald Light Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"], .stMarkdown, .stText, p, span, div {
        font-family: 'Space Grotesk', sans-serif;
        color: #1e293b;
    }

    /* Ana arkaplan — beyaz */
    .stApp {
        background: #ffffff !important;
    }

    /* Izgara efektini kaldır */
    .stApp::before {
        display: none;
    }

    /* Ana başlık — animasyonlu neon gradient */
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981, #34d399, #6ee7b7, #10b981);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s ease infinite;
        margin-bottom: 0.4rem;
        text-align: center;
        letter-spacing: -0.5px;
    }

    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Alt başlık */
    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2.5rem;
        letter-spacing: 0.3px;
    }

    /* Kart tasarımı — beyaz + emerald kenar */
    .card {
        border-radius: 16px;
        padding: 22px 26px;
        background: #ffffff;
        border: 1px solid rgba(16,185,129,0.3);
        box-shadow: 0 4px 16px rgba(16,185,129,0.08), 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        color: #1e293b;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #10b981, transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .card:hover {
        transform: translateY(-6px) scale(1.005);
        border-color: rgba(16,185,129,0.6);
        box-shadow: 0 16px 48px rgba(16,185,129,0.15), 0 4px 16px rgba(0,0,0,0.08);
    }

    .card:hover::before {
        opacity: 1;
    }

    .card h4 {
        color: #059669 !important;
        margin-top: 0 !important;
        margin-bottom: 14px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .card p {
        color: #374151 !important;
        line-height: 1.7 !important;
        margin: 6px 0 !important;
        font-size: 0.95rem !important;
    }

    /* Badge'lar */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        color: white;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-ga {
        background: linear-gradient(135deg, #10b981, #059669);
        box-shadow: 0 2px 8px rgba(16,185,129,0.4);
    }
    
    .badge-sa {
        background: linear-gradient(135deg, #8b5cf6, #6d28d9);
        box-shadow: 0 2px 8px rgba(139,92,246,0.4);
    }

    /* Streamlit buton özelleştirme */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1) !important;
        box-shadow: 0 4px 20px rgba(16,185,129,0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(16,185,129,0.5) !important;
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Tab'ların (Sekmelerin) eşit genişlikte olması için */
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        flex: 1 !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        white-space: pre-wrap !important;
    }

    /* En üstteki Streamlit header ve Sidebar Header (siyah bar) */
    [data-testid="stHeader"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebarHeader"] {
        background-color: transparent !important;
    }

    /* Yan panel açma/kapama (Toggle) ve Header ikonlarının görünürlüğü */
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] div[role="button"],
    button[kind="header"],
    [data-testid*="collapsedControl"],
    [data-testid*="collapsedControl"] button,
    [data-testid*="stSidebarCollapsedControl"],
    [data-testid*="CollapseButton"] button {
        background-color: #10b981 !important; /* Yeşil Arka Plan */
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        padding: 6px !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stHeader"] svg,
    [data-testid*="collapsedControl"] svg,
    [data-testid*="CollapseButton"] svg,
    button[kind="header"] svg {
        fill: #ffffff !important; /* Beyaz İkon */
        color: #ffffff !important;
        stroke: #ffffff !important;
    }

    [data-testid="stHeader"] button:hover,
    button[kind="header"]:hover,
    [data-testid*="collapsedControl"]:hover {
        background-color: #059669 !important; /* Koyu Yeşil Hover */
    }

    /* Selectbox (Açılır Menü) aydınlık tema ayarı */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border-color: rgba(16,185,129,0.4) !important;
    }
    div[data-baseweb="select"] * {
        color: #1e293b !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background-color: #f0fdf8 !important;
    }
    
    div[data-baseweb="popover"] > div {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] li {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #f0fdf8 !important;
    }

    /* Sidebar — aydınlık (Üst kısmı siyah bar olacak şekilde gradyan) */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #0f172a 0%, #0f172a 3.75rem, #f8faf9 3.75rem, #f8faf9 100%) !important;
        border-right: 1px solid rgba(16,185,129,0.25) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #059669 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.9rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid rgba(16,185,129,0.25) !important;
        padding-bottom: 8px !important;
    }

    /* Slider — Emerald rengi */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #10b981 !important;
        border-color: #10b981 !important;
        box-shadow: 0 0 12px rgba(16,185,129,0.6) !important;
    }

    /* Tab tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(16,185,129,0.05) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        border: 1px solid rgba(16,185,129,0.12) !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #64748b !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(16,185,129,0.4) !important;
    }

    /* Metric kartlar — aydınlık */
    [data-testid="stMetric"] {
        background: #f0fdf8 !important;
        border: 1px solid rgba(16,185,129,0.3) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(16,185,129,0.6) !important;
        box-shadow: 0 8px 24px rgba(16,185,129,0.15) !important;
        transform: translateY(-2px);
    }

    [data-testid="stMetricValue"] {
        color: #059669 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Tablo — aydınlık */
    [data-testid="stTable"] table {
        border-collapse: separate !important;
        border-spacing: 0 4px !important;
    }

    [data-testid="stTable"] th {
        background: rgba(16,185,129,0.1) !important;
        color: #059669 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        border: none !important;
        padding: 10px 14px !important;
    }

    [data-testid="stTable"] td {
        background: #ffffff !important;
        color: #1e293b !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        border: none !important;
        border-bottom: 1px solid #f1f5f9 !important;
        padding: 10px 14px !important;
        transition: background 0.2s ease !important;
    }

    [data-testid="stTable"] tr:hover td {
        background: #f0fdf8 !important;
    }

    /* İlerleme çubuğu */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981, #34d399) !important;
        border-radius: 4px !important;
        box-shadow: 0 0 12px rgba(16,185,129,0.5) !important;
    }

    /* Horizontal divider */
    hr {
        border-color: rgba(16,185,129,0.15) !important;
        margin: 24px 0 !important;
    }

    /* Select box */
    [data-testid="stSelectbox"] > div > div {
        background: rgba(16,185,129,0.06) !important;
        border-color: rgba(16,185,129,0.25) !important;
        border-radius: 10px !important;
    }

    /* Puls animasyonu — başlık altındaki çizgi */
    .accent-line {
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #10b981, #34d399);
        border-radius: 2px;
        margin: 0 auto 2rem;
        animation: pulse-line 2.5s ease-in-out infinite;
        box-shadow: 0 0 12px rgba(16,185,129,0.6);
    }

    @keyframes pulse-line {
        0%, 100% { opacity: 1; width: 80px; }
        50% { opacity: 0.6; width: 120px; }
    }

    /* Stat kutu (hero bölümü) — aydınlık */
    .stat-box {
        text-align: center;
        padding: 20px;
        border-radius: 14px;
        background: #f0fdf8;
        border: 1px solid rgba(16,185,129,0.25);
        transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .stat-box:hover {
        border-color: rgba(16,185,129,0.6);
        box-shadow: 0 0 30px rgba(16,185,129,0.15);
        transform: translateY(-4px);
    }

    .stat-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #059669;
    }

    .stat-label {
        font-size: 0.78rem;
        color: #475569;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Sabit Araç Şablonları (Küçükten Büyüğe Sıralı)
VEHICLE_TEMPLATES = [
    Bin("A-01", "Küçük Araç (Motokurye)", 15.0, 10.0, 8.0),
    Bin("A-02", "Orta Araç (Minivan)", 25.0, 15.0, 12.0),
    Bin("A-03", "Büyük Araç (Kamyonet)", 40.0, 20.0, 18.0),
    Bin("A-04", "TIR (Uzun Yol)", 60.0, 25.0, 24.0)
]

# 2. 15 Standart Koli Verisi
STANDARD_ITEMS = [
    {"id": "K-01", "name": "Küçük Kargo", "d": 3, "h": 3, "w": 4},
    {"id": "K-02", "name": "Küçük Kargo", "d": 4, "h": 3, "w": 3},
    {"id": "K-03", "name": "Orta Kargo", "d": 5, "h": 4, "w": 4},
    {"id": "K-04", "name": "Orta Kargo", "d": 6, "h": 4, "w": 5},
    {"id": "K-05", "name": "Büyük Kargo", "d": 8, "h": 5, "w": 6},
    {"id": "K-06", "name": "Büyük Kargo", "d": 7, "h": 6, "w": 6},
    {"id": "K-07", "name": "Uzun Kargo", "d": 10, "h": 3, "w": 4},
    {"id": "K-08", "name": "Uzun Kargo", "d": 12, "h": 3, "w": 3},
    {"id": "K-09", "name": "Geniş Kargo", "d": 5, "h": 5, "w": 8},
    {"id": "K-10", "name": "Geniş Kargo", "d": 6, "h": 4, "w": 8},
    {"id": "K-11", "name": "Orta Kargo", "d": 5, "h": 5, "w": 5},
    {"id": "K-12", "name": "Küçük Kargo", "d": 3, "h": 4, "w": 3},
    {"id": "K-13", "name": "Büyük Kargo", "d": 9, "h": 5, "w": 7},
    {"id": "K-14", "name": "Orta Kargo", "d": 6, "h": 5, "w": 4},
    {"id": "K-15", "name": "Uzun Kargo", "d": 11, "h": 3, "w": 4}
]

# State Yönetimi
if 'packages' not in st.session_state:
    st.session_state.packages = [Item(x['id'], x['name'], x['d'], x['h'], x['w']) for x in STANDARD_ITEMS]
if 'ga_results' not in st.session_state:
    st.session_state.ga_results = None
if 'woa_results' not in st.session_state:
    st.session_state.woa_results = None

# Arayüz Başlığı
st.markdown('<div class="main-title"> KargoNet A.Ş.</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Meta-Sezgisel Optimizasyon · Genetik Algoritma vs Balina Sürü Optimizasyonu</div>', unsafe_allow_html=True)
st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

# ----------------- YAN PANEL (SIDEBAR) -----------------

st.sidebar.markdown("### ⚙️ Parametreler")

# Çok kriterli ağırlık katsayıları
st.sidebar.markdown("**Amaç Fonksiyonu Ağırlıkları:**")
w1 = st.sidebar.slider("w1 (Araç Sayısı Ağırlığı)", 0.0, 1.0, 0.60, 0.05)
w2 = 1.0 - w1
st.sidebar.caption(f"Açıklama: f(x) = {w1:.2f} * Araç_Sayısı + {w2:.2f} * Boşluk_Oranı")

tab_params = st.sidebar.tabs(["🧬 Genetik (GA)", "🐳 Balina (WOA)"])

with tab_params[0]:
    st.markdown("**GA Parametreleri:**")
    ga_pop_size = st.slider("Popülasyon Boyutu", 10, 100, 30, 5)
    ga_gens = st.slider("Nesil Sayısı", 10, 150, 50, 5)
    ga_cx_rate = st.slider("Çaprazlama Oranı", 0.1, 1.0, 0.8, 0.05)
    ga_mut_rate = st.slider("Mutasyon Oranı", 0.01, 0.5, 0.1, 0.01)
    ga_tour_size = st.slider("Turnuva Seçim Boyutu", 2, 8, 3, 1)

with tab_params[1]:
    st.markdown("**WOA Parametreleri:**")
    woa_pop_size = st.slider("Balina Sayısı (Popülasyon)", 10, 100, 30, 5)
    woa_iter = st.slider("Maksimum İterasyon (WOA)", 10, 150, 50, 5)
    woa_b = st.slider("Spiral Katsayısı (b)", 0.1, 5.0, 1.0, 0.1)
    st.caption("Açıklama: Kabarcık Ağı (Spiral) mesafesi Hamming uzaklığı ve b katsayısı ile kesikli uzayda simüle edilir.")

# ----------------- ANA SAYFA TASARIMI -----------------
tab_main = st.tabs(["📊 Veri Seti & Hazırlık", "⚡ Optimizasyon & Canlı Analiz", "🔮 3D İnteraktif Görselleştirme"])

# ==================== TAB 1: VERİ SETİ & HAZIRLIK ====================
with tab_main[0]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("###  Koli Veri Seti Seçimi")
        dataset_option = st.radio(
            "Kullanılacak Veri Setini Seçin:",
            ["15 Standart Ödev Kolisi (Önerilen)", "Rastgele Koli Seti Üret (50 - 150 Koli)"]
        )
        
        if dataset_option == "15 Standart Ödev Kolisi (Önerilen)":
            if st.button("Ödev Setini Yükle"):
                st.session_state.packages = [Item(x['id'], x['name'], x['d'], x['h'], x['w']) for x in STANDARD_ITEMS]
                st.success("15 standart ödev kolisi başarıyla yüklendi!")
        else:
            num_random = st.slider("Üretilecek Koli Sayısı:", 50, 150, 80)
            if st.button(f"{num_random} Rastgele Koli Üret"):
                random_items = []
                # 15 kargo tipinin boyutlarını baz alarak gerçekçi rastgele koliler üretelim
                types = ["Küçük Kargo", "Orta Kargo", "Büyük Kargo", "Uzun Kargo", "Geniş Kargo"]
                for i in range(1, num_random + 1):
                    t = random.choice(types)
                    if t == "Küçük Kargo":
                        d, h, w = random.randint(2, 4), random.randint(2, 4), random.randint(3, 4)
                    elif t == "Orta Kargo":
                        d, h, w = random.randint(4, 6), random.randint(3, 5), random.randint(4, 5)
                    elif t == "Büyük Kargo":
                        d, h, w = random.randint(7, 9), random.randint(4, 6), random.randint(5, 7)
                    elif t == "Uzun Kargo":
                        d, h, w = random.randint(10, 13), random.randint(2, 3), random.randint(3, 4)
                    else:  # Geniş Kargo
                        d, h, w = random.randint(4, 6), random.randint(3, 5), random.randint(7, 9)
                        
                    random_items.append(Item(f"K-{i:03d}", t, d, h, w))
                st.session_state.packages = random_items
                st.success(f"{num_random} adet rastgele koli başarıyla oluşturuldu!")
                
        # Mevcut koli özetini göster
        total_item_vol = sum(it.volume for it in st.session_state.packages)
        st.markdown(f"""
        <div class="card">
            <h4>📊 Koli Kümesi Analitiği</h4>
            <p>• <b>Toplam Koli Adedi:</b> {len(st.session_state.packages)} adet</p>
            <p>• <b>Toplam Yük Hacmi:</b> {total_item_vol:,.1f} dm³ (desi³)</p>
            <p>• <b>Ortalama Koli Boyutları:</b> 
            D: {np.mean([it.d for it in st.session_state.packages]):.1f} | 
            Y: {np.mean([it.h for it in st.session_state.packages]):.1f} | 
            G: {np.mean([it.w for it in st.session_state.packages]):.1f}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Filodaki Araç Tipleri")
        # Araçları tablo halinde gösterelim
        vehicle_data = []
        for v in VEHICLE_TEMPLATES:
            vehicle_data.append({
                "Araç ID": v.id,
                "Araç Türü": v.name,
                "Derinlik (dm)": f"{int(v.d)}",
                "Yükseklik (dm)": f"{int(v.h)}",
                "Genişlik (dm)": f"{int(v.w)}",
                "Max Hacim (dm³)": f"{int(v.max_volume)}"
            })
        st.table(vehicle_data)
        
        st.info("💡 Not: Optimizasyon algoritması, kargo yükünü sığdırabilmek için bu araç tiplerinden "
                "ihtiyacı kadar olanını (sınırsız sayıda kullanılabilir) en verimli kombinasyonla otomatik açar.")

    st.markdown("### Aktif Koli Detay Listesi")
    grid_data = []
    for it in st.session_state.packages:
        grid_data.append({
            "Koli ID": it.id,
            "Kargo Türü": it.name,
            "Derinlik (D)": f"{int(it.d)}",
            "Yükseklik (Y)": f"{int(it.h)}",
            "Genişlik (G)": f"{int(it.w)}",
            "Hacim (desi³)": f"{int(it.volume)}"
        })
    st.table(grid_data)

# ==================== TAB 2: OPTİMİZASYON & CANLI ANALİZ ====================
with tab_main[1]:
    st.markdown("<h3 style='text-align: center;'>⚡ Sezgisel Optimizasyon Algoritmaları Canlı Analiz Paneli</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#666;'>Genetik Algoritma (GA) ve Balina Sürü Optimizasyonu (WOA) algoritmalarını canlı olarak çalıştırın ve karşılaştırın.</p>", unsafe_allow_html=True)
    
    col_ga, col_woa = st.columns(2)
    
    # --- SOL SÜTUN: GENETİK ALGORİTMA ---
    with col_ga:
        st.markdown("<h4 style='color:#1f4e79; text-align:center;'>🧬 Genetik Algoritma (GA)</h4>", unsafe_allow_html=True)
        st.markdown("<div style='color:#666; text-align:center; min-height:50px; display:flex; align-items:center; justify-content:center; font-size:0.95rem; margin-bottom:10px;'>Doğal seçilim, çaprazlama ve mutasyon mekanizmalarına dayalı küresel arama.</div>", unsafe_allow_html=True)
        
        run_ga = st.button("🚀 Genetik Algoritmayı (GA) Canlı Çalıştır", key="btn_run_ga", use_container_width=True)
        
        if run_ga:
            st.info("GA Optimizasyonu başlatıldı... Lütfen bekleyin...")
            progress_bar_ga = st.progress(0)
            status_text_ga = st.empty()
            chart_placeholder_ga = st.empty()
            
            history_fitness_ga = []
            start_time_ga = time.time()
            
            ga_generator = run_genetic_algorithm(
                st.session_state.packages, VEHICLE_TEMPLATES,
                pop_size=ga_pop_size, generations=ga_gens,
                crossover_rate=ga_cx_rate, mutation_rate=ga_mut_rate,
                tournament_size=ga_tour_size, w1=w1, w2=w2
            )
            
            for gen, best_state, all_fits in ga_generator:
                history_fitness_ga.append(best_state.fitness)
                chart_placeholder_ga.line_chart(history_fitness_ga)
                progress_bar_ga.progress(int((gen / ga_gens) * 100))
                status_text_ga.text(f"Nesil: {gen}/{ga_gens} | En İyi Fitness: {best_state.fitness:.4f}")
                time.sleep(0.01)
                
            exec_time_ga = time.time() - start_time_ga
            st.success(f"GA başarıyla tamamlandı! Çalışma süresi: {exec_time_ga:.2f} saniye.")
            
            packing_details_ga = []
            for b in best_state.bins:
                for it in b.packed_items:
                    rot_str = f"{it.rot_d}x{it.rot_h}x{it.rot_w} (Tip {it.rotation_type})"
                    packing_details_ga.append([
                        it.id, it.name, b.id, b.name.split(' (')[0], f"({it.x:.0f}, {it.y:.0f}, {it.z:.0f})", rot_str
                    ])
                    
            bin_details_ga = []
            avg_util_ga = []
            for b in best_state.bins:
                bin_details_ga.append([
                    b.id, b.name, b.max_volume, b.used_volume, f"{b.utilization_ratio*100:.1f}%"
                ])
                avg_util_ga.append(b.utilization_ratio * 100)
                
            st.session_state.ga_results = {
                "best_fitness": best_state.fitness,
                "num_bins": len(best_state.bins),
                "avg_utilization": np.mean(avg_util_ga) if avg_util_ga else 0.0,
                "exec_time": exec_time_ga,
                "bins": best_state.bins,
                "packing_details": packing_details_ga,
                "bin_details": bin_details_ga,
                "history": history_fitness_ga
            }

    # --- SAĞ SÜTUN: BALİNA SÜRÜ OPTİMİZASYONU ---
    with col_woa:
        st.markdown("<h4 style='color:#7030a0; text-align:center;'>🐳 Balina Sürü Optimizasyonu (WOA)</h4>", unsafe_allow_html=True)
        st.markdown("<div style='color:#666; text-align:center; min-height:50px; display:flex; align-items:center; justify-content:center; font-size:0.95rem; margin-bottom:10px;'>Kambur balinaların kabarcık ağıyla helezonik avlanma davranışına dayalı sömürü.</div>", unsafe_allow_html=True)
        
        run_woa = st.button("🚀 Balina Algoritmasını (WOA) Canlı Çalıştır", key="btn_run_woa", use_container_width=True)
        
        if run_woa:
            st.info("WOA Optimizasyonu başlatıldı... Lütfen bekleyin...")
            progress_bar_woa = st.progress(0)
            status_text_woa = st.empty()
            chart_placeholder_woa = st.empty()
            
            history_fitness_woa = []
            start_time_woa = time.time()
            
            woa_generator = run_whale_optimization_algorithm(
                st.session_state.packages, VEHICLE_TEMPLATES,
                pop_size=woa_pop_size, max_iter=woa_iter,
                w1=w1, w2=w2, b=woa_b
            )
            
            for iteration, best_state, all_fits in woa_generator:
                history_fitness_woa.append(best_state.fitness)
                chart_placeholder_woa.line_chart(history_fitness_woa)
                progress_bar_woa.progress(int((iteration / woa_iter) * 100))
                status_text_woa.text(f"İterasyon: {iteration}/{woa_iter} | En İyi Fitness: {best_state.fitness:.4f}")
                time.sleep(0.01)
                
            exec_time_woa = time.time() - start_time_woa
            st.success(f"WOA başarıyla tamamlandı! Çalışma süresi: {exec_time_woa:.2f} saniye.")
            
            packing_details_woa = []
            for b in best_state.bins:
                for it in b.packed_items:
                    rot_str = f"{it.rot_d}x{it.rot_h}x{it.rot_w} (Tip {it.rotation_type})"
                    packing_details_woa.append([
                        it.id, it.name, b.id, b.name.split(' (')[0], f"({it.x:.0f}, {it.y:.0f}, {it.z:.0f})", rot_str
                    ])
                    
            bin_details_woa = []
            avg_util_woa = []
            for b in best_state.bins:
                bin_details_woa.append([
                    b.id, b.name, b.max_volume, b.used_volume, f"{b.utilization_ratio*100:.1f}%"
                ])
                avg_util_woa.append(b.utilization_ratio * 100)
                
            st.session_state.woa_results = {
                "best_fitness": best_state.fitness,
                "num_bins": len(best_state.bins),
                "avg_utilization": np.mean(avg_util_woa) if avg_util_woa else 0.0,
                "exec_time": exec_time_woa,
                "bins": best_state.bins,
                "packing_details": packing_details_woa,
                "bin_details": bin_details_woa,
                "history": history_fitness_woa
            }

    # Sonuçların Özeti
    st.markdown("---")
    st.markdown("### 🏆 Optimizasyon Sonuç Özet Paneli")
    
    if st.session_state.ga_results or st.session_state.woa_results:
        col_res_ga, col_res_woa = st.columns(2)
        
        with col_res_ga:
            st.markdown("##### 🧬 Genetik Algoritma (GA) Sonuçları")
            if st.session_state.ga_results:
                res_ga = st.session_state.ga_results
                c1, c2, c3 = st.columns(3)
                c1.metric("En İyi Fitness", f"{res_ga['best_fitness']:.4f}")
                c2.metric("Araç Sayısı", f"{res_ga['num_bins']} Araç")
                c3.metric("Ort. Doluluk", f"{res_ga['avg_utilization']:.1f}%")
            else:
                st.info("GA henüz çalıştırılmadı.")
                
        with col_res_woa:
            st.markdown("##### 🐳 Balina Optimizasyonu (WOA) Sonuçları")
            if st.session_state.woa_results:
                res_woa = st.session_state.woa_results
                c1, c2, c3 = st.columns(3)
                c1.metric("En İyi Fitness", f"{res_woa['best_fitness']:.4f}")
                c2.metric("Araç Sayısı", f"{res_woa['num_bins']} Araç")
                c3.metric("Ort. Doluluk", f"{res_woa['avg_utilization']:.1f}%")
            else:
                st.info("WOA henüz çalıştırılmadı.")
                
        # Yakınsama Grafiğini Çiz (İkisi de varsa karşılaştırmalı çiz)
        st.markdown("#### Fitness Yakınsama Eğrileri Karşılaştırması")
        fig_comp = go.Figure()
        
        if st.session_state.ga_results:
            fig_comp.add_trace(go.Scatter(
                y=st.session_state.ga_results['history'],
                name="🧬 Genetik Algoritma (GA)",
                line=dict(color='#10b981', width=3),
                mode='lines+markers',
                marker=dict(size=5, color='#10b981')
            ))
        if st.session_state.woa_results:
            fig_comp.add_trace(go.Scatter(
                y=st.session_state.woa_results['history'],
                name="🐳 Balina Sürü (WOA)",
                line=dict(color='#f97316', width=3),
                mode='lines+markers',
                marker=dict(size=5, color='#f97316')
            ))
            
        fig_comp.update_layout(
            title=dict(
                text="Yakınsama Grafiği: GA ve WOA Karşılaştırması",
                font=dict(size=16, color='#1e293b')
            ),
            xaxis_title="İterasyon / Nesil Numarası",
            yaxis_title="En İyi Uygunluk Değeri (Fitness Value)",
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#1e293b'),
            xaxis=dict(gridcolor='#e2e8f0', linecolor='#94a3b8', tickfont=dict(color='#1e293b'), title_font=dict(color='#1e293b')),
            yaxis=dict(gridcolor='#e2e8f0', linecolor='#94a3b8', tickfont=dict(color='#1e293b'), title_font=dict(color='#1e293b')),
        )
        st.plotly_chart(fig_comp, use_container_width=True, theme=None)
    else:
        st.warning("⚠️ Lütfen optimizasyonu başlatmak için yukarıdaki çalıştırma butonuna basın!")

# ==================== TAB 3: 3D İNTERAKTİF GÖRSELLEŞTİRME ====================
with tab_main[2]:
    st.markdown("### 🔮 Etkileşimli 3D Yükleme Düzeni Simülatörü")
    
    options_alg = []
    if st.session_state.ga_results:
        options_alg.append("🧬 Genetik Algoritma (GA)")
    if st.session_state.woa_results:
        options_alg.append("🐳 Balina Sürü Optimizasyonu (WOA)")
        
    if not options_alg:
        st.warning("⚠️ Lütfen görselleştirme yapabilmek için önce en az bir optimizasyon algoritmasını çalıştırın!")
    else:
        selected_alg = st.selectbox("Görselleştirilecek Algoritma Çıktısı:", options_alg)
        
        # Sonuç verisini seç
        res_data = st.session_state.ga_results if "GA" in selected_alg else st.session_state.woa_results
        
        # Hangi aracı çizdirelim?
        bins_list = res_data['bins']
        selected_bin_id = st.selectbox(
            "Görüntülenecek Araç (Plaka/ID):",
            [f"{b.id} - {b.name} (Doluluk: {b.utilization_ratio*100:.1f}%)" for b in bins_list]
        )
        
        # Seçilen aracı bul
        bin_idx = [b.id for b in bins_list].index(selected_bin_id.split(' - ')[0])
        bin_obj = bins_list[bin_idx]
        
        st.markdown(f"#### 🚚 {bin_obj.id} ({bin_obj.name}) Yükleme Düzeni")
        
        # Plotly 3D Kutu çizdirme motoru
        fig = go.Figure()
        
        # 1. Aracın Kendisini (Wireframe Konteyner) Çizelim
        D, H, G = bin_obj.d, bin_obj.h, bin_obj.w
        
        # Wireframe köşeleri
        x_lines = [0, D, D, 0, 0, None, 0, D, D, 0, 0, None, 0, 0, None, D, D, None, D, D, None, 0, 0]
        y_lines = [0, 0, H, H, 0, None, 0, 0, H, H, 0, None, 0, 0, None, 0, 0, None, H, H, None, H, H]
        z_lines = [0, 0, 0, 0, 0, None, G, G, G, G, G, None, 0, G, None, 0, G, None, 0, G, None, 0, G]
        
        fig.add_trace(go.Scatter3d(
            x=x_lines, y=y_lines, z=z_lines,
            mode='lines',
            line=dict(color='black', width=3),
            name='Araç Sınırları (Konteyner)',
            hoverinfo='none'
        ))
        
        # 2. İçindeki Kutuları (Solid Mesh3d) Teker Teker Çizelim
        # Renk paleti
        colors_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for idx, item in enumerate(bin_obj.packed_items):
            x, y, z = item.x, item.y, item.z
            dx, dy, dz = item.rot_d, item.rot_h, item.rot_w
            
            # Kutunun 8 köşesi
            vertices_x = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
            vertices_y = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
            vertices_z = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
            
            # Üçgen yüzey endeksleri (Kutunun 12 üçgen yüzeyi)
            i_tri = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
            j_tri = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 2, 6]
            k_tri = [2, 3, 6, 7, 5, 4, 6, 7, 7, 4, 6, 5]
            
            color_sel = colors_palette[idx % len(colors_palette)]
            
            # Solid Mesh çizdir
            fig.add_trace(go.Mesh3d(
                x=vertices_x, y=vertices_y, z=vertices_z,
                i=i_tri, j=j_tri, k=k_tri,
                color=color_sel,
                opacity=0.8,
                name=f"{item.id} - {item.name}",
                flatshading=True,
                hovertemplate=(
                    f"<b>Koli: {item.id} ({item.name})</b><br>"
                    f"Konum (x,y,z): ({x:.1f}, {y:.1f}, {z:.1f})<br>"
                    f"Boyutlar (D,Y,G): {dx:.1f} x {dy:.1f} x {dz:.1f}<br>"
                    f"Hacim: {item.volume:.1f} dm³<br>"
                    "<extra></extra>"
                )
            ))
            
        fig.update_layout(
            title=f"{bin_obj.id} 3D Yerleşim Şeması (Plotly İnteraktif)",
            scene=dict(
                xaxis=dict(title='Derinlik (D)', range=[-2, max(65, D+5)]),
                yaxis=dict(title='Yükseklik (Y)', range=[-2, max(30, H+5)]),
                zaxis=dict(title='Genişlik (G)', range=[-2, max(26, G+5)]),
                aspectmode='data'
            ),
            width=900,
            height=700,
            showlegend=False,
            font=dict(color='#1e293b'),
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff'
        )
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
        
        # Aracın yerleşim detay tablosunu çizdirelim
        st.markdown("##### Araç Yük Detay Tablosu")
        grid_bin_items = []
        for it in bin_obj.packed_items:
            grid_bin_items.append({
                "Koli ID": it.id,
                "Kargo Türü": it.name,
                "Derinlik (x)": int(it.x),
                "Yükseklik (y)": int(it.y),
                "Genişlik (z)": int(it.z),
                "Aktif Ebatlar (D x Y x G)": f"{int(it.rot_d)} x {int(it.rot_h)} x {int(it.rot_w)}",
                "Hacim (dm³)": int(it.volume)
            })
        st.table(grid_bin_items)


