import streamlit as st
import math

# --- 1. 컨트롤러 매칭 함수 ---
def get_controller_recommendation(total_px, brand="Novastar"):
    if brand == "Novastar":
        if total_px > 8800000: return "Nova Pro UHD Jr / H Series"
        elif total_px > 3900000: return "MCTRL4K / VX1000"
        elif total_px > 2300000: return "VX600 / VX1000"
        elif total_px > 1300000: return "VX400 / MCTRL660"
        else: return "MCTRL300 / VX200"
    elif brand == "Colorlight":
        if total_px > 8800000: return "Z8t / Z6 Ultra"
        elif total_px > 3900000: return "X16E / X20"
        elif total_px > 2300000: return "X8e / X12"
        elif total_px > 1300000: return "X4e / VX4S-N(CL)"
        else: return "S2 / S4"

# --- 2. 전선 굵기(SQ) 산출 함수 ---
def get_wire_sq(ampere):
    if ampere <= 18: return "2.5 SQ"
    elif ampere <= 26: return "4.0 SQ"
    elif ampere <= 34: return "6.0 SQ"
    elif ampere <= 48: return "10.0 SQ"
    elif ampere <= 65: return "16.0 SQ"
    else: return "25.0 SQ 이상 권장"

# --- 3. 데이터베이스 (피치, 규격 정보 포함) ---
db = {
    "실내": {
        "P0.9 (Fine)": {"pitch": 0.9, "c_w": 600, "c_h": 337.5, "p_w": 666, "p_h": 375, "power": 350, "weight": 6.8},
        "P1.25": {"pitch": 1.25, "c_w": 600, "c_h": 337.5, "p_w": 480, "p_h": 270, "power": 300, "weight": 6.5},
        "P1.53": {"pitch": 1.53, "c_w": 640, "c_h": 480, "p_w": 418, "p_h": 313, "power": 250, "weight": 7.5},
        "P1.86": {"pitch": 1.86, "c_w": 640, "c_h": 480, "p_w": 344, "p_h": 258, "power": 250, "weight": 7.5},
        "P2.5": {"pitch": 2.5, "c_w": 640, "c_h": 480, "p_w": 256, "p_h": 192, "power": 220, "weight": 7.2},
        "P4.0 (In-Max)": {"pitch": 4.0, "c_w": 512, "c_h": 512, "p_w": 128, "p_h": 128, "power": 200, "weight": 8.0},
    },
    "실외": {
        "P3.0 (Out)": {"pitch": 3.0, "c_w": 960, "c_h": 960, "p_w": 320, "p_h": 320, "power": 500, "weight": 35.0},
        "P4.0 (Out)": {"pitch": 4.0, "c_w": 960, "c_h": 960, "p_w": 240, "p_h": 240, "power": 450, "weight": 35.0},
        "P6.0 (Out)": {"pitch": 6.0, "c_w": 960, "c_h": 960, "p_w": 160, "p_h": 160, "power": 450, "weight": 35.0},
        "P10.0 (Out)": {"pitch": 10.0, "c_w": 960, "c_h": 960, "p_w": 96, "p_h": 96, "power": 400, "weight": 35.0},
        "P16.0 (Out-Max)": {"pitch": 16.0, "c_w": 1024, "c_h": 1024, "p_w": 64, "p_h": 64, "power": 400, "weight": 40.0}
    }
}

# --- 4. 메인 설정 및 사이드바 ---
st.set_page_config(page_title="LED 설계 마스터 v6.0", layout="wide")
st.title("🏗️ LED 전광판 통합 설계 마스터 v6.0")

st.sidebar.header("1. 제품 사양 선택")
env = st.sidebar.selectbox("설치 환경", ["실내", "실외"])
pitch_list = list(db[env].keys()) + ["직접 입력 (Custom)"]
selected_pitch = st.sidebar.selectbox("픽셀 피치 선택", pitch_list)

p = {}

if selected_pitch == "직접 입력 (Custom)":
    st.sidebar.info("🛠️ 제품 카탈로그의 수치를 입력하세요.")
    p_name = st.sidebar.text_input("커스텀 제품 이름", value="Custom LED Cabinet")
    p_val = st.sidebar.number_input("픽셀 피치 (mm)", value=2.5, step=0.1, format="%.2f")
    c_w = st.sidebar.number_input("캐비닛 가로 (mm)", value=640.0)
    c_h = st.sidebar.number_input("캐비닛 세로 (mm)", value=480.0)
    
    auto_p_w = int(c_w / p_val) if p_val > 0 else 0
    auto_p_h = int(c_h / p_val) if p_val > 0 else 0
    
    st.sidebar.caption(f"💡 계산된 해상도: {auto_p_w} x {auto_p_h} px")
    p_w = st.sidebar.number_input("확정 가로 해상도 (px)", value=auto_p_w)
    p_h = st.sidebar.number_input("확정 세로 해상도 (px)", value=auto_p_h)
    
    p_power = st.sidebar.number_input("평균 전력 (W/m²)", value=300)
    p_weight = st.sidebar.number_input("캐비닛 무게 (kg/pcs)", value=7.5)
    
    p = {"name": p_name, "pitch": p_val, "c_w": c_w, "c_h": c_h, "p_w": p_w, "p_h": p_h, "power": p_power, "weight": p_weight}
else:
    p = db[env][selected_pitch]
    p["name"] = selected_pitch

st.sidebar.header("2. 목표 설치 공간")
target_w = st.sidebar.number_input("목표 가로 (mm)", value=5000.0)
target_h = st.sidebar.number_input("목표 세로 (mm)", value=3000.0)

st.sidebar.header("3. 전기 및 배선")
p_mode = st.sidebar.radio("공급 방식", ["3상4선(380V)", "단상(220V)"])
branch_limit_amp = st.sidebar.selectbox("분기 차단기 용량", [20, 30], index=0)
margin_percent = st.sidebar.slider("전력 할증 (%)", 0, 100, 70)
cable_dist = st.sidebar.slider("컨트롤러 거리 (m)", 5, 100, 20)

# --- 5. 연산 로직 ---
nw, nh = max(1, round(target_w / p['c_w'])), max(1, round(target_h / p['c_h']))
fw, fh = nw * p['c_w'], nh * p['c_h']
diff_w, diff_h = fw - target_w, fh - target_h
total_cabs = nw * nh
res_w, res_h = nw * p['p_w'], nh * p['p_h']
total_px = res_w * res_h
area = (fw * fh) / 1_000_000

design_power_kw = ((area * p['power'] * 2.5) / 1000) * (1 + margin_percent/100)
if p_mode == "3상4선(380V)":
    calc_amp = (design_power_kw * 1000) / (math.sqrt(3) * 380)
else:
    calc_amp = (design_power_kw * 1000) / 220

main_breaker = max(20, math.ceil(calc_amp/10)*10 + 10)
main_wire_sq = get_wire_sq(calc_amp)

branch_safe_watt = branch_limit_amp * 220 * 0.7
total_watt_val = design_power_kw * 1000
num_branches = math.ceil(total_watt_val / branch_safe_watt) if total_watt_val > 0 else 1
cabs_per_branch = math.floor(total_cabs / num_branches) if num_branches > 0 else 0

total_weight = (total_cabs * p['weight']) + (area * (15 if env == "실내" else 30))
ports_needed = math.ceil(total_px / 650000)
lan_total_m = (ports_needed * cable_dist) + ((total_cabs - ports_needed) * 1.2)

def get_aspect_ratio(w, h):
    gcd = math.gcd(int(w), int(h))
    return f"{int(w/gcd)}:{int(h/gcd)}"
aspect_ratio = get_aspect_ratio(res_w, res_h)

# --- 6. 결과 UI ---
st.subheader(f"📊 {p['name']} (P{p['pitch']}) 설계 리포트")

m1, m2, m3, m4 = st.columns(4)
m1.metric("최종 화면비", aspect_ratio)
m2.metric("실제 화면 규격", f"{fw/1000:.2f} x {fh/1000:.2f} m")
m3.metric("설계 전력", f"{design_power_kw:.2f} kW")
m4.metric("메인 전류", f"{calc_amp:.1f} A")

st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.success("### 📐 하드웨어 규격 상세")
    st.write(f"• **사용 캐비닛 종류:** `{p['name']}`")
    st.write(f"• **캐비닛 개별 크기:** `{p['c_w']} x {p['c_h']} mm` (가로x세로)")
    st.write(f"• **캐비닛 개별 해상도:** `{p['p_w']} x {p['p_h']} px` (피치: P{p['pitch']})")
    st.divider()
    st.table({
        "구분": ["목표 (Target)", "실제 (Actual)", "오차 (Diff)"],
        "가로 (W)": [f"{target_w:,} mm", f"{fw:,} mm", f"{diff_w:+} mm"],
        "세로 (H)": [f"{target_h:,} mm", f"{fh:,} mm", f"{diff_h:+} mm"]
    })
    st.write(f"• **전체 구성:** {nw}열 x {nh}단 (총 {total_cabs}대)")
    st.write(f"• **전체 해상도:** `{res_w} x {res_h} px` (총 {total_px:,} px)")
    st.write(f"• **총 예상 하중:** {total_weight:.1f} kg")

with col_r:
    st.error("### ⚡ 전기 및 시스템 설계")
    st.write(f"• **메인 차단기:** `{main_breaker}A ({'4P' if p_mode=='3상4선(380V)' else '2P'})` / `{main_wire_sq}`")
    st.divider()
    st.write(f"• **분기 차단기:** `{branch_limit_amp}A` x `{num_branches} 회선` (단상)")
    st.write(f"• **회선당 부하:** 회선당 약 {cabs_per_branch}대 연결 / `2.5 SQ` 배선")
    st.divider()
    
    st.write(f"• **Novastar 추천:** `{get_controller_recommendation(total_px, 'Novastar')}`")
    st.write(f"• **Colorlight 추천:** `{get_controller_recommendation(total_px, 'Colorlight')}`")
    st.write(f"• **데이터 포트:** 최소 {ports_needed} 포트 사용 / LAN: 약 {lan_total_m:.0f}m")

# --- 7. 요약 리포트 ---
st.markdown("---")
if st.button("📝 현장 제출용 요약서 생성"):
    summary = f"""[LED 전광판 시공 설계 발주서]

1. 제품 정보
- 캐비닛 종류: {p['name']}
- 캐비닛 크기: {p['c_w']} x {p['c_h']} mm (P{p['pitch']})
- 실제 화면규격: {fw:,} x {fh:,} mm (오차 W:{diff_w:+} / H:{diff_h:+})
- 전체 해상도: {res_w} x {res_h} px ({aspect_ratio})
- 전체 구성: {nw}열 x {nh}단 (총 {total_cabs}대)

2. 전기 시공
- 설계부하: {design_power_kw:.2f} kW / {calc_amp:.1f} A
- 메인차단기: {main_breaker}A / 전선: {main_wire_sq}
- 분기차단기: {branch_limit_amp}A x {num_branches}회선 (회선당 {cabs_per_branch}대)

3. 시스템 및 하중
- 컨트롤러: {get_controller_recommendation(total_px, 'Novastar')}
- 하중: {total_weight:.1f} kg / LAN: 약 {lan_total_m:.0f}m"""
    st.text_area("내용 복사(Ctrl+C)", value=summary, height=400)
