import streamlit as st
import google.generativeai as genai
import datetime
import calendar
import random
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
# --- KHU VỰC TIÊU ĐỀ MỚI CÓ LOGO TÙY CHỈNH ---
col_logo, col_title = st.columns([1, 20]) # Tạo 2 cột: Cột 1 rất nhỏ để chứa logo, cột 2 rộng để chứa chữ

with col_logo:
    # Bạn có thể thay đổi số 45 ở width để logo to ra hoặc nhỏ lại cho vừa mắt
    st.image("logo.png", width=90) 

with col_title:
    # Dùng HTML để đẩy dòng chữ lên một chút cho thẳng hàng canh giữa với Logo
    st.markdown("<h1 style='margin-top: -15px;'>Y Lý Cát Thời - Kinh Dịch Hội - Mai Hoa Dịch Số</h1>", unsafe_allow_html=True)
# ----------------------------------------------

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
    
    # 3.1 Khung nhập liệu Dương Lịch (Bỏ tiêu đề, đổi tên nhãn)
    c1, c2, c3 = st.columns(3)
    with c1:
        nam_duong = st.selectbox("Năm Dương Lịch", range(2024, 2036), index=now.year - 2024)
    with c2:
        thang_duong = st.selectbox("Tháng Dương Lịch", range(1, 13), index=now.month - 1)
    with c3:
        max_days_duong = calendar.monthrange(nam_duong, thang_duong)[1]
        default_day = min(now.day, max_days_duong) 
        ngay_duong = st.selectbox("Ngày Dương Lịch", range(1, max_days_duong + 1), index=default_day - 1)

    # =========================================================================
    # LÕI QUY ĐỔI: Chuyển Dương sang Âm 
    # =========================================================================
    solar_date = Solar(nam_duong, thang_duong, ngay_duong)
    lunar_date = Converter.Solar2Lunar(solar_date)

    nam_am = lunar_date.year
    thang_am = lunar_date.month
    ngay_am = lunar_date.day

    # 3.2 Khung hiển thị Âm Lịch
    c4, c5, c6 = st.columns(3)
    with c4:
        # Mẹo: Dùng selectbox với 1 giá trị duy nhất trong danh sách [ ]
        # Ô sẽ giữ nguyên màu sắc bình thường, click được nhưng không thể đổi giá trị
        st.selectbox("Năm Âm Lịch", [nam_am])
    with c5:
        st.selectbox("Tháng Âm Lịch", [thang_am])
    with c6:
        st.selectbox("Ngày Âm Lịch", [ngay_am])

    # ĐÃ CẬP NHẬT: Dùng format_func để gán bộ từ điển GIO_HIENTHI vào dropdown
    gio_kham = st.selectbox(
        "Giờ Khám (Địa Chi)", 
        CHI, 
        index=((now.hour + 1) // 2) % 12,
        format_func=lambda x: GIO_HIENTHI[x] 
    )
    
    bo_phan = st.text_input("Nhập bộ phận cơ thể cần khám(Mắt, Dạ dày, Răng...)")

    btn_phan_tich = st.button("🔍 Phân Tích Bệnh Án", type="primary", use_container_width=True)

# 4. Tính toán Dịch Lý chạy ẩn phía sau
solar_date = Converter.Lunar2Solar(Lunar(nam_am, thang_am, ngay_am))
data = tinh_can_chi_tu_ngay_duong(solar_date)

with col_trai:
    st.info(f"**Năm:** {data['nam']} | **Ngày:** {data['ngay']}")

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
# TUYỆT CHIÊU CACHING: Bộ nhớ đệm giúp lưu lại các ca bệnh trùng nhau
# ==============================================================================
@st.cache_data(show_spinner=False, ttl=86400) # ttl=86400: Nhớ kết quả trong 1 ngày (24h)
def xin_loi_khuyen_ai(context_text):
    try:
        # 1. Bốc thăm ngẫu nhiên 1 trong số các API Key bạn có trong két sắt
        danh_sach_keys = st.secrets["GEMINI_API_KEYS"]
        key_duoc_chon = random.choice(danh_sach_keys)
        
        genai.configure(api_key=key_duoc_chon)
        
        # 2. Prompt Thần Y (Giữ nguyên)
        prompt_bac_si = """
        Bạn là một vị Lương Y uyên bác, am hiểu sâu sắc về Dịch Lý Y Khoa (Y Lý Cát Thời).
        Nhiệm vụ của bạn là phân tích sự tương tác giữa khí huyết cơ thể và thời gian (Năm, Tháng, Ngày, Giờ) để đưa ra lời khuyên về THỜI ĐIỂM can thiệp y tế.
        
        NGUYÊN TẮC TỐI THƯỢNG (BẮT BUỘC TUÂN THỦ 100%):
        1. BÁM SÁT DỮ LIỆU: Chỉ được phép luận giải dựa trên những Sát Tinh, Cát Thần và [Phạm Nhân Thần / Phạm Lưu Chú] CÓ TRONG "Kết quả Dịch Lý thô".
        2. KHÔNG BỊA ĐẶT: Tuyệt đối không tự ý lôi thêm các kiến thức tử vi, phong thủy bên ngoài (ví dụ: Tam Nương, Nguyệt Kỵ, Kim Lâu, Không Vong...) vào để hù dọa bệnh nhân.
        3. GIỚI HẠN CHUẨN ĐOÁN (Xử lý trạng thái [Bình Thường]):
           - Bạn chỉ xem xét sự thuận lợi của "Thời Điểm", KHÔNG chẩn đoán mức độ nặng nhẹ của "Bệnh Lý".
           - Nếu "Kết quả Dịch Lý thô" ghi là [Bình Thường]: Tuyệt đối KHÔNG được dùng từ "An toàn cho sức khỏe". Hãy kết luận chuẩn mực theo Dịch lý: "Thời điểm này khí huyết bình hòa, không vướng các cấm kỵ Sát tinh, là thời điểm trung tính, thuận lợi để tiến hành thăm khám hoặc trị liệu."
        
        BỐ CỤC TRÌNH BÀY BẮT BUỘC:
        - ☯️ PHÂN TÍCH MẠCH LÝ DỊCH SỐ: Dựa đúng vào các dòng Sát/Cát trong kết quả thô để giải thích hiện tượng khí huyết (tụ hay tán, sinh hay khắc).
        - ⚠️ LUẬN GIẢI THỦ THUẬT: Đọc kỹ phần [Phạm Nhân Thần] hoặc [Phạm Lưu Chú] để cảnh báo rõ ràng về các thao tác xâm lấn: Thích Huyết (rạch da, mổ), Thích Hại (châm cứu) hoặc Âm Thương (nội soi, nắn xương).
        - 📝 CHỈ ĐỊNH CỦA LƯƠNG Y: Kết luận dứt khoát về mặt thời gian: THÍCH HỢP LÀM NGAY hay NÊN DỜI NGÀY KHÁC (nếu phạm quá nhiều Sát tinh).
        - 🏥 KHUYẾN CÁO Y KHOA (In nghiêng ở cuối cùng): "Lưu ý: Luận giải trên chỉ áp dụng để chọn thời điểm tốt nhất theo Y Lý Á Đông. Nếu bạn đang trong tình trạng đau đớn cấp tính, chấn thương hoặc nguy kịch, hãy đến ngay phòng Cấp cứu (Emergency) gần nhất. Việc cứu người là tối thượng, tuyệt đối không trì hoãn để chờ đợi giờ tốt."
        """
        
        config = genai.GenerationConfig(temperature=0.2, top_k=1)
        
        # 3. CHUYỂN SANG MÔ HÌNH FLASH SIÊU TỐC ĐỘ VÀ MIỄN PHÍ CAO
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=prompt_bac_si, generation_config=config)
        
        response = model.generate_content(context_text)
        return response.text
    except Exception as e:
        return f"Lỗi hệ thống A.I: {e}"

# ==============================================================================
# NÚT BẤM VÀ HIỂN THỊ
# ==============================================================================
if btn_phan_tich:
    if not bo_phan:
        st.error("Lỗi: Lương y cần biết bạn muốn chữa/khám bộ phận nào.")
    else:
        with st.spinner("Đang chẩn đoán mạch và hội chẩn với A.I..."):
            
            # 1. Máy tính vẫn chạy ngầm và tính toán đủ 100% quy tắc
            benh_an_tho = engine.quet_benh_an(
                data['chi_nam'], thang_am, data['can_ngay'], 
                data['chi_ngay'], gio_kham, ngay_am, bo_phan, data['hoang_dao_list']
            )

            # 2. Dữ liệu thô vẫn được bí mật nhét vào Prompt cho AI
            context = f"Thông tin Khám: Tháng {thang_am} Âm, Ngày {data['ngay']}, Giờ {gio_kham}.\nCơ quan can thiệp: {bo_phan}\nKết quả Dịch Lý thô:\n{benh_an_tho}"

            # 3. AI phân tích và trả về văn bản Lương Y
            loi_khuyen = xin_loi_khuyen_ai(context)
            
            if "Lỗi hệ thống" not in loi_khuyen:
                st.success("Hoàn tất luận giải!")
                st.write(loi_khuyen)
            else:
                st.error(loi_khuyen)