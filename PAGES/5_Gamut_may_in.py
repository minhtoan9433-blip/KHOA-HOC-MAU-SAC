# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import colour
import cs_utils as cs

st.set_page_config(page_title="Gamut máy in", layout="wide")
st.title("5. Gamut màu của máy in (từ file Lab)")

file_tai_len = st.sidebar.file_uploader("Tải file gamut (csv: ColorSpace, C, M, Y, R, G, B)", type=["csv"])
dung_mau = st.sidebar.checkbox("Dùng file mẫu GamutMayIn_CMY_RGB_2.csv", value=file_tai_len is None)
nguon_sang = st.sidebar.radio("White point của số liệu Lab", ("D50", "D65"), index=0)
so_sanh = st.sidebar.checkbox("So sánh với gamut sRGB", value=True)

nguon = file_tai_len if file_tai_len is not None else (cs.DATA / "GamutMayIn_CMY_RGB_2.csv" if dung_mau else None)
if nguon is None:
    st.info("Hãy tải file csv lên hoặc tích chọn dùng file mẫu ở thanh bên.")
    st.stop()

try:
    df = pd.read_csv(nguon).set_index("ColorSpace")
    lab = cs.lab_cac_dinh(df)  # (6,3) theo thứ tự R, Y, G, C, B, M
except Exception as e:  # noqa: BLE001
    st.error(f"File không đúng định dạng (cần cột ColorSpace và các dòng L, a, b; các cột C,M,Y,R,G,B): {e}")
    st.stop()

st.subheader("Dữ liệu Lab của các màu cơ bản")
st.dataframe(df)

_, xy = cs.lab_sang_xyz_xy(lab, nguon_sang)
rgb = cs.lab_sang_srgb(lab, nguon_sang)
nhan = cs.THU_TU_GAMUT
xs = np.append(xy[:, 0], xy[0, 0])
ys = np.append(xy[:, 1], xy[0, 1])

col1, col2 = st.columns(2)
with col1:
    fig, ax = cs.ve_cie1931()
    ax.plot(xs, ys, "k-", lw=2, label="Gamut máy in")
    ax.scatter(xy[:, 0], xy[:, 1], c=rgb, s=90, edgecolors="k", zorder=5)
    for k, (x, y) in zip(nhan, xy):
        ax.annotate(k, (x, y), textcoords="offset points", xytext=(7, 7), fontsize=11)
    if so_sanh:
        p = np.asarray(colour.RGB_COLOURSPACES["sRGB"].primaries, float)
        ax.plot(np.append(p[:, 0], p[0, 0]), np.append(p[:, 1], p[0, 1]), "--", color="tab:red", lw=1.5, label="sRGB")
    ax.legend(loc="upper right")
    st.pyplot(fig, clear_figure=True)
with col2:
    import matplotlib.pyplot as plt

    fig2, ax2 = plt.subplots(figsize=(6.2, 6.2))
    a_, b_ = lab[:, 1], lab[:, 2]
    ax2.plot(np.append(a_, a_[0]), np.append(b_, b_[0]), "k-", lw=2)
    ax2.scatter(a_, b_, c=rgb, s=110, edgecolors="k", zorder=5)
    for k, a, b in zip(nhan, a_, b_):
        ax2.annotate(k, (a, b), textcoords="offset points", xytext=(7, 7), fontsize=11)
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.axvline(0, color="gray", lw=0.8)
    ax2.set_xlim(-100, 100)
    ax2.set_ylim(-100, 100)
    ax2.set_aspect("equal")
    ax2.set_xlabel("a*")
    ax2.set_ylabel("b*")
    ax2.set_title("Gamut máy in trên mặt phẳng a*b*")
    ax2.grid(alpha=0.3)
    st.pyplot(fig2, clear_figure=True)

S_in = cs.dien_tich_da_giac(xy[:, 0], xy[:, 1])
p = np.asarray(colour.RGB_COLOURSPACES["sRGB"].primaries, float)
S_srgb = cs.dien_tich_da_giac(p[:, 0], p[:, 1])
S_ab = cs.dien_tich_da_giac(lab[:, 1], lab[:, 2])
m1, m2, m3 = st.columns(3)
m1.metric("Diện tích gamut máy in (xy)", f"{S_in:.4f}")
m2.metric("So với sRGB", f"{S_in / S_srgb * 100:.0f}%")
m3.metric("Diện tích trên a*b*", f"{S_ab:.0f}")
st.caption("Gamut máy in là đa giác 6 đỉnh R–Y–G–C–B–M (mực chồng); nhỏ hơn nhiều so với tam giác sRGB, đặc biệt ở vùng xanh lục và xanh lam.")
cs.thanh_ben()
