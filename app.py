import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# Page configuration
st.set_page_config(layout="wide", page_title="Duel Map Analysis")

st.title("Duel Map")
st.caption("Icons with a black border contain video footage. Click to play.")

# ==========================
# Data Setup
# ==========================
# (Type, X, Y, Video_Path or None)
events_raw = [
    # -------- GAME 1 --------
    ("DUEL LOST", 97.90, 74.74, None),
    ("DUEL WON", 58.01, 70.09, "videos/sample1.mp4"), # Example with video
    ("DUEL WON", 61.66, 26.54, None),
    ("DUEL WON", 49.03, 57.12, None),
    ("DUEL WON", 93.25, 60.11, "videos/sample2.mp4"), # Example with video
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
    ("FOULED", 39.55, 39.67, "videos/sample3.mp4"), # Example with video
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

df = pd.DataFrame(events_raw, columns=["type", "x", "y", "video"])

def get_style(event_type, has_video):
    colors = {
        "DUEL LOST": (0.9, 0, 0),       # Red
        "DUEL WON": (0, 0.6, 0),        # Green
        "AERIAL WON": (0.1, 0.4, 0.9),  # Blue
        "AERIAL LOST": (0.7, 0, 0.7),   # Purple
        "FOULED": (1, 0.5, 0),          # Orange
    }
    markers = {
        "DUEL LOST": 'x',
        "DUEL WON": 'o',
        "AERIAL WON": '^',
        "AERIAL LOST": 'v',
        "FOULED": 's',
    }

    base_color = colors.get(event_type, (0, 0, 0))
    marker = markers.get(event_type, 'o')
    
    # Linewidth for X markers (Duel Lost)
    lw = 3.5 if marker == 'x' else 1.0
    
    if has_video:
        # Brighter, full opacity, black border
        return marker, (*base_color, 1.0), 110, lw, 'black'
    else:
        # Slightly dimmer, no distinct border
        return marker, (*base_color, 0.6), 80, lw, (*base_color, 0.1)

# ==========================
# Visualization
# ==========================
col1, col2 = st.columns([1.2, 1])

with col1:
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 8))
    
    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        marker, color, size, lw, ec = get_style(row["type"], has_vid)
        
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=3 if has_vid else 2)

    # Attack Direction (Bottom)
    ax.annotate('', xy=(80, 84), xytext=(40, 84),
                arrowprops=dict(arrowstyle='->', color
