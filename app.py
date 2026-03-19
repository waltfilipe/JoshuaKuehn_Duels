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
st.caption("Markers with a **thick black border** contain video footage. Click them to play.")

# ==========================
# Data Setup
# ==========================
events_raw = [
    ("DUEL LOST", 97.90, 74.74, None), ("DUEL WON", 58.01, 70.09, "videos/Duel Won 1.mp4"),
    ("DUEL WON", 61.66, 26.54, None), ("DUEL WON", 49.03, 57.12, None),
    ("DUEL WON", 93.25, 60.11, None), ("DUEL WON", 104.22, 66.60, None),
    ("DUEL WON", 107.71, 77.74, None), ("DUEL LOST", 62.33, 66.93, None),
    ("DUEL WON", 86.10, 40.17, None), ("DUEL LOST", 85.60, 66.43, None),
    ("DUEL WON", 78.62, 42.33, "videos/Duel Lost 1 low.mp4"), ("DUEL WON", 74.63, 33.85, "videos/Duel Lost 1 low.mp4"),
    ("DUEL LOST", 85.60, 51.64, "videos/Duel Lost 1 low.mp4"), ("DUEL LOST", 108.21, 25.54, None),
    ("DUEL WON", 59.50, 45.65, None), ("DUEL LOST", 98.07, 37.67, "videos/Duel Lost 2.mp4"),
    ("AERIAL WON", 71.97, 22.71, None), ("DUEL LOST", 38.89, 16.56, "videos/Duel Lost 3.mp4"),
    ("DUEL WON", 78.78, 29.19, None),
    ("DUEL LOST", 97.57, 73.41, None), ("DUEL WON", 100.23, 74.08, None),
    ("DUEL LOST", 89.09, 75.24, "videos/Duel Lost 4.mp4"), ("DUEL WON", 94.74, 75.08, "videos/Duel Won 2.mp4"),
    ("DUEL WON", 63.66, 21.38, None), ("DUEL LOST", 81.94, 63.11, "videos/Duel Lost 5.mp4"),
    ("FOULED", 39.55, 39.67, None), ("DUEL LOST", 51.02, 40.00, "videos/Duel Lost 6.mp4"),
    ("DUEL WON", 99.90, 28.86, None), ("AERIAL WON", 111.86, 54.79, None),
    ("DUEL LOST", 89.26, 56.79, None), ("AERIAL WON", 98.90, 31.69, None),
    ("AERIAL WON", 65.65, 27.70, None), ("AERIAL LOST", 66.32, 4.76, None),
    ("FOULED", 60.17, 54.46, None), ("DUEL WON", 59.67, 44.32, None),
    ("DUEL LOST", 85.93, 75.24, None), ("AERIAL WON", 109.70, 1.10, None),
    ("DUEL LOST", 48.70, 2.93, None), ("DUEL WON", 59.00, 21.05, "videos/Duel Won 3.mp4"),
    ("DUEL LOST", 92.08, 61.61, None), ("DUEL WON", 109.54, 44.16, None),
    ("DUEL LOST", 77.45, 3.93, None),
]

df = pd.DataFrame(events_raw, columns=["type", "x", "y", "video"])

# Stats helper columns
df["zone"] = df["y"].apply(lambda y: "CENTRAL" if 26.6 < y <= 53.3 else "WIDE")
df["is_duel"] = df["type"].str.contains("DUEL|AERIAL")
df["won"] = df["type"].str.contains("WON")

# ==========================
# Main Layout
# ==========================
col_map, col_vid = st.columns([1.2, 1])

with col_map:
    st.subheader("Interactive Pitch")
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#f8f8f8', line_color='#4a4a4a')
    fig, ax = pitch.draw(figsize=(10, 8))
    
    for _, row in df.iterrows():
        has_vid = row["video"] is not None
        
        # Style Logic
        color = (0, 0.6, 0) if "WON" in row["type"] else (0.9, 0, 0) if "LOST" in row["type"] else (1, 0.5, 0)
        marker = 'x' if "LOST" in row["type"] else 's' if "FOULED" in row["type"] else 'o'
        
        if has_vid:
            alpha, size, lw, ec = 1.0, 130, 3.5, 'black' # Clear, big, black border
        else:
            alpha, size, lw, ec = 0.2, 70, 1.0, (*color, 0.2) # Faded, small, no border
            
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=(*color, alpha), 
                      edgecolors=ec, linewidths=lw, ax=ax, zorder=4 if has_vid else 2)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Won', markerfacecolor=(0, 0.6, 0, 0.8), markersize=9),
        Line2D([0], [0], marker='x', color=(0.9, 0, 0, 0.8), label='Lost', markersize=9, markeredgewidth=2),
        Line2D([0], [0], marker='o', color='w', label='Video Clip', markerfacecolor='none', markeredgecolor='black', markeredgewidth=2, markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.01, 0.99), frameon=True, fontsize='small')

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches='tight')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # FIXED WIDTH is key for coordinate consistency
    click = streamlit_image_coordinates(img_obj, width=800)

# ==========================
# Interaction & Coordinate Logic
# ==========================
selected_event = None
if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Map pixel to Pitch Data
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calculate distance to markers
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Tolerance radius
    RADIUS = 5 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        # Prioritize markers with videos if click is near multiple
        vids = candidates[candidates["video"].notnull()]
        selected_event = vids.loc[vids["dist"].idxmin()] if not vids.empty else candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video & Statistics (Right Side)
# ==========================
with col_vid:
    st.subheader("Video Analysis")
    if selected_event is not None:
        st.success(f"**Type:** {selected_event['type']}")
        if selected_event["video"]:
            try:
                # Force video display
                st.video(selected_event["video"])
            except Exception as e:
                st.error(f"Error loading file: {selected_event['video']}")
        else:
            st.warning("No video for this event.")
    else:
        st.info("Click a marker with a **black border** to watch the video.")

    st.write("---")
    st.subheader("Duel Stats by Zone")
    
    s1, s2 = st.columns(2)
    for zone, col in zip(["CENTRAL", "WIDE"], [s1, s2]):
        subset = df[(df["zone"] == zone) & (df["is_duel"])]
        total = len(subset)
        won = subset["won"].sum()
        pct = (won / total * 100) if total > 0 else 0
        col.metric(f"{zone} ZONES", f"{int(won)}/{total}", f"{pct:.1f}% Success")
