import hashlib
import re
from datetime import date

import pandas as pd
import streamlit as st

from ui_v2 import hero, card, empty_state, source_badge
from automatic import brief
from chat_research import published, parse_bundle, trends, growth, request_text


def _money(value):
    if value is None:
        return "자료 없음"
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return str(value)


def _percent(value):
    if value is None:
        return "자료 없음"
    try:
        return f"{float(value):+.1f}%"
    except (TypeError, ValueError):
        return str(value)


def _price_frame(price_bundle):
    if not price_bundle:
        return None
    rows = price_bundle.get("rows") or price_bundle.get("data") or []
    if not rows:
        return None
    frame = pd.DataFrame(rows)
    if "date" not in frame.columns or "close" not in frame.columns:
        return None
    frame["date"] = frame["date"].astype(str)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame = frame.dropna(subset=["close"])
    return frame if not frame.empty else None


def _research_map(state):
    reports = published()
    for item in state.get("chat_research", []):
        code = item.get("code")
        if code not in reports or item.get("as_of", "") >= reports[code].get("as_of", ""):
            reports[code] = item
    return reports


def _stock_map(state):
    stocks = {item["code"]: item for item in state.get("stocks", []) if item.get("code")}
    for position in st.session_state.get("account_snapshot", {}).get("positions", []):
        code = position.get("code")
        if code:
            stocks[code] = {**stocks.get(code, {}), **position, "code": code}
    return stocks


def _build_rows(stocks, reports):
    rows = []
    details = {}
    for key, stock in stocks.items():
        report = reports.get(key)
        if not report and key.startswith("pending-"):
            matches = [
                value for value in reports.values()
                if value.get("name", "").strip().casefold() == stock.get("name", "").strip().casefold()
            ]
            if len(matches) == 1:
                report = matches[0]
        report = report or {}
        financial = report.get("financial") or {}
        valuation = report.get("valuation") or {}
        flow = report.get("flow") or {}
        trend, frame = trends(report.get("prices"), report.get("as_of", date.today().isoformat()))
        code = report.get("code", key if not key.startswith("pending-") else "확인 필요")
        rows.append(
            {
                "종목": stock.get("name", "종목"),
                "코드": code,
                "매출 성장": growth(financial["revenue"], financial["prior_revenue"]) if financial else "조사 필요",
                "영업이익 성장": growth(financial["operating_profit"], financial["prior_operating_profit"]) if financial else "조사 필요",
                "외국인 / 기관": (
                    f"{flow['foreign']:+,.0f} / {flow['institution']:+,.0f} {flow['unit']}"
                    if flow else "조사 필요"
                ),
                "적정주가 참고": f"{valuation['base']:,.0f}원" if valuation else "조사 필요",
                "일봉": trend.get("daily", "자료 없음"),
                "주봉": trend.get("weekly", "자료 없음"),
                "조사일": report.get("as_of", "미조사"),
            }
        )
        details[key] = (stock, report, trend, frame)
    return rows, details


def _render_market_cards():
    st.subheader("시장 스냅샷")
    columns = st.columns(4)
    market_cards = [
        ("KOSPI", "데이터 연결 필요", "market.index"),
        ("KOSDAQ", "데이터 연결 필요", "market.index"),
        ("외국인 수급", "데이터 연결 필요", "market.investor_flow"),
        ("원/달러", "데이터 연결 필요", "macro.fx"),
    ]
    for column, (title, value, capability) in zip(columns, market_cards):
        with column:
            card(title, value, f"Capability · {capability}")


def _render_portfolio_summary():
    snapshot = st.session_state.get("account_snapshot") or {}
    positions = snapshot.get("positions") or []
    st.subheader("내 포트폴리오")
    if not positions:
        empty_state(
            "계좌 연결 대기",
            "계좌를 연결하면 보유 종목, 평가금액, 손익 요약을 이 영역에 표시합니다.",
        )
        return

    total_value = snapshot.get("total_value")
    total_profit = snapshot.get("total_profit")
    a, b, c = st.columns(3)
    a.metric("평가금액", _money(total_value) if total_value is not None else "자료 없음")
    b.metric("평가손익", _money(total_profit) if total_profit is not None else "자료 없음")
    c.metric("보유 종목", f"{len(positions)}개")
    portfolio_rows = []
    for position in positions[:10]:
        portfolio_rows.append(
            {
                "종목": position.get("name", position.get("code", "")),
                "수량": position.get("quantity", position.get("qty", "자료 없음")),
                "평가금액": position.get("value", position.get("market_value", "자료 없음")),
                "손익": position.get("profit", position.get("pnl", "자료 없음")),
            }
        )
    st.dataframe(pd.DataFrame(portfolio_rows), hide_index=True, use_container_width=True)


def _render_watchlist(stocks, details):
    st.subheader("관심 종목")
    if not stocks:
        empty_state("관심 종목 없음", "종목을 추가하면 이곳에서 분석 상태와 조사일을 확인할 수 있습니다.")
        return
    rows = []
    for key, stock in stocks.items():
        _, report, _, _ = details.get(key, (stock, {}, {}, None))
        rows.append(
            {
                "종목": stock.get("name", ""),
                "코드": report.get("code", "확인 필요" if key.startswith("pending-") else key),
                "상태": "조사 결과 있음" if report else "조사 필요",
                "조사일": report.get("as_of", "미조사"),
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def _render_sector_and_flow(reports):
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("업종별 등락률")
            empty_state("업종 데이터 연결 대기", "sector.performance Capability가 연결되면 업종별 등락과 거래대금을 표시합니다.")
    with right:
        with st.container(border=True):
            st.subheader("투자자별 매매동향")
            flows = []
            for report in reports.values():
                flow = report.get("flow") or {}
                if flow:
                    flows.append(
                        {
                            "종목": report.get("name", report.get("code", "")),
                            "외국인": flow.get("foreign"),
                            "기관": flow.get("institution"),
                            "단위": flow.get("unit", ""),
                        }
                    )
            if flows:
                st.dataframe(pd.DataFrame(flows), hide_index=True, use_container_width=True)
            else:
                empty_state("수급 데이터 없음", "조사 결과에 수급 자료가 포함되면 외국인·기관 순매수를 표시합니다.")


def _render_news(reports, stocks):
    with st.container(border=True):
        st.subheader("최신 뉴스 · 공시")
        notices = []
        for key, stock in stocks.items():
            report = reports.get(key) or {}
            for notice in report.get("disclosures", [])[:5]:
                notices.append({"name": stock.get("name", report.get("name", "")), **notice})
        notices = sorted(notices, key=lambda item: item.get("date", ""), reverse=True)
        if notices:
            for notice in notices[:8]:
                title = f"{notice.get('date', '')} · {notice.get('name', '')} · {notice.get('title', '공시') }"
                url = notice.get("url")
                if url:
                    st.link_button(title, url, use_container_width=True)
                else:
                    st.write(title)
        else:
            empty_state("공시 데이터 연결 대기", "선택 종목의 공식 공시가 수집되면 최신 변화 목록을 표시합니다.")


def _render_selected_detail(stocks, details, sample_mode):
    if not details:
        return
    st.subheader("기업 하나를 깊게 보기")
    selected = st.selectbox(
        "자세히 볼 종목",
        list(details),
        format_func=lambda key: stocks[key].get("name", key),
        key="research_selected",
    )
    stock, report, trend, frame = details[selected]
    if not report:
        st.info("이 종목의 조사 결과가 아직 없습니다. 조사 요청문을 대화창에 보내세요.")
        if stock.get("report"):
            st.write("기존 공식 결산 분석: " + brief(stock["report"])["summary"])
        return

    st.markdown(f"### {stock.get('name', report.get('name', '종목'))}")
    st.caption("조사일 " + report.get("as_of", "미조사") + " · 실시간 분석이 아닐 수 있습니다.")
    summary = report.get("summary")
    if summary:
        with st.container(border=True):
            st.markdown("**핵심 요약**")
            st.write(summary.get("text", ""))
            if summary.get("source"):
                st.link_button("요약 근거", summary["source"])

    tabs = st.tabs(["기업 정보", "실적", "주가 흐름", "가격과 확인 사항"])
    with tabs[0]:
        business = report.get("business")
        if business:
            st.write(business.get("text", ""))
            if business.get("source"):
                st.link_button("설명의 원문 근거", business["source"])
        else:
            st.info("기업 설명 조사 필요")
    with tabs[1]:
        financial = report.get("financial")
        if financial:
            st.caption(
                f"누적 {financial.get('period', '')} / 전년 {financial.get('prior_period', '')} · "
                f"{financial.get('basis', '')} · {financial.get('currency', '')} {financial.get('unit', '')}"
            )
            st.dataframe(
                [
                    {
                        "항목": "매출",
                        "이번 누적": financial.get("revenue"),
                        "전년 누적": financial.get("prior_revenue"),
                        "변화": growth(financial.get("revenue"), financial.get("prior_revenue")),
                    },
                    {
                        "항목": "영업이익",
                        "이번 누적": financial.get("operating_profit"),
                        "전년 누적": financial.get("prior_operating_profit"),
                        "변화": growth(financial.get("operating_profit"), financial.get("prior_operating_profit")),
                    },
                ],
                hide_index=True,
                use_container_width=True,
            )
            if financial.get("source"):
                st.link_button("실적 근거", financial["source"])
        else:
            st.info("전년 같은 기간 누적 실적 조사 필요")
    with tabs[2]:
        flow = report.get("flow")
        if flow:
            a, b = st.columns(2)
            a.metric("외국인 순매수", f"{flow.get('foreign', 0):+,.0f}")
            b.metric("기관 순매수", f"{flow.get('institution', 0):+,.0f}")
            if flow.get("source"):
                st.link_button("수급 근거", flow["source"])
        a, b = st.columns(2)
        a.metric("일봉 추세", trend.get("daily", "자료 없음"))
        b.metric("주봉 추세", trend.get("weekly", "자료 없음"))
        if frame is not None:
            st.caption("가격 자료 마지막 거래일 " + str(frame["date"].iloc[-1]))
            st.line_chart(frame.set_index("date")["close"])
            if report.get("prices", {}).get("source"):
                st.link_button("가격 자료 근거", report["prices"]["source"])
        else:
            st.info("가격 시계열 자료가 없습니다.")
    with tabs[3]:
        valuation = report.get("valuation")
        if valuation:
            a, b, c = st.columns(3)
            a.metric("낮은 참고가", f"{valuation.get('low', 0):,.0f}원")
            b.metric("기본 참고가", f"{valuation.get('base', 0):,.0f}원")
            c.metric("높은 참고가", f"{valuation.get('high', 0):,.0f}원")
            st.write(valuation.get("method", ""))
            if valuation.get("source"):
                st.link_button("평가 근거", valuation["source"])
        else:
            st.info("평가 가정과 가격 근거 조사 필요")
        for gap in report.get("data_gaps", []):
            st.write("확인 필요 · " + str(gap))

    if not sample_mode:
        with st.expander("투자일지 남기기"):
            with st.form("research_note"):
                note = st.text_area("투자일지 · 다음 확인할 조건")
                if st.form_submit_button("기록 저장") and note.strip():
                    try:
                        from datetime import datetime, timezone
                        store = st.session_state.get("research_store")
                        if store is not None:
                            store.log(
                                "journal",
                                {
                                    "code": selected,
                                    "at": datetime.now(timezone.utc).isoformat(),
                                    "kind": "note",
                                    "note": note.strip(),
                                },
                            )
                            st.success("일지를 저장했습니다.")
                        else:
                            st.warning("저장 연결을 확인하세요.")
                    except Exception:
                        st.error("저장 실패. 입력 내용을 보관하세요.")


def render_research(store, state, sample_mode):
    st.session_state.research_store = store
    hero(
        "시장을 읽고, 더 나은 판단을 만듭니다.",
        "시장 지수·포트폴리오·관심 종목·수급·공시를 한 화면에서 확인하는 StockDash 홈입니다.",
        "STOCKDASH · OVERVIEW",
    )

    if sample_mode:
        st.info("둘러보기 중입니다. 개인 목록을 저장하려면 대시보드 비밀번호를 설정하세요.")
    else:
        with st.expander("＋ 종목 추가", expanded=not state.get("stocks")):
            with st.form("research_manual"):
                name = st.text_input("종목명", placeholder="예: 삼성전자")
                with st.expander("종목코드를 알고 있다면 · 선택"):
                    code = st.text_input("종목코드", max_chars=6)
                if st.form_submit_button("내 목록에 추가"):
                    if not name.strip() or (code and not re.fullmatch(r"[0-9]{6}", code)):
                        st.error("종목명과 숫자 6자리 코드를 확인하세요. 코드는 생략할 수 있습니다.")
                    else:
                        known = next(
                            (
                                item for item in state.get("stocks", [])
                                if item.get("name", "").strip().casefold() == name.strip().casefold()
                            ),
                            {},
                        )
                        identity = known.get("code") or code or "pending-" + hashlib.sha256(name.strip().casefold().encode()).hexdigest()[:16]
                        try:
                            store.save_stock({"code": identity, "name": name.strip(), "kind": known.get("kind", "관심")})
                            st.rerun()
                        except Exception:
                            st.error("목록 저장에 실패했습니다. 저장 공간 설정을 확인하세요.")

    reports = _research_map(state)
    stocks = _stock_map(state)
    rows, details = _build_rows(stocks, reports)

    _render_market_cards()
    left, right = st.columns([2, 1])
    with left:
        with st.container(border=True):
            st.subheader("삼성전자 · 주요 주가 흐름")
            samsung_key = next(
                (
                    key for key, item in stocks.items()
                    if "삼성전자" in item.get("name", "")
                ),
                None,
            )
            samsung_report = reports.get(samsung_key, {}) if samsung_key else {}
            samsung_frame = _price_frame(samsung_report.get("prices"))
            if samsung_frame is not None:
                st.line_chart(samsung_frame.set_index("date")["close"])
                st.caption("수집된 가격 자료 기준 · 실시간 시세가 아닐 수 있습니다.")
            else:
                empty_state(
                    "삼성전자 가격 데이터 연결 대기",
                    "삼성전자 조사 결과에 가격 시계열이 포함되면 이 영역에 차트를 표시합니다. 임의의 가격은 표시하지 않습니다.",
                )
    with right:
        _render_portfolio_summary()

    _render_watchlist(stocks, details)
    _render_sector_and_flow(reports)
    _render_news(reports, stocks)

    with st.expander("조사 요청 · 최신 내용으로 업데이트"):
        st.write("① 종목을 추가하거나 포트폴리오에서 계좌를 불러옵니다. ② 아래 요청문을 복사해 지금 대화창에 보냅니다. ③ 조사 결과가 반영되면 이 화면을 새로고침합니다.")
        st.code(request_text(list(stocks.values())), language=None)
        st.caption("요청문에는 종목명만 포함됩니다. 이 채팅에 요청문을 보내야 조사가 시작됩니다.")
        if st.button("반영된 조사 결과 다시 읽기"):
            st.rerun()
        if not sample_mode:
            with st.expander("조사 파일 가져오기 · 고급"):
                upload = st.file_uploader("별도로 받은 조사 JSON 가져오기 · 선택", type=["json"])
                if upload and st.button("조사 파일 검증·저장"):
                    try:
                        reports_to_save = parse_bundle(upload.getvalue())

                        def save(data):
                            merged = {item["code"]: item for item in data.get("chat_research", [])}
                            for item in reports_to_save:
                                if item["code"] not in merged or item["as_of"] >= merged[item["code"]]["as_of"]:
                                    merged[item["code"]] = item
                            data["chat_research"] = list(merged.values())

                        store.change(save)
                        st.rerun()
                    except (ValueError, KeyError, TypeError):
                        st.error("조사 파일의 형식·출처·기간을 확인하세요. 기존 결과는 유지했습니다.")
                    except Exception:
                        st.error("저장에 실패했습니다. 기존 결과는 유지했습니다.")

    if not stocks:
        with st.container(border=True):
            st.subheader("첫 관심종목을 담아보세요")
            st.write("위의 종목 추가를 열고 기업 이름 하나만 입력하면 시작할 수 있습니다.")
        return

    _render_selected_detail(stocks, details, sample_mode)

    with st.expander("전체 지표 비교"):
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.info("비교할 조사 결과가 없습니다.")
