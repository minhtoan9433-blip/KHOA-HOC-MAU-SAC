# -*- coding: utf-8 -*-
"""
Hàm dùng chung cho project "Khoa học Màu sắc".

Các trang trong thư mục pages/ đều `import cs_utils as cs`.
Phần tính toán thuần numpy được tách ra đây để dễ kiểm tra; thư viện
`colour` và `streamlit` chỉ được import khi hàm cần đến.
"""
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")  # chỉ vẽ ra ảnh cho Streamlit, không mở cửa sổ riêng

GOC = Path(__file__).resolve().parent
DATA = GOC / "data"
ASSETS = GOC / "assets"

# ============================================================
# >>> SỬA THÔNG TIN CÁ NHÂN Ở ĐÂY <<<
# ============================================================
THONG_TIN = {
    "ho_ten": "Họ và tên của bạn",
    "mssv": "MSSV của bạn",
    "lop": "Lớp của bạn",
    "mon": "Ứng dụng Matlab trong công nghệ in",
    "gvhd": "Tên thầy",
    "truong": "Trường Đại học Công nghệ Kỹ thuật TP. HCM",
    "khoa": "Khoa In và Truyền thông",
}
# Logo: đặt file vào thư mục assets/ với đúng tên dưới đây
LOGO_TRUONG = "logo_truong.png"
LOGO_KHOA = "logo_khoa.png"

NGUON_QUAN_SAT = "CIE 1931 2 Degree Standard Observer"

# Ma trận XYZ (D65, thang 0-1) -> sRGB tuyến tính
M_XYZ_SANG_RGB = np.array(
    [
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252],
    ]
)


# ------------------------------------------------------------
# Giao diện dùng chung (import streamlit trễ)
# ------------------------------------------------------------
def tim_logo(ten_file):
    """Tìm file logo trong assets/, không phân biệt hoa thường, nhận png/jpg/jpeg."""
    goc = Path(ten_file).stem.lower()
    if ASSETS.is_dir():
        for f in sorted(ASSETS.iterdir()):
            if f.stem.lower() == goc and f.suffix.lower() in (".png", ".jpg", ".jpeg"):
                return f
    return None


def hien_logo(ten_file, width=None):
    import streamlit as st

    duong_dan = tim_logo(ten_file)
    if duong_dan is not None:
        if width:
            st.image(str(duong_dan), width=width)
        else:
            st.image(str(duong_dan))
    else:
        st.caption(f"(chưa có {ten_file} trong thư mục {ASSETS})")


def thanh_ben():
    """Logo + tên sinh viên ở cuối sidebar của mọi trang."""
    import streamlit as st

    t = THONG_TIN
    st.sidebar.markdown("---")
    with st.sidebar:
        hien_logo(LOGO_TRUONG)  # banner trường + khoa, tự co theo bề rộng sidebar
        hien_logo(LOGO_KHOA, width=90)
    st.sidebar.caption(f"{t['ho_ten']} – MSSV {t['mssv']}")


def o_mau(r, g, b, cao=110):
    """Chuỗi HTML hiển thị một ô màu; r,g,b là số nguyên 0-255."""
    r, g, b = (int(np.clip(round(v), 0, 255)) for v in (r, g, b))
    return (
        f"<div style='width:100%;height:{cao}px;background:rgb({r},{g},{b});"
        "border:1px solid #888;border-radius:8px'></div>"
    )


# ------------------------------------------------------------
# Màu sắc cơ bản
# ------------------------------------------------------------
def srgb_encode(tuyen_tinh):
    """Mã hoá gamma sRGB (tuyến tính 0-1 -> 0-1)."""
    x = np.asarray(tuyen_tinh, float)
    return np.where(
        x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055
    )


def lay_cmfs(ten=NGUON_QUAN_SAT):
    """Trả về (bước sóng [N], giá trị x̄ȳz̄ [N,3]) từ colour-science."""
    import colour

    cmfs = colour.MSDS_CMFS[ten]
    return np.asarray(cmfs.wavelengths, float), np.asarray(cmfs.values, float)


def mau_don_sac(wl, cmfs_wl, cmfs_xyz):
    """
    Màu hiển thị (sRGB, 0-1) của ánh sáng đơn sắc tại các bước sóng `wl`.
    Cách làm giống hàm plot_visible_spectrum của colour: lấy XYZ của đơn sắc,
    đổi sang sRGB tuyến tính, cắt phần âm (ngoài gamut), chuẩn hoá max = 1
    rồi mã hoá gamma.
    Trả về (rgb [N,3], XYZ [N,3]).
    """
    wl = np.asarray(wl, float)
    XYZ = np.column_stack([np.interp(wl, cmfs_wl, cmfs_xyz[:, k]) for k in range(3)])
    tt = np.clip(XYZ @ M_XYZ_SANG_RGB.T, 0, None)
    tt = tt / np.maximum(tt.max(axis=1, keepdims=True), 1e-12)
    return np.clip(srgb_encode(tt), 0, 1), XYZ


def dien_tich_da_giac(x, y):
    """Diện tích đa giác (công thức dây giày)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


# ------------------------------------------------------------
# Biểu đồ CIE 1931
# ------------------------------------------------------------
def ve_cie1931(kich_thuoc=(7, 7)):
    """Vẽ biểu đồ CIE 1931 (móng ngựa); trả về (figure, axes)."""
    from colour.plotting import plot_chromaticity_diagram_CIE1931

    fig, ax = plot_chromaticity_diagram_CIE1931(show=False)
    fig.set_size_inches(*kich_thuoc)
    ax.set_xlim([-0.1, 0.85])
    ax.set_ylim([-0.1, 0.90])
    ax.set_title("CIE 1931 Chromaticity Diagram\n2 Degree Standard Observer")
    return fig, ax


def xy_nguon_sang(ten="D65"):
    import colour

    return np.asarray(colour.CCS_ILLUMINANTS[NGUON_QUAN_SAT][ten], float)


# ------------------------------------------------------------
# CIELab
# ------------------------------------------------------------
def lab_sang_xyz_xy(lab, nguon="D50"):
    """Lab (N,3) -> (XYZ, xy) với white point `nguon` (D50 hoặc D65)."""
    import colour

    lab = np.atleast_2d(np.asarray(lab, float))
    wp = xy_nguon_sang(nguon)
    XYZ = colour.Lab_to_XYZ(lab, illuminant=wp)
    xy = colour.XYZ_to_xy(XYZ)
    return np.atleast_2d(XYZ), np.atleast_2d(xy)


def lab_sang_srgb(lab, nguon="D50"):
    """Lab (N,3) -> sRGB hiển thị 0-1 (có thích nghi sắc về D65)."""
    import colour

    XYZ, _ = lab_sang_xyz_xy(lab, nguon)
    rgb = colour.XYZ_to_sRGB(XYZ, illuminant=xy_nguon_sang(nguon))
    return np.clip(np.atleast_2d(rgb), 0, 1)


def nen_ab(L, nguon="D50", gioi_han=128, buoc=2):
    """
    Ảnh RGBA nền cho mặt phẳng a*b* ở độ sáng L*. Điểm ngoài gamut sRGB
    có alpha = 0 (trong suốt).
    """
    import colour

    a = np.arange(-gioi_han, gioi_han + 1, buoc, dtype=float)
    A, B = np.meshgrid(a, a)
    lab = np.stack([np.full_like(A, float(L)), A, B], axis=-1).reshape(-1, 3)
    wp = xy_nguon_sang(nguon)
    XYZ = colour.Lab_to_XYZ(lab, illuminant=wp)
    tt = np.asarray(colour.XYZ_to_sRGB(XYZ, illuminant=wp, apply_cctf_encoding=False))
    trong = np.all((tt >= -1e-3) & (tt <= 1 + 1e-3), axis=1)
    rgb = np.clip(srgb_encode(np.clip(tt, 0, 1)), 0, 1)
    anh = np.dstack(
        [rgb.reshape(A.shape + (3,)), trong.reshape(A.shape).astype(float)]
    )
    return anh  # hàng 0 ứng với b* nhỏ nhất -> dùng origin="lower"


# Các mốc góc sắc h°ab (theo vị trí thực của màu sRGB trong CIELab: đỏ ≈ 40°,
# vàng ≈ 100°, lục ≈ 136°, cyan ≈ 196°, xanh lam ≈ 306°, magenta ≈ 328°)
_TEN_HUE = [
    (0, "hồng đỏ"),
    (40, "đỏ"),
    (70, "cam"),
    (95, "vàng"),
    (125, "vàng lục"),
    (150, "lục (xanh lá)"),
    (195, "lục lam (cyan)"),
    (245, "xanh da trời"),
    (290, "xanh lam (blue)"),
    (325, "tím / magenta"),
]


def ten_hue(h):
    """Tên màu gần đúng theo góc sắc h (độ) trong mặt phẳng a*b*."""
    gan_nhat = min(_TEN_HUE, key=lambda t: min(abs(h - t[0]), 360 - abs(h - t[0])))
    return gan_nhat[1]


def muc_do_dE(dE):
    if dE < 1:
        return "không nhận ra bằng mắt thường"
    if dE < 2:
        return "chỉ người có kinh nghiệm mới nhận ra"
    if dE < 3.5:
        return "người bình thường nhận ra khi so sánh cạnh nhau"
    if dE < 5:
        return "khác biệt rõ ràng"
    return "hai màu khác nhau hẳn"


def nhan_xet_lab(lab1, lab2, de2000=None):
    """
    Tính các độ chênh Lab1 -> Lab2 và sinh nhận xét tiếng Việt.
    Trả về dict gồm các số liệu và `nhan_xet` (danh sách câu), `ket_luan`.
    """
    L1, a1, b1 = (float(v) for v in lab1)
    L2, a2, b2 = (float(v) for v in lab2)
    dL, da, db = L2 - L1, a2 - a1, b2 - b1
    C1, C2 = float(np.hypot(a1, b1)), float(np.hypot(a2, b2))
    h1 = float(np.degrees(np.arctan2(b1, a1)) % 360)
    h2 = float(np.degrees(np.arctan2(b2, a2)) % 360)
    dC = C2 - C1
    dh = (h2 - h1 + 180) % 360 - 180
    dE76 = float(np.sqrt(dL**2 + da**2 + db**2))
    dH2 = max(da**2 + db**2 - dC**2, 0.0)  # ΔH*² = Δa²+Δb²-ΔC²
    dE = dE76 if de2000 is None else float(de2000)
    ten_dE = "ΔE*ab" if de2000 is None else "ΔE00"

    nx = []
    if abs(dL) < 1:
        nx.append(f"Độ sáng gần như không đổi (ΔL* = {dL:+.2f}).")
    else:
        nx.append(
            f"Màu {'sáng hơn' if dL > 0 else 'tối hơn'} "
            f"(L* từ {L1:.1f} → {L2:.1f}, ΔL* = {dL:+.2f})."
        )
    if abs(da) >= 1:
        nx.append(
            f"Trục a* {'tăng' if da > 0 else 'giảm'} {abs(da):.2f}: màu dịch về phía "
            f"{'đỏ / magenta' if da > 0 else 'xanh lá'}."
        )
    else:
        nx.append(f"Trục a* gần như không đổi (Δa* = {da:+.2f}).")
    if abs(db) >= 1:
        nx.append(
            f"Trục b* {'tăng' if db > 0 else 'giảm'} {abs(db):.2f}: màu dịch về phía "
            f"{'vàng' if db > 0 else 'xanh dương'}."
        )
    else:
        nx.append(f"Trục b* gần như không đổi (Δb* = {db:+.2f}).")
    if abs(dC) >= 1:
        nx.append(
            f"Độ bão hoà (chroma) C*ab {'tăng' if dC > 0 else 'giảm'} từ {C1:.1f} → {C2:.1f}: "
            f"màu {'rực / sặc sỡ hơn' if dC > 0 else 'xỉn / nhạt hơn, tiến gần trục xám'}."
        )
    else:
        nx.append(f"Độ bão hoà gần như không đổi (C*ab: {C1:.1f} → {C2:.1f}).")
    if min(C1, C2) < 5:
        nx.append("Có một màu rất gần trục xám (C* < 5) nên góc sắc h° không ổn định, không nên so sánh.")
    else:
        nx.append(
            f"Góc sắc từ {h1:.1f}° ({ten_hue(h1)}) sang {h2:.1f}° ({ten_hue(h2)}), "
            f"Δh = {dh:+.1f}°."
        )
    nx.append(f"{ten_dE} = {dE:.2f}: {muc_do_dE(dE)}.")

    dong_gop = {"độ sáng": dL**2, "độ bão hoà": dC**2, "sắc độ (hue)": dH2}
    chu_dao = max(dong_gop, key=dong_gop.get)
    ket_luan = (
        f"Từ Lab1 sang Lab2, thành phần thay đổi nhiều nhất là {chu_dao}. "
        f"Màu mới {'sáng hơn' if dL > 1 else 'tối hơn' if dL < -1 else 'có độ sáng tương đương'}, "
        f"{'bão hoà hơn' if dC > 1 else 'xỉn hơn' if dC < -1 else 'bão hoà tương đương'}"
        + (f", hướng về {ten_hue(h2)}." if min(C1, C2) >= 5 else ".")
        + f" Mức khác biệt: {muc_do_dE(dE)}."
    )
    return dict(
        dL=dL, da=da, db=db, dC=dC, dh=dh, dE76=dE76, C1=C1, C2=C2, h1=h1, h2=h2,
        nhan_xet=nx, ket_luan=ket_luan,
    )


# ------------------------------------------------------------
# Gamut máy in
# ------------------------------------------------------------
THU_TU_GAMUT = ["R", "Y", "G", "C", "B", "M"]  # đi vòng quanh đa giác gamut


def lab_cac_dinh(df):
    """df có index ColorSpace (L, a, b) và các cột C,M,Y,R,G,B -> ma trận (6,3) theo THU_TU_GAMUT."""
    return np.array([[df.loc["L", k], df.loc["a", k], df.loc["b", k]] for k in THU_TU_GAMUT], float)


# ------------------------------------------------------------
# Đặc tính hoá máy in nửa tone
# ------------------------------------------------------------
def nap_halftone(duong_dan=None):
    """Trả về W, P (121x31: hàng 0 là giấy trắng), yellow (11x31), magenta (11x31)."""
    from scipy.io import loadmat

    duong_dan = DATA / "halftone.mat" if duong_dan is None else duong_dan
    d = loadmat(str(duong_dan))
    W = np.atleast_2d(d["W"])
    P = np.vstack((W, d["P"]))
    yellow = P[:11, :]
    magenta = P[0 : 11 * 11 : 11, :]  # hàng 0, 11, 22, ..., 110
    return W, P, yellow, magenta


def gettrc(dig, R, W, Solid, n):
    """Đường cong tái tạo tông (công thức 11.5 – Yule-Nielsen). Trả về (a_thực, hệ số đa thức bậc 3)."""
    R = R ** (1 / n)
    W = W ** (1 / n)
    Solid = Solid ** (1 / n)
    c = np.zeros(len(dig))
    for i in range(len(dig)):
        c[i] = np.sum((Solid - R[i, :]) * (Solid - W)) / np.sum((Solid - W) * (Solid - W))
    c = 1 - c
    p = np.polyfit(dig, c, 3)
    return c, p


def du_bao_pho(a_mag_muc_tieu, a_yel_muc_tieu, P, yellow, magenta, n=20):
    """
    Dự báo phổ phản xạ khi in chồng Magenta và Yellow bằng mô hình
    Demichel + Yule-Nielsen. Trả về (phổ đo, phổ dự báo, a_mag thực, a_yel thực).
    """
    muc_tieu = np.round(np.linspace(0, 1, 11), 1)
    i_mag = int(np.argmin(np.abs(muc_tieu - a_mag_muc_tieu)))
    i_yel = int(np.argmin(np.abs(muc_tieu - a_yel_muc_tieu)))
    do = P[i_mag * 11 + i_yel, :]

    a_muc_tieu = np.linspace(0, 1, 11)
    _, p_mag = gettrc(a_muc_tieu, magenta, magenta[0, :], magenta[10, :], n)
    _, p_yel = gettrc(a_muc_tieu, yellow, yellow[0, :], yellow[10, :], n)
    a_mag = float(np.polyval(p_mag, a_mag_muc_tieu))
    a_yel = float(np.polyval(p_yel, a_yel_muc_tieu))

    # Diện tích các vùng theo Demichel
    Am = a_mag * (1 - a_yel)  # chỉ có magenta
    Ay = a_yel * (1 - a_mag)  # chỉ có yellow
    Aw = (1 - a_mag) * (1 - a_yel)  # giấy trắng
    Ao = a_mag * a_yel  # chồng lên nhau
    overlap = P[120, :]
    WW = P[0, :]
    du_bao = (
        Am * magenta[10, :] ** (1 / n)
        + Ay * yellow[10, :] ** (1 / n)
        + Ao * overlap ** (1 / n)
        + Aw * WW ** (1 / n)
    ) ** n
    return do, du_bao, a_mag, a_yel
