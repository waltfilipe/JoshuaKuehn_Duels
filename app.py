import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# ==========================
# Page Configuration
# ==========================
st.set_page_config(layout="wide", page_title="Duel Map Analysis")

st.title("Duel Map Analysis")
st.caption("Click on the icons on the pitch to play the corresponding video analysis.")

# ==========================
# Data Setup (All English labels)
# ==========================
events_raw = [
    # -------- GAME 1 --------
    ("DUEL LOST", 97.90, 74.74, None), 
    ("DUEL WON", 58.01, 70.09, "videos/Duel Won 1.mp4"),
    ("DUEL WON", 61.66, 26.54, None), 
    ("DUEL WON", 49.03, 57.12, None),
    ("DUEL WON", 93.25, 60.11, None), 
    ("DUEL WON", 104.22, 66.60, None),
    ("DUEL WON", 107.71, 77.74, None), 
    ("DUEL LOST", 62.33, 66.93, None),
    ("DUEL WON", 86.10, 40.17, None), 
    ("DUEL LOST", 85.60, 66.43, None),
    ("DUEL WON", 78.62, 42.33, "videos/Duel Lost 1 low.mp4"), 
    ("DUEL WON", 74.63, 33.85, "videos/Duel Lost 1 low.mp4"),
    ("DUEL LOST", 85.60, 51.64, "videos/Duel Lost 1 low.mp4"), 
    ("DUEL LOST", 108.21, 25.54, None),
    ("DUEL WON", 59.50, 45.65, None), 
    ("DUEL LOST", 98.07, 37.67, "videos/Duel Lost 2.mp4"),
    ("AERIAL WON", 71.97, 22.71, "videos/Duelo Aereo 1.mp4"), 
    ("DUEL LOST", 38.89, 16.56, "videos/Duel Lost 3.mp4"),
    ("DUEL WON", 78.78, 29.19, None),
    # -------- GAME 2 --------
    ("DUEL LOST", 97.57, 73.41, None), 
    ("DUEL WON", 100.23, 74.08, None),
    ("DUEL LOST", 89.09, 75.24, "videos/Duel Lost 4.mp4"), 
    ("DUEL WON", 94.74, 75.08, "videos/Duel Won 2.mp4"),
    ("DUEL WON", 63.66, 21.38, None), 
    ("DUEL LOST", 81.94, 63.11, "videos/Duel Lost 5.mp4"),
    ("FOULED", 39.55, 39.67, None), 
    ("DUEL LOST", 51.02, 40.00, "videos/Duel Lost 6.mp4"),
    ("DUEL WON", 99.90, 28.86, None), 
    ("AERIAL WON", 111.86, 54.79, "videos/Duelo Aéreo 2.mp4"),
    ("DUEL LOST", 89.26, 56.79, None), 
    ("AERIAL WON", 98.90, 31.69, "videos/Duelo Aereo 3.mp4"),
    ("AERIAL WON", 65.65, 27.70, "videos/Duelo Aereo 4.mp4"), 
    ("AERIAL LOST", 66.32, 4.76, "videos/Duelo Aereo 5.mp4"),
    ("FOULED", 60.17, 54.46, None), 
    ("DUEL WON", 59.67, 44.32, None),
    ("DUEL LOST", 85.93, 75.24, None), 
    ("AERIAL WON", 109.70, 46.16, "videos/Duelo Aereo 6.mp4"),
    ("DUEL LOST", 48.70, 2.93, None), 
    ("DUEL WON", 59.00, 21.05, "videos/Duel Won 3.mp4"),
    ("DUEL LOST", 92.08, 61.61, None), 
    ("DUEL WON", 109.54, 44.16, None),
    ("DUEL LOST", 77.45, 3.93, None),
]

df = pd.DataFrame(events_raw, columns=["type", "x", "y", "video"])

def get_style(event_type, has_video):
    event_type = event_type.upper() # Garante que a comparação ignore maiúsculas/minúsculas
    
    # 1. DUELOS AÉREOS (Prioritário)
    if "AERIAL" in event_type or "AIR" in event_type:
        if "WON" in event_type:
            # Triângulo para cima (Verde limão brilhante)
            return '^', (0.2, 0.9, 0.2, 0.9), 110, 1.2
        if "LOST" in event_type:
            # Triângulo para baixo (Vermelho escuro)
            alpha = 0.9 if has_video else 0.15
            return 'v', (0.7, 0, 0, alpha), 110, 1.2

    # 2. DUELOS TERRESTRES / OUTROS
    if "WON" in event_type: 
        return 'o', (0, 0.6, 0, 0.8), 90, 0.5
    
    if "LOST" in event_type: 
        alpha = 0.9 if has_video else 0.15
        return 'x', (0.9, 0, 0, alpha), 100, 2.5 # Aumentei um pouco o tamanho do 'x'
    
    if "FOULED" in event_type: 
        return 's', (1, 0.5, 0, 0.8), 90, 0.5
        
    return 'o', (0.5, 0.5, 0.5, 0.8), 90, 0.5

# ==========================
# Main Layout
# ==========================
col_map, col_vid = st.columns([1, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(8, 6))
    
    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        marker, color, size, lw = get_style(row["type"], has_vid)
        # Black border for events that contain video
        ec = 'black' if has_vid else color
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=3)
    # Attack Arrow
    ax.annotate('', xy=(70, 83), xytext=(50, 83),
        arrowprops=dict(arrowstyle='->', color='#4a4a4a', lw=1.2))
    ax.text(60, 86, "Attack Direction", ha='center', va='center', 
        fontsize=8, color='#4a4a4a', fontweight='bold')
    # Legend
    legend_elements = [
    # --- Seção de Duelos Terrestres ---
    Line2D([0], [0], marker='o', color='w', label='Duel Won', 
           markerfacecolor=(0, 0.6, 0, 0.8), markersize=10, linestyle='None'),
    
    Line2D([0], [0], marker='x', color='w', label='Duel Lost', 
           markeredgecolor=(0.9, 0, 0, 0.8), markersize=10, markeredgewidth=2, linestyle='None'),

    # --- Seção de Duelos Aéreos ---
    Line2D([0], [0], marker='^', color='w', label='Aerial Won', 
           markerfacecolor=(0.2, 0.9, 0.2, 0.9), markersize=10, linestyle='None'),
    
    Line2D([0], [0], marker='v', color='w', label='Aerial Lost', 
           markerfacecolor=(0.7, 0, 0, 0.8), markersize=10, linestyle='None'),

    # --- Outros ---
    Line2D([0], [0], marker='s', color='w', label='Fouled', 
           markerfacecolor=(1, 0.5, 0, 0.8), markersize=10, linestyle='None'),
    
    # Indicador de vídeo (Apenas borda branca para destacar no fundo preto se necessário, 
    # ou borda preta se estiver dentro do box branco)
    Line2D([0], [0], marker='o', color='w', label='Has Video (High Opacity)', 
           markerfacecolor='none', markeredgecolor='black', markersize=10, linestyle='None'),
]

    # Aplicando a legenda ao gráfico
    legend = ax.legend(
        handles=legend_elements, 
        loc='upper left', 
        bbox_to_anchor=(0.01, 0.99), 
        frameon=True, 
        facecolor='white',      # Fundo branco para contraste
        edgecolor='#333333',    # Borda cinza escuro discreta
        fontsize='small',
        title="Match Events",   # Título da legenda
        title_fontsize='medium',
        labelspacing=1.0,       # Espaço vertical entre itens
        borderpad=1.0           # Espaço entre o texto e a borda do box
    )
    
    # Deixar o título da legenda em negrito
    legend.get_title().set_fontweight('bold')

    # Convert plot to image for coordinate tracking
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Use fixed width to ensure coordinate scaling works
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# Interaction Logic
# ==========================
selected_event = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    # Map pixel click to actual image pixels
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Invert Y for Matplotlib logic and transform to pitch data coordinates
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calculate distance to markers
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Radius threshold for easier selection
    RADIUS = 5 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video Display & Stats
# ==========================
with col_vid:
    st.subheader("Video Analysis")
    if selected_event is not None:
        st.success(f"**Selected Event:** {selected_event['type']} at [X: {selected_event['x']}, Y: {selected_event['y']}]")
        
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error(f"Video file not found: {selected_event['video']}")
        else:
            st.warning("No video footage available for this specific event.")
    else:
        st.info("Select a marker on the pitch to load the video analysis.")

    st.divider()
    st.subheader("Performance by Zone")
    
    # Zone Logic (Statsbomb: Y goes from 0 to 80)
    # Central Corridor: 26.6 to 53.3 | Lateral: 0-26.6 and 53.3-80
    df['is_duel'] = df['type'].str.contains('DUEL|AERIAL')
    df['is_won'] = df['type'].str.contains('WON')
    
    central_mask = (df['y'] > 26.6) & (df['y'] < 53.3)
    
    # Central Stats
    central_df = df[central_mask & df['is_duel']]
    c_total = len(central_df)
    c_wins = central_df['is_won'].sum()
    c_rate = (c_wins / c_total * 100) if c_total > 0 else 0
    
    # Lateral Stats
    lateral_df = df[~central_mask & df['is_duel']]
    l_total = len(lateral_df)
    l_wins = lateral_df['is_won'].sum()
    l_rate = (l_wins / l_total * 100) if l_total > 0 else 0

    s_col1, s_col2 = st.columns(2)
    s_col1.metric("Central Zone", f"{c_wins}/{c_total}", f"{c_rate:.1f}% Success")
    s_col2.metric("Lateral Zones", f"{l_wins}/{l_total}", f"{l_rate:.1f}% Success")
