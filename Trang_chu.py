# -*- coding: utf-8 -*-
import streamlit as st
import cs_utils as cs

st.set_page_config(page_title="Khoa học Màu sắc", page_icon="🎨", layout="wide")

t = cs.THONG_TIN

# ---- Đầu trang: banner trường + khoa (trái), logo khoa (phải) ----
c1, c2 = st.columns([4, 1])
with c1:
    cs.hien_logo(cs.LOGO_TRUONG)
with c2:
    cs.hien_logo(cs.LOGO_KHOA, width=130)

st.markdown(
    f"""
    <div style='text-align:center'>
      <h1>🎨 KHOA HỌC MÀU SẮC</h1>
      <p>Môn học: <b>{t['mon']}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

col_a, col_b = st.columns([1, 2])
with col_a:
    st.subheader("Thông tin sinh viên")
    st.markdown(
        f"""
- **Họ và tên:** {t['Lưu Minh Toàn']}
- **MSSV:** {t['23458018']}
"""
    )
with col_b:
    st.subheader("Nội dung project")
    st.markdown(
        """
| # | Trang | Nội dung |
|---|-------|----------|
| 1 | Chuyển đổi sRGB ⇄ XYZ | Đổi qua lại giữa sRGB và CIE XYZ |
| 2 | Tính XYZ từ phổ | Đọc file phổ phản xạ (csv), tính X, Y, Z |
| 3 | Biểu đồ CIE 1931 | Biểu đồ sắc độ hình móng ngựa |
| 4 | Gamut thiết bị RGB | Tam giác gamut sRGB (và các không gian RGB khác) |
| 5 | Gamut máy in | Gamut máy in của khoa từ file Lab (csv) |
| 6 | Đặc tính hoá máy in nửa tone | Tái tạo tông, mô hình Demichel – Yule-Nielsen |
| 7 | ⭐ CIE dạng band 400–700 nm | Dải màu đơn sắc + đường cong x̄ ȳ z̄ |
| 8 | ⭐ CIELab Lab1 → Lab2 | Vẽ 2 màu lên CIE và a*b*, tính ΔE, nhận xét |
| 9 | ⭐ Bộ chuyển đổi màu tổng hợp | Chọn màu → sRGB, XYZ, xyY, Lab, LCh |

⭐ = phần mở rộng ngoài 6 nội dung bắt buộc.
"""
    )

st.info("👈 Chọn từng trang ở thanh bên trái để xem kết quả.")
cs.thanh_ben()
