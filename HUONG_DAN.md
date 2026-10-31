# Hướng dẫn chạy và hoàn thiện project "Khoa học Màu sắc"

## 1. Cài đặt (làm một lần)

1. Cài Python 3.10 trở lên (khi cài nhớ tích **Add Python to PATH**).
2. Giải nén thư mục `KhoaHocMauSac`, mở Terminal / CMD trong thư mục đó.
3. (Khuyến nghị) tạo môi trường ảo:
   ```
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS / Linux
   ```
4. Cài thư viện:
   ```
   pip install -r requirements.txt
   ```

## 2. Chạy web trên localhost

```
streamlit run Trang_chu.py
```

Trình duyệt tự mở `http://localhost:8501`. Dừng bằng `Ctrl + C`.

## 3. Việc BẮT BUỘC phải làm trước khi nộp

| Việc | Làm ở đâu |
|------|-----------|
| Điền họ tên, MSSV, lớp, tên thầy, tên trường, tên khoa | `cs_utils.py`, dictionary `THONG_TIN` ở đầu file |
| Thay logo trường | chép file vào `assets/logo_truong.png` (ghi đè file giữ chỗ) |
| Thay logo khoa | chép file vào `assets/logo_khoa.png` |

Logo nên là PNG nền trong suốt hoặc nền trắng, vuông hoặc gần vuông.

## 4. Cấu trúc project

```
KhoaHocMauSac/
├── Trang_chu.py            # trang chính: logo trường, logo khoa, thông tin SV, mục lục
├── cs_utils.py             # hàm dùng chung + THÔNG TIN CÁ NHÂN
├── requirements.txt
├── assets/                 # logo
├── data/                   # file dữ liệu của thầy
│   ├── Color_Cyan_Sample.csv
│   ├── GamutMayIn_CMY_RGB_2.csv
│   └── halftone.mat
└── pages/                  # mỗi file = một trang ở thanh bên (Streamlit tự nhận)
    ├── 1_Chuyen_doi_sRGB_XYZ.py            (bắt buộc)
    ├── 2_Tinh_XYZ_tu_pho.py                (bắt buộc)
    ├── 3_Bieu_do_CIE_1931.py               (bắt buộc)
    ├── 4_Gamut_thiet_bi_RGB.py             (bắt buộc)
    ├── 5_Gamut_may_in.py                   (bắt buộc)
    ├── 6_Dac_tinh_hoa_may_in_halftone.py   (bắt buộc)
    ├── 7_CIE_dang_band_400_700nm.py        (mở rộng ⭐)
    ├── 8_CIELab_Lab1_Lab2.py               (mở rộng ⭐)
    └── 9_Bo_chuyen_doi_mau_tong_hop.py     (mở rộng ⭐)
```

Muốn thêm trang mới: tạo file `pages/10_Ten_trang.py`, cuối file gọi `cs.thanh_ben()`.

## 5. Mỗi trang làm gì, và khác gì code mẫu của thầy

| Trang | Điểm chính | Cải tiến so với code mẫu |
|-------|-----------|--------------------------|
| 1 | sRGB ⇄ XYZ bằng `colour.sRGB_to_XYZ` / `XYZ_to_sRGB` | nhập số nguyên 0–255, hiện ô màu, cảnh báo khi XYZ ngoài gamut sRGB |
| 2 | Đọc csv phổ → `colour.sd_to_XYZ` | có file mẫu sẵn, vẽ phổ, chọn nguồn sáng D65/D50/A, thêm xy, Lab, sRGB |
| 3 | `plot_chromaticity_diagram_CIE1931` | tuỳ chọn đánh dấu D65/D50 |
| 4 | Tam giác gamut sRGB trên biểu đồ xy | thêm Adobe RGB, Display P3, BT.2020 và so sánh diện tích |
| 5 | Lab 6 đỉnh R-Y-G-C-B-M → xy → đa giác gamut | bỏ `session_state` rườm rà, thêm biểu đồ a*b*, so sánh sRGB, diện tích |
| 6 | Mô hình Demichel + Yule-Nielsen với `halftone.mat` | sửa lỗi tràn số `uint8` khi đổi màu, thêm dot gain 50 %, RMSE, ô màu đo/dự báo |
| 7 ⭐ | **CIE band 400–700 nm** tự vẽ bằng `imshow` | giới hạn 400–700 nm theo yêu cầu, kèm đường cong x̄ȳz̄ và quỹ tích phổ |
| 8 ⭐ | **Lab1 → Lab2** vẽ lên CIE xy và mặt phẳng a*b*, ΔE, nhận xét | nhận xét tự sinh bằng tiếng Việt |
| 9 ⭐ | Chọn màu → sRGB, XYZ, xyY, Lab, LCh | – |

## 6. Gợi ý khi vấn đáp

- **Vì sao Lab phải chọn D50/D65?** Lab chỉ có nghĩa khi biết white point. Số đo máy in thường theo D50, màn hình sRGB theo D65, nên khi hiển thị phải thích nghi sắc.
- **Vì sao màu đơn sắc trên band chỉ gần đúng?** Màu đơn sắc nằm ngoài gamut sRGB (RGB âm), nên phải cắt và chuẩn hoá (xem phần "Cách vẽ" ở trang 7).
- **ΔE*ab và ΔE00 khác nhau thế nào?** CIE76 là khoảng cách Euclid trong Lab, còn CIEDE2000 hiệu chỉnh theo cảm nhận mắt người, đặc biệt ở vùng xanh lam và màu xám.
- **Yule-Nielsen n = 20 để làm gì?** Tính đến hiện tượng tán xạ ánh sáng trong giấy (optical dot gain), làm điểm trame trông lớn hơn diện tích thật.
- Phần "Nhận xét" ở trang 8 do code tự sinh; hãy đọc, hiểu rồi diễn đạt lại theo ý mình khi báo cáo.

## 7. Lỗi thường gặp

| Lỗi | Cách xử lý |
|-----|-----------|
| `ModuleNotFoundError: colour` | `pip install colour-science` (tên gói khác tên import) |
| `streamlit` không phải lệnh nội bộ | dùng `python -m streamlit run Trang_chu.py` |
| Biểu đồ CIE hiện thêm cửa sổ riêng | `cs_utils.py` đã ép backend `Agg`; hãy chạy bằng `streamlit run` |
| `No such file ... halftone.mat` | giữ nguyên thư mục `data/` cạnh `Trang_chu.py`, chạy lệnh từ thư mục gốc project |
| Cảnh báo về `sd_to_XYZ` / nội suy | chỉ là cảnh báo của colour, không ảnh hưởng kết quả |
