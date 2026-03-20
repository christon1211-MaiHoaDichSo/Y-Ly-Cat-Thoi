import streamlit as st
import google.generativeai as genai
import datetime
import calendar
import random
import base64
from lunarcalendar import Converter, Solar, Lunar

# ==============================================================================
# BỘ DỮ LIỆU LOGIC (GIỮ NGUYÊN TỪ BẢN GỐC)
# ==============================================================================
CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
GIO_HIENTHI = {
    'Tý': 'Tý (11 P.M - 1 A.M)',
    'Sửu': 'Sửu (1 A.M - 3 A.M)',
    'Dần': 'Dần (3 A.M - 5 A.M)',
    'Mão': 'Mão (5 A.M - 7 A.M)',
    'Thìn': 'Thìn (7 A.M - 9 A.M)',
    'Tỵ': 'Tỵ (9 A.M - 11 A.M)',
    'Ngọ': 'Ngọ (11 A.M - 1 P.M)',
    'Mùi': 'Mùi (1 P.M - 3 P.M)',
    'Thân': 'Thân (3 P.M - 5 P.M)',
    'Dậu': 'Dậu (5 P.M - 7 P.M)',
    'Tuất': 'Tuất (7 P.M - 9 P.M)',
    'Hợi': 'Hợi (9 P.M - 11 P.M)'
}
DAO_NAMES = ['Thanh Long', 'Minh Đường', 'Thiên Hình', 'Chu Tước', 'Kim Quỹ', 'Bảo Quang', 'Bạch Hổ', 'Ngọc Đường', 'Thiên Lao', 'Nguyên Vũ', 'Tư Mệnh', 'Câu Trận']
DAO_TYPES = ['Hoàng Đạo', 'Hoàng Đạo', 'Hắc Đạo', 'Hắc Đạo', 'Hoàng Đạo', 'Hoàng Đạo', 'Hắc Đạo', 'Hoàng Đạo', 'Hắc Đạo', 'Hắc Đạo', 'Hoàng Đạo', 'Hắc Đạo']
START_CHI = {'Tý': 8, 'Ngọ': 8, 'Sửu': 10, 'Mùi': 10, 'Dần': 0, 'Thân': 0, 'Mão': 2, 'Dậu': 2, 'Thìn': 4, 'Tuất': 4, 'Tỵ': 6, 'Hợi': 6}

LUU_CHU_DETAILS = {
    'Tý': "Giờ Tý (23h-01h) - ĐỞM:\nKhí huyết dồn về Mật. Đởm tàng tinh trấp giúp tiêu hóa. Lúc này cơ thể cần ngủ say để mật tái tạo.",
    'Sửu': "Giờ Sửu (01h-03h) - CAN:\nKhí huyết dồn về Gan. Đụng dao kéo cực kỳ dễ gây xuất huyết lớn hoặc suy gan cấp.",
    'Dần': "Giờ Dần (03h-05h) - PHẾ:\nKhí huyết dồn về Phổi. Đây là lúc phân bổ khí huyết đi toàn thân.",
    'Mão': "Giờ Mão (05h-07h) - ĐẠI TRƯỜNG:\nKhí huyết dồn về Ruột già. Cơ thể tiến hành bài tiết cặn bã.",
    'Thìn': "Giờ Thìn (07h-09h) - VỊ:\nKhí huyết dồn về Dạ dày. Là lúc dạ dày co bóp mạnh nhất để tiêu hóa thức ăn.",
    'Tỵ': "Giờ Tỵ (09h-11h) - TỲ:\nKhí huyết dồn về Lá lách/Tuyến tụy. Hấp thu dưỡng chất từ dạ dày.",
    'Ngọ': "Giờ Ngọ (11h-13h) - TÂM:\nKhí huyết dồn về Tim. Khí huyết đẩy lên đỉnh điểm. Châm cứu sai huyệt giờ này dễ gây trụy tim, sốc phản vệ.",
    'Mùi': "Giờ Mùi (13h-15h) - TIÊU TRƯỜNG:\nKhí huyết dồn về Ruột non. Hấp thu nước và dinh dưỡng tinh.",
    'Thân': "Giờ Thân (15h-17h) - BÀNG QUANG:\nKhí huyết dồn về Bọng đái. Đào thải nước tiểu. Kinh bàng quang chạy dọc sống lưng, châm cứu vùng lưng rất nhạy cảm.",
    'Dậu': "Giờ Dậu (17h-19h) - THẬN:\nKhí huyết dồn về Thận. Thận tàng tinh, lúc này là thời điểm tích lũy nguyên khí.",
    'Tuất': "Giờ Tuất (19h-21h) - TÂM BÀO:\nKhí huyết dồn về Màng bao tim (hệ thống màng bảo vệ tim và mạch máu ngoại vi).",
    'Hợi': "Giờ Hợi (21h-23h) - TAM TIÊU:\nKhí huyết dồn về hệ thống Nội tiết và các màng khoang bụng/ngực. Cơ thể cần nghỉ ngơi hoàn toàn."
}

def tinh_can_chi_tu_ngay_duong(solar_date, gio_hien_tai=12):
    dt_thoi_diem = datetime.datetime(solar_date.year, solar_date.month, solar_date.day, gio_hien_tai, 0)
    lunar = Converter.Solar2Lunar(solar_date)
    can_nam_idx = (lunar.year + 6) % 10
    chi_nam_idx = (lunar.year + 8) % 12
    chi_thang_idx = (lunar.month + 1) % 12
    can_thang_idx = (can_nam_idx * 2 + lunar.month + 1) % 10
    ordinal = dt_thoi_diem.toordinal()
    can_ngay_idx = (ordinal + 4) % 10
    chi_ngay_idx = (ordinal + 2) % 12

    cac_gio = {'Hoàng Đạo': [], 'Hắc Đạo': []}
    start_idx = START_CHI[CHI[chi_ngay_idx]]
    for i in range(12):
        c_gio_idx = (can_ngay_idx * 2 + i) % 10
        dao_idx = (i - start_idx) % 12
        info = {'can_chi': f"{CAN[c_gio_idx]} {CHI[i]}", 'chi': CHI[i], 'ten_dao': DAO_NAMES[dao_idx], 'loai': DAO_TYPES[dao_idx]}
        cac_gio[DAO_TYPES[dao_idx]].append(info)

    return {
        'nam': f"{CAN[can_nam_idx]} {CHI[chi_nam_idx]}", 'thang': f"{CAN[can_thang_idx]} {CHI[chi_thang_idx]}",
        'ngay': f"{CAN[can_ngay_idx]} {CHI[chi_ngay_idx]}", 'chi_ngay': CHI[chi_ngay_idx], 'chi_nam': CHI[chi_nam_idx], 
        'can_ngay': CAN[can_ngay_idx], 'thang_am_so': lunar.month, 'ngay_am_so': lunar.day,
        'cac_gio': cac_gio, 'hoang_dao_list': [g['chi'] for g in cac_gio['Hoàng Đạo']]
    }

class YLyCatThoiEngine:
    def __init__(self):
        self.CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
        self.LUC_XUNG = {'Tý': 'Ngọ', 'Ngọ': 'Tý', 'Sửu': 'Mùi', 'Mùi': 'Sửu', 'Dần': 'Thân', 'Thân': 'Dần', 'Mão': 'Dậu', 'Dậu': 'Mão', 'Thìn': 'Tuất', 'Tuất': 'Thìn', 'Tỵ': 'Hợi', 'Hợi': 'Tỵ'}
        self.HUYET_KY = {1: 'Sửu', 2: 'Mùi', 3: 'Dần', 4: 'Thân', 5: 'Mão', 6: 'Dậu', 7: 'Thìn', 8: 'Tuất', 9: 'Tỵ', 10: 'Hợi', 11: 'Ngọ', 12: 'Tý'}
        self.HUYET_CHI = {1: 'Sửu', 2: 'Dần', 3: 'Mão', 4: 'Thìn', 5: 'Tỵ', 6: 'Ngọ', 7: 'Mùi', 8: 'Thân', 9: 'Dậu', 10: 'Tuất', 11: 'Hợi', 12: 'Tý'}
        self.TU_KHI = {1: 'Ngọ', 2: 'Mùi', 3: 'Thân', 4: 'Dậu', 5: 'Tuất', 6: 'Hợi', 7: 'Tý', 8: 'Sửu', 9: 'Dần', 10: 'Mão', 11: 'Thìn', 12: 'Tỵ'}
        self.THIEN_Y = {1: 'Mão', 2: 'Dần', 3: 'Sửu', 4: 'Tý', 5: 'Hợi', 6: 'Tuất', 7: 'Dậu', 8: 'Thân', 9: 'Mùi', 10: 'Ngọ', 11: 'Tỵ', 12: 'Thìn'}
        self.DIA_Y = {1: 'Mùi', 2: 'Thân', 3: 'Dậu', 4: 'Tuất', 5: 'Hợi', 6: 'Tý', 7: 'Sửu', 8: 'Dần', 9: 'Mão', 10: 'Thìn', 11: 'Tỵ', 12: 'Ngọ'}
        self.BENH_PHU = {'Tý': 'Hợi', 'Sửu': 'Tý', 'Dần': 'Sửu', 'Mão': 'Dần', 'Thìn': 'Mão', 'Tỵ': 'Thìn', 'Ngọ': 'Tỵ', 'Mùi': 'Ngọ', 'Thân': 'Mùi', 'Dậu': 'Thân', 'Tuất': 'Dậu', 'Hợi': 'Tuất'}
        self.NHAT_Y = {'Giáp': 'Mão', 'Ất': 'Hợi', 'Bính': 'Sửu', 'Đinh': 'Mùi', 'Mậu': 'Tỵ', 'Kỷ': 'Mão', 'Canh': 'Hợi', 'Tân': 'Sửu', 'Nhâm': 'Mùi', 'Quý': 'Tỵ'}
        self.NT_NGAY = {1: 'ngón chân cái', 2: 'mắt cá ngoài', 3: 'mặt trong đùi', 4: 'eo lưng', 5: 'miệng lưỡi họng', 6: 'ngón chân út', 7: 'mắt cá trong', 8: 'cổ chân', 9: 'mông', 10: 'lưng eo', 11: 'mũi', 12: 'chân tóc', 13: 'răng', 14: 'dạ dày', 15: 'khắp thân', 16: 'ngực vú', 17: 'khí xung', 18: 'trong bụng', 19: 'mu bàn chân', 20: 'dưới gối', 21: 'ngón út bàn tay', 22: 'đùi trước', 23: 'gan', 24: 'hai bên sườn', 25: 'vị', 26: 'tay và chân', 27: 'đầu gối', 28: 'âm bộ', 29: 'gối cẳng chân', 30: 'lòng bàn chân'}
        self.NT_CAN = {'Giáp': 'Đầu', 'Ất': 'Cổ Gáy', 'Bính': 'Vai Cánh Tay', 'Đinh': 'Ngực Sườn', 'Mậu': 'Bụng', 'Kỷ': 'Lưng', 'Canh': 'Gối', 'Tân': 'Tỳ', 'Nhâm': 'Thận', 'Quý': 'Chân'}
        self.NT_CHI = {'Tý': 'Mắt', 'Sửu': 'Tai', 'Dần': 'Ngực', 'Mão': 'Mũi', 'Thìn': 'Eo Lưng', 'Tỵ': 'Tay', 'Ngọ': 'Tim Bụng', 'Mùi': 'Chân', 'Thân': 'Đầu', 'Dậu': 'Lưng', 'Tuất': 'Đầu Họng', 'Hợi': 'Cổ Gáy'}
        self.NT_GIO = {'Tý': 'Mắt Cá', 'Sửu': 'Đầu', 'Dần': 'Tai', 'Mão': 'Mặt', 'Thìn': 'Cổ Gáy Hạng', 'Tỵ': 'Vú Ngực', 'Ngọ': 'Ngực', 'Mùi': 'Bụng', 'Thân': 'Tim', 'Dậu': 'Gối Lưng', 'Tuất': 'Eo Âm bộ', 'Hợi': 'Đùi'}

    def quet_benh_an(self, nam, thang, ngay_can, ngay_chi, gio, ngay_am, bo_phan, cac_gio_hoang_dao):
        benh_an_tho = []
        bo_phan = bo_phan.lower()
        chi_thang = self.CHI[(thang + 1) % 12]

        # 1. TAM PHÁ (Xung khắc rủi ro)
        if ngay_chi == self.LUC_XUNG.get(nam): benh_an_tho.append(f"[Tuế Phá]: Ngày {ngay_chi} xung Năm {nam}.")
        if ngay_chi == self.LUC_XUNG.get(chi_thang): benh_an_tho.append(f"[Nguyệt Phá]: Ngày {ngay_chi} xung Tháng {chi_thang}.")
        if gio == self.LUC_XUNG.get(ngay_chi): benh_an_tho.append(f"[Nhật Phá]: Giờ {gio} xung Ngày {ngay_chi}.")

        # 2. ĐẠI ĐẠO
        if gio in cac_gio_hoang_dao: benh_an_tho.append(f"[Hoàng Đạo]: Giờ {gio} - Khí quang hanh thông.")
        else: benh_an_tho.append(f"[Hắc Đạo]: Giờ {gio} - Trược khí cản trở.")

        # 3. TỨ ĐẠI HUNG TINH (Y Lý)
        if ngay_chi == self.HUYET_KY.get(thang): benh_an_tho.append("[Huyết Kỵ]: Có mặt (Kỵ chảy máu, dao kéo rạch da).")
        if ngay_chi == self.TU_KHI.get(thang): benh_an_tho.append("[Tử Khí]: Có mặt (Sinh khí cạn, kỵ can thiệp phẫu thuật nặng).")
        if ngay_chi == self.HUYET_CHI.get(thang): benh_an_tho.append("[Huyết Chi]: Có mặt (Da rỉ máu, tụ máu bầm, xuất huyết).")
        if gio == self.BENH_PHU.get(nam): benh_an_tho.append("[Bệnh Phù]: Có mặt (Trược khí hội tụ, dễ viêm nhiễm, lâu lành).")

        # 4. TAM ĐẠI CÁT THẦN (Y Khoa)
        if ngay_chi == self.THIEN_Y.get(thang): benh_an_tho.append("[Thiên Y]: Có mặt (Đại cát y tế, dễ gặp thầy giỏi thuốc hay).")
        if ngay_chi == self.DIA_Y.get(thang): benh_an_tho.append("[Địa Y]: Có mặt (Tốt cho đông y, bốc thuốc, điều dưỡng).")
        if gio == self.NHAT_Y.get(ngay_can): benh_an_tho.append(f"[Nhật Y]: Giờ {gio} cư ngụ (Có Thần Y trợ lực, giải trừ tai ách).")

        # 5. TAM SÁT NHÂN THẦN (Phân tách rõ ràng)
        # Theo Y Lý: Phạm Ngày -> Thích Huyết Sát | Phạm Can/Chi -> Thích Hại Sát | Phạm Giờ -> Âm Thương Sát
        nt_ngay_text = self.NT_NGAY.get(ngay_am, "")
        if nt_ngay_text and any(bp in nt_ngay_text.lower() or nt_ngay_text.lower() in bp for bp in bo_phan.split()):
            benh_an_tho.append(f"[Thích Huyết Sát]: Phạm Nhân Thần Ngày tại {nt_ngay_text.upper()}. Tuyệt đối kỵ rạch da, Thích Huyết.")

        nt_can_text = self.NT_CAN.get(ngay_can, "")
        nt_chi_text = self.NT_CHI.get(ngay_chi, "")
        if (nt_can_text and any(bp in nt_can_text.lower() or nt_can_text.lower() in bp for bp in bo_phan.split())) or \
           (nt_chi_text and any(bp in nt_chi_text.lower() or nt_chi_text.lower() in bp for bp in bo_phan.split())):
            benh_an_tho.append(f"[Thích Hại Sát]: Phạm Nhân Thần Can/Chi tại vùng {nt_can_text.upper()} - {nt_chi_text.upper()}. Nguy cơ tai biến nếu châm cứu (Thích Hại).")

        nt_gio_text = self.NT_GIO.get(gio, "")
        if nt_gio_text and any(bp in nt_gio_text.lower() or nt_gio_text.lower() in bp for bp in bo_phan.split()):
            benh_an_tho.append(f"[Âm Thương Sát]: Phạm Thời Thần (Giờ) tại {nt_gio_text.upper()}. Nguy cơ tổn thương ngầm, nội thương cơ xương khớp.")

        # 6. LƯU CHÚ KHÍ HUYẾT
        luu_chu_text = LUU_CHU_DETAILS.get(gio, "")
        if luu_chu_text and any(bp in luu_chu_text.lower() or luu_chu_text.lower() in bp for bp in bo_phan.split()):
            benh_an_tho.append(f"[Phạm Lưu Chú]: Khí huyết đang dồn về mãnh liệt. Cẩn thận sốc phản vệ hoặc xuất huyết cấp.")

        return "\n".join(benh_an_tho) if benh_an_tho else "[Bình Thường]: Không phạm sát tinh, không có cát thần."

# ==============================================================================
# GIAO DIỆN WEB VỚI STREAMLIT (THAY THẾ APP CŨ)
# ==============================================================================
# 1. Cấu hình trang
st.set_page_config(page_title="Y Lý Cát Thời", page_icon="logo.png", layout="wide")

import streamlit.components.v1 as components # Nhớ kéo lên đầu file dán dòng import này nếu chưa có nhé

# 2. Tiêu đề và Đồng hồ Client-side
# --- KHU VỰC TIÊU ĐỀ MỚI (CANH CHỈNH HOÀN HẢO 100%) ---

# 1. Hàm đọc và mã hóa file logo của bạn
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return "" # Nếu không tìm thấy file, sẽ không bị sập web

# Lấy mã của logo (Nhớ đảm bảo file tên là logo.png và để cùng thư mục)
img_base64 = get_base64_of_bin_file('logo.png')

# 2. Dùng Flexbox để khóa chặt Logo và Chữ trên cùng 1 trục ngang
st.markdown(
    f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{img_base64}" width="90" style="margin-right: 10px; border-radius: 8px;">
        <h1 style="margin: 0; padding: 0; font-size: 32px;">Y Lý Cát Thời - Kinh Dịch Hội - Mai Hoa Dịch Số</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")
# --------------------------------------------------------

# Đây là đoạn mã HTML/JS nhúng thẳng vào web. 
# Nó sẽ chạy trên trình duyệt của người dùng, lấy Múi Giờ và Thời Gian chính xác tại nơi họ đang đứng (từng giây một).
components.html("""
<div style="text-align: center; font-family: sans-serif; padding: 15px; background-color: #1E2022; color: white; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333;">
    <div style="font-size: 16px;">Dương Lịch (Đồng bộ theo múi giờ thiết bị của bạn)</div>
    <div id="clock" style="font-size: 24px; font-weight: bold; color: #D3A352; margin-top: 5px;">Đang tải thời gian...</div>
</div>
<script>
    function updateTime() {
        var now = new Date();
        var days = ['Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
        var dayName = days[now.getDay()];
        var dateStr = now.toLocaleDateString('vi-VN');
        var timeStr = now.toLocaleTimeString('vi-VN');
        document.getElementById('clock').innerHTML = "Hôm Nay Là : " + dayName + ", " + dateStr + " | " + timeStr;
    }
    setInterval(updateTime, 1000);
    updateTime();
</script>
""", height=110)

st.markdown("---")

engine = YLyCatThoiEngine()

# Lấy thời gian hiện tại làm mặc định
now = datetime.datetime.now()
dt_logic = now if now.hour < 23 else now + datetime.timedelta(days=1)
lunar_now = Converter.Solar2Lunar(Solar(dt_logic.year, dt_logic.month, dt_logic.day))

# 3. Chia màn hình làm 2 cột
col_trai, col_phai = st.columns([1, 1.5])

with col_trai:
    st.subheader("📋 Thông Tin Thời Gian")
    
    # =========================================================================
    # CSS CHUẨN XÁC: ĐỒNG BỘ 100% (VÀ TRẢ TỰ DO CHO Ô GIỜ KHÁM)
    # =========================================================================
    st.markdown("""
    <style>
    /* =========================================================
       1. ĐỒNG BỘ KÍCH THƯỚC (SIZE & BORDER) CHO 3 Ô DƯƠNG LỊCH
       ========================================================= */
    .st-key-duong_nam [data-baseweb="select"] > div,
    .st-key-duong_thang [data-baseweb="select"] > div,
    .st-key-duong_ngay [data-baseweb="select"] > div {
        background: #ffd6a8 !important;
        border: 2px solid #d27a1f !important;
        border-radius: 6px !important;
        height: 42px !important;
        min-height: 42px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    /* =========================================================
       2. ÉP MÀU CHỮ CAM (Sửa lỗi chữ đen do sai thẻ HTML)
       ========================================================= */
    .st-key-duong_nam [data-baseweb="select"] > div > div > div,
    .st-key-duong_thang [data-baseweb="select"] > div > div > div,
    .st-key-duong_ngay [data-baseweb="select"] > div > div > div,
    .st-key-duong_nam [data-baseweb="select"] input,
    .st-key-duong_thang [data-baseweb="select"] input,
    .st-key-duong_ngay [data-baseweb="select"] input {
        color: #c26000 !important;
        -webkit-text-fill-color: #c26000 !important;
        font-weight: bold !important;
    }

    .st-key-duong_nam [data-baseweb="select"] svg,
    .st-key-duong_thang [data-baseweb="select"] svg,
    .st-key-duong_ngay [data-baseweb="select"] svg {
        color: #c26000 !important;
    }

    .st-key-duong_nam [data-baseweb="select"]:focus-within > div,
    .st-key-duong_thang [data-baseweb="select"]:focus-within > div,
    .st-key-duong_ngay [data-baseweb="select"]:focus-within > div {
        border-color: #a9550f !important;
    }
    
    /* KHÔNG CÒN BẤT KỲ DÒNG RESET NÀO CHO GIỜ KHÁM Ở ĐÂY NỮA */
    </style>
    """, unsafe_allow_html=True)

    # 3.1 Khung nhập liệu Dương Lịch (Đã chuyển Năm sang Selectbox và cấp Key)
    c1, c2, c3 = st.columns(3)
    with c1:
        ds_nam = list(range(1900, 2036))
        nam_duong = st.selectbox(
            "Năm Dương Lịch",
            ds_nam,
            index=ds_nam.index(now.year),
            key="duong_nam"
        )
    with c2:
        thang_duong = st.selectbox(
            "Tháng Dương Lịch",
            list(range(1, 13)),
            index=now.month - 1,
            key="duong_thang"
        )
    with c3:
        max_days_duong = calendar.monthrange(int(nam_duong), thang_duong)[1]
        default_day = min(now.day, max_days_duong)
        ngay_duong = st.selectbox(
            "Ngày Dương Lịch",
            list(range(1, max_days_duong + 1)),
            index=default_day - 1,
            key="duong_ngay"
        )

    # LÕI QUY ĐỔI ÂM LỊCH
    solar_date = Solar(int(nam_duong), thang_duong, ngay_duong)
    lunar_date = Converter.Solar2Lunar(solar_date)
    nam_am, thang_am, ngay_am = lunar_date.year, lunar_date.month, lunar_date.day

    # 3.2 Khung hiển thị Âm Lịch
    c4, c5, c6 = st.columns(3)
    def ve_o_am_lich(tieu_de, gia_tri):
        return f'''
        <div style="font-size: 14px; margin-bottom: 6px; color: inherit; margin-top: 10px;">{tieu_de}</div>
        <div style="background-color: #9fcaff; border: 2px solid #004ccb; color: #004ccb; 
                    border-radius: 6px; padding: 0 12px; font-size: 15px; font-weight: bold;
                    height: 42px; display: flex; align-items: center; cursor: not-allowed; box-sizing: border-box;">
            {gia_tri}
        </div>
        '''

    with c4: st.markdown(ve_o_am_lich("Năm Âm Lịch", nam_am), unsafe_allow_html=True)
    with c5: st.markdown(ve_o_am_lich("Tháng Âm Lịch", thang_am), unsafe_allow_html=True)
    with c6: st.markdown(ve_o_am_lich("Ngày Âm Lịch", ngay_am), unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 3.3 Nhóm các công cụ thao tác (Đã cấp key="gio_kham" để cách ly CSS)
    gio_kham = st.selectbox(
        "Giờ Khám (Địa Chi)", 
        CHI, 
        index=((now.hour + 1) // 2) % 12,
        format_func=lambda x: GIO_HIENTHI[x],
        key="gio_kham"
    )
    
    bo_phan = st.text_input("Nhập bộ phận cơ thể cần khám (Mắt, Dạ dày, Răng...)")

    btn_phan_tich = st.button("🔍 Phân Tích Bệnh Án", type="primary", use_container_width=True)

    # 4. Tính toán Dịch Lý và thanh hiển thị Tứ Trụ
    data = tinh_can_chi_tu_ngay_duong(solar_date)
    st.info(f"**Năm:** {data['nam']} | **Tháng:** {data['thang']} | **Ngày:** {data['ngay']}")

# 5. Khung Cột Phải (Bảng 12 Giờ)
with col_phai:
    st.subheader("⏳ Bảng Cát Hung 12 Canh Giờ")
    
    # Chia tiếp làm 2 cột cho Hoàng Đạo và Hắc Đạo
    col_hd, col_hac = st.columns(2)
    
    # Chức năng Pop-up (Expander) của Streamlit thay thế cho Toplevel cũ
    with col_hd:
        st.markdown("### 🟢 Hoàng Đạo")
        for info in data['cac_gio']['Hoàng Đạo']:
            with st.expander(f"{info['can_chi']} ({info['ten_dao']})"):
                st.write(LUU_CHU_DETAILS.get(info['chi'], ""))

    with col_hac:
        st.markdown("### 🔴 Hắc Đạo")
        for info in data['cac_gio']['Hắc Đạo']:
            with st.expander(f"{info['can_chi']} ({info['ten_dao']})"):
                st.write(LUU_CHU_DETAILS.get(info['chi'], ""))

# 6. Khu vực AI Trả Lời
st.markdown("---")
st.subheader("📜 Thần Y Luận Giải")

# ==============================================================================
# HÀM AI LUẬN GIẢI (BẢN CHUẨN: TÍCH HỢP TÝ NGỌ LƯU CHÚ & THẦN SÁT)
# ==============================================================================
@st.cache_data(show_spinner=False, ttl=86400) 
def xin_loi_khuyen_ai(context_text):
    try:
        danh_sach_keys = st.secrets["GEMINI_API_KEYS"]
        key_duoc_chon = random.choice(danh_sach_keys)
        genai.configure(api_key=key_duoc_chon)
        
        # PROMPT "THẦN Y": NẠP TOÀN BỘ KIẾN THỨC CỐT LÕI VÀ BẢNG TRA CỨU
        prompt_bac_si = """
        Bạn là một vị Thần Y phương Đông, tinh thông Dịch Lý Y Khoa, Tý Ngọ Lưu Chú, hệ thống Nhân Thần và Thần Sát.
        Dưới đây là BỘ KIẾN THỨC CỐT LÕI BẮT BUỘC bạn phải dùng để hội chẩn:

        1. TÝ NGỌ LƯU CHÚ (Đồng hồ Tạng Phủ):
        - Tý (23h-1h): Đởm | Sửu (1h-3h): Can | Dần (3h-5h): Phế | Mão (5h-7h): Đại tràng
        - Thìn (7h-9h): Vị | Tỵ (9h-11h): Tỳ | Ngọ (11h-13h): Tâm | Mùi (13h-15h): Tiểu tràng
        - Thân (15h-17h): Bàng quang | Dậu (17h-19h): Thận | Tuất (19h-21h): Tâm bào | Hợi (21h-23h): Tam tiêu
        *Nguyên tắc:* Giờ vượng của tạng phủ nào thì KỴ châm cứu, phẫu thuật vào tạng phủ đó.

        2. LÝ THUYẾT NHÂN THẦN (Huyết Mạch Trú Ngụ):
        Khí huyết di chuyển và trú ngụ tại các bộ phận theo Can, Chi và Giờ. Phải đối chiếu bộ phận bệnh nhân muốn khám với bảng sau. Nếu trùng: TUYỆT ĐỐI CẤM đâm chích, mổ xẻ để tránh xuất huyết không cầm.
        - Nhân thần theo 10 Thiên Can: Giáp (Đầu), Ất (Cổ họng), Bính (Vai), Đinh (Ngực), Mậu (Bụng), Kỷ (Tỳ, Vị), Canh (Rốn), Tân (Đùi), Nhâm (Cẳng chân), Quý (Bàn chân).
        - Nhân thần theo 12 Địa Chi: Tý (Đầu), Sửu (Mắt, Tai, Mũi), Dần (Môi, Răng), Mão (Ngực, Lưng), Thìn (Bụng), Tỵ (Bàn tay), Ngọ (Tim, Ngực), Mùi (Dạ dày, Tỳ), Thân (Lưng, Đùi), Dậu (Đầu gối), Tuất (Cẳng chân), Hợi (Bàn chân).
        - Nhân thần theo 12 Canh Giờ: Tý (Mắt cá ngoài), Sửu (Mép, Răng, Hông), Dần (Lỗ tai), Mão (Mặt, Trán), Thìn (Ngực, Cổ tay), Tỵ (Bàn tay), Ngọ (Ngực, Rốn), Mùi (Gót chân), Thân (Lưng, Đùi), Dậu (Đầu gối, Mắt cá trong), Tuất (Bụng dưới, Âm bộ), Hợi (Bắp chân).

        3. 9 THẦN SÁT Y KHOA:
        - Cát Thần (Nên làm): Thiên Y, Địa Y, Nhật Y.
        - Hung Thần (Kỵ dao kéo, trích huyết): Thích Huyết Sát, Thích Hại Sát, Huyết Kỵ, Âm Thương Sát, Huyết Chi, Bệnh Phù, Tử Khí / Tử Thần.

        4. HỆ THỐNG XUNG PHÁ (Khí Huyết Hỗn Loạn):
        - Nhật Phá (Giờ xung Ngày), Nguyệt Phá (Ngày xung Tháng), Tuế Phá (Ngày xung Năm).
        *Nguyên tắc:* Phạm xung phá là lúc âm dương giao chiến, cấm can thiệp dao kéo.

        NHIỆM VỤ CỦA BẠN:
        Dựa vào [Kết quả Dịch Lý thô], rà soát ĐẦY ĐỦ 4 mục trên đối với "Cơ quan can thiệp". 
        - Trình bày rõ Nhân thần theo Can/Chi/Giờ hiện tại đang ở đâu, có phạm vào cơ quan cần khám không.
        - Tổng hợp thành KẾT LUẬN rõ ràng: Nên hay Không nên can thiệp vào giờ này.

        BỐ CỤC BẮT BUỘC:
        - ☯️ VẬN HÀNH TÝ NGỌ LƯU CHÚ & NHÂN THẦN
        - ⚔️ PHÂN TÍCH XUNG PHÁ & THẦN SÁT
        - ⚖️ KẾT LUẬN & ĐIỀU HƯỚNG Y KHOA
        """
        
        # Để Temp = 0.2 để AI vừa tuân thủ quy tắc, vừa linh hoạt trong câu chữ luận giải
        config = genai.GenerationConfig(temperature=0.2, top_k=1)
        model = genai.GenerativeModel('gemini-2.5-pro', system_instruction=prompt_bac_si, generation_config=config)
        
        response = model.generate_content(context_text)
        return response.text
    except Exception as e:
        return f"Lỗi hệ thống A.I: {e}"

# ==============================================================================
# NÚT BẤM VÀ HIỂN THỊ (ĐÃ BỔ SUNG LỚP AN TOÀN Y KHOA)
# ==============================================================================

# Danh sách các từ khóa báo hiệu tình trạng khẩn cấp
TU_KHOA_CAP_CUU = [
    'khó thở', 'đau ngực', 'sốt cao', 'co giật', 'liệt', 
    'chảy máu', 'nôn ra máu', 'cấp cứu', 'đột quỵ', 'đau dữ dội', 
    'bất tỉnh', 'mất nhận thức', 'gãy xương'
]

if btn_phan_tich:
    if not bo_phan:
        st.error("Lỗi: Lương y cần biết bạn muốn chữa/khám bộ phận nào.")
    else:
        # LỚP BẢO VỆ 1: Kiểm tra từ khóa cấp cứu
        is_cap_cuu = any(tu_khoa in bo_phan.lower() for tu_khoa in TU_KHOA_CAP_CUU)
        
        if is_cap_cuu:
            st.error("🚨 CẢNH BÁO Y KHOA KHẨN CẤP 🚨")
            st.warning("""
            Hệ thống phát hiện dấu hiệu nguy hiểm liên quan đến tính mạng. 
            Tuyệt đối không dùng thuốc Nam hay chờ đợi giờ tốt lúc này.
            **YÊU CẦU:** Gọi ngay cấp cứu 115 hoặc đến bệnh viện gần nhất ngay lập tức!
            """)
        else:
            # Nếu an toàn, tiếp tục phân tích Dịch Lý và gọi AI
            with st.spinner("Đang chẩn đoán mạch và hội chẩn Dịch Lý..."):
                
                # 1. Thuật toán tính toán Dịch Lý
                benh_an_tho = engine.quet_benh_an(
                    data['chi_nam'], thang_am, data['can_ngay'], 
                    data['chi_ngay'], gio_kham, ngay_am, bo_phan, data['hoang_dao_list']
                )

                # 2. Đóng gói dữ liệu gửi cho AI
                context = f"Thông tin Khám: Tháng {thang_am} Âm, Ngày {data['ngay']}, Giờ {gio_kham}.\nCơ quan can thiệp/Triệu chứng: {bo_phan}\nKết quả Dịch Lý thô:\n{benh_an_tho}"

                # 3. AI phân tích và trả kết quả
                loi_khuyen = xin_loi_khuyen_ai(context)
                
                if "Lỗi hệ thống" not in loi_khuyen:
                    st.success("Hoàn tất luận giải!")
                    st.write(loi_khuyen)
                else:
                    st.error(loi_khuyen)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 14px;'>© 2025 Y Lý Cát Thời - Kinh Dịch Hội - Mai Hoa Dịch Số- Ứng dụng thuộc bản quyền tác giả Chris Nhật Tôn. Vui lòng tham khảo ý kiến bác sĩ chuyên khoa trước khi áp dụng.</div>", unsafe_allow_html=True)