# -*- coding: utf-8 -*-
"""개인종목별 검색모델 v4.0 · 모바일 최적화 Streamlit UI
원본 분석 로직은 stock_analysis_v4_0.py의 run_pipeline을 그대로 호출합니다.
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path



import numpy as np
import pandas as pd
import streamlit as st

import stock_analysis_v4_0 as model





st.set_page_config(
    page_title="Stock Glass · v4.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Glassmorphism + responsive/mobile styles
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root { --ink:#F5F7FF; --muted:#C4CEE8; --line:rgba(255,255,255,.19); --glass:rgba(255,255,255,.095); --cyan:#76E4F7; --violet:#B7A3FF; }
html, body, [class*="css"] { font-family:'DM Sans','Noto Sans KR',sans-serif; }
.stApp { color:var(--ink); background:radial-gradient(ellipse at 12% 5%,rgba(74,92,190,.38),transparent 35%),radial-gradient(ellipse at 90% 22%,rgba(0,193,204,.20),transparent 32%),linear-gradient(135deg,#080D1D 0%,#101A36 48%,#0B1830 100%); background-attachment:fixed; }
[data-testid="stHeader"] { background:rgba(8,13,29,.28); }
[data-testid="stAppViewContainer"] { background:transparent; }
.block-container { max-width:1180px; padding-top:1.35rem; padding-bottom:5rem; }
.hero { position:relative; overflow:hidden; padding:1.6rem 1.65rem; border:1px solid rgba(255,255,255,.23); border-radius:26px; background:linear-gradient(125deg,rgba(255,255,255,.15),rgba(255,255,255,.045)); box-shadow:0 18px 55px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.17); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px); margin-bottom:1.15rem; }
.hero:after { content:''; position:absolute; width:230px;height:230px;right:-55px;top:-100px;border-radius:50%;background:radial-gradient(circle,rgba(118,228,247,.28),rgba(183,163,255,.06) 68%,transparent 70%);pointer-events:none; }
.eyebrow { color:var(--cyan); letter-spacing:.13em; text-transform:uppercase; font-size:.73rem; font-weight:800; }
.hero h1 { color:#FFFFFF; font-size:clamp(1.8rem,4vw,2.8rem); line-height:1.15; margin:.5rem 0 .6rem; letter-spacing:-.04em; }
.hero p { color:#D7E0F7; margin:0; font-size:.96rem; line-height:1.7; }
.glass-card { border:1px solid rgba(255,255,255,.18); border-radius:20px; padding:1.1rem 1.2rem; background:linear-gradient(145deg,rgba(255,255,255,.13),rgba(255,255,255,.055)); box-shadow:0 12px 32px rgba(0,0,0,.18),inset 0 1px 0 rgba(255,255,255,.11); backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px); height:100%; }
.kpi-label { color:#D3DDF6; font-size:.83rem; font-weight:700; margin-bottom:.4rem; }
.kpi-value { color:#FFFFFF; font-size:clamp(1.25rem,3.5vw,1.9rem); font-weight:800; letter-spacing:-.025em; overflow-wrap:anywhere; }
.kpi-sub { color:#AEBFE1; font-size:.78rem; margin-top:.38rem; line-height:1.5; }
.section-title { color:#F5F7FF; font-size:1.12rem; font-weight:800; margin:.85rem 0 .7rem; letter-spacing:-.015em; }
.small-note { color:#C8D4EF; font-size:.86rem; line-height:1.65; }
/* Glass containers */
div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stDataFrame"], div[data-testid="stTable"] { border:1px solid rgba(255,255,255,.17); border-radius:18px; background:rgba(255,255,255,.065); box-shadow:0 10px 28px rgba(0,0,0,.13); }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color:#F5F7FF !important; font-weight:750 !important; }
[data-testid="stExpander"] [data-testid="stMarkdownContainer"], [data-testid="stExpander"] p { color:#DCE5FA; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button { width:100%; border-radius:14px; min-height:3.15rem; font-weight:800; border:1px solid rgba(118,228,247,.65); background:linear-gradient(110deg,#5E70E8,#4A9FEA 60%,#37BFC8); color:#FFFFFF; box-shadow:0 8px 24px rgba(69,123,230,.27); transition:transform .18s ease,box-shadow .18s ease; }
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { border-color:#B7F4FF; background:linear-gradient(110deg,#7180F7,#58B0F2 60%,#45D2D5); color:#FFFFFF; transform:translateY(-1px); box-shadow:0 12px 30px rgba(69,150,230,.34); }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(255,255,255,.13),rgba(255,255,255,.055)); border:1px solid rgba(255,255,255,.17); padding:1rem; border-radius:17px; box-shadow:inset 0 1px 0 rgba(255,255,255,.08); }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color:#C9D6F1 !important; font-weight:700 !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color:#FFFFFF !important; }
[data-testid="stMetricDelta"] { color:#C9D6F1 !important; }
.stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label, .stCheckbox label, .stMultiSelect label, [data-testid="stWidgetLabel"] p { color:#E4EBFC !important; font-weight:700 !important; }
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"], [data-baseweb="input"] input { border-radius:12px; background:rgba(245,248,255,.97) !important; color:#17213B !important; border:1px solid rgba(196,211,245,.9) !important; }
.stTextInput input::placeholder { color:#687694 !important; opacity:1; }
[data-baseweb="select"] * { color:#17213B !important; }
[data-baseweb="popover"] *, [role="listbox"] * { color:#17213B !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:#B9C8E8 !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li { color:#E1E9FB; }
.stMarkdown strong, .stMarkdown b { color:#FFFFFF; }
hr { border-color:rgba(255,255,255,.18); }
[data-testid="stAlert"] { border-radius:15px; }
[data-testid="stDataFrame"] *, [data-testid="stTable"] * { color:#E8EEFC; }
[data-testid="stDataFrame"] { background:rgba(255,255,255,.96); }
[data-testid="stDataFrame"] * { color:#17213B !important; }
[data-testid="stJson"] { color:#E0E9FC; }
footer { visibility:hidden; }
@media (max-width:680px) {
 .block-container { padding:.7rem .65rem 4rem; }
 .hero { padding:1.15rem 1rem; border-radius:20px; }
 .glass-card { padding:.9rem; border-radius:16px; }
 h2 { font-size:1.15rem !important; } h3 { font-size:1rem !important; }
 [data-testid="stMetric"] { padding:.8rem; }
 .stDataFrame, [data-testid="stTable"] { overflow-x:auto; }
}
@media (prefers-reduced-motion:reduce) { * { transition:none !important; } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">STOCK GLASS · PERSONAL QUANT WORKBENCH</div>
  <h1>급등주 진단 <span style="background:linear-gradient(90deg,#76E4F7,#B7A3FF);-webkit-background-clip:text;background-clip:text;color:transparent">v4.0</span></h1>
  <p>모바일·PC 반응형 화면 · 워크포워드 검증 · 최종 홀드아웃 · 비용 반영</p>
</div>
""", unsafe_allow_html=True)

with st.expander("분석 설정", expanded=True):
    with st.form("analysis_form", clear_on_submit=False):
        c1, c2 = st.columns([1.25, 1])
        with c1:
            symbol = st.text_input("종목 코드", value=st.session_state.get("symbol", "MRNA"), help="미국 예: MRNA, NVDA / 한국 예: 005930")
            target_pct = st.number_input("목표 수익률 (%)", min_value=0.1, max_value=500.0, value=15.0, step=0.5)
            max_holding = st.number_input("최대 보유 거래일", min_value=1, max_value=252, value=20, step=1)
        with c2:
            fee_pct = st.number_input("매매 수수료 (% / 편도)", min_value=0.0, max_value=20.0, value=0.05, step=0.01, format="%.3f")
            slippage_pct = st.number_input("슬리피지 (% / 편도)", min_value=0.0, max_value=20.0, value=0.15, step=0.01, format="%.3f")
            st.caption("미국 종목의 원화 환율 손익은 v4.0에서 별도 계산하지 않습니다.")
        run = st.form_submit_button("분석 실행", type="primary", width='stretch')

if run:
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        st.error("종목 코드를 입력해 주세요.")
    else:
        st.session_state["symbol"] = normalized_symbol
        with st.spinner(f"{normalized_symbol} 데이터를 불러오고 v4.0 검증을 실행하고 있습니다. 표본 수에 따라 시간이 걸릴 수 있습니다."):
            try:
                # The model code is kept as the source of truth; only the UI changes here.
                result = model.run_pipeline(normalized_symbol, float(target_pct), int(max_holding), float(fee_pct), float(slippage_pct))
                st.session_state["analysis_result"] = result
                st.session_state["analysis_error"] = None
            except Exception as exc:
                st.session_state["analysis_result"] = None
                st.session_state["analysis_error"] = f"{type(exc).__name__}: {exc}"

if st.session_state.get("analysis_error"):
    st.error("분석 중 오류가 발생했습니다. 아래 오류를 확인해 주세요.")
    st.code(st.session_state["analysis_error"])

result = st.session_state.get("analysis_result")
if result:
    judgement = result.get("operating_judgement", {})
    status = judgement.get("판정", result.get("latest_signal", "관찰"))
    status_color = {"매수검토":"#76F0C5", "관찰":"#FFD479", "매수제외":"#FF929F"}.get(status, "#D9E4FF")
    st.markdown(f"<div class='glass-card' style='margin:.8rem 0 1rem;border-color:{status_color}55'><div class='eyebrow'>LATEST DIAGNOSIS · {result['data_end']}</div><div style='font-size:clamp(1.5rem,5vw,2.2rem);font-weight:800;color:{status_color};margin:.3rem 0'>{status}</div><div style='color:#DCE5FA'>{result['stock_name']} ({result['symbol']}) · {result['currency_label']}</div><div class='small-note' style='margin-top:.6rem'>모델 점수 {result['latest_probability']:.1f}% · 정밀도 기준 임계값 {result['optimal_threshold']:.1f}% · 원시 신호: {result.get('raw_model_signal','확인 불가')}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>핵심 지표</div>", unsafe_allow_html=True)
    close_text = model.format_price(result.get("latest_close"), result["symbol"])
    target_text = model.format_price(result.get("latest_close", np.nan) * (1 + result.get("target_pct", 15) / 100), result["symbol"])
    stop_text = model.format_price(result.get("suggested_stop_price"), result["symbol"])
    kpis = [
        ("현재가", close_text, f"데이터 종료일 {result['data_end']}"),
        ("참고 목표가", target_text, f"종가 기준 +{result['target_pct']:.1f}%"),
        ("참고 손절가", stop_text, f"종가 대비 {result.get('suggested_stop_pct', np.nan):.2f}%"),
        ("RSI(14)", f"{result.get('latest_rsi', np.nan):.1f}", "기술적 보조지표"),
    ]
    cols = st.columns(2)
    for i, (label, value, sub) in enumerate(kpis):
        with cols[i % 2]:
            st.markdown(f"<div class='glass-card' style='margin-bottom:.7rem'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-sub'>{sub}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>최종 홀드아웃 검증</div>", unsafe_allow_html=True)
    hm = result.get("holdout_metrics", {})
    tm = result.get("holdout_trade_metrics", {})
    pcols = st.columns(2)
    metrics = [("정밀도", hm.get("정밀도")), ("재현율", hm.get("재현율")), ("F1", hm.get("F1")), ("기저율", hm.get("기저율", hm.get("기저확률")))]
    for i, (label, value) in enumerate(metrics):
        with pcols[i % 2]:
            st.metric(label, f"{float(value):.2f}%" if value is not None and np.isfinite(value) else "계산 불가")
    trade_cols = st.columns(2)
    for i, (label, key) in enumerate([("CAGR", "CAGR_%"), ("MDD", "MDD_%")]):
        val = tm.get(key, tm.get("CAGR" if key == "CAGR_%" else "MDD", np.nan))
        with trade_cols[i]:
            st.metric(label, f"{float(val):.2f}%" if val is not None and np.isfinite(val) else "계산 불가")
    st.caption("정밀도·재현율·F1은 분류 지표이며, CAGR·MDD는 홀드아웃 구간의 실제 거래 시뮬레이션 지표입니다. 과거 결과는 미래 수익을 보장하지 않습니다.")

    with st.expander("판정 근거 및 1차·2차 기준표", expanded=True):
        for reason in judgement.get("판정근거", []):
            st.write(f"• {reason}")
        criteria = judgement.get("분류기준표", [])
        if criteria:
            st.dataframe(pd.DataFrame(criteria), width='stretch', hide_index=True)
        for warning in judgement.get("경고및해석", []):
            st.warning(warning)

    with st.expander("정밀도·재현율·F1 임계값 비교"):
        comparison = result.get("threshold_comparison", [])
        if comparison:
            rows = []
            for item in comparison:
                rows.append({
                    "기준": item.get("기준"), "임계값(%)": round(float(item.get("임계값", np.nan)), 2),
                    "WF 정밀도(%)": round(float(item.get("과거기준", {}).get("정밀도", np.nan)), 2),
                    "WF 재현율(%)": round(float(item.get("과거기준", {}).get("재현율", np.nan)), 2),
                    "WF F1(%)": round(float(item.get("과거기준", {}).get("F1", np.nan)), 2),
                    "홀드아웃 정밀도(%)": round(float(item.get("홀드아웃", {}).get("정밀도", np.nan)), 2),
                    "홀드아웃 재현율(%)": round(float(item.get("홀드아웃", {}).get("재현율", np.nan)), 2),
                    "홀드아웃 F1(%)": round(float(item.get("홀드아웃", {}).get("F1", np.nan)), 2),
                    "신호 수 WF/홀드아웃": f"{item.get('과거신호수')} / {item.get('홀드아웃신호수')}"
                })
            st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)

    with st.expander("데이터 범위·표본 충분성"):
        diag = result.get("sample_diagnostics", {})
        st.write(f"가격 데이터: {result.get('data_start')} ~ {result.get('data_end')}")
        st.write(f"라벨 데이터: {result.get('label_data_start')} ~ {result.get('label_data_end')}")
        st.write(f"학습 종료일: {result.get('train_end')} · 최신 재학습 종료일: {result.get('deploy_train_end')}")
        st.write(f"홀드아웃 기간: {result.get('holdout_signal_start')} ~ {result.get('holdout_signal_end')}")
        st.json(diag, expanded=False)

    with st.expander("워크포워드 구간별 결과"):
        folds = result.get("walk_forward_folds", [])
        if folds:
            st.dataframe(pd.DataFrame(folds), width='stretch', hide_index=True)
        else:
            st.info("표시할 워크포워드 결과가 없습니다.")

    with st.expander("차트: 상장 이후 장기 흐름"):
        p = result.get("chart_long_path")
        if p and os.path.exists(p): st.image(p, width='stretch')
        else: st.info("장기 차트를 생성하지 못했습니다.")
    with st.expander("차트: 최근 가격·볼린저 밴드·RSI·거래량·ATR"):
        p = result.get("chart_recent_path")
        if p and os.path.exists(p): st.image(p, width='stretch')
        else: st.info("최근 차트를 생성하지 못했습니다.")

    # Export the original v4.0 Word report for mobile/desktop download.
    st.markdown("<div class='section-title'>보고서 내보내기</div>", unsafe_allow_html=True)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / f"{result['symbol']}_v4_0_diagnostic.docx"
            model.generate_word_report(result, str(report_path))
            report_bytes = report_path.read_bytes()
        st.download_button("📄 진단 보고서 다운로드 (.docx)", data=report_bytes,
                           file_name=f"{result['symbol']}_v4_0_diagnostic.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           width='stretch')
    except Exception as exc:
        st.warning(f"Word 보고서 생성에 실패했습니다: {exc}")

    st.info("실전 검증 전 안내: 모델의 점수는 성공확률로 보정된 값이 아닙니다. 매수·매도는 모델 판정만으로 결정하지 말고, 비용·유동성·공시·손실 감당 범위를 함께 확인하세요.")
else:
    st.markdown("""
    <div class="glass-card">
      <div class="section-title">빠른 시작</div>
      <p>1. 종목 코드를 입력합니다.</p>
      <p>2. 목표 수익률·최대 보유일·거래 비용을 설정합니다.</p>
      <p>3. <b>분석 실행</b>을 누르면 현재 판정, 홀드아웃 검증, 워크포워드 결과와 차트를 확인할 수 있습니다.</p>
      <p class="small-note">처음에는 MRNA 등 한 종목으로 화면과 데이터 연결을 점검한 뒤 다른 종목을 확인하세요. 데이터 공급자가 최신 가격을 아직 제공하지 않을 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
