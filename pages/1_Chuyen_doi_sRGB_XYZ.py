# -*- coding: utf-8 -*-
import numpy as np
import streamlit as st
import colour
import cs_utils as cs

st.set_page_config(page_title="sRGB ⇄ XYZ", layout="wide")
st.title("1. Chuyển đổi không gian màu sRGB ⇄ XYZ")

chon = st.sidebar.radio("Chiều chuyển đổi", ("sRGB to XYZ", "XYZ to sRGB"))
col1, col2 = st.columns(2)

if chon == "sRGB to XYZ":
    with col1:
        st.subheader("sRGB → XYZ")
        R = st.number_input("Nhập R (0–255)", min_value=0, max_value=255, value=255, step=1)
        G = st.number_input("Nhập G (0–255)", min_value=0, max_value=255, value=128, step=1)
        B = st.number_input("Nhập B (0–255)", min_value=0, max_value=255, value=0, step=1)

        rgb = np.array([R, G, B], dtype=float) / 255.0
        XYZ = colour.sRGB_to_XYZ(rgb) * 100  # nguồn sáng D65, Y của trắng = 100
        xy = colour.XYZ_to_xy(XYZ / 100)
        st.markdown(f"### X = {XYZ[0]:.2f},  Y = {XYZ[1]:.2f},  Z = {XYZ[2]:.2f}")
        st.write(f"Toạ độ sắc độ: x = {xy[0]:.4f}, y = {xy[1]:.4f}")
    with col2:
        st.subheader("Màu đã nhập")
        st.markdown(cs.o_mau(R, G, B, 160), unsafe_allow_html=True)
else:
    with col1:
        st.subheader("XYZ → sRGB")
        # mặc định là màu đỏ sRGB (255, 0, 0)
        X = st.number_input("Nhập X", min_value=0.0, value=41.24, step=0.1, format="%.4f")
        Y = st.number_input("Nhập Y", min_value=0.0, value=21.26, step=0.1, format="%.4f")
        Z = st.number_input("Nhập Z", min_value=0.0, value=1.93, step=0.1, format="%.4f")

        XYZ = np.array([X, Y, Z]) / 100.0
        rgb = np.asarray(colour.XYZ_to_sRGB(XYZ)) * 255
        ngoai_gamut = bool(np.any(rgb < -0.5) or np.any(rgb > 255.5))
        rgb_hien_thi = np.clip(np.round(rgb), 0, 255) + 0.0  # "+ 0.0" để tránh hiện "-0"
        st.markdown(
            f"### R = {rgb_hien_thi[0]:.0f},  G = {rgb_hien_thi[1]:.0f},  B = {rgb_hien_thi[2]:.0f}"
        )
        if ngoai_gamut:
            st.warning(
                "Màu XYZ này nằm ngoài gamut sRGB (giá trị thô: "
                f"R={rgb[0]:.1f}, G={rgb[1]:.1f}, B={rgb[2]:.1f}), nên đã bị cắt về 0–255."
            )
    with col2:
        st.subheader("Màu tương ứng")
        st.markdown(cs.o_mau(*rgb_hien_thi, 160), unsafe_allow_html=True)

with st.expander("Cơ sở lý thuyết"):
    st.markdown(
        r"""
**sRGB → XYZ** (nguồn sáng D65):

1. Chuẩn hoá: $R', G', B' = R/255,\ G/255,\ B/255$
2. Giải mã gamma sRGB (về tuyến tính):
   $C_{lin} = C'/12.92$ nếu $C' \le 0.04045$, ngược lại $C_{lin}=\left(\frac{C'+0.055}{1.055}\right)^{2.4}$
3. Nhân ma trận: $\begin{bmatrix}X\\Y\\Z\end{bmatrix} = M \begin{bmatrix}R_{lin}\\G_{lin}\\B_{lin}\end{bmatrix}$

với $M=\begin{bmatrix}0.4124&0.3576&0.1805\\0.2126&0.7152&0.0722\\0.0193&0.1192&0.9505\end{bmatrix}$.

**XYZ → sRGB** làm ngược lại: nhân $M^{-1}$, rồi mã hoá gamma, nhân 255.
Màu có thành phần RGB âm hoặc > 1 nằm ngoài gamut sRGB.
"""
    )
cs.thanh_ben()
