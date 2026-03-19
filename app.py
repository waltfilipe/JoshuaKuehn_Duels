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
st.set_page_config(layout="wide", page_title="Duel Map Analysis")

st.title("Duel Map")
st.caption("Ícones com borda preta possuem vídeo. Clique para reproduzir.")

# ==========================
# Dados
# ==========================
events_raw = [
    ("DUEL LOST", 97.90, 74.74, None), ("DUEL WON", 58.01, 70.09, "videos/Duel Won 1.mp4"),
    ("DUEL WON", 61.66, 26.54, None), ("DUEL WON", 49.03, 57.12, None),
    ("DUEL WON", 93.25, 60.11, None), ("DUEL WON", 104.22, 66.60, None),
    ("DUEL WON", 107.71, 77.74, None), ("DUEL LOST", 62.33, 66.93, None),
    ("DUEL WON", 86.10, 40.17, None), ("DUEL LOST", 85.60, 66.43, None),
    ("DUEL WON", 78.62, 42.33, "videos/Duel Lost 1 low.mp4"), ("DUEL WON", 74.63, 33.85, "videos/Duel Lost 1 low.mp4"),
    ("DUEL LOST", 85.60, 51.64, "videos/Duel Lost 1 low.mp4"), ("DUEL LOST", 108.21, 25.54, None),
    ("DUEL WON", 59.50, 45.65, None), ("DUEL LOST", 98.07, 37.67, None),
    ("AERIAL WON", 71.97, 22.71, None), ("DUEL LOST", 38.89, 16.56, None),
    ("DUEL WON", 78.78, 29.19, None),
    ("DUEL LOST", 97.57, 73.41, None), ("DUEL WON", 100.23, 74.08, None),
    ("DUEL LOST", 89.09, 75.24, None), ("DUEL WON", 94.74, 75.08, "videos/Duel Won 2"),
    ("DUEL WON", 63.66, 21.38, None), ("DUEL LOST", 81.94, 63.11, None),
    ("FOULED", 39.55, 39.67, None), ("DUEL LOST", 51.02, 40.00, None),
    ("DUEL WON", 99.90, 28.86, None), ("AERIAL WON", 111.86, 54.79, None),
    ("DUEL LOST", 89.26, 56.79, None), ("AERIAL WON", 98.90, 31.69, None),
    ("AERIAL WON", 65.65, 27.70, None), ("AERIAL LOST", 66.32, 4.76, None),
    ("FOULED", 60.17, 54.46, None), ("DUEL WON", 59.67, 44.32, None),
    ("DUEL LOST", 85.93, 75.24, None), ("AERIAL WON", 109.70, 1.10, None),
    ("DUEL LOST", 48.70, 2.93, None), ("DUEL WON", 59.00, 21.05, "videos/Duel Won 3"),
    ("DUEL LOST", 92.08, 61.61, None), ("DUEL WON", 109.54, 44.16, None),
    ("DUEL LOST", 77.45, 3.93, None),
]

df = pd.DataFrame(events_raw, columns=["type", "x", "y", "video"])

# Lógica de Zonas
df["zone"] = df["y"].apply(lambda y: "CENTRAL" if 26.6 < y <= 53.3 else "WIDE")
df["is_duel"] = df["type"].isin(["DUEL WON", "DUEL LOST", "AERIAL WON", "AERIAL LOST"])
df["won"] = df["type"].isin(["DUEL WON", "AERIAL WON"])

def get_style(event_type, has_video):
    colors = {"DUEL LOST": (0.9, 0, 0), "DUEL WON": (0, 0.6, 0), "AERIAL WON": (0.1, 0.4, 0.9), "AERIAL LOST": (0.7, 0, 0.7), "FOULED": (1, 0.5, 0)}
    markers = {"DUEL LOST": 'x', "DUEL WON": 'o', "AERIAL WON": '^', "AERIAL LOST": 'v', "FOULED": 's'}
    
    base_color = colors.get(event_type, (0, 0, 0))
    marker = markers.get(event_type, 'o')
    lw = 3.0 if marker == 'x' else 1.0
    ec = 'black' if has_video else base_color
    alpha = 1.0 if has_video else 0.6
    
    return marker, (*base_color, alpha), 100, lw, ec

# ==========================
# Layout Principal
# ==========================
col1, col2 = st.columns([1.2, 1])

with col1:
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 8))
    
    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        marker, color, size, lw, ec = get_style(row["type"], has_vid)
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=3)

    # Direção de Ataque
    ax.annotate('', xy=(80, 84), xytext=(40, 84),
                arrowprops=dict(arrowstyle='->', color='#4a4a4a', lw=1.5), clip_on=False)
    ax.text(60, 87, "DIREÇÃO DE ATAQUE", ha='center', va='center', 
            fontsize=9, color='#4a4a4a', fontweight='bold')

    # Legenda Compacta
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Ganhou', markerfacecolor=(0, 0.6, 0), markersize=8),
        Line2D([0], [0], marker='x', color=(0.9, 0, 0), label='Perdeu', markersize=8, markeredgewidth=2),
        Line2D([0], [0], marker='^', color='w', label='Aéreo Ganho', markerfacecolor=(0.1, 0.4, 0.9), markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Sofrida', markerfacecolor=(1, 0.5, 0), markersize=8),
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.01, 0.99), frameon=True, fontsize='x-small')

    # Renderização da Imagem para clique
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches='tight')
    buf.seek(0)
    image = Image.open(buf)
    
    # O componente de clique
    click = streamlit_image_coordinates(image, width=800)

# ==========================
# Lógica de Interação (Fora das colunas para processar antes do vídeo)
# ==========================
selected_event = None
if click is not None:
    real_w, real_h = image.size
    disp_w, disp_h = click["width"], click["height"]
    
    # Escalar coordenadas de pixels
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Inverter eixo Y para o Matplotlib e converter para dados do campo
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calcular distância e encontrar o evento mais próximo
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Raio de busca (ajustável)
    RADIUS = 4 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        # Se houver vários perto, prioriza o mais perto de fato
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Coluna de Vídeo e Estatísticas
# ==========================
with col2:
    st.subheader("Análise de Vídeo")
    if selected_event is not None:
        st.success(f"**Evento Selecionado:** {selected_event['type']}")
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error("Arquivo de vídeo não encontrado.")
        else:
            st.warning("Não há vídeo disponível para este evento.")
    else:
        st.info("Clique em um ícone no mapa para ver os detalhes.")

    st.write("---")
    st.subheader("Estatísticas por Zona")
    
    stat_col1, stat_col2 = st.columns(2)
    for zone, col in zip(["CENTRAL", "WIDE"], [stat_col1, stat_col2]):
        subset = df[(df["zone"] == zone) & (df["is_duel"])]
        total = len(subset)
        won = subset["won"].sum()
        pct = (won / total * 100) if total > 0 else 0
        col.metric(label=f"ZONA {zone}", value=f"{won}/{total}", delta=f"{pct:.1f}% Sucesso")
