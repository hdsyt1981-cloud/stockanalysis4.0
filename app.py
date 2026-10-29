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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root { --ink:#eef4ff; --muted:#aab8d3; --line:rgba(255,255,255,.15); --glass:rgba(255,255,255,.085); }
html, body, [class*="css"] { font-family:'DM Sans','Noto Sans KR',sans-serif; }
.stApp { color:var(--ink); background: radial-gradient(ellipse at 8% 0%, #263f78 0%, transparent 38%), radial-gradient(ellipse at 100% 15%, #4c2c72 0%, transparent 33%), linear-gradient(145deg,#07111f 0%,#101a30 48%,#101323 100%); background-attachment:fixed; }
[data-testid="stHeader"] { background:rgba(5,12,26,.35); }
[data-testid="stAppViewContainer"] > .main { background:transparent; }
.block-container { max-width:1180px; padding-top:1.25rem; padding-bottom:5rem; }
.hero { padding:1.25rem 1.35rem; border:1px solid var(--line); border-radius:24px; background:linear-gradient(130deg,rgba(255,255,255,.14),rgba(255,255,255,.045)); box-shadow:0 18px 60px rgba(0,0,0,.22); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px); margin-bottom:1rem; }
.eyebrow { color:#a9c8ff; letter-spacing:.12em; text-transform:uppercase; font-size:.72rem; font-weight:800; }
.hero h1 { color:#fff; font-size:clamp(1.65rem,4vw,2.6rem); line-height:1.12; margin:.35rem 0 .5rem 0; }
.hero p { color:#c1cde2; margin:0; font-size:.96rem; }
.glass-card { border:1px solid var(--line); border-radius:20px; padding:1rem 1.1rem; background:var(--glass); box-shadow:0 10px 30px rgba(0,0,0,.13); backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px); height:100%; }
.kpi-label { color:#aab8d3; font-size:.78rem; font-weight:600; margin-bottom:.35rem; }
.kpi-value { color:#fff; font-size:clamp(1.25rem,3.5vw,1.9rem); font-weight:800; letter-spacing:-.03em; overflow-wrap:anywhere; }
.kpi-sub { color:#aab8d3; font-size:.75rem; margin-top:.3rem; }
.section-title { color:#f5f8ff; font-size:1.12rem; font-weight:800; margin:.6rem 0 .65rem; }
.small-note { color:#aab8d3; font-size:.82rem; line-height:1.55; }
div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stDataFrame"], div[data-testid="stTable"] { border:1px solid var(--line); border-radius:18px; background:rgba(255,255,255,.045); }
.stButton > button, .stDownloadButton > button { width:100%; border-radius:14px; min-height:3rem; font-weight:800; border:1px solid rgba(255,255,255,.22); background:linear-gradient(110deg,#7c9cff,#b28aff); color:#081225; box-shadow:0 8px 24px rgba(100,120,255,.18); }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:#fff; color:#050d1b; }
[data-testid="stMetric"] { background:rgba(255,255,255,.07); border:1px solid var(--line); padding:1rem; border-radius:18px; }
[data-testid="stMetricLabel"] { color:#b6c5df !important; }
[data-testid="stMetricValue"] { color:#fff !important; }
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { border-radius:12px; }
hr { border-color:rgba(255,255,255,.12); }
[data-testid="stAlert"] { border-radius:16px; }
footer { visibility:hidden; }
@media (max-width: 680px) {
 .block-container { padding: .7rem .7rem 4rem .7rem; }
 .hero { padding:1rem; border-radius:18px; }
 .glass-card { padding:.85rem; border-radius:16px; }
 h2 { font-size:1.15rem !important; }
 h3 { font-size:1rem !important; }
 [data-testid="stMetric"] { padding:.75rem; }
 .stDataFrame, [data-testid="stTable"] { overflow-x:auto; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">STOCK GLASS · PERSONAL QUANT WORKBENCH</div>
  <h1>급등주 진단 <span style="color:#a9bdff">v4.0</span></h1>
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
        run = st.form_submit_button("분석 실행", type="primary", use_container_width=True)

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
    status_color = {"매수검토":"#78f0c1", "관찰":"#ffd580", "매수제외":"#ff9baf"}.get(status, "#c1cde2")
    st.markdown(f"<div class='glass-card' style='margin:.8rem 0 1rem;border-color:{status_color}55'><div class='eyebrow'>LATEST DIAGNOSIS · {result['data_end']}</div><div style='font-size:clamp(1.5rem,5vw,2.2rem);font-weight:800;color:{status_color};margin:.3rem 0'>{status}</div><div style='color:#c1cde2'>{result['stock_name']} ({result['symbol']}) · {result['currency_label']}</div><div class='small-note' style='margin-top:.6rem'>모델 점수 {result['latest_probability']:.1f}% · 정밀도 기준 임계값 {result['optimal_threshold']:.1f}% · 원시 신호: {result.get('raw_model_signal','확인 불가')}</div></div>", unsafe_allow_html=True)

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
            st.dataframe(pd.DataFrame(criteria), use_container_width=True, hide_index=True)
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
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

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
            st.dataframe(pd.DataFrame(folds), use_container_width=True, hide_index=True)
        else:
            st.info("표시할 워크포워드 결과가 없습니다.")

    with st.expander("차트: 상장 이후 장기 흐름"):
        p = result.get("chart_long_path")
        if p and os.path.exists(p): st.image(p, use_container_width=True)
        else: st.info("장기 차트를 생성하지 못했습니다.")
    with st.expander("차트: 최근 가격·볼린저 밴드·RSI·거래량·ATR"):
        p = result.get("chart_recent_path")
        if p and os.path.exists(p): st.image(p, use_container_width=True)
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
                           use_container_width=True)
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
