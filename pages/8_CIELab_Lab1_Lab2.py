# -*- coding: utf-8 -*-
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import colour
import cs_utils as cs

st.set_page_config(page_title="CIELab Lab1 → Lab2", layout="wide")
st.title("8. Biểu đồ CIELab: dịch chuyển màu từ Lab1 sang Lab2")

nguon = st.sidebar.radio("White point của Lab", ("D50", "D65"), index=0,
                         help="Số liệu đo máy in thường theo D50 (ICC / ISO 13655).")
phong_to = st.sidebar.checkbox("Phóng to vùng chứa hai màu trên biểu đồ CIE", value=False)


@st.cache_data(show_spinner=False)
def nen_ab_cache(L, nguon):
    return cs.nen_ab(L, nguon)



def dat_nhan(ax, diem, huong):
    """Đặt nhãn Lab1/Lab2 lệch ra phía ngoài mũi tên (huong = vector từ Lab1 sang Lab2)."""
    d = np.asarray(huong, float)
    d = d / (np.linalg.norm(d) + 1e-12)
    for ten, (x, y), dau in zip(("Lab1", "Lab2"), diem, (-1, 1)):
        ax.annotate(ten, (x, y), textcoords="offset points", xytext=tuple(dau * 26 * d),
                    ha="center", va="center", fontsize=12, weight="bold")


c1, c2 = st.columns(2)
with c1:
    st.subheader("Màu Lab1")
    L1 = st.number_input("L*₁", 0.0, 100.0, 62.67, 0.5, format="%.2f")
    a1 = st.number_input("a*₁", -128.0, 128.0, -20.83, 0.5, format="%.2f")
    b1 = st.number_input("b*₁", -128.0, 128.0, -42.09, 0.5, format="%.2f")
with c2:
    st.subheader("Màu Lab2")
    L2 = st.number_input("L*₂", 0.0, 100.0, 40.07, 0.5, format="%.2f")
    a2 = st.number_input("a*₂", -128.0, 128.0, 11.67, 0.5, format="%.2f")
    b2 = st.number_input("b*₂", -128.0, 128.0, -27.66, 0.5, format="%.2f")
st.caption("Giá trị mặc định lấy từ Cyan và Blue trong file gamut máy in của khoa.")

lab = np.array([[L1, a1, b1], [L2, a2, b2]])
_, xy = cs.lab_sang_xyz_xy(lab, nguon)
rgb = cs.lab_sang_srgb(lab, nguon)

try:
    dE00 = float(colour.delta_E(lab[0], lab[1], method="CIE 2000"))
except Exception:  # noqa: BLE001
    dE00 = None
kq = cs.nhan_xet_lab(lab[0], lab[1], dE00)

# ---- Ô màu + số liệu ----
s1, s2, s3 = st.columns([1, 1, 2])
s1.markdown("**Lab1**")
s1.markdown(cs.o_mau(*(rgb[0] * 255), 80), unsafe_allow_html=True)
s2.markdown("**Lab2**")
s2.markdown(cs.o_mau(*(rgb[1] * 255), 80), unsafe_allow_html=True)
with s3:
    m = st.columns(4)
    m[0].metric("ΔL*", f"{kq['dL']:+.2f}")
    m[1].metric("Δa*", f"{kq['da']:+.2f}")
    m[2].metric("Δb*", f"{kq['db']:+.2f}")
    m[3].metric("ΔC*ab", f"{kq['dC']:+.2f}")
    m = st.columns(4)
    m[0].metric("ΔE*ab (CIE76)", f"{kq['dE76']:.2f}")
    m[1].metric("ΔE00 (CIE2000)", "–" if dE00 is None else f"{dE00:.2f}")
    m[2].metric("h°ab₁ → h°ab₂", f"{kq['h1']:.0f}° → {kq['h2']:.0f}°")
    m[3].metric("Δx , Δy", f"{xy[1,0]-xy[0,0]:+.3f} , {xy[1,1]-xy[0,1]:+.3f}")

# ---- Hai biểu đồ ----
g1, g2 = st.columns(2)
with g1:
    fig, ax = cs.ve_cie1931()
    ax.scatter(xy[:, 0], xy[:, 1], c=rgb, s=170, edgecolors="k", linewidths=1.5, zorder=6)
    dat_nhan(ax, xy, xy[1] - xy[0])
    ax.annotate("", xy=xy[1], xytext=xy[0],
                arrowprops=dict(arrowstyle="-|>", color="k", lw=2, shrinkA=8, shrinkB=8), zorder=5)
    if phong_to:
        tam = xy.mean(axis=0)
        r = max(0.06, 1.5 * float(np.abs(xy[1] - xy[0]).max()))
        ax.set_xlim(tam[0] - r, tam[0] + r)
        ax.set_ylim(tam[1] - r, tam[1] + r)
    st.pyplot(fig, clear_figure=True)
with g2:
    L_nen = st.slider("L* của màu nền", 10, 95, int(round((L1 + L2) / 2)))
    anh = nen_ab_cache(L_nen, nguon)
    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.imshow(anh, extent=[-128, 128, -128, 128], origin="lower", interpolation="bilinear")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.axvline(0, color="gray", lw=0.8)
    ax2.annotate("", xy=(a2, b2), xytext=(a1, b1),
                 arrowprops=dict(arrowstyle="-|>", color="k", lw=2, shrinkA=8, shrinkB=8), zorder=5)
    ax2.scatter([a1, a2], [b1, b2], c=rgb, s=170, edgecolors="k", linewidths=1.5, zorder=6)
    dat_nhan(ax2, [(a1, b1), (a2, b2)], (a2 - a1, b2 - b1))
    ax2.set_xlim(-128, 128)
    ax2.set_ylim(-128, 128)
    ax2.set_aspect("equal")
    ax2.set_xlabel("a*   (← xanh lá | đỏ →)")
    ax2.set_ylabel("b*   (← xanh dương | vàng →)")
    ax2.set_title(f"Mặt phẳng a*b* của CIELab tại L* = {L_nen}")
    st.pyplot(fig2, clear_figure=True)
    st.caption("Vùng trắng: ngoài gamut sRGB ở độ sáng này nên không hiển thị được trên màn hình.")

# ---- Nhận xét ----
st.subheader("Nhận xét sự chuyển dịch màu từ Lab1 sang Lab2")
for cau in kq["nhan_xet"]:
    st.markdown(f"- {cau}")
dx, dy = xy[1] - xy[0]
st.markdown(
    f"- Trên biểu đồ CIE xy, điểm màu dịch chuyển Δx = {dx:+.4f}, Δy = {dy:+.4f}: "
    f"{'về phía đỏ (x tăng)' if dx > 0 else 'về phía xanh lam (x giảm)'}, "
    f"{'và về phía lục (y tăng)' if dy > 0 else 'và xa vùng lục (y giảm)'}."
)
st.success(kq["ket_luan"])

with st.expander("Công thức"):
    st.markdown(
        r"""
- $C^*_{ab}=\sqrt{a^{*2}+b^{*2}}$, $h_{ab}=\arctan2(b^*,a^*)$
- $\Delta E^*_{ab}=\sqrt{\Delta L^{*2}+\Delta a^{*2}+\Delta b^{*2}}$ (CIE76); $\Delta E_{00}$ là công thức CIEDE2000, sát cảm nhận mắt người hơn.
- Lab → XYZ dùng white point đã chọn, XYZ → xy: $x=X/(X+Y+Z)$, $y=Y/(X+Y+Z)$.
- Để hiển thị lên màn hình sRGB: thích nghi sắc về D65 rồi đổi sang sRGB.
"""
    )
cs.thanh_ben()
