import html
import streamlit as st
from src.chain import get_recommendation_stream, get_structured_recommendation

st.set_page_config(page_title="카드 추천 AI", page_icon="💳", layout="wide")

# 다크 + 비비드 테마 CSS
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e0e0;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
        border-right: 1px solid #333;
    }

    /* 메인 타이틀 */
    .main-title {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff6bcb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* 섹션 헤더 */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid;
    }
    .section-header.credit {
        color: #7b2ff7;
        border-color: #7b2ff7;
    }
    .section-header.check {
        color: #00d2ff;
        border-color: #00d2ff;
    }

    /* 카드 컨테이너 */
    .card-box {
        background: linear-gradient(145deg, #1e1e36, #2a2a4a);
        border: 1px solid #444;
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .card-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(123, 47, 247, 0.3);
    }
    .card-box.check-type:hover {
        box-shadow: 0 8px 30px rgba(0, 210, 255, 0.3);
    }

    /* 넘버링 뱃지 */
    .card-number {
        position: absolute;
        top: 0;
        left: 0;
        color: #fff;
        font-weight: 800;
        font-size: 1rem;
        padding: 0.4rem 1rem 0.4rem 0.8rem;
        border-radius: 16px 0 16px 0;
    }
    .card-number.credit {
        background: linear-gradient(135deg, #7b2ff7, #a855f7);
    }
    .card-number.check {
        background: linear-gradient(135deg, #00d2ff, #0ea5e9);
    }

    /* 카드 이름 */
    .card-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 1.5rem;
        margin-bottom: 0.2rem;
    }
    .card-company {
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 0.3rem;
    }
    .card-fee {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 1rem;
    }

    /* 추천 이유 */
    .reason-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #7b2ff7;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .reason-text {
        font-size: 0.95rem;
        color: #d0d0d0;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* 절약 금액 뱃지 */
    .saving-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00d2ff22, #7b2ff722);
        border: 1px solid #7b2ff7;
        color: #00d2ff;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin-top: 0.3rem;
    }

    /* 링크 버튼 */
    .card-link-btn {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.5rem 1.2rem;
        background: linear-gradient(135deg, #ff6bcb, #ff9de0);
        color: #1a1a2e !important;
        font-size: 0.85rem;
        font-weight: 700;
        text-decoration: none;
        border-radius: 8px;
        transition: opacity 0.2s;
    }
    .card-link-btn:hover {
        opacity: 0.8;
        color: #1a1a2e !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #7b2ff7, #00d2ff) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.7rem 2rem !important;
        border-radius: 12px !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.85 !important;
    }

    /* 텍스트 영역 */
    .stTextArea textarea {
        background: #1a1a2e !important;
        color: #e0e0e0 !important;
        border: 1px solid #444 !important;
        border-radius: 10px !important;
    }

    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background: #1a1a2e !important;
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-title">CARD RECOMMEND AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">소비 패턴을 입력하면 AI가 맞춤 카드를 추천해드립니다</div>', unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown("### 사용자 정보 입력")

    examples = {
        "직접 입력": "",
        "🎓 이세봉(26세, 유학생)": "서울 소재 대학원(공학계열) 재학 중인 중국 유학생입니다. 중국 부모님 송금 100만원+소액 과외 20만원으로 월 수입 약 120만원입니다. 고시원/원룸 월세 45만원, 학교 근처 중국음식점+편의점 식비 월 25만원, 지하철/버스 교통비 월 2만5천원, 중국 부모님 계좌 해외송금 수수료 월 1~2회 약 5만원, 알리익스프레스·타오바오 직구 해외결제 월 15만원, 외국인 전용 통신 요금제 월 3만원, OTT(아이치이·유튜브)+게임 여가비 월 2만원을 씁니다. 해외결제 수수료 면제, 해외송금 우대, 편의점 할인, 교통 할인이 필요합니다.",
        "✈️ 김지연(34세, 직장인 여성)": "서울 거주 마케팅회사 대리, 월 실수령 약 280만원입니다. 해외여행 연 2회(항공+숙박) 연 300만원, 피부과/내과 등 의료비 월 20만원, 주유·주차·정비 등 차량 유지비 연 180만원, 무신사·올리브영 등 온라인쇼핑 월 25만원, 스타벅스 출퇴근 커피 월 10만원을 씁니다. 항공 마일리지, 해외결제 수수료 면제, 의료비 할인이 필요합니다.",
        "🍗 박민수(42세, 자영업자)": "경기도 거주, 치킨 프랜차이즈 운영, 월 카드 지출 약 500만원(사업비 포함)입니다. 마트 식자재 대량 구매 월 200만원, 배달용 오토바이+자차 주유비 월 40만원, 사업장 회선 포함 통신/인터넷 월 20만원, 직원 식사 등 외식/회식 월 30만원, 배민 광고비 월 50만원을 씁니다. 높은 전월실적 조건 충족 가능하며, 마트 적립, 주유 할인, 포인트 환급 극대화가 필요합니다.",
        "💻 최수아(28세, 사회초년생)": "서울 자취, IT 스타트업 신입 개발자, 월 실수령 약 280만원입니다. 월세 자동이체 월 70만원, 배달앱(배민/쿠팡이츠) 위주 식비 월 35만원, 넷플릭스·유튜브프리미엄·Spotify 등 OTT/구독 월 4만원, 헬스장+PT 월 25만원, 쿠팡 로켓배송 쇼핑 월 25만원을 씁니다. 배달앱 할인, 구독서비스 할인, 쿠팡 적립, 스트리밍 혜택이 필요합니다.",
        "🏌️ 정태양(52세, 중년 직장인)": "수도권 거주 대기업 부장, 월 실수령 약 600만원입니다. 골프 라운딩+연습장 월 80만원, 접대 포함 고급 레스토랑 외식 월 70만원, 국내 리조트/호텔 여행 연 240만원, 백화점 의류/선물 월 50만원, 자녀 학원비 송금 월 100만원을 씁니다. 골프장 할인, 라운지 이용, 호텔 할인, 백화점 VIP 혜택, 높은 캐시백이 필요합니다.",
    }

    selected = st.selectbox("예시 페르소나 선택", list(examples.keys()))
    persona_text = st.text_area(
        "소비 패턴을 자유롭게 작성해주세요",
        value=examples[selected],
        height=200,
        placeholder="예: 대중교통으로 출퇴근하고, 편의점과 카페를 자주 이용하는 직장인입니다...",
    )


def render_card(rec, index, card_type="credit"):
    """카드 추천 결과를 렌더링"""
    card_name = html.escape(rec.get("card_name", "알 수 없음"))
    card_company = html.escape(rec.get("card_company", ""))
    reason = html.escape(rec.get("reason", ""))
    saving = html.escape(rec.get("monthly_saving", ""))
    annual_fee = html.escape(rec.get("annual_fee", ""))
    card_url = rec.get("card_url", "")

    link_html = ""
    if card_url and card_url.startswith(("http://", "https://")):
        safe_url = html.escape(card_url)
        link_html = f'<a class="card-link-btn" href="{safe_url}" target="_blank">카드 상세 보기 &rarr;</a>'

    fee_html = ""
    if annual_fee:
        fee_html = f'<div class="card-fee">연회비: {annual_fee}</div>'

    box_class = "card-box check-type" if card_type == "check" else "card-box"

    # 상세 설명 요약: 각 섹션의 첫 줄(제목+핵심)만 추출
    detail = rec.get("detail_description", "")
    detail_summary_html = ""
    if detail:
        lines = [l.strip() for l in detail.split("\n") if l.strip()]
        summary_items = []
        for line in lines:
            if line.startswith("[") and line.endswith("]"):
                summary_items.append(html.escape(line.strip("[]")))
        if not summary_items:
            summary_items = [html.escape(l) for l in lines[:5]]
        detail_summary_html = (
            '<div class="reason-label" style="margin-top:1rem;">주요 혜택</div>'
            '<div class="reason-text">' + " · ".join(summary_items[:8]) + '</div>'
        )

    st.markdown(f"""
    <div class="{box_class}">
        <div class="card-number {card_type}">#{index}</div>
        <div class="card-name">{card_name}</div>
        <div class="card-company">{card_company}</div>
        {fee_html}
        <div class="reason-label">추천 이유</div>
        <div class="reason-text">{reason}</div>
        <div class="reason-label">예상 월 절약 금액</div>
        <div class="saving-badge">{saving if saving else "산정 불가"}</div>
        {detail_summary_html}
        <br>{link_html}
    </div>
    """, unsafe_allow_html=True)


# 추천 버튼
mode = st.radio("출력 방식", ["구조화 카드", "스트리밍 텍스트"], horizontal=True)

if st.button("카드 추천 받기", type="primary", use_container_width=True):
    if not persona_text.strip():
        st.warning("소비 패턴을 입력해주세요.")
    elif mode == "스트리밍 텍스트":
        stream, source_cards = get_recommendation_stream(persona_text)
        st.write_stream(stream)
        if source_cards:
            st.markdown("---")
            st.markdown("**참고 카드:**")
            for card in source_cards:
                name = html.escape(card.get("card_name", ""))
                url = card.get("card_url", "")
                if url and url.startswith(("http://", "https://")):
                    st.markdown(f"- [{name}]({url})")
                else:
                    st.markdown(f"- {name}")
    else:
        with st.spinner("AI가 맞춤 카드를 분석하고 있습니다..."):
            result = get_structured_recommendation(persona_text)

        credit_recs = result.get("credit", [])
        check_recs = result.get("check", [])

        if not credit_recs and not check_recs:
            st.error("추천 결과를 생성하지 못했습니다. 다시 시도해주세요.")
        else:
            col_credit, col_check = st.columns(2)

            with col_credit:
                if credit_recs:
                    st.markdown(
                        '<div class="section-header credit">💳 신용카드 TOP 3</div>',
                        unsafe_allow_html=True,
                    )
                    for i, rec in enumerate(credit_recs, 1):
                        render_card(rec, i, "credit")

            with col_check:
                if check_recs:
                    st.markdown(
                        '<div class="section-header check">🏦 체크카드 TOP 3</div>',
                        unsafe_allow_html=True,
                    )
                    for i, rec in enumerate(check_recs, 1):
                        render_card(rec, i, "check")
