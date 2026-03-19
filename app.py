import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# Configuração da página
st.set_page_config(layout="wide", page_title="Duels Analysis")

st.title("Defensive & Duel Map")
st.caption("Ícones com borda preta e cor forte possuem vídeo. Ícones claros são apenas registro.")

# ==========================
# Data Setup
# ==========================
# Lista de tuplas: (Tipo, X, Y, Video_Path ou None)
eventos_raw = [
    # -------- GAME 1 --------
    ("DUEL LOST", 97.90, 74.74, None),
    ("DUEL WON", 58.01, 70.09, "videos/video1.mp4"), # Exemplo com vídeo
    ("DUEL WON", 61.66, 26.54, None),
    ("DUEL WON", 49.03, 57.12, None),
    ("DUEL WON", 93.25, 60.11, "videos/video2.mp4"), # Exemplo com vídeo
    ("DUEL WON", 104.22, 66.60, None),
    ("DUEL WON", 107.71, 77.74, None),
    ("DUEL LOST", 62.33, 66.93, None),
    ("DUEL WON", 86.10, 40.17, None),
    ("DUEL LOST", 85.60, 66.43, None),
    ("DUEL WON", 78.62, 42.33, None),
    ("DUEL WON", 74.63, 33.85, None),
    ("DUEL LOST", 85.60, 51.64, None),
    ("DUEL LOST", 108.21, 25.54, None),
    ("DUEL WON", 59.50, 45.65, None),
    ("DUEL LOST", 98.07, 37.67, None),
    ("AERIAL WON", 71.97, 22.71, None),
    ("DUEL LOST", 38.89, 16.56, None),
    ("DUEL WON", 78.78, 29.19, None),

    # -------- GAME 2 --------
    ("DUEL LOST", 97.57, 73.41, None),
    ("DUEL WON", 100.23, 74.08, None),
    ("DUEL LOST", 89.09, 75.24, None),
    ("DUEL WON", 94.74, 75.08, None),
    ("DUEL WON", 63.66, 21.38, None),
    ("DUEL LOST", 81.94, 63.11, None),
    ("FOULED", 39.55, 39.67, "videos/video3.mp4"), # Exemplo com vídeo
    ("DUEL LOST", 51.02, 40.00, None),
    ("DUEL WON", 99.90, 28.86, None),
    ("AERIAL WON", 111.86, 54.79, None),
    ("DUEL LOST", 89.26, 56.79, None),
    ("AERIAL WON", 98.90, 31.69, None),
    ("AERIAL WON", 65.65, 27.70, None),
    ("AERIAL LOST", 66.32, 4.76, None),
    ("FOULED", 60.17, 54.46, None),
    ("DUEL WON", 59.67, 44.32, None),
    ("DUEL LOST", 85.93, 75.24, None),
    ("AERIAL WON", 109.70, 1.10, None),
    ("DUEL LOST", 48.70, 2.93, None),
    ("DUEL WON", 59.00, 21.05, None),
    ("DUEL LOST", 92.08, 61.61, None),
    ("DUEL WON", 109.54, 44.16, None),
    ("DUEL LOST", 77.45, 3.93, None),
]

df = pd.DataFrame(eventos_raw, columns=["type", "x", "y", "video"])

def get_style(event_type, has_video):
    # Cores base (RGBA)
    colors = {
        "DUEL LOST": (1, 0, 0),        # Vermelho
        "DUEL WON": (0, 0.6, 0),       # Verde
        "AERIAL WON": (0.2, 0.3, 1),   # Azul
        "AERIAL LOST": (0.8, 0, 0.8),  # Roxo
        "FOULED": (1, 0.6, 0),         # Laranja
        "INTERCEPTION": (0.3, 0.3, 0.3) # Cinza
    }
    
    # Marcadores
    markers = {
        "DUEL LOST": 'x',
        "DUEL WON": 'o',
        "AERIAL WON": '^',
        "AERIAL LOST": 'v',
        "FOULED": 's',
        "INTERCEPTION": 'D'
    }

    base_color = colors.get(event_type, (0, 0, 0))
    marker = markers.get(event_type, 'o')
    
    if has_video:
        # Cor forte, opacidade total, borda preta
        return marker, (*base_color, 1.0), 120, 1.5, 'black'
    else:
        # Cor lavada, semi-transparente, sem borda destacada
        return marker, (*base_color, 0.3), 80, 0.5, (*base_color, 0.3)

# ==========================
# Layout
# ==========================
col1, col2 = st.columns([1, 1])

with col1:
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f5f5f5', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 8))
    
    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        marker, color, size, lw, ec = get_style(row["type"], has_vid)
        
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=3 if has_vid else 2)

    ax.set_title("Mapa de Duelos e Ações Defensivas", fontsize=16, pad=20)

    # Legenda Customizada
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Duel Won', markerfacecolor=(0, 0.6, 0, 1), markersize=10),
        Line2D([0], [0], marker='x', color='red', label='Duel Lost', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='^', color='w', label='Aerial Won', markerfacecolor=(0.2, 0.3, 1, 1), markersize=10),
        Line2D([0], [0], marker='v', color='w', label='Aerial Lost', markerfacecolor=(0.8, 0, 0.8, 1), markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Fouled', markerfacecolor=(1, 0.6, 0, 1), markersize=10),
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), 
              frameon=True, fontsize='small', edgecolor='black', facecolor='white')

    # Renderização para clique
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    buf.seek(0)
    image = Image.open(buf)
    
    click = streamlit_image_coordinates(image, width=800)

# ==========================
# Lógica de Seleção
# ==========================
selected_event = None

if click is not None:
    real_w, real_h = image.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Busca o evento mais próximo dentro de um raio
    RADIUS = 4 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        # Prioriza o mais próximo que TENHA vídeo, se houver
        with_video = candidates[candidates["video"].notnull()]
        if not with_video.empty:
            selected_event = with_video.loc[with_video["dist"].idxmin()]
        else:
            selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video Player (Direita)
# ==========================
with col2:
    st.subheader("Análise de Vídeo")
    if selected_event is not None:
        st.info(f"**Evento Selecionado:** {selected_event['type']}")
        
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error("Arquivo de vídeo não encontrado no caminho especificado.")
        else:
            st.warning("Este evento não possui vídeo disponível.")
    else:
        st.write("---")
        st.info("Clique em um ícone no mapa para carregar o vídeo correspondente.")
        st.write("Apenas ícones com contorno preto possuem vídeos vinculados.")
