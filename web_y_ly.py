import streamlit as st
import google.generativeai as genai
import datetime
import calendar
import random
import base64
import json
from lunarcalendar import Converter, Solar, Lunar
import streamlit.components.v1 as components

def get_device_now():
    raw = st.query_params.get("client_now")
    if raw:
        try:
            return datetime.datetime.fromisoformat(raw)
        except:
            pass
    return datetime.datetime.now()

def get_client_layout():
    raw = st.query_params.get("client_layout")
    if raw:
        return str(raw).strip().lower()
    return "desktop"

# THÊM DÒNG NÀY ĐỂ DÙNG LỊCH TIẾT KHÍ:
import lunar_python
# ==============================================================================
# BỘ DỮ LIỆU TỪ ĐIỂN TIẾT KHÍ, NGŨ HÀNH VÀ MÀU SẮC GIAO DIỆN
# ==============================================================================
TU_DIEN_CAN_CHI_LP = {'甲': 'Giáp', '乙': 'Ất', '丙': 'Bính', '丁': 'Đinh', '戊': 'Mậu', '己': 'Kỷ', '庚': 'Canh', '辛': 'Tân', '壬': 'Nhâm', '癸': 'Quý', '子': 'Tý', '丑': 'Sửu', '寅': 'Dần', '卯': 'Mão', '辰': 'Thìn', '巳': 'Tỵ', '午': 'Ngọ', '未': 'Mùi', '申': 'Thân', '酉': 'Dậu', '戌': 'Tuất', '亥': 'Hợi'}

NGU_HANH_CAN = {"Giáp": "Mộc", "Ất": "Mộc", "Bính": "Hỏa", "Đinh": "Hỏa", "Mậu": "Thổ", "Kỷ": "Thổ", "Canh": "Kim", "Tân": "Kim", "Nhâm": "Thủy", "Quý": "Thủy"}
NGU_HANH_CHI = {"Dần": "Mộc", "Mão": "Mộc", "Tỵ": "Hỏa", "Ngọ": "Hỏa", "Thìn": "Thổ", "Tuất": "Thổ", "Sửu": "Thổ", "Mùi": "Thổ", "Thân": "Kim", "Dậu": "Kim", "Hợi": "Thủy", "Tý": "Thủy"}
AM_DUONG_CAN = {
    "Giáp": "Dương", "Ất": "Âm",
    "Bính": "Dương", "Đinh": "Âm",
    "Mậu": "Dương", "Kỷ": "Âm",
    "Canh": "Dương", "Tân": "Âm",
    "Nhâm": "Dương", "Quý": "Âm"
}

# Tàng can theo Chủ (chính khí) / Kiêm (trung + dư khí)
CHI_TANG_CAN_META = {
    "Tý":  {"chu": ["Quý"], "kiem": []},
    "Sửu": {"chu": ["Kỷ"], "kiem": ["Quý", "Tân"]},
    "Dần": {"chu": ["Giáp"], "kiem": ["Bính", "Mậu"]},
    "Mão": {"chu": ["Ất"], "kiem": []},
    "Thìn":{"chu": ["Mậu"], "kiem": ["Ất", "Quý"]},
    "Tỵ":  {"chu": ["Bính"], "kiem": ["Mậu", "Canh"]},
    "Ngọ": {"chu": ["Đinh"], "kiem": ["Kỷ"]},
    "Mùi": {"chu": ["Kỷ"], "kiem": ["Đinh", "Ất"]},
    "Thân":{"chu": ["Canh"], "kiem": ["Nhâm", "Mậu"]},
    "Dậu": {"chu": ["Tân"], "kiem": []},
    "Tuất":{"chu": ["Mậu"], "kiem": ["Tân", "Đinh"]},
    "Hợi": {"chu": ["Nhâm"], "kiem": ["Giáp"]},
}

# 12 Trường Sinh (tính theo Nhật Can)
TRUONG_SINH_STAGES = [
    "Trường Sinh","Mộc Dục","Quan Đới","Lâm Quan","Đế Vượng","Suy",
    "Bệnh","Tử","Mộ","Tuyệt","Thai","Dưỡng"
]

# Điểm “Trường Sinh” bắt đầu theo từng Nhật Can
TRUONG_SINH_START = {
    "Giáp":"Hợi", "Ất":"Ngọ",
    "Bính":"Dần", "Đinh":"Dậu",
    "Mậu":"Dần", "Kỷ":"Thân",
    "Canh":"Tỵ",  "Tân":"Tý",
    "Nhâm":"Thân","Quý":"Mão",
}
MAU_NGU_HANH = {"Hỏa": "#d90000", "Thủy": "#0066d9", "Mộc": "#006c00", "Kim": "#7e7e7e", "Thổ": "#8b6200"}
JIEQI_VIET = {
    "立春": "Lập Xuân",
    "雨水": "Vũ Thủy",
    "惊蛰": "Kinh Trập",
    "春分": "Xuân Phân",
    "清明": "Thanh Minh",
    "谷雨": "Cốc Vũ",
    "立夏": "Lập Hạ",
    "小满": "Tiểu Mãn",
    "芒种": "Mang Chủng",
    "夏至": "Hạ Chí",
    "小暑": "Tiểu Thử",
    "大暑": "Đại Thử",
    "立秋": "Lập Thu",
    "处暑": "Xử Thử",
    "白露": "Bạch Lộ",
    "秋分": "Thu Phân",
    "寒露": "Hàn Lộ",
    "霜降": "Sương Giáng",
    "立冬": "Lập Đông",
    "小雪": "Tiểu Tuyết",
    "大雪": "Đại Tuyết",
    "冬至": "Đông Chí",
    "小寒": "Tiểu Hàn",
    "大寒": "Đại Hàn"
}
# CÁI NÀY BẠN THÊM VÀO TRƯỚC HÀM render_ui_battu_tietkhi
def load_chutinh_images():
    # Sử dụng hàm get_base64_of_bin_file mà bạn đã có sẵn ở dưới
    danh_sach = {
        "Chính Ấn": "chinhan.png",
        "Chính Quan": "chinhquan.png",
        "Chính Tài": "chinhtai.png",
        "Kiếp Tài": "kieptai.png",
        "Thất Sát": "thatsat.png",
        "Thiên Ấn": "thienan.png",
        "Thiên Tài": "thientai.png",
        "Thực Thần": "thucthan.png",
        "Thương Quan": "thuongquan.png",
        "Tỷ Kiên": "tykien.png",    # Nếu bạn có file này
        "Nhật Chủ": "nhatchu.png"
    }
    
    img_dict = {}
    for ten, ten_file in danh_sach.items():
        try:
            with open(ten_file, 'rb') as f:
                img_dict[ten] = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        except FileNotFoundError:
            img_dict[ten] = "" # Bỏ trống nếu thiếu file
    return img_dict

DICT_HINH_CHU_TINH = load_chutinh_images()
def render_ui_battu_tietkhi(
    nam, thang, ngay, gio_chi_name,
    gio_display=None, live_from_device=False,
    actual_hour=None, actual_minute=None, actual_second=None
):
    if actual_hour is None:
        h_val = CHI_TO_HOUR[gio_chi_name] + 1
        if h_val >= 24: h_val = 0
        m_val = 30; s_val = 0
    else:
        h_val = int(actual_hour)
        m_val = int(actual_minute or 0)
        s_val = int(actual_second or 0)

    solar_lp = lunar_python.Solar.fromYmdHms(int(nam), int(thang), int(ngay), h_val, m_val, s_val)
    lunar_lp = solar_lp.getLunar()

    can_nam = TU_DIEN_CAN_CHI_LP[lunar_lp.getYearGanExact()]
    chi_nam = TU_DIEN_CAN_CHI_LP[lunar_lp.getYearZhiExact()]
    can_thang = TU_DIEN_CAN_CHI_LP[lunar_lp.getMonthGanExact()]
    chi_thang = TU_DIEN_CAN_CHI_LP[lunar_lp.getMonthZhiExact()]
    can_ngay = TU_DIEN_CAN_CHI_LP[lunar_lp.getDayGanExact()]
    chi_ngay = TU_DIEN_CAN_CHI_LP[lunar_lp.getDayZhiExact()]
    can_gio = TU_DIEN_CAN_CHI_LP[lunar_lp.getTimeGan()]
    chi_gio = TU_DIEN_CAN_CHI_LP[lunar_lp.getTimeZhi()]
    
    current_jq_name = "—"
    next_jq_name = "—"
    next_jq_iso = ""

    try:
        prev_jq = lunar_lp.getPrevJieQi(False)
        next_jq = lunar_lp.getNextJieQi(False)
        if prev_jq: current_jq_name = prev_jq.getName()
        if next_jq:
            next_jq_name = next_jq.getName()
            next_solar = next_jq.getSolar()
            next_jq_iso = f"{next_solar.getYear():04d}-{next_solar.getMonth():02d}-{next_solar.getDay():02d}T{next_solar.getHour():02d}:{next_solar.getMinute():02d}:{next_solar.getSecond():02d}"
    except Exception:
        pass

    if gio_display is None:
        gio_display = f"{h_val:02d}:{m_val:02d}:{s_val:02d}"

    pillars = [
        {"key": "year",  "title": "Năm",   "val": str(nam),            "can": can_nam,   "chi": chi_nam},
        {"key": "month", "title": "Tháng", "val": f"{int(thang):02d}", "can": can_thang, "chi": chi_thang},
        {"key": "day",   "title": "Ngày",  "val": f"{int(ngay):02d}",  "can": can_ngay,  "chi": chi_ngay},
        {"key": "hour",  "title": "Giờ",   "val": gio_display,         "can": can_gio,   "chi": chi_gio},
    ]

    cards = []
    for p in pillars:
        nap_am, hanh_na = NA_AM_60.get(f"{p['can']} {p['chi']}", ("Chưa rõ", "Thổ"))
        mau_can = MAU_NGU_HANH.get(NGU_HANH_CAN.get(p["can"]), "#333")
        mau_chi = MAU_NGU_HANH.get(NGU_HANH_CHI.get(p["chi"]), "#333")
        mau_ombre = MAU_NEN_OMBRE.get(hanh_na, "linear-gradient(180deg, #fff 0%, #f0f0f0 100%)")
        mau_vien = MAU_NGU_HANH.get(hanh_na, "#dddddd")
        prefix = p["key"]
        
        # BƠM MÀU TRỰC TIẾP TỪ PYTHON ĐỂ KHÔNG BAO GIỜ BỊ TRẮNG XÓA
        cards.append(
            f'<div class="bt-card" id="bt-{prefix}-card" style="background:{mau_ombre}; border: 1.5px solid {mau_vien}88;">'
            f'  <div class="bt-title">{p["title"]}</div>'
            f'  <div class="bt-val" id="bt-{prefix}-val">{p["val"]}</div>'
            f'  <div class="bt-chutinh" id="bt-{prefix}-ct"></div>'
            f'  <div class="bt-canchi-vert">'
            f'      <div id="bt-{prefix}-can" class="bt-can" style="color:{mau_can};">{p["can"].upper()}</div>'
            f'      <div id="bt-{prefix}-chi" class="bt-chi" style="color:{mau_chi};">{p["chi"].upper()}</div>'
            f'  </div>'
            f'  <div class="bt-tang-pho-grid">'
            f'      <div class="bt-tang" id="bt-{prefix}-tang"></div>'
            f'      <div class="bt-pho" id="bt-{prefix}-pho"></div>'
            f'  </div>'
            f'  <div class="bt-truongsinh" id="bt-{prefix}-ts">—</div>'
            f'  <div class="bt-napam" id="bt-{prefix}-napam" style="color:{mau_vien};">{nap_am}</div>'
            f'</div>'
        )

    cards_html = "".join(cards)
    
    live_script = ""
    if live_from_device:
        # PHẦN 1: BƠM BIẾN (F-STRING)
        live_script_vars = f"""
        <script>
            const TU_DIEN = {json.dumps(TU_DIEN_CAN_CHI_LP, ensure_ascii=False)};
            const NA_AM_60 = {json.dumps(NA_AM_60, ensure_ascii=False)};
            const MAU_NGU_HANH = {json.dumps(MAU_NGU_HANH, ensure_ascii=False)};
            const NGU_HANH_CAN = {json.dumps(NGU_HANH_CAN, ensure_ascii=False)};
            const NGU_HANH_CHI = {json.dumps(NGU_HANH_CHI, ensure_ascii=False)};
            const AM_DUONG_CAN = {json.dumps(AM_DUONG_CAN, ensure_ascii=False)};
            const CHI_TANG_CAN_META = {json.dumps(CHI_TANG_CAN_META, ensure_ascii=False)};
            const TRUONG_SINH_START = {json.dumps(TRUONG_SINH_START, ensure_ascii=False)};
            const TRUONG_SINH_STAGES = {json.dumps(TRUONG_SINH_STAGES, ensure_ascii=False)};
            const MAU_NEN_OMBRE = {json.dumps(MAU_NEN_OMBRE, ensure_ascii=False)};
            const INITIAL_CURRENT_TERM = {json.dumps(current_jq_name, ensure_ascii=False)};
            const INITIAL_NEXT_TERM = {json.dumps(next_jq_name, ensure_ascii=False)};
            const INITIAL_NEXT_TERM_ISO = {json.dumps(next_jq_iso, ensure_ascii=False)};
            const JIEQI_VIET = {json.dumps(JIEQI_VIET, ensure_ascii=False)};
            const CAN_ORDER = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"];
            const CHI_ORDER = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
            
            // MAP HÌNH ẢNH LOGO (Bạn nhớ giữ hàm load_chutinh_images() ở trên nhé)
            const CHU_TINH_IMAGES = {json.dumps(DICT_HINH_CHU_TINH, ensure_ascii=False) if 'DICT_HINH_CHU_TINH' in globals() else "{}"};
        </script>
        """

        # PHẦN 2: LOGIC JS (CHUỖI RAW THÔNG THƯỜNG - KHÔNG SỢ LỖI { })
        live_script_logic = """
        <script>
            function pad2(n) { return String(n).padStart(2, "0"); }
            function setOnlyValue(prefix, valueText) {
                const valEl = document.getElementById(`bt-${prefix}-val`);
                if (valEl) valEl.textContent = valueText;
            }
            function getNapAm(can, chi) {
                const key = `${can} ${chi}`;
                return NA_AM_60[key] || ["Chưa rõ", "Thổ"];
            }
            function mapCn(ch) { return TU_DIEN[ch] || ch; }
            function mapJieQiName(name) { return JIEQI_VIET[name] || name || "—"; }

            const CAN_NORM = {"GIÁP":"Giáp","ẤT":"Ất","BÍNH":"Bính","ĐINH":"Đinh","MẬU":"Mậu","KỶ":"Kỷ","CANH":"Canh","TÂN":"Tân","NHÂM":"Nhâm","QUÝ":"Quý"};
            const CHI_NORM = {"TÝ":"Tý","SỬU":"Sửu","DẦN":"Dần","MÃO":"Mão","THÌN":"Thìn","TỴ":"Tỵ","NGỌ":"Ngọ","MÙI":"Mùi","THÂN":"Thân","DẬU":"Dậu","TUẤT":"Tuất","HỢI":"Hợi"};

            function normCanText(s) { if(!s) return ""; s=(""+s).trim().toUpperCase(); return CAN_NORM[s] || s; }
            function normChiText(s) { if(!s) return ""; s=(""+s).trim().toUpperCase(); return CHI_NORM[s] || s; }

            const SINH = {"Mộc":"Hỏa","Hỏa":"Thổ","Thổ":"Kim","Kim":"Thủy","Thủy":"Mộc"};
            const KHAC = {"Mộc":"Thổ","Thổ":"Thủy","Thủy":"Hỏa","Hỏa":"Kim","Kim":"Mộc"};
            function sameYinYang(a,b) { return (AM_DUONG_CAN[a]||"") === (AM_DUONG_CAN[b]||""); }

            function getTenGod(dayCan, otherCan){
              const eDay = NGU_HANH_CAN[dayCan];
              const eOther = NGU_HANH_CAN[otherCan];
              if(!eDay || !eOther) return {full:"—", short:"—"};
              const sameYY = sameYinYang(dayCan, otherCan);

              if(eDay === eOther) return sameYY ? {full:"Tỷ Kiên", short:"T.Kiên"} : {full:"Kiếp Tài", short:"K.Tài"};
              if(SINH[eDay] === eOther) return sameYY ? {full:"Thực Thần", short:"T.Thần"} : {full:"Thương Quan", short:"T.Quan"};
              if(SINH[eOther] === eDay) return sameYY ? {full:"Thiên Ấn", short:"T.Ấn"} : {full:"Chính Ấn", short:"C.Ấn"};
              if(KHAC[eDay] === eOther) return sameYY ? {full:"Thiên Tài", short:"T.Tài"} : {full:"Chính Tài", short:"C.Tài"};
              if(KHAC[eOther] === eDay) return sameYY ? {full:"Thất Sát", short:"T.Sát"} : {full:"Chính Quan", short:"C.Quan"};
              return {full:"—", short:"—"};
            }

            function getTruongSinh(dayCan, chi){
              const start = TRUONG_SINH_START[dayCan];
              if(!start) return "—";
              const idxStart = CHI_ORDER.indexOf(start);
              const idxChi = CHI_ORDER.indexOf(chi);
              if(idxStart < 0 || idxChi < 0) return "—";
              const dir = (AM_DUONG_CAN[dayCan] === "Dương") ? 1 : -1;
              const delta = (idxChi - idxStart) * dir;
              const k = ((delta % 12) + 12) % 12;
              return TRUONG_SINH_STAGES[k] || "—";
            }

            function updatePillarTenGod(prefix, dayCan){
              const canEl = document.getElementById("bt-"+prefix+"-can");
              const chiEl = document.getElementById("bt-"+prefix+"-chi");
              const ctEl  = document.getElementById("bt-"+prefix+"-ct");
              const tangEl= document.getElementById("bt-"+prefix+"-tang");
              const phoEl = document.getElementById("bt-"+prefix+"-pho");
              const tsEl  = document.getElementById("bt-"+prefix+"-ts");
              if(!canEl || !chiEl) return;

              // Lấy textContent để an toàn 100%
              const can = normCanText(canEl.textContent);
              const chi = normChiText(chiEl.textContent);

              // 1. Chèn Logo Chủ Tinh
              if(ctEl){
                const godName = (prefix === "day") ? "Nhật Chủ" : getTenGod(dayCan, can).full;
                const imgSrc = CHU_TINH_IMAGES[godName];
                if(imgSrc && imgSrc.length > 10) {
                    ctEl.innerHTML = `<img src="${imgSrc}" class="img-logo-chutinh" alt="${godName}">`;
                } else {
                    // Fallback cực đẹp nếu bạn lỡ xóa file png
                    ctEl.innerHTML = `<div class="fallback-ct">${godName.toUpperCase()}</div>`;
                }
              }

              // 2. Chèn Tàng Ẩn (có màu) & Phó Tinh (viết tắt)
              const meta = CHI_TANG_CAN_META[chi] || {chu:[], kiem:[]};
              const tangList = (meta.chu||[]).concat(meta.kiem||[]);
              
              let tangHTML = "";
              let phoHTML = "";
              tangList.forEach(tc => {
                  const pt = getTenGod(dayCan, tc).short;
                  const color = MAU_NGU_HANH[NGU_HANH_CAN[tc]] || "#333";
                  tangHTML += `<span style="color:${color};">${tc}</span>`;
                  phoHTML += `<span>${pt}</span>`;
              });
              
              if(tangEl) tangEl.innerHTML = tangHTML;
              if(phoEl) phoEl.innerHTML = phoHTML;

              // 3. Trường Sinh
              if(tsEl) tsEl.textContent = getTruongSinh(dayCan, chi);
            }

            function updateThapThanAll(){
              const dayCanEl = document.getElementById("bt-day-can");
              if(!dayCanEl) return;
              const dayCan = normCanText(dayCanEl.textContent);
              ["year","month","day","hour"].forEach(p => updatePillarTenGod(p, dayCan));
            }

            function applyPillarMeta(prefix, can, chi) {
                const cardEl = document.getElementById(`bt-${prefix}-card`);
                const canEl = document.getElementById(`bt-${prefix}-can`);
                const chiEl = document.getElementById(`bt-${prefix}-chi`);
                const napamEl = document.getElementById(`bt-${prefix}-napam`);

                if (canEl) {
                    canEl.textContent = String(can).toUpperCase();
                    canEl.style.color = MAU_NGU_HANH[NGU_HANH_CAN[can]] || "#333";
                }
                if (chiEl) {
                    chiEl.textContent = String(chi).toUpperCase();
                    chiEl.style.color = MAU_NGU_HANH[NGU_HANH_CHI[chi]] || "#333";
                }

                const napInfo = getNapAm(can, chi);
                const mauVien = MAU_NGU_HANH[napInfo[1]] || "#dddddd";

                if (napamEl) {
                    napamEl.textContent = napInfo[0];
                    napamEl.style.color = mauVien;
                }
                if (cardEl) {
                    cardEl.style.background = MAU_NEN_OMBRE[napInfo[1]] || "linear-gradient(180deg, #fff 0%, #f0f0f0 100%)";
                    cardEl.style.border = `1.5px solid ${mauVien}88`;
                }
            }

            function solarToOrdinal(y, m, d) {
                const a = Math.floor((14 - m) / 12);
                const y1 = y + 4800 - a;
                const m1 = m + 12 * a - 3;
                const jdn = d + Math.floor((153 * m1 + 2) / 5) + 365 * y1 + Math.floor(y1 / 4) - Math.floor(y1 / 100) + Math.floor(y1 / 400) - 32045;
                return jdn - 1721425;
            }
            function getDayCanChiByAppRule(now) {
                const ordinal = solarToOrdinal(now.getFullYear(), now.getMonth() + 1, now.getDate());
                const canIdx = (ordinal + 4) % 10;
                const chiIdx = (ordinal + 2) % 12;
                return { can: CAN_ORDER[canIdx], chi: CHI_ORDER[chiIdx], canIdx: canIdx };
            }
            function getHourChiIndex(hour24) { return Math.floor((hour24 + 1) / 2) % 12; }
            function getHourCanChiByAppRule(now, dayCanIdx) {
                const chiIdx = getHourChiIndex(now.getHours());
                const canIdx = (dayCanIdx * 2 + chiIdx) % 10;
                return { can: CAN_ORDER[canIdx], chi: CHI_ORDER[chiIdx] };
            }
            function solarObjToDate(solarObj) {
                return new Date(solarObj.getYear(), solarObj.getMonth() - 1, solarObj.getDay(), solarObj.getHour(), solarObj.getMinute(), solarObj.getSecond());
            }
            function formatCountdown(ms) {
                if (ms < 0) ms = 0;
                const totalSeconds = Math.floor(ms / 1000);
                return { days: Math.floor(totalSeconds / 86400), hours: Math.floor((totalSeconds % 86400) / 3600), minutes: Math.floor((totalSeconds % 3600) / 60), seconds: totalSeconds % 60 };
            }
            function resizeIframeToContent() {
                try {
                    const h = Math.max(document.body ? document.body.scrollHeight : 0, document.documentElement ? document.documentElement.scrollHeight : 0);
                    if (window.frameElement && h > 0) window.frameElement.style.height = `${h + 8}px`;
                } catch (e) {}
            }
            function updateValuesFromDeviceOnly() {
                const now = new Date();
                setOnlyValue("year", String(now.getFullYear()));
                setOnlyValue("month", pad2(now.getMonth() + 1));
                setOnlyValue("day", pad2(now.getDate()));
                setOnlyValue("hour", `${pad2(now.getHours())}:${pad2(now.getMinutes())}:${pad2(now.getSeconds())}`);
            }

            function updateExactCanChi() {
                const now = new Date();
                const dayInfo = getDayCanChiByAppRule(now);
                const hourInfo = getHourCanChiByAppRule(now, dayInfo.canIdx);

                applyPillarMeta("day", dayInfo.can, dayInfo.chi);
                applyPillarMeta("hour", hourInfo.can, hourInfo.chi);

                if (typeof window.Solar !== "undefined") {
                    const solar = window.Solar.fromYmdHms(now.getFullYear(), now.getMonth() + 1, now.getDate(), now.getHours(), now.getMinutes(), now.getSeconds());
                    const lunar = solar.getLunar();
                    applyPillarMeta("year", mapCn(lunar.getYearGanExact()), mapCn(lunar.getYearZhiExact()));
                    applyPillarMeta("month", mapCn(lunar.getMonthGanExact()), mapCn(lunar.getMonthZhiExact()));
                }
                
                // ĐÂY LÀ CHÌA KHÓA: Gọi hàm tính thập thần luôn luôn chạy dù Lịch Âm tải xong hay chưa
                updateThapThanAll(); 
                return true;
            }

            function updateJieQiInfo() {
                const currentEl = document.getElementById("bt-current-term");
                const countdownEl = document.getElementById("bt-next-term-countdown");
                if (!currentEl || !countdownEl) return false;
                let currentName = INITIAL_CURRENT_TERM || "—";
                let nextName = INITIAL_NEXT_TERM || "—";
                let nextDate = INITIAL_NEXT_TERM_ISO ? new Date(INITIAL_NEXT_TERM_ISO) : null;

                if (typeof window.Solar !== "undefined") {
                    try {
                        const now = new Date();
                        const lunar = window.Solar.fromYmdHms(now.getFullYear(), now.getMonth() + 1, now.getDate(), now.getHours(), now.getMinutes(), now.getSeconds()).getLunar();
                        const prev = lunar.getPrevJieQi(false);
                        const next = lunar.getNextJieQi(false);
                        if (prev) currentName = prev.getName();
                        if (next) { nextName = next.getName(); nextDate = solarObjToDate(next.getSolar()); }
                    } catch (e) {}
                }
                currentEl.textContent = `Tiết Khí : ${mapJieQiName(currentName)}`;
                if (!nextDate || isNaN(nextDate.getTime())) {
                    countdownEl.textContent = "Không tìm thấy tiết khí tiếp theo";
                    resizeIframeToContent(); return true;
                }
                const diff = nextDate.getTime() - new Date().getTime();
                const t = formatCountdown(diff);
                countdownEl.textContent = `Còn ${t.days} ngày ${t.hours} giờ ${t.minutes} phút ${t.seconds} giây sang tiết khí tiếp theo : ${mapJieQiName(nextName)}`;
                resizeIframeToContent(); return true;
            }

            function bootTopCards() {
                updateValuesFromDeviceOnly(); updateExactCanChi(); updateJieQiInfo(); resizeIframeToContent();
                if (window.__ylctBtTimer) clearInterval(window.__ylctBtTimer);
                window.__ylctBtTimer = setInterval(() => { updateValuesFromDeviceOnly(); updateExactCanChi(); updateJieQiInfo(); resizeIframeToContent(); }, 1000);
                if (typeof window.Solar !== "undefined") return;
                const s = document.createElement("script");
                s.src = "https://cdnjs.cloudflare.com/ajax/libs/lunar-javascript/1.7.5/lunar.min.js";
                s.onload = () => { updateExactCanChi(); updateJieQiInfo(); resizeIframeToContent(); };
                document.head.appendChild(s);
            }
            bootTopCards();
        </script>
        """
        live_script = live_script_vars + live_script_logic

    # CSS MỚI: BÁM SÁT ẢNH THIẾT KẾ BO GÓC CỦA BẠN (CẢ PC VÀ MOBILE)
    return f"""
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 0; font-family: "Times New Roman", serif; background: transparent; }}
        .bt-container {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            padding: 5px;
        }}
        .bt-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            border-radius: 20px; 
            padding: 16px 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            text-align: center;
            box-sizing: border-box;
            min-height: max-content; 
        }}
        
        /* Chữ Năm, Tháng, Ngày, Giờ (Đã phóng to) */
        .bt-title {{ font-size: 18px; font-weight: bold; color: #777; margin-bottom: 2px; text-transform: capitalize;}}
        .bt-val {{ font-size: 28px; font-weight: bold; color: #111; margin-bottom: 12px; font-family: Arial, sans-serif; line-height: 1;}}
        
        /* CHỈNH ẢNH LOGO THẬP THẦN (Đã phóng to và căn giữa tuyệt đối) */
        .bt-chutinh {{ 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin-bottom: 10px;
            height: 50px; /* Tăng không gian hiển thị */
            width: 100%;
        }}
        .img-logo-chutinh {{
            height: 160px; /* Phóng to để phá bỏ lớp viền trong suốt */
            width: auto;
            object-fit: contain;
            margin: -55px 0; /* Cắt gọt rìa trong suốt thừa */
            transform: scale(5.0); /* Phóng to logo lên cho rõ nét */
            transform-origin: center center; /* Khóa tâm, chống lệch */
        }}
        .fallback-ct {{ font-size: 12px; font-weight: bold; background: #fff; padding: 3px 12px; border-radius: 12px; border: 2px solid #aaa; color: #555; font-family: Arial, sans-serif; }}

        /* Cấu trúc Can Chi dọc (Đã thu nhỏ lại cho cân đối) */
        .bt-canchi-vert {{
            display: flex;
            flex-direction: column;
            font-size: 32px; /* Đã thu nhỏ từ 42px xuống 32px */
            line-height: 1.15;
            font-weight: 900;
            margin-bottom: 16px;
            letter-spacing: 1px;
            flex-shrink: 0; 
            gap: 4px; 
        }}

        /* Lưới hiển thị Tàng Ẩn và Phó tinh */
        .bt-tang-pho-grid {{
            display: flex;
            flex-direction: column;
            width: 80%;
            margin-bottom: 16px;
            gap: 6px;
        }}
        .bt-tang, .bt-pho {{
            display: flex;
            justify-content: space-around;
            width: 100%;
        }}
        .bt-tang {{ font-size: 16px; font-weight: bold; }}
        .bt-pho {{ font-size: 14px; font-family: Arial, sans-serif; color: #000; }}

        .bt-truongsinh {{ font-size: 18px; font-weight: bold; color: #000; margin-bottom: 12px; letter-spacing: 0.5px;}}
        .bt-napam {{ font-size: 15px; font-weight: bold; font-family: Arial, sans-serif; }}

        /* Khu vực đếm ngược Tiết Khí */
        .bt-term-wrap {{ text-align: center; margin-top: 10px; font-family: Arial, sans-serif; }}
        .bt-term-current {{ font-size: 16px; font-weight: bold; color: #5b4636; margin-bottom: 4px;}}
        .bt-term-countdown {{ font-size: 14px; color: #6c6c6c; }}

        /* RESPONSIVE CHO ĐIỆN THOẠI */
        @media (max-width: 768px) {{
            .bt-container {{ gap: 6px; padding: 2px; }}
            .bt-card {{ padding: 10px 4px; border-radius: 14px; }}
            
            .bt-title {{ font-size: 14px; margin-bottom: 2px; }} /* Phóng to trên Mobile */
            .bt-val {{ font-size: 20px; margin-bottom: 8px; }}
            
            .bt-chutinh {{ margin-bottom: 8px; height: 30px; }}
            .img-logo-chutinh {{ height: 120px; margin: -45px 0; transform: scale(1.3); }}
            .fallback-ct {{ font-size: 9px; padding: 2px 6px; border-width: 1px; }}

            .bt-canchi-vert {{ font-size: 24px; margin-bottom: 12px; flex-shrink: 0; }} /* Thu nhỏ trên mobile */
            
            .bt-tang-pho-grid {{ width: 95%; margin-bottom: 12px; gap: 4px;}}
            .bt-tang {{ font-size: 13px; }}
            .bt-pho {{ font-size: 11px; }}
            
            .bt-truongsinh {{ font-size: 14px; margin-bottom: 8px; }}
            .bt-napam {{ font-size: 10px; }}
            
            .bt-term-current {{ font-size: 13px; }}
            .bt-term-countdown {{ font-size: 11px; }}
        }}
    </style>
    </head>
    <body>
        <div class="bt-container">{cards_html}</div>
        <div class="bt-term-wrap">
            <div class="bt-term-current" id="bt-current-term">Tiết Khí : Đang tải...</div>
            <div class="bt-term-countdown" id="bt-next-term-countdown">Còn ... sang tiết khí tiếp theo</div>
        </div>
        {live_script}
        <script>
        (function() {{
            function resizeBtFrame() {{
                const h = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
                if (window.frameElement) window.frameElement.style.height = (h + 10) + "px";
            }}
            window.addEventListener("load", resizeBtFrame);
            window.addEventListener("resize", resizeBtFrame);
            setTimeout(resizeBtFrame, 500);
            new MutationObserver(resizeBtFrame).observe(document.body, {{ childList: true, subtree: true }});
        }})();
        </script>
    </body>
    </html>
    """


# Hiệu ứng Ombre (chuyển màu từ trắng sang nhạt) dành cho nền các Thẻ
MAU_NEN_OMBRE = {
    "Hỏa": "linear-gradient(180deg, #ffffff 70%, #ffefef 100%)",
    "Thủy": "linear-gradient(180deg, #ffffff 70%, #f0f7ff 100%)",
    "Mộc": "linear-gradient(180deg, #ffffff 70%, #f0fff0 100%)",
    "Kim": "linear-gradient(180deg, #ffffff 50%, #e0e4e8 100%)",
    "Thổ": "linear-gradient(180deg, #ffffff 70%, #fff8f0 100%)"
}

NA_AM_60 = {
    "Giáp Tý": ("Hải Trung Kim", "Kim"), "Ất Sửu": ("Hải Trung Kim", "Kim"), "Bính Dần": ("Lư Trung Hỏa", "Hỏa"), "Đinh Mão": ("Lư Trung Hỏa", "Hỏa"),
    "Mậu Thìn": ("Đại Lâm Mộc", "Mộc"), "Kỷ Tỵ": ("Đại Lâm Mộc", "Mộc"), "Canh Ngọ": ("Lộ Bàng Thổ", "Thổ"), "Tân Mùi": ("Lộ Bàng Thổ", "Thổ"),
    "Nhâm Thân": ("Kiếm Phong Kim", "Kim"), "Quý Dậu": ("Kiếm Phong Kim", "Kim"), "Giáp Tuất": ("Sơn Đầu Hỏa", "Hỏa"), "Ất Hợi": ("Sơn Đầu Hỏa", "Hỏa"),
    "Bính Tý": ("Giản Hạ Thủy", "Thủy"), "Đinh Sửu": ("Giản Hạ Thủy", "Thủy"), "Mậu Dần": ("Thành Đầu Thổ", "Thổ"), "Kỷ Mão": ("Thành Đầu Thổ", "Thổ"),
    "Canh Thìn": ("Bạch Lạp Kim", "Kim"), "Tân Tỵ": ("Bạch Lạp Kim", "Kim"), "Nhâm Ngọ": ("Dương Liễu Mộc", "Mộc"), "Quý Mùi": ("Dương Liễu Mộc", "Mộc"),
    "Giáp Thân": ("Tuyền Trung Thủy", "Thủy"), "Ất Dậu": ("Tuyền Trung Thủy", "Thủy"), "Bính Tuất": ("Ốc Thượng Thổ", "Thổ"), "Đinh Hợi": ("Ốc Thượng Thổ", "Thổ"),
    "Mậu Tý": ("Tích Lịch Hỏa", "Hỏa"), "Kỷ Sửu": ("Tích Lịch Hỏa", "Hỏa"), "Canh Dần": ("Tùng Bách Mộc", "Mộc"), "Tân Mão": ("Tùng Bách Mộc", "Mộc"),
    "Nhâm Thìn": ("Trường Lưu Thủy", "Thủy"), "Quý Tỵ": ("Trường Lưu Thủy", "Thủy"), "Giáp Ngọ": ("Sa Trung Kim", "Kim"), "Ất Mùi": ("Sa Trung Kim", "Kim"),
    "Bính Thân": ("Sơn Hạ Hỏa", "Hỏa"), "Đinh Dậu": ("Sơn Hạ Hỏa", "Hỏa"), "Mậu Tuất": ("Bình Địa Mộc", "Mộc"), "Kỷ Hợi": ("Bình Địa Mộc", "Mộc"),
    "Canh Tý": ("Bích Thượng Thổ", "Thổ"), "Tân Sửu": ("Bích Thượng Thổ", "Thổ"), "Nhâm Dần": ("Kim Bạch Kim", "Kim"), "Quý Mão": ("Kim Bạch Kim", "Kim"),
    "Giáp Thìn": ("Phú Đăng Hỏa", "Hỏa"), "Ất Tỵ": ("Phú Đăng Hỏa", "Hỏa"), "Bính Ngọ": ("Thiên Hà Thủy", "Thủy"), "Đinh Mùi": ("Thiên Hà Thủy", "Thủy"),
    "Mậu Thân": ("Đại Trạch Thổ", "Thổ"), "Kỷ Dậu": ("Đại Trạch Thổ", "Thổ"), "Canh Tuất": ("Thoa Xuyến Kim", "Kim"), "Tân Hợi": ("Thoa Xuyến Kim", "Kim"),
    "Nhâm Tý": ("Tang Đố Mộc", "Mộc"), "Quý Sửu": ("Tang Đố Mộc", "Mộc"), "Giáp Dần": ("Đại Khê Thủy", "Thủy"), "Ất Mão": ("Đại Khê Thủy", "Thủy"),
    "Bính Thìn": ("Sa Trung Thổ", "Thổ"), "Đinh Tỵ": ("Sa Trung Thổ", "Thổ"), "Mậu Ngọ": ("Thiên Thượng Hỏa", "Hỏa"), "Kỷ Mùi": ("Thiên Thượng Hỏa", "Hỏa"),
    "Canh Thân": ("Thạch Lựu Mộc", "Mộc"), "Tân Dậu": ("Thạch Lựu Mộc", "Mộc"), "Nhâm Tuất": ("Đại Hải Thủy", "Thủy"), "Quý Hợi": ("Đại Hải Thủy", "Thủy")
}

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
CHI_TO_HOUR = {
    'Tý': 23, 'Sửu': 1, 'Dần': 3, 'Mão': 5, 'Thìn': 7, 'Tỵ': 9,
    'Ngọ': 11, 'Mùi': 13, 'Thân': 15, 'Dậu': 17, 'Tuất': 19, 'Hợi': 21
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
LUU_CHU_TARGETS = {
    'Tý': ['mật', 'đởm'],
    'Sửu': ['gan'],
    'Dần': ['phổi'],
    'Mão': ['ruột già', 'đại trường'],
    'Thìn': ['dạ dày', 'vị'],
    'Tỵ': ['tỳ', 'lá lách', 'tụy'],
    'Ngọ': ['tim', 'tâm'],
    'Mùi': ['ruột non', 'tiểu trường'],
    'Thân': ['bàng quang', 'bọng đái', 'lưng'],
    'Dậu': ['thận'],
    'Tuất': ['tâm bào', 'mạch ngoại vi'],
    'Hợi': ['tam tiêu', 'nội tiết', 'ngực', 'bụng']
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
        'chi_thang': CHI[chi_thang_idx], # <--- THÊM DÒNG NÀY ĐỂ XUẤT CHI THÁNG
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

    def _normalize_text(self, text):
        return (text or "").strip().lower()

    def _match_body_part(self, bo_phan_input, mo_ta_tham_chieu):
        a = self._normalize_text(bo_phan_input)
        b = self._normalize_text(mo_ta_tham_chieu)

        if not a or not b:
            return False

        if a in b or b in a:
            return True

        nhom_dong_nghia = [
            {"răng", "nướu", "lợi", "hàm", "răng khôn", "răng miệng", "miệng"},
            {"mắt", "nhãn", "mí mắt", "nhãn cầu"},
            {"tai"},
            {"mũi", "xoang"},
            {"miệng", "môi", "lưỡi", "họng", "cổ họng"},
            {"đầu", "đầu mặt"},
            {"cổ", "cổ gáy", "gáy"},
            {"ngực", "vú"},
            {"bụng", "dạ dày", "vị", "tỳ"},
            {"tim", "tâm"},
            {"tay", "bàn tay", "cổ tay", "cánh tay"},
            {"lưng", "eo", "eo lưng"},
            {"chân", "bàn chân", "gót chân", "cẳng chân", "đùi", "gối", "đầu gối"},
            {"âm bộ", "bụng dưới"},
            {"gan"},
            {"thận"},
        ]

        for nhom in nhom_dong_nghia:
            if any(x in a for x in nhom) and any(x in b for x in nhom):
                return True

        return False


    def phan_loai_thu_tuc(self, bo_phan, loai_ui=None):
        mapping = {
            "Khám Tổng Quát - Xét Nghiệm Sơ Bộ": {
                "loai": "tham_kham",
                "ten_goi": "Khám Tổng Quát - Xét Nghiệm Sơ Bộ",
                "muc_do": "rất thấp",
                "xam_lan": "không xâm lấn",
                "dinh_huong_luan": "luận mềm, thiên về phát hiện sớm, đọc kết quả, theo dõi",
                "uu_tien": "ưu tiên phát hiện"
            },
            "Khám Chuyên Khoa - Xét Nghiệm Chuyên Sâu": {
                "loai": "tham_kham_chuyen_sau",
                "ten_goi": "Khám Chuyên Khoa - Xét Nghiệm Chuyên Sâu",
                "muc_do": "thấp",
                "xam_lan": "ít xâm lấn hoặc không xâm lấn",
                "dinh_huong_luan": "luận theo hướng khảo sát sâu hơn, đối chiếu triệu chứng kỹ hơn",
                "uu_tien": "ưu tiên phát hiện"
            },
            "Chẩn Đoán Hình Ảnh (X-ray, CT, MRI, Siêu Âm...)": {
                "loai": "chan_doan_hinh_anh",
                "ten_goi": "Chẩn Đoán Hình Ảnh",
                "muc_do": "thấp",
                "xam_lan": "không xâm lấn",
                "dinh_huong_luan": "luận theo hướng nhìn bệnh rõ hơn, dễ phát hiện bất thường hơn",
                "uu_tien": "ưu tiên phát hiện"
            },
            "Nội Soi - Thăm Dò Chẩn Đoán": {
                "loai": "tham_do_chan_doan",
                "ten_goi": "Nội Soi - Thăm Dò Chẩn Đoán",
                "muc_do": "vừa",
                "xam_lan": "xâm lấn nhẹ đến vừa",
                "dinh_huong_luan": "luận trung tính-thận trọng, vừa là chẩn đoán vừa có tác động vào cơ thể",
                "uu_tien": "cân bằng phát hiện và an toàn"
            },
            "Xét Nghiệm Máu / Nước Tiểu / Lấy Mẫu": {
                "loai": "xet_nghiem_lay_mau",
                "ten_goi": "Xét Nghiệm Máu / Nước Tiểu / Lấy Mẫu",
                "muc_do": "thấp",
                "xam_lan": "xâm lấn rất nhẹ",
                "dinh_huong_luan": "luận nhẹ, thiên về chất lượng mẫu và khả năng phát hiện sớm",
                "uu_tien": "ưu tiên phát hiện"
            },
            "Tiêm / Truyền / Chích Ngừa": {
                "loai": "tiem_truyen",
                "ten_goi": "Tiêm / Truyền / Chích Ngừa",
                "muc_do": "thấp",
                "xam_lan": "xâm lấn nhẹ",
                "dinh_huong_luan": "luận thận trọng nhẹ, chú ý phản ứng cơ thể và khả năng dung nạp",
                "uu_tien": "ưu tiên an toàn"
            },
            "Nha Khoa Nhẹ Nhàng (Cạo Vôi, Trám Răng, Vệ Sinh, Deep Clean...)": {
                "loai": "nha_khoa_nhe",
                "ten_goi": "Nha Khoa Nhẹ Nhàng",
                "muc_do": "vừa",
                "xam_lan": "xâm lấn nhẹ",
                "dinh_huong_luan": "luận thận trọng vừa, chú ý chảy máu nhẹ, kích ứng, ê buốt",
                "uu_tien": "ưu tiên an toàn"
            },
            "Nha Khoa Chuyên Sâu (Nhổ Răng, Nhổ Răng Khôn, Niềng Răng...)": {
                "loai": "nha_khoa_sau",
                "ten_goi": "Nha Khoa Chuyên Sâu",
                "muc_do": "cao",
                "xam_lan": "xâm lấn vừa đến mạnh",
                "dinh_huong_luan": "luận thận trọng rõ, ưu tiên tránh phạm Nhân Thần, Hung Thần, Lưu Chú",
                "uu_tien": "ưu tiên an toàn"
            },
            "Tiểu Phẫu Nhẹ (Gây Tê, Rạch Nhẹ, Xử Lý Mô Mềm...)": {
                "loai": "tieu_phau_nhe",
                "ten_goi": "Tiểu Phẫu Nhẹ",
                "muc_do": "cao",
                "xam_lan": "xâm lấn vừa",
                "dinh_huong_luan": "luận thận trọng rõ, tránh các hung điểm trực phạm",
                "uu_tien": "ưu tiên an toàn"
            },
            "Tiểu Phẫu Chuyên Sâu": {
                "loai": "tieu_phau_sau",
                "ten_goi": "Tiểu Phẫu Chuyên Sâu",
                "muc_do": "cao",
                "xam_lan": "xâm lấn vừa đến mạnh",
                "dinh_huong_luan": "luận mạnh tay hơn, coi trọng giờ khí và các thần sát bất lợi",
                "uu_tien": "ưu tiên an toàn"
            },
            "Đại Phẫu - Phẫu Thuật Gây Mê": {
                "loai": "dai_phau",
                "ten_goi": "Đại Phẫu - Phẫu Thuật Gây Mê",
                "muc_do": "rất cao",
                "xam_lan": "xâm lấn mạnh",
                "dinh_huong_luan": "luận nghiêm ngặt nhất, tránh hung thần và các điểm phá/xung",
                "uu_tien": "ưu tiên an toàn tuyệt đối"
            },
            "Phẫu Thuật Nội Soi": {
                "loai": "phau_thuat_noi_soi",
                "ten_goi": "Phẫu Thuật Nội Soi",
                "muc_do": "cao",
                "xam_lan": "xâm lấn vừa đến mạnh",
                "dinh_huong_luan": "luận nghiêng về can thiệp xâm lấn, vẫn có yếu tố thăm dò nhưng lấy an toàn làm chính",
                "uu_tien": "ưu tiên an toàn"
            },
            "Trị Liệu Nhẹ Nhàng": {
                "loai": "tri_lieu_nhe",
                "ten_goi": "Trị Liệu Nhẹ Nhàng",
                "muc_do": "thấp",
                "xam_lan": "không xâm lấn hoặc rất nhẹ",
                "dinh_huong_luan": "luận mềm, thiên về độ hanh thông, đáp ứng cơ thể, hiệu quả phục hồi",
                "uu_tien": "ưu tiên đáp ứng"
            },
            "Trị Liệu Chuyên Sâu": {
                "loai": "tri_lieu_sau",
                "ten_goi": "Trị Liệu Chuyên Sâu",
                "muc_do": "vừa",
                "xam_lan": "ít xâm lấn hoặc xâm lấn nhẹ",
                "dinh_huong_luan": "luận trung tính-thận trọng, chú ý mức chịu đựng và tiến triển hồi phục",
                "uu_tien": "ưu tiên đáp ứng"
            },
            "Phục Hồi Chức Năng - Vật Lý Trị Liệu": {
                "loai": "phuc_hoi_chuc_nang",
                "ten_goi": "Phục Hồi Chức Năng - Vật Lý Trị Liệu",
                "muc_do": "thấp",
                "xam_lan": "không xâm lấn hoặc rất nhẹ",
                "dinh_huong_luan": "luận theo hướng hỗ trợ phục hồi, giảm cản trở, tăng độ đáp ứng",
                "uu_tien": "ưu tiên phục hồi"
            },
            "Châm Cứu - Bấm Huyệt - Trị Liệu Đông Y": {
                "loai": "cham_cuu_dong_y",
                "ten_goi": "Châm Cứu - Bấm Huyệt - Trị Liệu Đông Y",
                "muc_do": "vừa",
                "xam_lan": "xâm lấn nhẹ hoặc không xâm lấn",
                "dinh_huong_luan": "luận kỹ Nhân Thần, Thích Huyết Sát, Thích Hại Sát, Âm Thương Sát",
                "uu_tien": "ưu tiên tránh phạm"
            },
            "Thẩm Mỹ Nhẹ Nhàng (Xăm Mày, Xăm Môi, Bơm Môi, Chăm Sóc Da...)": {
                "loai": "tham_my_nhe",
                "ten_goi": "Thẩm Mỹ Nhẹ Nhàng",
                "muc_do": "vừa",
                "xam_lan": "xâm lấn nhẹ",
                "dinh_huong_luan": "luận thận trọng vừa, chú ý chảy máu, sưng, lành thương và tính thẩm mỹ",
                "uu_tien": "ưu tiên lành thương"
            },
            "Thẩm Mỹ Chuyên Sâu (Nâng Mũi, Cắt Mí, Độn Cằm, Nâng Ngực...)": {
                "loai": "tham_my_sau",
                "ten_goi": "Thẩm Mỹ Chuyên Sâu",
                "muc_do": "rất cao",
                "xam_lan": "xâm lấn mạnh",
                "dinh_huong_luan": "luận gần như đại phẫu, rất coi trọng hung-cát và hồi phục hậu thủ thuật",
                "uu_tien": "ưu tiên an toàn tuyệt đối"
            },
            "Da Liễu - Laser - Đốt - Can Thiệp Bề Mặt Da": {
                "loai": "da_lieu_laser",
                "ten_goi": "Da Liễu - Laser - Đốt",
                "muc_do": "vừa",
                "xam_lan": "xâm lấn nhẹ đến vừa",
                "dinh_huong_luan": "luận chú ý kích ứng, viêm, chảy dịch, lành thương bề mặt",
                "uu_tien": "ưu tiên lành thương"
            },
            "Sản Phụ Khoa / Nam Khoa - Thủ Thuật / Can Thiệp": {
                "loai": "san_phu_nam_khoa",
                "ten_goi": "Sản Phụ Khoa / Nam Khoa - Thủ Thuật / Can Thiệp",
                "muc_do": "cao",
                "xam_lan": "xâm lấn vừa đến mạnh",
                "dinh_huong_luan": "luận thận trọng cao, tránh các điểm phá/xung và các hung thần trực phạm",
                "uu_tien": "ưu tiên an toàn"
            },
            "Các Hoạt Động Khác / Chưa Rõ": {
                "loai": "khac",
                "ten_goi": "Các Hoạt Động Khác / Chưa Rõ",
                "muc_do": "chưa xác định",
                "xam_lan": "chưa xác định",
                "dinh_huong_luan": "luận trung tính, không cực đoan, chờ thêm dữ liệu",
                "uu_tien": "cân bằng"
            }
        }

        if loai_ui in mapping:
            return mapping[loai_ui]

        return {
            "loai": "khac",
            "ten_goi": "Các Hoạt Động Khác / Chưa Rõ",
            "muc_do": "chưa xác định",
            "xam_lan": "chưa xác định",
            "dinh_huong_luan": "luận trung tính, không cực đoan, chờ thêm dữ liệu",
            "uu_tien": "cân bằng"
        }

    def lap_bao_cao_chi_tiet(self, nam_chi, thang_am, ngay_can, ngay_chi, gio, ngay_am, bo_phan, loai_ui, cac_gio_hoang_dao):
        
        # Sửa lỗi ẩn: Phải phân loại thủ thuật trước khi dùng để tính toán ở dưới
        phan_loai = self.phan_loai_thu_tuc(bo_phan, loai_ui)
        chi_thang = self.CHI[(thang_am + 1) % 12]

        nt_ngay_text = self.NT_NGAY.get(ngay_am, "")
        nt_can_text = self.NT_CAN.get(ngay_can, "")
        nt_chi_text = self.NT_CHI.get(ngay_chi, "")
        nt_gio_text = self.NT_GIO.get(gio, "")
        luu_chu_text = LUU_CHU_DETAILS.get(gio, "")
        luu_chu_targets = LUU_CHU_TARGETS.get(gio, [])

        nhat_pha = gio == self.LUC_XUNG.get(ngay_chi)
        nguyet_pha = ngay_chi == self.LUC_XUNG.get(chi_thang)
        tue_pha = ngay_chi == self.LUC_XUNG.get(nam_chi)

        dao_type = "Hoàng Đạo" if gio in cac_gio_hoang_dao else "Hắc Đạo"
        nhat_y = gio == self.NHAT_Y.get(ngay_can)

        pham_nt_gio = self._match_body_part(bo_phan, nt_gio_text)
        pham_nt_can = self._match_body_part(bo_phan, nt_can_text)
        pham_nt_chi = self._match_body_part(bo_phan, nt_chi_text)
        pham_nt_ngay = self._match_body_part(bo_phan, nt_ngay_text)
        pham_luu_chu = any(self._match_body_part(bo_phan, target) for target in luu_chu_targets)

        hung_than = {
            "Thích Huyết Sát": {
                "pham": pham_nt_ngay,
                "can_cu": f"Nhân Thần Ngày trú tại: {nt_ngay_text}"
            },
            "Thích Hại Sát - Can Ngày": {
                "pham": pham_nt_can,
                "can_cu": f"Nhân Thần theo Can Ngày trú tại: {nt_can_text}"
            },
            "Thích Hại Sát - Chi Ngày": {
                "pham": pham_nt_chi,
                "can_cu": f"Nhân Thần theo Chi Ngày trú tại: {nt_chi_text}"
            },
            "Âm Thương Sát": {
                "pham": pham_nt_gio,
                "can_cu": f"Nhân Thần theo Canh Giờ trú tại: {nt_gio_text}"
            },
            "Huyết Kỵ": {
                "pham": ngay_chi == self.HUYET_KY.get(thang_am),
                "can_cu": f"Tháng âm {thang_am} ứng Huyết Kỵ tại chi: {self.HUYET_KY.get(thang_am)}"
            },
            "Huyết Chi": {
                "pham": ngay_chi == self.HUYET_CHI.get(thang_am),
                "can_cu": f"Tháng âm {thang_am} ứng Huyết Chi tại chi: {self.HUYET_CHI.get(thang_am)}"
            },
            "Bệnh Phù": {
                "pham": gio == self.BENH_PHU.get(nam_chi),
                "can_cu": f"Năm chi {nam_chi} ứng Bệnh Phù tại giờ chi: {self.BENH_PHU.get(nam_chi)}"
            },
            "Tử Khí": {
                "pham": ngay_chi == self.TU_KHI.get(thang_am),
                "can_cu": f"Tháng âm {thang_am} ứng Tử Khí tại chi: {self.TU_KHI.get(thang_am)}"
            }
        }

        cat_than = {
            "Thiên Y": {
                "co": ngay_chi == self.THIEN_Y.get(thang_am),
                "can_cu": f"Tháng âm {thang_am} ứng Thiên Y tại chi: {self.THIEN_Y.get(thang_am)}"
            },
            "Địa Y": {
                "co": ngay_chi == self.DIA_Y.get(thang_am),
                "can_cu": f"Tháng âm {thang_am} ứng Địa Y tại chi: {self.DIA_Y.get(thang_am)}"
            }
        }

        pham_hung_chinh = (
            nhat_pha or nguyet_pha or tue_pha or
            hung_than["Thích Huyết Sát"]["pham"] or
            hung_than["Thích Hại Sát - Can Ngày"]["pham"] or
            hung_than["Thích Hại Sát - Chi Ngày"]["pham"] or
            hung_than["Âm Thương Sát"]["pham"] or
            hung_than["Huyết Kỵ"]["pham"] or
            hung_than["Huyết Chi"]["pham"] or
            hung_than["Bệnh Phù"]["pham"] or
            hung_than["Tử Khí"]["pham"] or
            (pham_luu_chu and phan_loai["loai"] in ["xam_lan_nhe", "xam_lan_manh"])
        )

        co_tro_luc_cat = (
            dao_type == "Hoàng Đạo" or
            cat_than["Thiên Y"]["co"] or
            cat_than["Địa Y"]["co"] or
            nhat_y
        )

        if phan_loai["loai"] in ["tham_kham", "chan_doan_hinh_anh"]:
            if pham_hung_chinh:
                tong_quyet = "Thời điểm này không quá lý tưởng cho việc thăm khám hoặc khảo sát."
                nen_lam = "Nếu việc khám hoặc chụp chưa gấp, nên chọn thời điểm sáng sủa hơn để dễ thuận cho việc phát hiện và kết luận."
                khong_nen_lam = "Không nên quá chủ quan với kết quả đầu tiên; nếu lâm sàng còn nghi ngờ, nên đọc kỹ hoặc tái kiểm tra."
            elif dao_type == "Hắc Đạo" and not co_tro_luc_cat:
                tong_quyet = "Đây là thời điểm có thể đi khám hoặc chụp, nhưng khí tượng chưa thật sự hanh thông."
                nen_lam = "Vẫn có thể tiến hành, nhất là với khám tổng quát, X-ray, MRI, CT hoặc siêu âm; nên giữ hồ sơ rõ ràng và trao đổi kỹ với bác sĩ đọc kết quả."
                khong_nen_lam = "Không nên kỳ vọng quá nhiều vào một lần khảo sát duy nhất nếu triệu chứng còn mơ hồ hoặc kéo dài."
            else:
                tong_quyet = "Thời điểm này tương đối thuận cho việc thăm khám và khảo sát."
                nen_lam = "Có thể tiến hành khám, chụp hoặc kiểm tra; nếu có cát khí hỗ trợ thì ý nghĩa thiên về phát hiện sớm, nhìn bệnh rõ hơn và dễ chốt hướng theo dõi."
                khong_nen_lam = "Không nên vì giờ đẹp mà chủ quan bỏ qua việc đối chiếu triệu chứng, phim chụp và ý kiến chuyên môn."

        elif phan_loai["loai"] in ["xam_lan_nhe", "xam_lan_manh"]:
            if pham_hung_chinh:
                tong_quyet = "Thời điểm này không thuận cho thủ thuật hoặc can thiệp xâm lấn."
                nen_lam = "Nên dời sang giờ khác hoặc ngày khác để tránh va phạm hung khí."
                khong_nen_lam = "Không nên tiến hành nhổ, chích, rạch, mổ hay can thiệp xâm lấn vào lúc này."
            elif dao_type == "Hắc Đạo" and not co_tro_luc_cat:
                tong_quyet = "Thời điểm này không xấu gắt, nhưng chưa phải khí tượng đẹp cho can thiệp."
                nen_lam = "Nếu chưa gấp, nên ưu tiên đổi sang giờ thuận hơn."
                khong_nen_lam = "Không nên quyết nhanh chỉ vì thấy chưa phạm đại hung."
            else:
                tong_quyet = "Thời điểm này tương đối thuận cho can thiệp khi cần thiết."
                nen_lam = "Có thể tiến hành nếu đã chuẩn bị kỹ và tuân thủ nguyên tắc chuyên môn an toàn."
                khong_nen_lam = "Không nên chủ quan; cát khí chỉ hỗ trợ, không thay thế kỹ thuật và vô khuẩn."

        else:
            if pham_hung_chinh:
                tong_quyet = "Thời điểm này có dấu hiệu chưa thuận."
                nen_lam = "Nên cân nhắc kỹ mục đích thực hiện và ưu tiên đổi thời điểm nếu có thể."
                khong_nen_lam = "Không nên quyết định vội khi còn yếu tố hung chưa được hóa giải."
            elif dao_type == "Hắc Đạo" and not co_tro_luc_cat:
                tong_quyet = "Thời điểm này tạm dùng được, nhưng chưa thật sự đẹp."
                nen_lam = "Có thể làm nếu cần, song nên giữ hướng theo dõi cẩn thận."
                khong_nen_lam = "Không nên kết luận quá cát."
            else:
                tong_quyet = "Thời điểm này tương đối ổn."
                nen_lam = "Có thể tiến hành trong khuôn khổ an toàn và hợp lý."
                khong_nen_lam = "Không nên chủ quan."

        report = {
            "co_quan_can_thiep": bo_phan,
            "phan_loai_thu_tuc": phan_loai,
            "loai_hoat_dong_ui": loai_ui,
            "1_Nhat_Pha": {
                "pham": nhat_pha,
                "dien_giai": f"Giờ {gio} {'xung' if nhat_pha else 'không xung'} Ngày {ngay_chi}."
            },
            "2_Nguyet_Pha": {
                "pham": nguyet_pha,
                "dien_giai": f"Ngày {ngay_chi} {'xung' if nguyet_pha else 'không xung'} Tháng {chi_thang}."
            },
            "3_Tue_Pha": {
                "pham": tue_pha,
                "dien_giai": f"Ngày {ngay_chi} {'xung' if tue_pha else 'không xung'} Năm {nam_chi}."
            },
            "4_Hoang_Hac_Dao": {
                "trang_thai": dao_type,
                "pham_tnluu_chu": pham_luu_chu,
                "vung_luu_chu": luu_chu_targets,
                "chi_tiet_tnluu_chu": luu_chu_text
            },
            "5_Nhat_Y": {
                "co": nhat_y,
                "dien_giai": f"Giờ {gio} {'là' if nhat_y else 'không phải'} Nhật Y theo Can ngày {ngay_can}."
            },
            "6_Nhan_Than_Canh_Gio": {
                "vi_tri": nt_gio_text,
                "pham_bo_phan": pham_nt_gio,
                "dien_giai": f"Nhân Thần Canh Giờ trú tại {nt_gio_text}."
            },
            "7_Nhan_Than_Can_Ngay": {
                "vi_tri": nt_can_text,
                "pham_bo_phan": pham_nt_can,
                "dien_giai": f"Nhân Thần Can Ngày trú tại {nt_can_text}."
            },
            "8_Nhan_Than_Chi_Ngay": {
                "vi_tri": nt_chi_text,
                "pham_bo_phan": pham_nt_chi,
                "dien_giai": f"Nhân Thần Chi Ngày trú tại {nt_chi_text}."
            },
            "9_Hung_Than": hung_than,
            "10_Cat_Than": cat_than,
            "12_Ket_Luan": {
                "tong_quyet": tong_quyet,
                "nen_lam": nen_lam,
                "khong_nen_lam": khong_nen_lam
            }
        }

        return report

# ==============================================================================
# GIAO DIỆN WEB VỚI STREAMLIT (THAY THẾ APP CŨ)
# ==============================================================================
# 1. Cấu hình trang
st.set_page_config(
    page_title="Y Lý Cát Thời",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Y Lý Cát Thời - Kinh Dịch Hội - Mai Hoa Dịch Số"
    }
)
components.html("""
<script>
(function () {
    function pad2(n) { return String(n).padStart(2, "0"); }

    const now = new Date();
    const dateKey = `${now.getFullYear()}-${pad2(now.getMonth() + 1)}-${pad2(now.getDate())}`;
    const stamp = `${dateKey}T${pad2(now.getHours())}:${pad2(now.getMinutes())}:${pad2(now.getSeconds())}`;
    const tz = String(now.getTimezoneOffset());

    const vw = Math.max(
        window.parent.innerWidth || 0,
        window.innerWidth || 0,
        document.documentElement.clientWidth || 0
    );

    const layout = vw <= 768 ? "mobile" : "desktop";

    const url = new URL(window.parent.location.href);
    const oldNow = url.searchParams.get("client_now");
    const oldDate = url.searchParams.get("client_date");
    const oldTz = url.searchParams.get("client_tz");
    const oldLayout = url.searchParams.get("client_layout");

    if (!oldNow || !oldDate || oldDate !== dateKey || oldTz !== tz || oldLayout !== layout) {
        url.searchParams.set("client_now", stamp);
        url.searchParams.set("client_date", dateKey);
        url.searchParams.set("client_tz", tz);
        url.searchParams.set("client_layout", layout);
        window.parent.location.replace(url.toString());
    }
})();
</script>
""", height=0)
st.set_option("client.toolbarMode", "minimal")

# --- KHU VỰC TIÊU ĐỀ STICKY HEADER MỚI (CHỐNG TRÀN, PHÓNG TO LOGO, ĐỒNG NHẤT PC & MOBILE) ---

# 1. Hàm đọc và mã hóa file logo của bạn (Giữ nguyên)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        # Nếu không tìm thấy file, trả về chuỗi rỗng để không bị lỗi app
        return "" 

img_base64 = get_base64_of_bin_file('logo.png')

img_base64 = get_base64_of_bin_file('logo.png')

# ==============================================================================
# CODE MỚI: XỬ LÝ BACKGROUND VÀ OPACITY
# ==============================================================================
# Tạo thanh trượt ở sidebar để điều chỉnh độ đậm nhạt của background
do_ro_net = st.sidebar.slider("Độ rõ nét hình nền (%)", min_value=0, max_value=100, value=15, step=5)

# Đọc file hình nền monogram
bg_base64 = get_base64_of_bin_file('monogram.png') 

if bg_base64:
    # Tính toán độ mờ của lớp phủ màu trắng (overlay)
    # Ví dụ: rõ nét 15% -> lớp phủ trắng sẽ che 85% (0.85)
    overlay_opacity = 1.0 - (do_ro_net / 100.0)
    
    bg_css = f"""
    <style>
    .stApp {{
        /* Dùng linear-gradient phủ màu trắng đè lên hình để tạo hiệu ứng opacity */
        background-image: linear-gradient(rgba(255, 255, 255, {overlay_opacity}), rgba(255, 255, 255, {overlay_opacity})), url("data:image/png;base64,{bg_base64}");
        background-size: 600px; /* Chỉnh kích thước lặp lại của monogram, bạn có thể tăng giảm số này */
        background-repeat: repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# 2. Header mới: PC nhỏ gọn hơn, mobile gọn 1 hàng
st.markdown(
    f"""
    <style>
    .ylct-header {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin: 4px 0 8px 0;
        padding: 2px 8px;
        width: 100%;
        box-sizing: border-box;
    }}

    .ylct-header img {{
        width: 90px;   /* Giữ logo to như cũ trên PC */
        height: auto;
        border-radius: 8px;
        flex-shrink: 0;
    }}

    .ylct-header .ylct-title {{
        margin: 0;
        padding: 0;
        font-size: 16px;   /* nhỏ còn khoảng 1/2 so với 32 */
        font-weight: 700;
        line-height: 1.1;
        color: #1f2430;
        text-align: center;
        white-space: nowrap;
    }}

    @media (max-width: 768px) {{
        .ylct-header {{
            justify-content: center;
            gap: 8px;
            margin: 2px 0 6px 0;
            padding: 2px 6px;
            flex-wrap: nowrap;
        }}

        .ylct-header img {{
            width: 42px;   /* mobile thu nhỏ để không che mất phần dưới */
        }}

        .ylct-header .ylct-title {{
            font-size: 15px;
            line-height: 1.05;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: left;
            max-width: 78vw;
        }}
    }}
    </style>

    <div class="ylct-header">
        <img src="data:image/png;base64,{img_base64}">
        <div class="ylct-title">Y Lý Cát Thời Dân Gian</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

now_top = get_device_now()
gio_top = CHI[((now_top.hour + 1) // 2) % 12]
client_layout = get_client_layout()

battu_top_html = render_ui_battu_tietkhi(
    now_top.year,
    now_top.month,
    now_top.day,
    gio_top,
    gio_display=now_top.strftime("%H:%M:%S"),
    live_from_device=True,
    actual_hour=now_top.hour,
    actual_minute=now_top.minute,
    actual_second=now_top.second
)

top_cards_height = 260 if client_layout == "mobile" else 400
components.html(battu_top_html, height=top_cards_height, scrolling=False)

st.markdown(
    "<div style='height:8px;border-top:1px solid #d9d9d9;margin:4px 0 0 0;'></div>",
    unsafe_allow_html=True
)

engine = YLyCatThoiEngine()

# Lấy thời gian hiện tại làm mặc định
now = get_device_now()
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


    loai_hoat_dong = st.selectbox(
        "Loại hoạt động y khoa",
        [
            "Khám Tổng Quát - Xét Nghiệm Sơ Bộ",
            "Khám Chuyên Khoa - Xét Nghiệm Chuyên Sâu",
            "Chẩn Đoán Hình Ảnh (X-ray, CT, MRI, Siêu Âm...)",
            "Nội Soi - Thăm Dò Chẩn Đoán",
            "Xét Nghiệm Máu / Nước Tiểu / Lấy Mẫu",
            "Tiêm / Truyền / Chích Ngừa",
            "Nha Khoa Nhẹ Nhàng (Cạo Vôi, Trám Răng, Vệ Sinh, Deep Clean...)",
            "Nha Khoa Chuyên Sâu (Nhổ Răng, Nhổ Răng Khôn, Niềng Răng...)",
            "Tiểu Phẫu Nhẹ (Gây Tê, Rạch Nhẹ, Xử Lý Mô Mềm...)",
            "Tiểu Phẫu Chuyên Sâu",
            "Đại Phẫu - Phẫu Thuật Gây Mê",
            "Phẫu Thuật Nội Soi",
            "Trị Liệu Nhẹ Nhàng",
            "Trị Liệu Chuyên Sâu",
            "Phục Hồi Chức Năng - Vật Lý Trị Liệu",
            "Châm Cứu - Bấm Huyệt - Trị Liệu Đông Y",
            "Thẩm Mỹ Nhẹ Nhàng (Xăm Mày, Xăm Môi, Bơm Môi, Chăm Sóc Da...)",
            "Thẩm Mỹ Chuyên Sâu (Nâng Mũi, Cắt Mí, Độn Cằm, Nâng Ngực...)",
            "Da Liễu - Laser - Đốt - Can Thiệp Bề Mặt Da",
            "Sản Phụ Khoa / Nam Khoa - Thủ Thuật / Can Thiệp",
            "Các Hoạt Động Khác / Chưa Rõ"
        ],
        index=0,
        key="loai_hoat_dong"
    )

    bo_phan = st.text_input(
        "Bộ phận cơ thể đang xem (Mắt, Dạ dày, Răng, Cổ họng...)",
        key="bo_phan_input"
    )

    trieu_chung = st.text_area(
        "Triệu chứng hiện tại (nếu có)",
        placeholder="Ví dụ: đau âm ỉ, sưng, chảy máu, sốt, khó thở, đau ngực...",
        key="trieu_chung"
    )

    btn_phan_tich = st.button(
        "🔍 Phân Tích Bệnh Án",
        type="primary",
        use_container_width=True,
        key="btn_phan_tich"
    )


    # 4. Tính toán Dịch Lý và thanh hiển thị Tứ Trụ
    data = tinh_can_chi_tu_ngay_duong(solar_date, CHI_TO_HOUR[gio_kham])

    solar_now_legacy = Solar(now.year, now.month, now.day)
    gio_now_legacy = CHI_TO_HOUR[CHI[((now.hour + 1) // 2) % 12]]
    data_now_legacy = tinh_can_chi_tu_ngay_duong(solar_now_legacy, gio_now_legacy)

    st.info(
        f"Âm Lịch Hôm Nay : "
        f"Năm {data_now_legacy['nam']} | Tháng {data_now_legacy['thang']} | Ngày {data_now_legacy['ngay']}"
    )

    st.caption(
        f"Phần luận giải bên dưới vẫn dùng ngày bạn chọn ở form: "
        f"Năm {data['nam']} | Tháng {data['thang']} | Ngày {data['ngay']}"
    )

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

        prompt_bac_si = """
Bạn là bộ máy luận giải y lý cát thời với giọng văn tự nhiên, mềm mại, chuyên nghiệp, giống một bác sĩ hiểu huyền học chứ không phải máy đọc checklist.

NGUYÊN TẮC BẮT BUỘC:
- Chỉ dùng dữ liệu đã có trong JSON đầu vào.
- Không được tự bịa công thức ngoài dữ liệu.
- Không được nhắc lại câu hỏi.
- Không được viết kiểu: "Giờ đang xem có phải Nhật Y hay không?"
- Chỉ được viết CÂU TRẢ LỜI.
- Không lan man.
- Nếu không phạm thì chỉ ghi ngắn: "Không Phạm".
- Chỉ giải thích khi thật sự có phạm, có cát thần, hoặc cần cảnh báo.
- Giọng văn phải mềm mại, rõ ràng, chuyên nghiệp, có logic huyền học.
- Không viết cứng đơ kiểu máy móc.
- Vẫn phải có logic rõ, nhưng diễn đạt tự nhiên như đang giải thích cho bệnh nhân.
- Không được cực đoan hóa mọi trường hợp thành “nên” hoặc “không nên can thiệp”.
- Phải phân biệt rõ:
  + thăm khám / khám tổng quát
  + chẩn đoán hình ảnh / chụp khảo sát
  + thủ thuật xâm lấn nhẹ
  + can thiệp / phẫu thuật xâm lấn
- Trong JSON đầu vào sẽ có:
  + bo_phan
  + loai_hoat_dong
  + trieu_chung
- Hãy ưu tiên dùng trường loai_hoat_dong để xác định bản chất việc đang làm, không tự đoán bừa từ tên bộ phận.
- Hãy dùng trieu_chung để làm mềm giọng bác sĩ và đánh giá mức độ cần theo dõi, nhưng không tự bịa bệnh.

THỨ TỰ LUẬN GIẢI BẮT BUỘC:

1. Nhật Phá
- Nếu không phạm: ghi đúng mẫu "1. Nhật Phá: Không Phạm"
- Nếu phạm: ghi "1. Nhật Phá: Có Phạm - ..." rồi giải thích ngắn hậu quả

2. Nguyệt Phá
- Nếu không phạm: chỉ ghi "Không Phạm"
- Nếu phạm: giải thích ngắn

3. Tuế Phá
- Nếu không phạm: chỉ ghi "Không Phạm"
- Nếu phạm: giải thích ngắn

4. Hoàng Đạo / Hắc Đạo + liên hệ với Tý Ngọ Lưu Chú
- Không ghi lại câu hỏi
- Chỉ ghi theo kiểu:
  "4. Thời Khí: Hoàng Đạo - có trợ lực"
  hoặc
  "4. Thời Khí: Hắc Đạo - nên xem xét thận trọng"
- Phải xét thêm dữ liệu Tý Ngọ Lưu Chú:
  - Nếu bộ phận đang xem trùng hoặc gần vùng khí huyết đang vượng theo Tý Ngọ Lưu Chú, phải cảnh báo rõ
  - Nếu không phạm, có thể nói ngắn là không bị Tý Ngọ Lưu Chú cản trở trực tiếp
- Hoàng Đạo là điểm tốt phụ trợ
- Hắc Đạo là điểm cần thận trọng
- Hoàng/Hắc Đạo không được phép tự lật ngược hung thần nặng

5. Nhật Y
- Chỉ ghi:
  "5. Nhật Y: Có Bổ Trợ"
  hoặc
  "5. Nhật Y: Không Bổ Trợ"
- Nếu có bổ trợ, giải thích ngắn là trợ lực hồi phục hay giảm trở ngại

6. Nhân Thần Canh Giờ
- Nếu không phạm: chỉ ghi "6. Nhân Thần Canh Giờ: Không Phạm"
- Nếu phạm: ghi rõ phạm tại đâu, vì sao cần tránh

7. Nhân Thần Can Ngày
- Nếu không phạm: chỉ ghi "7. Nhân Thần Can Ngày: Không Phạm"
- Nếu phạm: giải thích ngắn, rõ

8. Nhân Thần Chi Ngày
- Nếu không phạm: chỉ ghi "8. Nhân Thần Chi Ngày: Không Phạm"
- Nếu phạm: giải thích ngắn, rõ

9. Hung Thần
- Không liệt kê toàn bộ nếu tất cả đều không phạm
- Nếu tất cả đều không phạm, chỉ ghi:
  "9. Hung Thần: Không Phạm"
- Nếu có 1 hoặc nhiều hung thần phạm:
  - ghi tên từng hung thần đang phạm
  - giải thích ngắn hung thần đó gây bất lợi gì
- Chỉ ghi các hung thần thực sự xuất hiện

10. Cát Thần
- Không nhắc Nhật Y ở mục này
- Chỉ xét Thiên Y và Địa Y
- Nếu không có cát thần: ghi
  "10. Cát Thần: Không Có"
- Nếu có, ghi rõ:
  "10. Cát Thần: Thiên Y - trợ lực ..."
  hoặc
  "10. Cát Thần: Địa Y - bổ trợ ..."
- Chỉ giải thích tác dụng thực tế, không nói dài

LƯU Ý VỀ NGỮ KHÍ:
- Nếu là hoạt động thăm khám hoặc chẩn đoán hình ảnh:
  + Không dùng giọng quá nặng như phẫu thuật.
  + Nếu giờ thuận, có thể nói theo hướng thuận cho việc phát hiện sớm, nhìn dấu hiệu rõ hơn, dễ chốt hướng theo dõi hơn.
  + Nếu giờ chưa đẹp hoặc rơi vào Hắc Đạo, không được nói theo kiểu cấm khám; chỉ được khuyên thận trọng hơn khi đọc kết quả, đối chiếu triệu chứng và tái kiểm nếu cần.

- Nếu là thủ thuật hoặc can thiệp xâm lấn:
  + Khi đó mới được dùng giọng thận trọng mạnh hơn.
  + Nếu có triệu chứng kéo dài, sưng đau, chảy máu hoặc dấu hiệu viêm, có thể nhắc người đọc lưu ý theo dõi sát và tuân thủ bác sĩ chuyên khoa.
- Trong JSON, trường "phan_loai_thu_tuc" là dữ liệu ưu tiên cao.
- Phải dùng các trường:
  + loai
  + muc_do
  + xam_lan
  + dinh_huong_luan
  + uu_tien
  để quyết định giọng điệu và mức độ thận trọng.
- Không được luận cùng một giọng cho khám tổng quát, chẩn đoán hình ảnh, nha khoa chuyên sâu và đại phẫu.

➥ Kết Luận Cuối Cùng : 
- Phải đưa ra kết luận dứt khoát, không mập mờ
- Không được chỉ chép lại dữ liệu
- Phải phân tích logic toàn bộ rồi quyết định
- Viết như bác sĩ đang khuyên bệnh nhân
- Tự nhiên, dịu, sáng nghĩa
- Nhưng phải có quyết định rõ
- Không được chỉ lặp lại dữ liệu
- Sau 10 mục chính, viết thêm 1 đoạn tổng hợp 3 đến 5 câu theo giọng bác sĩ:
  bình tĩnh, tự nhiên, sáng nghĩa, giúp người đọc hiểu bản chất của thời điểm đó.
- Với hoạt động thăm khám hoặc chẩn đoán hình ảnh, không dùng giọng cấm đoán như phẫu thuật.
- Với hoạt động xâm lấn, mới được nhấn mạnh mức độ kiêng kỵ.

QUY TẮC RA QUYẾT ĐỊNH:
- Nếu phạm Nhật Phá, Nguyệt Phá, Tuế Phá, hoặc phạm Hung Thần quan trọng, hoặc phạm Nhân Thần đúng bộ phận, hoặc phạm Tý Ngọ Lưu Chú đúng vùng đang can thiệp:
  => kết luận thiên về KHÔNG NÊN
- Nếu không phạm các điểm hung chính, lại có Hoàng Đạo hoặc có Thiên Y / Địa Y / Nhật Y:
  => có thể kết luận NÊN hoặc CÓ THỂ TIẾN HÀNH
- Nếu không phạm hung lớn nhưng rơi vào Hắc Đạo:
  => kết luận trung tính thận trọng, ưu tiên đổi sang giờ đẹp hơn nếu không gấp
- Cát thần chỉ bổ trợ, không được lật ngược hung nặng

CUỐI CÙNG PHẢI VIẾT ĐÚNG 2 DÒNG:
✅ Nên: ...
⛔ Không Nên: ...

MẪU VĂN PHONG:
"Xét tổng thể, thời điểm này không phạm các hung điểm lớn. Với một việc mang tính thăm khám hoặc chẩn đoán, giờ này không tạo trở ngại trực tiếp. Nếu đi vào thời khí thuận, ý nghĩa thiên về dễ phát hiện vấn đề sớm hơn, thuận cho việc đọc dấu hiệu và định hướng theo dõi. Nếu rơi vào giờ khí tượng kém hơn, vẫn có thể tiến hành, nhưng nên đọc kết quả kỹ và đối chiếu triệu chứng cẩn thận."

➥ Kết Luận Cuối Cùng : 
✅ Nên: ...
⛔ Không Nên: ...

Không được viết lại câu hỏi. Không được dài dòng. Phải đưa ra quyết định thật sự.
"""

        config = genai.GenerationConfig(
            temperature=0.25,
            top_k=8,
            top_p=0.9
        )

        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=prompt_bac_si,
            generation_config=config
        )

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
        is_cap_cuu = any(tu_khoa in trieu_chung.lower() for tu_khoa in TU_KHOA_CAP_CUU)
        
        if is_cap_cuu:
            st.error("🚨 CẢNH BÁO Y KHOA KHẨN CẤP 🚨")
            st.warning("""
            Hệ thống phát hiện dấu hiệu nguy hiểm liên quan đến tính mạng. 
            Tuyệt đối không dùng thuốc Nam hay chờ đợi giờ tốt lúc này.
            **YÊU CẦU:** Gọi ngay cấp cứu  hoặc đến bệnh viện gần nhất ngay lập tức!
            """)
        else:
            # Nếu an toàn, tiếp tục phân tích Dịch Lý và gọi AI
            with st.spinner("Đang chẩn đoán mạch và hội chẩn Dịch Lý..."):
                bao_cao = engine.lap_bao_cao_chi_tiet(
                    data['chi_nam'],
                    thang_am,
                    data['can_ngay'],
                    data['chi_ngay'],
                    gio_kham,
                    ngay_am,
                    bo_phan,
                    loai_hoat_dong,
                    data['hoang_dao_list']
                )

                context = json.dumps(
                    {
                        "thong_tin_kham": {
                            "nam": data['nam'],
                            "thang": data['thang'],
                            "ngay": data['ngay'],
                            "thang_am": thang_am,
                            "ngay_am": ngay_am,
                            "gio_kham": gio_kham,
                            "bo_phan": bo_phan,
                            "loai_hoat_dong": loai_hoat_dong,
                            "trieu_chung": trieu_chung
                        },
                        "bao_cao_ylct": bao_cao
                    },
                    ensure_ascii=False,
                    indent=2
                )

                loi_khuyen = xin_loi_khuyen_ai(context)

                if "Lỗi hệ thống" not in loi_khuyen:
                    st.success("Hoàn tất luận giải!")
                    st.markdown(loi_khuyen)

                    st.markdown("""
                    <div style="
                        font-size: 12px;
                        font-style: italic;
                        color: #b8c0cc;
                        margin-top: 8px;
                        line-height: 1.6;
                    ">
                    🚨Khuyến cáo y tế: Nếu có các dấu hiệu nguy cấp như khó thở, đau ngực dữ dội, sốt cao liên tục, chảy máu không cầm, ngất, co giật, méo miệng, yếu liệt, đau bụng dữ dội, nôn ra máu hoặc bất kỳ biểu hiện bất thường nghiêm trọng nào, cần đi cấp cứu ngay hoặc gọi số Cấp Cứu Khẩn Cấp, không thể chờ Ngày - Giờ Tốt.
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("Xem dữ liệu logic thô"):
                        st.json(bao_cao)
                else:
                    st.error(loi_khuyen)

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 14px;'>© 2025 Y Lý Cát Thời - Kinh Dịch Hội - Mai Hoa Dịch Số - Ứng dụng thuộc bản quyền tác giả Chris Nhật Tôn. Vui lòng tham khảo ý kiến bác sĩ chuyên khoa trước khi áp dụng.</div>", unsafe_allow_html=True)