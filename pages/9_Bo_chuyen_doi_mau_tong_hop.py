# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import colour
import cs_utils as cs

st.set_page_config(page_title="Bộ chuyển đổi màu", layout="wide")
st.title("9. Bộ chuyển đổi màu tổng hợp")

c1, c2 = st.columns([1, 2])
with c1:
    hex_mau = st.color_picker("Chọn một màu", "#2E86C1")
    st.markdown(cs.o_mau(*[int(hex_mau[i:i + 2], 16) for i in (1, 3, 5)], 140), unsafe_allow_html=True)

rgb255 = np.array([int(hex_mau[i:i + 2], 16) for i in (1, 3, 5)], float)
rgb01 = rgb255 / 255.0
wp = cs.xy_nguon_sang("D65")

XYZ = colour.sRGB_to_XYZ(rgb01)
xy = colour.XYZ_to_xy(XYZ)
Lab = colour.XYZ_to_Lab(XYZ, illuminant=wp)
LCh = colour.Lab_to_LCHab(Lab)
lin = np.where(rgb01 <= 0.04045, rgb01 / 12.92, ((rgb01 + 0.055) / 1.055) ** 2.4)

with c2:
    bang = pd.DataFrame(
        [
            ("HEX", hex_mau.upper()),
            ("sRGB (0–255)", f"{rgb255[0]:.0f}, {rgb255[1]:.0f}, {rgb255[2]:.0f}"),
            ("RGB tuyến tính (0–1)", f"{lin[0]:.4f}, {lin[1]:.4f}, {lin[2]:.4f}"),
            ("CIE XYZ (D65, Y trắng = 100)", f"{XYZ[0]*100:.2f}, {XYZ[1]*100:.2f}, {XYZ[2]*100:.2f}"),
            ("CIE xyY", f"{xy[0]:.4f}, {xy[1]:.4f}, {XYZ[1]:.4f}"),
            ("CIELab (D65)", f"{Lab[0]:.2f}, {Lab[1]:.2f}, {Lab[2]:.2f}"),
            ("CIELCh(ab)", f"{LCh[0]:.2f}, {LCh[1]:.2f}, {LCh[2]:.1f}°"),
        ],
        columns=["Không gian màu", "Giá trị"],
    ).set_index("Không gian màu")
    st.table(bang)

fig, ax = cs.ve_cie1931(kich_thuoc=(5.5, 5.5))
ax.scatter([xy[0]], [xy[1]], c=[rgb01], s=160, edgecolors="k", linewidths=1.5, zorder=6)
ax.annotate("Màu đã chọn", (xy[0], xy[1]), textcoords="offset points", xytext=(10, 10))
st.pyplot(fig, clear_figure=True)
cs.thanh_ben()
