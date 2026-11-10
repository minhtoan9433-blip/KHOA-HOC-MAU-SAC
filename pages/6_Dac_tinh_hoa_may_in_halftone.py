# -*- coding: utf-8 -*-
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import colour
import cs_utils as cs

st.set_page_config(page_title="Đặc tính hoá máy in nửa tone", layout="wide")
st.title("6. Đặc tính hoá máy in nửa tone")

W, P, yellow, magenta = cs.nap_halftone()
CMFS = colour.MSDS_CMFS[cs.NGUON_QUAN_SAT]
ILLUM = colour.SDS_ILLUMINANTS["D65"]
N_YN = 20  # hệ số Yule-Nielsen
LUOI = np.round(np.linspace(0, 1, 11), 1)
MAU_VANG = "#FF8000"
MAU_TIM = "#FF00FF"
BUOC_SONG = np.linspace(400, 700, 31)


def pho_sang_rgb(phan_xa):
    """Phổ phản xạ (31 điểm, 400-700 nm) -> sRGB uint8."""
    sd = colour.SpectralDistribution({400 + 10 * i: float(r) for i, r in enumerate(phan_xa)})
    XYZ = colour.sd_to_XYZ(sd, CMFS, ILLUM)
    rgb = np.asarray(colour.XYZ_to_sRGB(XYZ / 100)) * 255
    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)  # cắt trước khi ép kiểu, tránh tràn số


@st.cache_data(show_spinner="Đang tính màu của 121 mẫu...")
def tao_anh_tron_mau(kich_thuoc=40):
    anh = np.zeros((kich_thuoc * 11, kich_thuoc * 11, 3), np.uint8)
    k = 0
    for x in range(11):
        for y in range(11):
            anh[x * kich_thuoc:(x + 1) * kich_thuoc, y * kich_thuoc:(y + 1) * kich_thuoc, :] = pho_sang_rgb(P[k])
            k += 1
    return anh[::-1, :, :]  # đảo hàng để magenta tăng dần từ dưới lên


muc = st.sidebar.radio(
    "Chọn các mục sau",
    (
        "Ảnh trộn màu vàng và tím",
        "Phổ màu vàng và tím trên nền trắng",
        "Đường cong tái tạo tông màu vàng và tím",
        "Trộn hai màu vàng và tím",
    ),
)

if muc == "Ảnh trộn màu vàng và tím":
    anh = tao_anh_tron_mau()
    _, giua, _ = st.columns([1, 3, 1])
    with giua:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(anh)
        vi_tri = list(range(20, 440, 40))
        ax.set_xticks(vi_tri)
        ax.set_xticklabels([f"{v:.1f}" for v in LUOI])
        ax.set_yticks(vi_tri)
        ax.set_yticklabels([f"{v:.1f}" for v in LUOI[::-1]])
        ax.set_xlabel("Yellow")
        ax.set_ylabel("Magenta")
        ax.set_title("Mix Yellow and Magenta Colors")
        st.pyplot(fig, clear_figure=True)
    st.caption("121 mẫu = 11 mức tỷ lệ hạt trame vàng × 11 mức magenta, màu tính từ phổ phản xạ đo được (D65, 2°).")

elif muc == "Phổ màu vàng và tím trên nền trắng":
    c1, c2 = st.columns(2)
    for cot, du_lieu, mau, ten in ((c1, yellow, MAU_VANG, "vàng"), (c2, magenta, MAU_TIM, "tím")):
        with cot:
            fig, ax = plt.subplots(figsize=(5, 5))
            for i in range(11):
                ax.plot(BUOC_SONG, du_lieu[i], color=mau, alpha=0.35 + 0.065 * i)
            ax.set_xlim(400, 700)
            ax.set_ylim(0, 1)
            ax.set_xlabel("Bước sóng (nm)")
            ax.set_ylabel("Phổ phản xạ")
            ax.set_title(f"Phổ màu {ten} trên nền trắng với a = 0:0.1:1")
            ax.grid(alpha=0.3)
            st.pyplot(fig, clear_figure=True)

elif muc == "Đường cong tái tạo tông màu vàng và tím":
    c1, c2 = st.columns(2)
    x_ve = np.linspace(0, 1, 101)
    for cot, du_lieu, mau, ten in ((c1, yellow, MAU_VANG, "vàng"), (c2, magenta, MAU_TIM, "tím")):
        with cot:
            a_thuc, p = cs.gettrc(LUOI, du_lieu, du_lieu[0, :], du_lieu[10, :], N_YN)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.plot(LUOI, a_thuc, "o", color=mau, label="Điểm đo")
            ax.plot(x_ve, np.polyval(p, x_ve), "k", label="Đa thức bậc 3")
            ax.plot([0, 1], [0, 1], ":", color="gray", label="Lý tưởng")
            ax.set_xlabel("Giá trị mục tiêu của a")
            ax.set_ylabel("Giá trị thực tế của a")
            ax.set_title(f"Đường cong tái tạo tông màu {ten}")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig, clear_figure=True)
            st.metric(f"Độ tăng tông (dot gain) ở 50% – {ten}", f"{(a_thuc[5] - 0.5) * 100:+.1f}%")

else:
    _, giua, _ = st.columns([1, 3, 1])
    with giua:
        a_mag = st.select_slider("Tỷ lệ hạt trame của màu tím (magenta)", options=list(LUOI), value=0.5)
        a_yel = st.select_slider("Tỷ lệ hạt trame của màu vàng (yellow)", options=list(LUOI), value=0.5)
        do, du_bao, a_mag_thuc, a_yel_thuc = cs.du_bao_pho(a_mag, a_yel, P, yellow, magenta, N_YN)

        fig, ax = plt.subplots(figsize=(5.5, 5))
        ax.plot(BUOC_SONG, do, "ro", label="Giá trị đo")
        ax.plot(BUOC_SONG, du_bao, "b", label="Giá trị dự báo")
        ax.set_ylim(0, 1)
        ax.set_xlabel("Bước sóng (nm)")
        ax.set_ylabel("Phổ phản xạ")
        ax.set_title(f"Phổ phản xạ khi trộn tím và vàng\na_mag = {a_mag:.1f}, a_yel = {a_yel:.1f}")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig, clear_figure=True)

        rmse = float(np.sqrt(np.mean((do - du_bao) ** 2)))
        m1, m2, m3 = st.columns(3)
        m1.metric("a_mag thực tế", f"{a_mag_thuc:.3f}")
        m2.metric("a_yel thực tế", f"{a_yel_thuc:.3f}")
        m3.metric("RMSE phổ", f"{rmse:.4f}")
        s1, s2 = st.columns(2)
        s1.markdown("**Màu đo**")
        s1.markdown(cs.o_mau(*pho_sang_rgb(do), 70), unsafe_allow_html=True)
        s2.markdown("**Màu dự báo**")
        s2.markdown(cs.o_mau(*pho_sang_rgb(du_bao), 70), unsafe_allow_html=True)

with st.expander("Cơ sở lý thuyết"):
    st.markdown(
        r"""
- **Demichel**: khi in chồng hai màu với tỷ lệ diện tích hạt trame thực $a_m, a_y$, bề mặt chia thành 4 vùng:
  giấy trắng $A_w=(1-a_m)(1-a_y)$, chỉ magenta $A_m=a_m(1-a_y)$, chỉ yellow $A_y=a_y(1-a_m)$, chồng nhau $A_o=a_ma_y$.
- **Yule–Nielsen** (hệ số $n=20$): $R^{1/n} = \sum_i A_i\,R_i^{1/n}$, trong đó $R_i$ là phổ của từng vùng,
  có tính đến hiện tượng ánh sáng tán xạ trong giấy (optical dot gain).
- Tỷ lệ diện tích thực $a$ được ước lượng từ phổ đo (công thức 11.5), rồi khớp đa thức bậc 3 để có
  **đường cong tái tạo tông** (TRC) $a_{thực}=f(a_{mục\ tiêu})$.
"""
    )
cs.thanh_ben()
