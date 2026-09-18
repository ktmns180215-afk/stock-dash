from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("홈", "⌂"),
    ("시장 현황", "▥"),
    ("종목 분석", "◫"),
    ("공시 분석", "▤"),
    ("테마 & 섹터", "◇"),
    ("포트폴리오", "▣"),
    ("관심 종목", "☆"),
    ("AI 인사이트", "✦"),
    ("데이터 연결 관리", "⚙"),
]


def apply_theme():
    st.markdown(
        """
<style>
:root {
  --bg: #f6f8fc;
  --surface: #ffffff;
  --surface-soft: #f8fbff;
  --line: #e5eaf2;
  --text: #14213d;
  --muted: #718096;
  --blue: #2563eb;
  --blue-soft: #eaf2ff;
  --green: #059669;
  --red: #ef3340;
}

html, body, [class*="css"] {
  font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}

.stApp {
  background: var(--bg);
  color: var(--text);
}

.block-container {
  max-width: 1480px;
  padding-top: 1.25rem;
  padding-bottom: 3.5rem;
}

header[data-testid="stHeader"] {
  background: rgba(246, 248, 252, .92);
  backdrop-filter: blur(12px);
}

section[data-testid="stSidebar"] {
  background: #ffffff;
  border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] > div {
  padding-top: .85rem;
}

[data-testid="stSidebar"] .stRadio > label {
  display: none;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  gap: .3rem;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  border-radius: 10px;
  padding: .65rem .7rem;
  color: #52627a;
  transition: background .15s ease, color .15s ease;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background: #f3f6fb;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background: #eaf2ff;
  color: #1d4ed8;
  font-weight: 750;
  box-shadow: inset 3px 0 #2563eb;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p {
  color: #1d4ed8;
}

h1, h2, h3, h4 {
  color: var(--text);
  letter-spacing: -.035em;
}

h1 { font-weight: 800; }
h2, h3 { font-weight: 750; }
p, li { line-height: 1.6; }

[data-testid="stCaptionContainer"] {
  color: var(--muted);
}

[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 7px 22px rgba(20, 33, 61, .035);
}

[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--text); font-weight: 800; }

[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--line) !important;
  border-radius: 16px !important;
  background: var(--surface);
  box-shadow: 0 7px 22px rgba(20, 33, 61, .03);
}

.stButton > button, .stFormSubmitButton > button {
  border-radius: 10px;
  min-height: 2.65rem;
  font-weight: 700;
}

.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
  background: var(--blue);
  border-color: var(--blue);
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
  border-radius: 11px !important;
  border-color: #dce4f0;
}

.stTextInput input {
  min-height: 44px;
  background: #ffffff;
}

.stTabs [data-baseweb="tab-list"] { gap: 6px; overflow-x: auto; }
.stTabs [data-baseweb="tab"] {
  border-radius: 10px;
  padding: 9px 13px;
  white-space: nowrap;
}

.stDataFrame {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}

.planx-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 4px 0 28px;
}

.planx-brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #2563eb, #60a5fa);
  color: #ffffff;
  font-size: 20px;
  font-weight: 800;
  box-shadow: 0 5px 12px rgba(37, 99, 235, .2);
}

.planx-brand-title {
  font-size: 21px;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -.04em;
  color: #14213d;
}

.planx-brand-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 3px;
}

.planx-hero {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 58%, #eff6ff 100%);
  border: 1px solid #e2eaf5;
  border-radius: 20px;
  padding: 26px 28px;
  margin-bottom: 18px;
  box-shadow: 0 12px 32px rgba(20, 33, 61, .04);
}

.planx-eyebrow {
  color: #2563eb;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.planx-hero h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
}

.planx-hero p {
  margin: 9px 0 0;
  color: #718096;
  font-size: 14px;
  max-width: 760px;
}

.planx-card {
  background: #ffffff;
  border: 1px solid #e5eaf2;
  border-radius: 14px;
  padding: 18px 20px;
  min-height: 122px;
  box-shadow: 0 7px 22px rgba(20, 33, 61, .03);
  border-top: 3px solid #dbeafe;
}

.planx-card-title {
  font-size: 12px;
  color: #718096;
  margin-bottom: 8px;
  font-weight: 750;
}

.planx-card-value {
  font-size: 25px;
  color: #14213d;
  font-weight: 800;
  letter-spacing: -.035em;
  font-variant-numeric: tabular-nums;
}

.planx-card-note {
  margin-top: 7px;
  font-size: 11px;
  color: #94a3b8;
}

.planx-empty {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  padding: 22px;
  color: #718096;
}

.planx-source {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #64748b;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 10px;
}

.planx-status-ok { color: #047857; background: #ecfdf5; border-color: #a7f3d0; }
.planx-status-wait { color: #92400e; background: #fffbeb; border-color: #fde68a; }
.planx-status-bad { color: #b91c1c; background: #fef2f2; border-color: #fecaca; }

hr { border-color: #e5eaf2 !important; }

@media (max-width: 900px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .planx-hero { padding: 22px 20px; }
  .planx-hero h1 { font-size: 28px; }
}

@media (max-width: 640px) {
  .block-container { padding-top: 1.1rem; }
  .planx-hero h1 { font-size: 26px; }
  .planx-card { min-height: 100px; padding: 14px; }
  .planx-card-value { font-size: 22px; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def brand():
    st.markdown(
        """
<div class="planx-brand">
  <div class="planx-brand-mark">↗</div>
  <div>
    <div class="planx-brand-title">StockDash</div>
    <div class="planx-brand-sub">Data to Insight.</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "PLANX INVESTMENT OS"):
    st.markdown(
        f"""
<div class="planx-hero">
  <div class="planx-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def card(title: str, value: str, note: str = "", status: str = ""):
    status_html = f'<div class="planx-card-note">{html.escape(status)}</div>' if status else ""
    st.markdown(
        f"""
<div class="planx-card">
  <div class="planx-card-title">{html.escape(title)}</div>
  <div class="planx-card-value">{html.escape(value)}</div>
  <div class="planx-card-note">{html.escape(note)}</div>
  {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str):
    st.markdown(
        f"""
<div class="planx-empty">
  <strong style="color:#334155">{html.escape(title)}</strong><br>
  <span>{html.escape(message)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def source_badge(label: str, state: str = "wait"):
    cls = {"ok": "planx-status-ok", "bad": "planx-status-bad"}.get(state, "planx-status-wait")
    st.markdown(
        f'<span class="planx-source {cls}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )
