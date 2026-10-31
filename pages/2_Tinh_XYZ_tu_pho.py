# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import colour
import cs_utils as cs

st.set_page_config(page_title="Tính XYZ từ phổ", layout="wide")
st.title("2. Tính giá trị 3 thành phần X, Y, Z từ file phổ")

file_tai_len = st.sidebar.file_uploader("Tải file phổ phản xạ (csv: bước sóng, hệ số phản xạ)", type=["csv"])
dung_mau = st.sidebar.checkbox("Dùng file mẫu Color_Cyan_Sample.csv", value=file_tai_len is None)
ten_nguon = st.sidebar.selectbox("Nguồn sáng", ["D65", "D50", "A"], index=0)

nguon = file_tai_len if file_tai_len is not None else (cs.DATA / "Color_Cyan_Sample.csv" if dung_mau else None)

if nguon is None:
    st.info("Hãy tải file csv lên hoặc tích chọn dùng file mẫu ở thanh bên.")
else:
    try:
        df = pd.read_csv(nguon, header=None)
        df = df.iloc[:, :2].apply(pd.to_numeric, errors="coerce").dropna()
        df.columns = ["Bước sóng (nm)", "Phản xạ"]
        if len(df) < 3:
            raise ValueError("File phải có ít nhất 3 dòng số (bước sóng, phản xạ).")
    except Exception as e:  # noqa: BLE001
        st.error(f"Không đọc được file: {e}")
        st.stop()

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Dữ liệu phổ")
        st.caption(f"{len(df)} điểm, từ {df.iloc[0, 0]:.0f} đến {df.iloc[-1, 0]:.0f} nm")
        st.dataframe(df, height=330)
    with c2:
        fig, ax = plt.subplots(figsize=(6, 3.6))
        ax.plot(df["Bước sóng (nm)"], df["Phản xạ"], "-o", ms=3, color="tab:blue")
        ax.set_xlabel("Bước sóng (nm)")
        ax.set_ylabel("Hệ số phản xạ")
        ax.set_title("Phổ phản xạ của mẫu")
        ax.grid(alpha=0.3)
        st.pyplot(fig, clear_figure=True)

    if st.button("Tính XYZ", type="primary"):
        try:
            du_lieu = {int(w): float(r) for w, r in zip(df.iloc[:, 0], df.iloc[:, 1])}
            sd = colour.SpectralDistribution(du_lieu)
            cmfs = colour.MSDS_CMFS[cs.NGUON_QUAN_SAT]
            illuminant = colour.SDS_ILLUMINANTS[ten_nguon]

            XYZ = colour.sd_to_XYZ(sd, cmfs, illuminant)  # Y của nền trắng hoàn hảo = 100
            wp = cs.xy_nguon_sang(ten_nguon)
            xy = colour.XYZ_to_xy(XYZ / 100)
            Lab = colour.XYZ_to_Lab(XYZ / 100, illuminant=wp)
            rgb = np.clip(np.asarray(colour.XYZ_to_sRGB(XYZ / 100, illuminant=wp)), 0, 1) * 255
        except Exception as e:  # noqa: BLE001
            st.error(f"Lỗi khi tính toán: {e}")
            st.stop()

        st.success(f"**X = {XYZ[0]:.2f},  Y = {XYZ[1]:.2f},  Z = {XYZ[2]:.2f}**   (nguồn sáng {ten_nguon}, người quan sát 2°)")
        k1, k2, k3 = st.columns(3)
        k1.metric("x , y", f"{xy[0]:.4f} , {xy[1]:.4f}")
        k2.metric("L* , a* , b*", f"{Lab[0]:.1f} , {Lab[1]:.1f} , {Lab[2]:.1f}")
        k3.metric("sRGB", f"{rgb[0]:.0f} , {rgb[1]:.0f} , {rgb[2]:.0f}")
        st.markdown(cs.o_mau(*rgb, 90), unsafe_allow_html=True)

with st.expander("Cơ sở lý thuyết"):
    st.markdown(
        r"""
$X = k\sum_\lambda R(\lambda)\,S(\lambda)\,\bar x(\lambda)\Delta\lambda$, tương tự cho $Y, Z$ với $\bar y,\bar z$;
$k = 100 / \sum S(\lambda)\bar y(\lambda)\Delta\lambda$ để nền trắng hoàn hảo có $Y=100$.
$R(\lambda)$ là phổ phản xạ đo được, $S(\lambda)$ là phổ nguồn sáng, $\bar x,\bar y,\bar z$ là hàm màu CIE 1931 2°.
"""
    )
cs.thanh_ben()
