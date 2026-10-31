# -*- coding: utf-8 -*-
import streamlit as st
import cs_utils as cs

st.set_page_config(page_title="Biểu đồ CIE 1931", layout="centered")
st.title("3. Biểu đồ CIE 1931 hình móng ngựa")

hien_trang = st.sidebar.checkbox("Đánh dấu điểm trắng D65 và D50", value=False)

fig, ax = cs.ve_cie1931()
if hien_trang:
    for ten, mau in (("D65", "k"), ("D50", "tab:brown")):
        x, y = cs.xy_nguon_sang(ten)
        ax.plot(x, y, "o", color=mau, ms=6, label=f"{ten} ({x:.4f}, {y:.4f})")
    ax.legend(loc="upper right")
st.pyplot(fig, clear_figure=True)

st.caption(
    "Đường cong bao quanh là quỹ tích phổ (ánh sáng đơn sắc 380–780 nm), "
    "đoạn thẳng đáy là đường tím (purple line). Mọi màu nhìn thấy được nằm bên trong."
)
cs.thanh_ben()
