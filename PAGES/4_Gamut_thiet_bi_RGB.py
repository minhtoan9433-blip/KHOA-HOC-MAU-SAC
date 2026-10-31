# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import colour
import cs_utils as cs

st.set_page_config(page_title="Gamut thiết bị RGB", layout="wide")
st.title("4. Gamut màu của thiết bị RGB")

CAC_KGM = ["sRGB", "Adobe RGB (1998)", "Display P3", "ITU-R BT.2020"]
MAU_VE = {"sRGB": "k", "Adobe RGB (1998)": "tab:blue", "Display P3": "tab:green", "ITU-R BT.2020": "tab:red"}

chon = st.sidebar.multiselect("Không gian màu RGB", CAC_KGM, default=["sRGB"])
if not chon:
    st.info("Chọn ít nhất một không gian màu ở thanh bên.")
    st.stop()

col1, col2 = st.columns([3, 2])
with col1:
    fig, ax = cs.ve_cie1931()
    hang = []
    S_srgb = None
    for ten in chon:
        kgm = colour.RGB_COLOURSPACES[ten]
        xy = np.asarray(kgm.primaries, float)  # [R, G, B]
        xs = np.append(xy[:, 0], xy[0, 0])
        ys = np.append(xy[:, 1], xy[0, 1])
        ax.plot(xs, ys, "-o", color=MAU_VE[ten], lw=2, ms=4, label=ten)
        if ten == "sRGB":
            for nhan, (x, y) in zip("RGB", xy):
                ax.annotate(nhan, (x, y), textcoords="offset points", xytext=(6, 6), fontsize=11)
        S = cs.dien_tich_da_giac(xy[:, 0], xy[:, 1])
        hang.append(
            {
                "Không gian màu": ten,
                "R (x, y)": f"({xy[0,0]:.3f}, {xy[0,1]:.3f})",
                "G (x, y)": f"({xy[1,0]:.3f}, {xy[1,1]:.3f})",
                "B (x, y)": f"({xy[2,0]:.3f}, {xy[2,1]:.3f})",
                "Diện tích (xy)": round(S, 4),
            }
        )
    ax.legend(loc="upper right")
    st.pyplot(fig, clear_figure=True)

with col2:
    st.subheader("Toạ độ sắc độ các primaries")
    df = pd.DataFrame(hang)
    S_ref = cs.dien_tich_da_giac(*np.asarray(colour.RGB_COLOURSPACES["sRGB"].primaries, float).T)
    df["So với sRGB"] = (df["Diện tích (xy)"] / S_ref).map(lambda v: f"{v*100:.0f}%")
    st.dataframe(df.set_index("Không gian màu"))

    with st.expander("Kiểm chứng sRGB bằng sRGB_to_XYZ (cách làm của thầy)"):
        ket_qua = {}
        for nhan, rgb in (("R", [1, 0, 0]), ("G", [0, 1, 0]), ("B", [0, 0, 1])):
            xy = colour.XYZ_to_xy(colour.sRGB_to_XYZ(np.array(rgb, float)))
            ket_qua[nhan] = (round(float(xy[0]), 4), round(float(xy[1]), 4))
        st.write(ket_qua)
        st.caption("Cho ra cùng toạ độ với primaries chuẩn của sRGB: R(0.64, 0.33), G(0.30, 0.60), B(0.15, 0.06).")

st.caption("Gamut của thiết bị RGB là tam giác nối 3 primaries R, G, B trên biểu đồ xy.")
cs.thanh_ben()
