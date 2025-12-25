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
    """단상 220V, F-CV 전선 기준 간이 허용전류 매칭 (KEC 참고)"""
    if ampere <= 18: return "2.5 SQ"
    elif ampere <= 26: return "4.0 SQ"
    elif ampere <= 34: return "6.0 SQ"
    elif ampere <= 48: return "10.0 SQ"
    elif ampere <= 65: return "16.0 SQ"
    else: return "25.0 SQ 이상 권장"

# --- 3. 페이지 설정 및 데이터베이스 ---
st.set_page_config(page_title="LED 전광판 통합 설계 마스터 v5.5", layout="wide")
st.title("🏗️ LED 전광판 통합 설계 마스터 v5.5")
st.write("전기 시공 규격(차단기/전선SQ) 및 오차 분석 통합 버전")

db = {
    "실내": {
        "P0.9 (Fine)": {"m_w": 300, "m_h": 168.75, "c_w": 600, "c_h": 337.5, "p_w": 666, "p_h": 375, "power": 350, "weight": 6.8},
        "P1.25": {"m_w": 300, "m_h": 168.75, "c_w": 600, "c_h": 337.5, "p_w": 480, "p_h": 270, "power": 300, "weight": 6.5},
        "P1.53": {"m_w": 320, "m_h": 160, "c_w": 640, "c_h": 480, "p_w": 418, "p_h": 313, "power": 250, "weight": 7.5},
        "P1.86": {"m_w": 320, "m_h": 160, "c_w": 640, "c_h": 480, "p_w": 344, "p_h": 258, "power": 250, "weight": 7.5},
        "P2.5": {"m_w": 320, "m_h": 160, "c_w": 640, "c_h": 480, "p_w": 256, "p_h": 192, "power": 220, "weight": 7.2},
        "P4.0 (In-Max)": {"m_w": 256, "m_h": 128, "c_w": 512, "c_h": 512, "p_w": 128, "p_h": 128, "power": 200, "weight": 8.0},
    },
    "실외": {
        "P3.0 (Out)": {"m_w": 320, "m_h": 160, "c_w": 960, "c_h": 960, "p_w": 320, "p_h": 320, "power": 500, "weight": 35.0},
        "P4.0 (Out)": {"m_w": 320, "m_h": 160, "c_w": 960, "c_h": 960, "p_w": 240, "p_h": 240, "power": 450, "weight": 35.0},
        "P6.0 (Out)": {"m_w": 192, "m_h": 192, "c_w": 960, "c_h": 960, "p_w": 160, "p_h": 160, "power": 450, "weight": 35.0},
        "P10.0 (Out)": {"m_w": 320, "m_h": 160, "c_w": 960, "c_h": 960, "p_w": 96, "p_h": 96, "power": 400, "weight": 35.0},
        "P16.0 (Out-Max)": {"m_w": 256, "m_h": 256, "c_w": 1024, "c_h": 1024, "p_w": 64, "p_h": 64, "power": 400, "weight": 40.0}
    }
}

# --- 4. 사이드바 설정 ---
st.sidebar.header("1. 환경 및 제품 선택")
env = st.sidebar.selectbox("설치 환경", ["실내", "실외"])
selected_pitch = st.sidebar.selectbox("픽셀 피치 선택", list(db[env].keys()))

st.sidebar.header("2. 목표 설치 공간 (mm)")
target_w = st.sidebar.number_input("목표 가로(W)", value=5760)
target_h = st.sidebar.number_input("목표 세로(H)", value=3240)

st.sidebar.header("3. 전기 및 배선 설정")
p_mode = st.sidebar.radio("전력 공급 방식", ["3상4선(380V)", "단상(220V)"])
branch_limit_amp = st.sidebar.selectbox("분기 차단기 용량(A)", [20, 30], index=0)
margin_percent = st.sidebar.slider("전력 여유율 할증 (%)", 0, 100, 70)
cable_dist = st.sidebar.slider("컨트롤러↔화면 거리 (m)", 5, 100, 20)

# --- 5. 연산 로직 (변수 에러 방지를 위해 통합 계산) ---
p = db[env][selected_pitch]

# 규격 및 해상도
nw, nh = max(1, round(target_w / p['c_w'])), max(1, round(target_h / p['c_h']))
fw, fh = nw * p['c_w'], nh * p['c_h']
diff_w, diff_h = fw - target_w, fh - target_h
total_cabs = nw * nh
res_w, res_h = nw * p['p_w'], nh * p['p_h']
total_px = res_w * res_h
area = (fw * fh) / 1_000_000

# 전력 및 전류
base_kw = (area * p['power'] * 2.5) / 1000
design_power_kw = base_kw * (1 + margin_percent/100)

if p_mode == "3상4선(380V)":
    calc_amp = (design_power_kw * 1000) / (math.sqrt(3) * 380)
else:
    calc_amp = (design_power_kw * 1000) / 220

# 차단기 및 전선 굵기
main_breaker = max(20, math.ceil(calc_amp/10)*10 + 10)
main_wire_sq = get_wire_sq(calc_amp)

# 분기 회로 (안전율 70% 적용)
branch_safe_watt = branch_limit_amp * 220 * 0.7
num_branches = math.ceil((design_power_kw * 1000) / branch_safe_watt)
cabs_per_branch = math.floor(total_cabs / num_branches) if num_branches > 0 else 0

# 하중 및 케이블
total_weight = (total_cabs * p['weight']) + (area * (15 if env == "실내" else 30))
ports_needed = math.ceil(total_px / 650000)
lan_total_m = (ports_needed * cable_dist) + ((total_cabs - ports_needed) * 1.2)

# 화면비
def get_aspect_ratio(w, h):
    gcd = math.gcd(int(w), int(h))
    return f"{int(w/gcd)}:{int(h/gcd)}"
aspect_ratio = get_aspect_ratio(res_w, res_h)

# --- 6. 결과 UI ---
st.subheader(f"📊 {selected_pitch} 시공 설계 리포트")
m1, m2, m3, m4 = st.columns(4)
m1.metric("최종 화면비", aspect_ratio)
m2.metric("실제 화면 크기", f"{fw/1000:.2f} x {fh/1000:.2f}m")
m3.metric("설계 전력", f"{design_power_kw:.2f} kW")
m4.metric("메인 전류", f"{calc_amp:.1f} A")

st.markdown("---")
col_l, col_r = st.columns(2)

with col_l:
    st.success("### 📐 규격 및 해상도 상세")
    st.write("#### [규격 비교]")
    st.table({
        "구분": ["목표 규격", "실제 화면", "오차(Diff)"],
        "가로(W)": [f"{target_w:,} mm", f"{fw:,} mm", f"{diff_w:+} mm"],
        "세로(H)": [f"{target_h:,} mm", f"{fh:,} mm", f"{diff_h:+} mm"]
    })
    st.info(f"📍 **캐비닛 1대 해상도: {p['p_w']} x {p['p_h']} px**")
    st.write(f"• **전체 구성:** {nw}열 x {nh}단 (총 {total_cabs}대)")
    st.write(f"• **전체 해상도:** `{res_w} x {res_h} px` (총 {total_px:,} px)")
    st.write(f"• **예상 하중:** {total_weight:.1f} kg")

with col_r:
    st.error("### ⚡ 시스템 및 전기 시공")
    st.write(f"• **메인 차단기:** `{main_breaker}A ({'4P' if p_mode=='3상4선(380V)' else '2P'})`")
    st.write(f"• **메인 전선 굵기:** `{main_wire_sq}` (F-CV 기준)")
    st.divider()
    st.write(f"• **분기 차단기:** `{branch_limit_amp}A` x `{num_branches}회선` (단상)")
    st.write(f"• **회선당 부하:** 약 {cabs_per_branch}대 연결 / `2.5 SQ` 전선 권장")
    st.divider()
    
    nova_rec = get_controller_recommendation(total_px, "Novastar")
    color_rec = get_controller_recommendation(total_px, "Colorlight")
    st.write(f"• **Novastar 추천:** `{nova_rec}`")
    st.write(f"• **Colorlight 추천:** `{color_rec}`")
    st.write(f"• **필요 포트:** {ports_needed} Port / LAN 약 {lan_total_m:.0f}m")

# --- 7. 요약 리포트 생성 ---
st.markdown("---")
if st.button("📝 현장/발주용 요약 리포트 생성"):
    summary = f"""[LED 전광판 최종 시공 사양서]

1. 규격 및 구성
- 제품: {selected_pitch} ({env})
- 실제 규격: {fw:,} x {fh:,} mm (오차 W:{diff_w:+} / H:{diff_h:+})
- 해상도: {res_w} x {res_h} px (단위:{p['p_w']}x{p['p_h']})
- 구성: {nw}열 x {nh}단 (총 {total_cabs}대)

2. 전기 설비 사양
- 설계 전력: {design_power_kw:.2f} kW / 전류: {calc_amp:.1f}A
- 메인 차단기: {main_breaker}A / 메인 전선: {main_wire_sq}
- 분기 차단기: {branch_limit_amp}A x {num_branches}회선
- 분기 배선: 각 회로별 2.5 SQ 포설

3. 시스템 및 제어
- 컨트롤러: {nova_rec} ({ports_needed} Port 사용)
- LAN 케이블: 총 약 {lan_total_m:.0f}m 포설
- 총 예상하중: {total_weight:.1f} kg"""
    st.text_area("내용 복사(Ctrl+C)", value=summary, height=400)
