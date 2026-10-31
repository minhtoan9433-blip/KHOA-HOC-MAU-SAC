# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import cs_utils as cs

st.set_page_config(page_title="CIE dạng band", layout="wide")
st.title("7. Biểu đồ CIE dạng band (400–700 nm)")

with st.sidebar:
    w_min, w_max = st.slider("Khoảng bước sóng (nm)", 360, 830, (400, 700), step=10)
    hien_cmf = st.checkbox("Hiện đường cong x̄(λ), ȳ(λ), z̄(λ)", value=True)
    hien_locus = st.checkbox("Hiện quỹ tích phổ trên biểu đồ xy", value=True)

wl_cmf, xyz_cmf = cs.lay_cmfs()
wl = np.arange(w_min, w_max + 1, 1.0)
rgb, XYZ = cs.mau_don_sac(wl, wl_cmf, xyz_cmf)
cac_moc = np.arange(np.ceil(w_min / 50) * 50, w_max + 1, 50)

# ---------------- Dải band ----------------
if hien_cmf:
    fig, (ax_b, ax_c) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [1, 2.4], "hspace": 0.08}
    )
else:
    fig, ax_b = plt.subplots(figsize=(10, 2.4))
    ax_c = None

ax_b.imshow(np.repeat(rgb[np.newaxis, :, :], 20, axis=0), extent=[w_min, w_max, 0, 1], aspect="auto")
ax_b.set_yticks([])
ax_b.set_title(f"Phổ màu nhìn thấy {w_min:.0f}–{w_max:.0f} nm (CIE 1931 2°)")
if ax_c is None:
    ax_b.set_xticks(cac_moc)
    ax_b.set_xlabel("Bước sóng λ (nm)")
else:
    ax_b.tick_params(labelbottom=False)
    for k, (ten, mau) in enumerate((("x̄(λ)", "tab:red"), ("ȳ(λ)", "tab:green"), ("z̄(λ)", "tab:blue"))):
        ax_c.plot(wl, np.interp(wl, wl_cmf, xyz_cmf[:, k]), color=mau, lw=2, label=ten)
    ax_c.set_xlim(w_min, w_max)
    ax_c.set_xticks(cac_moc)
    ax_c.set_xlabel("Bước sóng λ (nm)")
    ax_c.set_ylabel("Giá trị tristimulus")
    ax_c.grid(alpha=0.3)
    ax_c.legend()
st.pyplot(fig, clear_figure=True)

# ---------------- Quỹ tích phổ + bảng ----------------
tong = XYZ.sum(axis=1)
x, y = XYZ[:, 0] / tong, XYZ[:, 1] / tong

c1, c2 = st.columns([3, 2])
with c1:
    if hien_locus:
        fig2, ax = plt.subplots(figsize=(6, 6))
        ax.plot(x, y, "-", color="lightgray", lw=1, zorder=1)
        ax.plot([x[-1], x[0]], [y[-1], y[0]], "--", color="gray", lw=1)  # đường tím
        ax.scatter(x, y, c=rgb, s=28, zorder=2)
        for w in cac_moc:
            i = int(np.argmin(np.abs(wl - w)))
            vec = np.array([x[i] - 0.33, y[i] - 0.33])
            vec = vec / (np.linalg.norm(vec) + 1e-9) * 0.035
            ax.plot(x[i], y[i], "ko", ms=4)
            ax.annotate(f"{w:.0f}", (x[i], y[i]), xytext=(x[i] + vec[0], y[i] + vec[1]),
                        ha="center", va="center", fontsize=9)
        ax.set_xlim(-0.05, 0.85)
        ax.set_ylim(-0.05, 0.90)
        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Quỹ tích phổ (spectral locus) theo bước sóng, nm")
        ax.grid(alpha=0.3)
        st.pyplot(fig2, clear_figure=True)
with c2:
    st.subheader("Bảng số liệu")
    bang = []
    for w in cac_moc:
        i = int(np.argmin(np.abs(wl - w)))
        r, g, b = (np.round(rgb[i] * 255)).astype(int)
        bang.append({"λ (nm)": int(w), "x": round(float(x[i]), 4), "y": round(float(y[i]), 4),
                     "sRGB hiển thị": f"#{r:02X}{g:02X}{b:02X}"})
    st.dataframe(pd.DataFrame(bang).set_index("λ (nm)"))
    st.caption(
        "Màu đơn sắc nằm ngoài gamut sRGB nên màu hiển thị chỉ là gần đúng: phần âm bị cắt, "
        "rồi chuẩn hoá để thành phần lớn nhất bằng 1."
    )

with st.expander("Cách vẽ"):
    st.markdown(
        r"""
1. Với mỗi bước sóng $\lambda$ lấy $(\bar x,\bar y,\bar z)$ từ bảng CIE 1931 2° → đó chính là XYZ của ánh sáng đơn sắc.
2. Đổi sang sRGB tuyến tính bằng ma trận $M^{-1}$, cắt các giá trị âm (ngoài gamut), chia cho thành phần lớn nhất.
3. Mã hoá gamma sRGB rồi ghép các cột màu thành dải ngang bằng `imshow` – chỉ lấy $\lambda\in[400, 700]$ nm
   (hàm mặc định của `colour` vẽ cả 360–830 nm).
4. Toạ độ sắc độ $x=X/(X+Y+Z)$, $y=Y/(X+Y+Z)$ cho quỹ tích phổ ở biểu đồ bên cạnh.
"""
    )
cs.thanh_ben()
