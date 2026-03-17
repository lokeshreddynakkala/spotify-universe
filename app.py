import streamlit as st
import pandas as pd
import json
import numpy as np
import joblib
import os

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify Universe",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GOOGLE FONTS + MASTER CSS ──────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.cdnfonts.com/css/circular-std" rel="stylesheet">

<style>
/* ── RESET & ROOT ── */
:root {
  --green:   #1DB954;
  --green2:  #1ed760;
  --black:   #0a0a0a;
  --card:    #111111;
  --border:  #1f1f1f;
  --muted:   #6a6a6a;
  --text:    #e8e8e8;
  --font-display: 'Circular Std', 'Circular', system-ui, -apple-system, sans-serif;
  --font-body:    'Circular Std', 'Circular', system-ui, -apple-system, sans-serif;
}

/* ── GLOBAL ── */
.stApp { background: var(--black) !important; color: var(--text); font-family: var(--font-body); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 100% !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--black); }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: #0d0d0d !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

/* ── SIDEBAR LOGO ── */
.sp-logo {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(90deg, var(--green), var(--green2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}
.sp-logo svg { flex-shrink: 0; }

/* ── SEARCH INPUT ── */
.stTextInput input {
  background: #161616 !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
  padding: 0.6rem 1rem !important;
  transition: border 0.2s;
}
.stTextInput input:focus { border-color: var(--green) !important; box-shadow: none !important; }
.stTextInput input::placeholder { color: var(--muted) !important; }
label[data-testid="stWidgetLabel"] { display: none !important; }

/* ── STAT CHIPS ── */
.stat-row { display: flex; gap: 0.75rem; margin-top: 1.25rem; }
.stat-chip {
  flex: 1;
  background: #161616;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.85rem 0.75rem;
  text-align: center;
}
.stat-chip .val {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--green);
  line-height: 1;
}
.stat-chip .lbl {
  font-size: 0.68rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.3rem;
}

/* ── PAGE HEADER ── */
.page-header {
  margin-bottom: 2rem;
}
.page-header h1 {
  font-family: var(--font-display) !important;
  font-size: clamp(2rem, 4vw, 3.2rem) !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em !important;
  color: #fff !important;
  line-height: 1.05 !important;
  margin: 0 0 0.4rem !important;
}
.page-header p {
  color: var(--muted) !important;
  font-size: 0.95rem !important;
  margin: 0 !important;
}

/* ── GENRE CARDS ── */
.genre-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
  margin-bottom: 2rem;
}
.genre-card {
  position: relative;
  border-radius: 14px;
  padding: 1.1rem 1rem 0.9rem;
  cursor: pointer;
  border: 1.5px solid transparent;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
  overflow: hidden;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.genre-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.15;
  transition: opacity 0.2s;
}
.genre-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.6); }
.genre-card:hover::before { opacity: 0.25; }
.genre-card.active { border-color: var(--green); box-shadow: 0 0 0 1px var(--green), 0 8px 30px rgba(29,185,84,0.25); }

/* card colour themes */
.gc-pop    { background: linear-gradient(135deg, #1a0a2e 0%, #0d1117 100%); }
.gc-pop    .gc-icon { color: #c084fc; }
.gc-pop    .gc-accent { background: radial-gradient(circle at 70% 30%, rgba(192,132,252,0.3) 0%, transparent 60%); }

.gc-steady { background: linear-gradient(135deg, #0a1f15 0%, #0d1117 100%); }
.gc-steady .gc-icon { color: var(--green); }
.gc-steady .gc-accent { background: radial-gradient(circle at 70% 30%, rgba(29,185,84,0.25) 0%, transparent 60%); }

.gc-rock   { background: linear-gradient(135deg, #1f0a0a 0%, #0d1117 100%); }
.gc-rock   .gc-icon { color: #f87171; }
.gc-rock   .gc-accent { background: radial-gradient(circle at 70% 30%, rgba(248,113,113,0.3) 0%, transparent 60%); }

.gc-chill  { background: linear-gradient(135deg, #0a1530 0%, #0d1117 100%); }
.gc-chill  .gc-icon { color: #60a5fa; }
.gc-chill  .gc-accent { background: radial-gradient(circle at 70% 30%, rgba(96,165,250,0.3) 0%, transparent 60%); }

.gc-pod    { background: linear-gradient(135deg, #1a150a 0%, #0d1117 100%); }
.gc-pod    .gc-icon { color: #fbbf24; }
.gc-pod    .gc-accent { background: radial-gradient(circle at 70% 30%, rgba(251,191,36,0.3) 0%, transparent 60%); }

.gc-accent {
  position: absolute; inset: 0; pointer-events: none;
}
.gc-icon {
  font-size: 2rem;
  margin-bottom: 0.6rem;
  position: relative;
  z-index: 1;
}
.gc-name {
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.01em;
  position: relative;
  z-index: 1;
}
.gc-count {
  font-size: 0.68rem;
  color: var(--muted);
  margin-top: 0.15rem;
  position: relative;
  z-index: 1;
}

/* ── BUTTONS (hidden, replaced by HTML cards) ── */
div[data-testid="column"] .stButton button {
  display: none !important;
}

/* ── DIVIDER ── */
.sp-divider { border: none; border-top: 1px solid var(--border); margin: 0 0 2rem; }

/* ── SECTION LABEL ── */
.section-label {
  font-family: var(--font-display);
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted);
  margin-bottom: 0.75rem;
}

/* ── CANVAS WRAPPER ── */
.canvas-wrap {
  background: #0e0e0e;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.25rem;
  position: relative;
}
.canvas-wrap h3 {
  font-family: var(--font-display) !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  color: #fff !important;
  margin: 0 0 1rem !important;
}

/* ── TABLE WRAP ── */
.table-wrap {
  background: #0e0e0e;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.25rem;
  height: 100%;
}
.table-wrap h3 {
  font-family: var(--font-display) !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  color: #fff !important;
  margin: 0 0 1rem !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border-radius: 10px !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] * {
  font-family: var(--font-body) !important;
  font-size: 0.82rem !important;
}

/* ── METRICS strip ── */
.metrics-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 2rem;
}
.metric-card {
  background: #0e0e0e;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
}
.metric-card .mc-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  margin-bottom: 0.35rem;
}
.metric-card .mc-val {
  font-family: var(--font-display);
  font-size: 1.7rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}
.metric-card .mc-sub {
  font-size: 0.72rem;
  color: var(--green);
  margin-top: 0.2rem;
}

/* ── SEARCH BANNER ── */
.search-banner {
  background: linear-gradient(90deg, #0f2017 0%, #0a0a0a 100%);
  border: 1px solid #1a3325;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  font-family: var(--font-display);
  font-size: 0.9rem;
  color: var(--green);
}
.search-banner span { color: var(--muted); font-family: var(--font-body); font-size: 0.82rem; margin-left: 0.5rem; }

/* ── EMPTY STATE ── */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--muted);
  font-size: 0.9rem;
}
.empty-state .es-icon { font-size: 3rem; margin-bottom: 1rem; }

/* ── PREDICT SECTION ── */
.predict-wrap {
  background: #0e0e0e;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
}
.predict-wrap h2 {
  font-family: var(--font-display) !important;
  font-size: 1.35rem !important;
  font-weight: 800 !important;
  color: #fff !important;
  letter-spacing: -0.02em !important;
  margin: 0 0 0.3rem !important;
}
.predict-wrap .predict-sub {
  color: var(--muted);
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}
.result-box {
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  margin-top: 0.5rem;
  border: 1px solid var(--border);
}
.result-box .rb-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin-bottom: 0.4rem;
}
.result-box .rb-val {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1.1;
}
.result-box .rb-sub {
  font-size: 0.75rem;
  margin-top: 0.35rem;
  color: var(--muted);
}
.rb-cluster { background: #111827; border-color: #1f2937; }
.rb-cluster .rb-val { color: var(--green); }
.rb-hit    { background: #1a1200; border-color: #3d2d00; }
.rb-hit    .rb-val { color: #fbbf24; }
.rb-miss   { background: #0f0f0f; border-color: #222; }
.rb-miss   .rb-val { color: var(--muted); }
.prob-bar-track {
  height: 6px; border-radius: 99px;
  background: #1f1f1f; margin-top: 0.6rem; overflow: hidden;
}
.prob-bar-fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--green), var(--green2));
  transition: width 0.6s ease;
}

/* ── SPINNER OVERRIDE ── */
div[data-testid="stSpinner"] > div {
  display: flex !important;
  align-items: center !important;
  gap: 0.75rem !important;
  padding: 0.85rem 1.25rem !important;
  background: #0e0e0e !important;
  border: 1px solid #1f1f1f !important;
  border-radius: 12px !important;
  margin-top: 1rem !important;
}
div[data-testid="stSpinner"] svg {
  width: 20px !important; height: 20px !important;
  color: var(--green) !important;
}
div[data-testid="stSpinner"] p {
  font-family: var(--font-body) !important;
  font-size: 0.82rem !important;
  color: #6a6a6a !important;
  margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('spotify_final_ml.csv')
        # Ensure required columns exist
        for col in ['pca1', 'pca2', 'energy', 'tempo', 'track', 'artist', 'cluster_name']:
            if col not in df.columns:
                df[col] = 0 if col not in ['track','artist','cluster_name'] else 'Unknown'
        return df
    except FileNotFoundError:
        st.error("⚠️ `spotify_final_ml.csv` not found. Place it in the same directory.")
        st.stop()

df = load_data()

# ─── SESSION STATE ──────────────────────────────────────────────────────────
if 'selected_civ' not in st.session_state:
    st.session_state.selected_civ = "Pop / Dance"

# ─── CLUSTER CONFIG ─────────────────────────────────────────────────────────
CLUSTERS = [
    {"name": "Pop / Dance",           "css": "gc-pop",    "icon": "🎛️", "full": "Pop / Dance"},
    {"name": "Steady / Balanced",     "css": "gc-steady", "icon": "🎵", "full": "Steady / Balanced"},
    {"name": "Rock / Intense",        "css": "gc-rock",   "icon": "🎸", "full": "Rock / Intense"},
    {"name": "Acoustic / Chill",      "css": "gc-chill",  "icon": "🎹", "full": "Acoustic / Chill"},
    {"name": "Podcasts / Exp",        "css": "gc-pod",    "icon": "🎙️", "full": "Podcasts / Experimental"},
]

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sp-logo">
      <svg width="28" height="28" viewBox="0 0 2931 2931" xmlns="http://www.w3.org/2000/svg">
        <path d="M1465.5 0C656.1 0 0 656.1 0 1465.5S656.1 2931 1465.5 2931 2931 2274.9 2931 1465.5 2274.9 0 1465.5 0zm671.8 2113.4c-26.3 43.2-82.6 56.7-125.6 30.4-344.2-210.3-777.3-257.8-1287.4-141.2-49.1 11.3-98-19.8-109.3-68.9-11.4-49.1 19.7-98 68.9-109.3 557.9-127.5 1036.7-72.7 1422.7 163.3 43.1 26.3 56.7 82.6 30.7 125.7zm179.2-398.5c-33.1 53.8-103.5 70.6-157.2 37.6-394.2-242.3-995-312.4-1461.2-170.9-60.4 18.3-124.2-15.7-142.6-76-18.3-60.4 15.8-124.1 76.1-142.5 532.9-161.7 1194.2-83.4 1646.7 194.7 53.7 33.1 70.6 103.5 37.6 157.1h.6zm15.4-415c-472.4-280.7-1251.5-306.5-1702.5-169.6-72.4 21.9-148.9-18.8-170.8-91.2-21.9-72.5 18.8-149 91.3-170.9 517.7-157.1 1378.1-126.8 1921.2 196.2 65.1 38.7 86.5 122.8 47.9 187.8-38.5 65.1-122.7 86.6-187.8 48l.7-.3z" fill="#1DB954"/>
      </svg>
      Spotify Universe
    </div>
    """, unsafe_allow_html=True)

    # Search
    st.markdown('<div class="section-label">Search</div>', unsafe_allow_html=True)
    search_query = st.text_input("search", placeholder="Artists or tracks…", label_visibility="collapsed")

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Library</div>', unsafe_allow_html=True)

    total_tracks  = len(df)
    total_artists = df['artist'].nunique()
    avg_energy    = df['energy'].mean() if 'energy' in df.columns else 0
    total_clusters = df['cluster_name'].nunique() if 'cluster_name' in df.columns else 5

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-chip">
        <div class="val">{total_tracks:,}</div>
        <div class="lbl">Tracks</div>
      </div>
      <div class="stat-chip">
        <div class="val">{total_artists:,}</div>
        <div class="lbl">Artists</div>
      </div>
    </div>
    <div class="stat-row">
      <div class="stat-chip">
        <div class="val">{avg_energy:.2f}</div>
        <div class="lbl">Avg Energy</div>
      </div>
      <div class="stat-chip">
        <div class="val">{total_clusters}</div>
        <div class="lbl">Genres</div>
      </div>
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Genres</div>', unsafe_allow_html=True)
    for c in CLUSTERS:
        count = len(df[df['cluster_name'] == c['full']]) if 'cluster_name' in df.columns else 0
        active = "active" if st.session_state.selected_civ == c['name'] else ""
        st.markdown(f"""
        <div class="genre-card {c['css']} {active}" style="min-height:unset;padding:0.65rem 0.85rem;margin-bottom:0.4rem;border-radius:10px;"
             onclick="void(0)">
          <div class="gc-accent"></div>
          <div style="display:flex;align-items:center;gap:0.6rem;position:relative;z-index:1;">
            <span style="font-size:1rem">{c['icon']}</span>
            <div>
              <div class="gc-name" style="font-size:0.75rem">{c['name']}</div>
              <div class="gc-count">{count:,} tracks</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── MAIN ───────────────────────────────────────────────────────────────────
current_cluster = next((c for c in CLUSTERS if c['name'] == st.session_state.selected_civ), CLUSTERS[0])

st.markdown(f"""
<div class="page-header">
  <h1>{current_cluster['icon']} {st.session_state.selected_civ}</h1>
  <p>Audio signature map · Machine learning clusters · Explore your music universe</p>
</div>
""", unsafe_allow_html=True)

# ─── GENRE NAVIGATION CARDS ─────────────────────────────────────────────────
cols = st.columns(5)
for i, c in enumerate(CLUSTERS):
    count = len(df[df['cluster_name'] == c['full']]) if 'cluster_name' in df.columns else 0
    active_cls = "active" if st.session_state.selected_civ == c['name'] else ""
    with cols[i]:
        st.markdown(f"""
        <div class="genre-card {c['css']} {active_cls}">
          <div class="gc-accent"></div>
          <div class="gc-icon">{c['icon']}</div>
          <div class="gc-name">{c['name']}</div>
          <div class="gc-count">{count:,} tracks</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(c['name'], key=f"nav_{i}"):
            st.session_state.selected_civ = c['name']
            st.rerun()

st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)

# ─── FILTER ─────────────────────────────────────────────────────────────────
if search_query:
    filtered_df = df[
        df['artist'].str.contains(search_query, case=False, na=False) |
        df['track'].str.contains(search_query, case=False, na=False)
    ]
    st.markdown(f"""
    <div class="search-banner">
      🔍 "{search_query}"<span>{len(filtered_df):,} results found</span>
    </div>
    """, unsafe_allow_html=True)
else:
    filtered_df = df[df['cluster_name'] == current_cluster['full']]

if filtered_df.empty:
    st.markdown("""
    <div class="empty-state">
      <div class="es-icon">🎵</div>
      <div>No tracks found. Try a different search or genre.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── METRICS STRIP ──────────────────────────────────────────────────────────
m_tracks = len(filtered_df)
m_artists = filtered_df['artist'].nunique()
m_energy = filtered_df['energy'].mean() if 'energy' in filtered_df.columns else 0
m_tempo = filtered_df['tempo'].mean() if 'tempo' in filtered_df.columns else 0

st.markdown(f"""
<div class="metrics-strip">
  <div class="metric-card">
    <div class="mc-label">Tracks</div>
    <div class="mc-val">{m_tracks:,}</div>
    <div class="mc-sub">in this playlist</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">Artists</div>
    <div class="mc-val">{m_artists:,}</div>
    <div class="mc-sub">unique voices</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">Avg Energy</div>
    <div class="mc-val">{m_energy:.2f}</div>
    <div class="mc-sub">intensity score</div>
  </div>
  <div class="metric-card">
    <div class="mc-label">Avg BPM</div>
    <div class="mc-val">{m_tempo:.0f}</div>
    <div class="mc-sub">beats per minute</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── D3 SCATTER + TABLE ─────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.1])

# Prepare data for D3 (sample for performance)
sample_df = filtered_df[['track', 'artist', 'pca1', 'pca2', 'energy']].dropna().head(600)
chart_data = sample_df.to_dict(orient='records')
chart_json = json.dumps(chart_data)

# D3 colour accent per cluster
ACCENT = {"gc-pop": "#c084fc", "gc-steady": "#1DB954", "gc-rock": "#f87171",
          "gc-chill": "#60a5fa", "gc-pod": "#fbbf24"}
accent_color = ACCENT.get(current_cluster['css'], "#1DB954")

with left_col:
    st.markdown('<div class="canvas-wrap"><h3>🌐 Audio Dimension Map</h3>', unsafe_allow_html=True)

    scatter_html = f"""
    <style>
      #sp-canvas {{ background: transparent; display: block; }}
      .sp-tooltip {{
        position: absolute; pointer-events: none;
        background: #181818; border: 1px solid #333;
        border-radius: 8px; padding: 8px 12px;
        font-family: 'Circular Std', 'Circular', system-ui, sans-serif; font-size: 12px; color: #e8e8e8;
        max-width: 200px; line-height: 1.4;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        opacity: 0; transition: opacity 0.15s;
      }}
      .sp-tooltip strong {{ color: {accent_color}; display: block; font-family: 'Circular Std', 'Circular', system-ui, sans-serif; font-weight: 700; }}
    </style>

    <div style="position:relative;">
      <canvas id="sp-canvas" width="560" height="420"></canvas>
      <div class="sp-tooltip" id="sp-tip"></div>
    </div>

    <script>
    (function(){{
      const DATA   = {chart_json};
      const ACCENT = "{accent_color}";
      const canvas = document.getElementById('sp-canvas');
      const ctx    = canvas.getContext('2d');
      const tip    = document.getElementById('sp-tip');
      const W = canvas.width, H = canvas.height;
      const PAD = 40;

      if (!DATA.length) return;

      // scales
      const xs = DATA.map(d => d.pca1), ys = DATA.map(d => d.pca2);
      const minX = Math.min(...xs), maxX = Math.max(...xs);
      const minY = Math.min(...ys), maxY = Math.max(...ys);
      const scX = v => PAD + (v - minX) / (maxX - minX) * (W - 2*PAD);
      const scY = v => H - PAD - (v - minY) / (maxY - minY) * (H - 2*PAD);

      function hexToRgb(hex) {{
        const r = parseInt(hex.slice(1,3),16);
        const g = parseInt(hex.slice(3,5),16);
        const b = parseInt(hex.slice(5,7),16);
        return [r,g,b];
      }}
      const [ar,ag,ab] = hexToRgb(ACCENT);

      function draw() {{
        ctx.clearRect(0, 0, W, H);

        // grid
        ctx.strokeStyle = '#1f1f1f';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {{
          const x = PAD + i * (W - 2*PAD) / 5;
          const y = PAD + i * (H - 2*PAD) / 5;
          ctx.beginPath(); ctx.moveTo(x, PAD); ctx.lineTo(x, H-PAD); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(PAD, y); ctx.lineTo(W-PAD, y); ctx.stroke();
        }}

        // axis labels
        ctx.fillStyle = '#4a4a4a';
        ctx.font = '10px "Circular Std", "Circular", system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Energy · Tempo · Loudness →', W/2, H - 6);
        ctx.save(); ctx.translate(12, H/2);
        ctx.rotate(-Math.PI/2); ctx.fillText('← Mood · Acoustics · Valence', 0, 0); ctx.restore();

        // dots
        DATA.forEach(d => {{
          const x = scX(d.pca1), y = scY(d.pca2);
          const e = d.energy ?? 0.5;
          const alpha = 0.25 + e * 0.65;
          const r = 2.5 + e * 2.5;

          // glow
          const grd = ctx.createRadialGradient(x,y,0, x,y,r*2.5);
          grd.addColorStop(0, `rgba(${{ar}},${{ag}},${{ab}},${{alpha * 0.4}})`);
          grd.addColorStop(1, `rgba(${{ar}},${{ag}},${{ab}},0)`);
          ctx.beginPath(); ctx.arc(x, y, r*2.5, 0, Math.PI*2);
          ctx.fillStyle = grd; ctx.fill();

          // dot
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2);
          ctx.fillStyle = `rgba(${{ar}},${{ag}},${{ab}},${{alpha}})`;
          ctx.fill();
        }});
      }}

      draw();

      // tooltip
      canvas.addEventListener('mousemove', e => {{
        const rect = canvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) * (W / rect.width);
        const my = (e.clientY - rect.top)  * (H / rect.height);
        let closest = null, minDist = 30;
        DATA.forEach(d => {{
          const dx = scX(d.pca1) - mx, dy = scY(d.pca2) - my;
          const dist = Math.sqrt(dx*dx + dy*dy);
          if (dist < minDist) {{ minDist = dist; closest = d; }}
        }});
        if (closest) {{
          tip.style.opacity = '1';
          tip.style.left = (e.clientX - rect.left + 12) + 'px';
          tip.style.top  = (e.clientY - rect.top  - 40) + 'px';
          tip.innerHTML = `<strong>${{closest.track}}</strong>${{closest.artist}}<br>Energy: ${{(closest.energy*100).toFixed(0)}}%`;
        }} else {{
          tip.style.opacity = '0';
        }}
      }});
      canvas.addEventListener('mouseleave', () => tip.style.opacity = '0');
    }})();
    </script>
    """
    st.components.v1.html(scatter_html, height=445)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="table-wrap"><h3>🎧 Track List</h3>', unsafe_allow_html=True)
    display_df = filtered_df[['track', 'artist', 'energy', 'tempo']].sort_values('energy', ascending=False).reset_index(drop=True)
    st.dataframe(
        display_df,
        column_config={
            "track":   st.column_config.TextColumn("Title", width="medium"),
            "artist":  st.column_config.TextColumn("Artist"),
            "energy":  st.column_config.ProgressColumn("Energy", format="%.2f", min_value=0, max_value=1),
            "tempo":   st.column_config.NumberColumn("BPM", format="%d"),
        },
        hide_index=True,
        use_container_width=True,
        height=460,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ─── PREDICT SONG PERFORMANCE ───────────────────────────────────────────────
st.markdown('<hr class="sp-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="predict-wrap">
  <h2>🎯 Predict Song Performance</h2>
  <div class="predict-sub">Enter audio features below to predict which cluster a track belongs to and whether it's likely to be a hit.</div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_cluster_model():
    path = "cluster_prediction_pipeline.pkl"
    if not os.path.exists(path):
        return None
    return joblib.load(path)

@st.cache_resource
def load_hit_model():
    base        = os.path.dirname(os.path.abspath(__file__))
    model_path  = os.path.join(base, "hit_prediction_ann_model.h5")
    scaler_path = os.path.join(base, "hit_scaler.pkl")
    if not os.path.exists(model_path):
        return None, None, f"Model file not found:\n{model_path}"
    if not os.path.exists(scaler_path):
        return None, None, f"Scaler file not found:\n{scaler_path}"
    try:
        from tensorflow.keras.models import load_model
        model  = load_model(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler, None
    except Exception as e:
        return None, None, str(e)

CLUSTER_MAP = {
    0: ("Pop / Dance",            "🎛️", "gc-pop"),
    1: ("Steady / Balanced",      "🎵", "gc-steady"),
    2: ("Rock / Intense",         "🎸", "gc-rock"),
    3: ("Acoustic / Chill",       "🎹", "gc-chill"),
    4: ("Podcasts / Experimental","🎙️", "gc-pod"),
}

# All 15 features the cluster model was trained on
CLUSTER_FEATURES = [
    'danceability','energy','key','loudness','mode',
    'speechiness','acousticness','instrumentalness','liveness','valence',
    'tempo','duration_ms','time_signature','chorus_hit','sections'
]

# The 15 features the hit ANN scaler was trained on (all except target cols)
HIT_FEATURES = [
    'danceability','energy','key','loudness','mode',
    'speechiness','acousticness','instrumentalness','liveness','valence',
    'tempo','duration_ms','time_signature','chorus_hit','sections'
]

# Config for every feature: label, min, max, default, step, type
FEAT_CFG = {
    'danceability':     dict(label="Danceability",      min=0.0,   max=1.0,    value=0.5,    step=0.01,  kind="slider",  tip="How suitable for dancing (0=low, 1=high)"),
    'energy':           dict(label="Energy",            min=0.0,   max=1.0,    value=0.5,    step=0.01,  kind="slider",  tip="Perceptual intensity and activity (0–1)"),
    'key':              dict(label="Key",               min=0,     max=11,     value=0,      step=1,     kind="int",     tip="Musical key (0=C, 1=C#, … 11=B)"),
    'loudness':         dict(label="Loudness (dB)",     min=-60.0, max=5.0,    value=-8.0,   step=0.1,   kind="slider",  tip="Overall loudness in dB (typical: -60 to 0)"),
    'mode':             dict(label="Mode",              min=0,     max=1,      value=1,      step=1,     kind="int",     tip="Major (1) or Minor (0)"),
    'speechiness':      dict(label="Speechiness",       min=0.0,   max=1.0,    value=0.05,   step=0.01,  kind="slider",  tip="Presence of spoken words (>0.66 = speech)"),
    'acousticness':     dict(label="Acousticness",      min=0.0,   max=1.0,    value=0.3,    step=0.01,  kind="slider",  tip="Confidence the track is acoustic (0–1)"),
    'instrumentalness': dict(label="Instrumentalness",  min=0.0,   max=1.0,    value=0.0,    step=0.01,  kind="slider",  tip="Predicts no vocals (>0.5 = instrumental)"),
    'liveness':         dict(label="Liveness",          min=0.0,   max=1.0,    value=0.15,   step=0.01,  kind="slider",  tip="Presence of live audience (>0.8 = live)"),
    'valence':          dict(label="Valence",           min=0.0,   max=1.0,    value=0.5,    step=0.01,  kind="slider",  tip="Musical positiveness / happiness (0–1)"),
    'tempo':            dict(label="Tempo (BPM)",       min=40.0,  max=220.0,  value=120.0,  step=1.0,   kind="slider",  tip="Estimated beats per minute"),
    'duration_ms':      dict(label="Duration (ms)",     min=30000, max=600000, value=210000, step=1000,  kind="int",     tip="Track length in milliseconds (210000 ≈ 3.5 min)"),
    'time_signature':   dict(label="Time Signature",    min=1,     max=7,      value=4,      step=1,     kind="int",     tip="Beats per bar (most songs = 4)"),
    'chorus_hit':       dict(label="Chorus Hit",        min=0.0,   max=1.0,    value=0.5,    step=0.01,  kind="slider",  tip="Estimated chorus hit score"),
    'sections':         dict(label="Sections",          min=1,     max=30,     value=9,      step=1,     kind="int",     tip="Number of musical sections in the track"),
}

with st.expander("⚙️  Enter Song Features", expanded=False):
    col1, col2, col3 = st.columns(3)
    inputs = {}
    cols_map = [col1, col2, col3]

    for idx, feat in enumerate(CLUSTER_FEATURES):
        cfg = FEAT_CFG[feat]
        col = cols_map[idx % 3]
        with col:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#6a6a6a;text-transform:uppercase;'
                f'letter-spacing:0.1em;margin-bottom:0.1rem;margin-top:0.6rem;">'
                f'{cfg["label"]}'
                f'<span style="font-size:0.65rem;color:#444;margin-left:0.4rem;text-transform:none;letter-spacing:0;">'
                f'— {cfg["tip"]}</span></div>',
                unsafe_allow_html=True
            )
            if cfg['kind'] == "slider":
                inputs[feat] = st.slider(
                    cfg['label'],
                    min_value=float(cfg['min']),
                    max_value=float(cfg['max']),
                    value=float(cfg['value']),
                    step=float(cfg['step']),
                    key=f"pred_{feat}",
                    label_visibility="collapsed"
                )
            else:
                inputs[feat] = st.number_input(
                    cfg['label'],
                    min_value=int(cfg['min']),
                    max_value=int(cfg['max']),
                    value=int(cfg['value']),
                    step=int(cfg['step']),
                    key=f"pred_{feat}",
                    label_visibility="collapsed"
                )

    btn_left, btn_right = st.columns(2)
    with btn_left:
        cluster_btn = st.button("🎵  Predict Cluster", type="primary", use_container_width=True, key="btn_cluster")
    with btn_right:
        hit_btn = st.button("🔥  Predict Hit", type="primary", use_container_width=True, key="btn_hit")

# ── Cluster prediction result ──
if 'btn_cluster' in st.session_state and st.session_state.btn_cluster:
    cluster_input = np.array([[inputs[f] for f in CLUSTER_FEATURES]])
    with st.spinner("Predicting cluster…"):
        cluster_pipeline = load_cluster_model()
    if cluster_pipeline is not None:
        try:
            cluster_id      = int(cluster_pipeline.predict(cluster_input)[0])
            cname, cicon, _ = CLUSTER_MAP.get(cluster_id, ("Unknown", "❓", "gc-steady"))
        except Exception as e:
            cluster_id, cname, cicon = -1, f"Error: {e}", "⚠️"
    else:
        cluster_id, cname, cicon = -1, "Model file not found", "⚠️"

    st.markdown(f"""
    <div class="result-box rb-cluster" style="margin-top:1rem;">
      <div class="rb-label">🎵 Cluster Prediction</div>
      <div class="rb-val">{cicon} {cname}</div>
      <div class="rb-sub">Based on audio DNA • Cluster ID: {cluster_id}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Hit prediction result ──
if 'btn_hit' in st.session_state and st.session_state.btn_hit:
    hit_input = np.array([[inputs[f] for f in HIT_FEATURES]])
    with st.spinner("Analysing audio features…"):
        ann_model, hit_scaler, hit_err = load_hit_model()
    if ann_model is not None:
        try:
            X_scaled  = hit_scaler.transform(hit_input)
            hit_prob  = float(ann_model.predict(X_scaled, verbose=0)[0][0])
            is_hit    = hit_prob >= 0.5
            pct       = int(hit_prob * 100)
            box_cls   = "rb-hit" if is_hit else "rb-miss"
            hit_label = "🔥 Likely a HIT!" if is_hit else "💤 Unlikely to be a hit"
            bar_style = "background:linear-gradient(90deg,#fbbf24,#f59e0b);" if is_hit else "background:#333;"
            st.markdown(
                f'''<div class="result-box {box_cls}" style="margin-top:1rem;">
                  <div class="rb-label">🔥 Hit Prediction</div>
                  <div class="rb-val">{hit_label}</div>
                  <div class="rb-sub">Confidence: {pct}%</div>
                  <div class="prob-bar-track">
                    <div class="prob-bar-fill" style="width:{pct}%;{bar_style}"></div>
                  </div>
                </div>''',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.markdown(
                f'''<div class="result-box rb-miss" style="margin-top:1rem;">
                  <div class="rb-label">🔥 Hit Prediction</div>
                  <div class="rb-val">⚠️ Prediction error</div>
                  <div class="rb-sub">{e}</div>
                </div>''',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'''<div class="result-box rb-miss" style="margin-top:1rem;">
              <div class="rb-label">🔥 Hit Prediction</div>
              <div class="rb-val">⚠️ Model could not be loaded</div>
              <div class="rb-sub">{hit_err}</div>
            </div>''',
            unsafe_allow_html=True
        )

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("""
<br>
<div style="text-align:center;color:#2a2a2a;font-size:0.72rem;font-family:'Circular Std','Circular',system-ui,sans-serif;padding-bottom:1rem;">
  Spotify Universe · ML Audio Clustering Dashboard
</div>
""", unsafe_allow_html=True)