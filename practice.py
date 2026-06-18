import streamlit as st
import random
import math

# --- ページ設定 ---
st.set_page_config(page_title="平方完成の練習アプリ", layout="wide")

# ===============================================
# ★数式を見やすくするためのCSS
# ===============================================
st.markdown(
    """
    <style>
    .katex { font-size: 2.2em !important; }
    .katex-display {
        padding-top: 1.0em !important;
        padding-bottom: 1.0em !important;
        line-height: 1.5 !important;
        overflow: visible !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 係数の生成ロジック ---
def generate_coefficients(mode):
    if mode == "Easy":
        A, C = 1, 0
        B = random.choice([i for i in range(-9, 10) if i != 0])
    elif mode == "Normal":
        A = 1
        B = random.choice([i for i in range(-9, 10) if i != 0])
        C = random.choice([i for i in range(-9, 10) if i != 0])
    else: 
        A = random.choice([i for i in range(-9, 10) if i not in [0, 1]])
        k = random.choice([i for i in range(-5, 6) if i != 0])
        B = A * k
        C = random.choice([i for i in range(-9, 10) if i != 0])
    return A, B, C

def get_max_steps(mode):
    """モードに応じて解答のステップ数を変える"""
    return 4 if mode == "Hard" else 2

# --- 状態の初期化 ---
if 'mode' not in st.session_state:
    st.session_state.mode = "Easy"
if 'A' not in st.session_state:
    st.session_state.A, st.session_state.B, st.session_state.C = generate_coefficients("Easy")
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- コールバック関数 ---
def on_mode_change():
    st.session_state.step = 0
    new_mode = st.session_state.mode_selector
    st.session_state.mode = new_mode
    st.session_state.A, st.session_state.B, st.session_state.C = generate_coefficients(new_mode)

def handle_button_click():
    max_steps = get_max_steps(st.session_state.mode)
    if st.session_state.step < max_steps:
        st.session_state.step += 1
    else:
        st.session_state.A, st.session_state.B, st.session_state.C = generate_coefficients(st.session_state.mode)
        st.session_state.step = 0

# --- 数式の整形関数 ---
def get_question_latex(A, B, C):
    if A == 1: term_a = "x^2"
    elif A == -1: term_a = "-x^2"
    else: term_a = f"{A}x^2"

    if B == 1: term_b = "+ x"
    elif B == -1: term_b = "- x"
    elif B > 0: term_b = f"+ {B}x"
    elif B < 0: term_b = f"- {-B}x"
    else: term_b = ""

    if C > 0: term_c = f"+ {C}"
    elif C < 0: term_c = f"- {-C}"
    else: term_c = ""

    return f"y = {term_a} {term_b} {term_c}".strip()

def get_answer_latex(A, B, C, step, mode):
    p = B // A

    # --- 共通パーツの作成 ---
    if A == 1: A_str = ""
    elif A == -1: A_str = "-"
    else: A_str = f"{A}"

    if p % 2 == 0:
        k = abs(p) // 2
        sign = "+" if p > 0 else "-"
        term_sq = f"(x {sign} {k})^2"
    else:
        sign = "+" if p > 0 else "-"
        term_sq = f"\\left(x {sign} \\frac{{{abs(p)}}}{{2}}\\right)^2"

    if p % 2 != 0:
        if p > 0: term_sub_sq = f"\\left(\\frac{{{p}}}{{2}}\\right)^2"
        else: term_sub_sq = f"\\left(-\\frac{{{-p}}}{{2}}\\right)^2"
    elif p > 0:
        term_sub_sq = f"{p // 2}^2"
    else:
        term_sub_sq = f"({p // 2})^2"

    if C > 0: term_C = f"+ {C}"
    elif C < 0: term_C = f"- {-C}"
    else: term_C = ""

    # 最終結果の定数項: (4C - A*p^2) / 4
    num = 4 * C - A * (p ** 2)
    den = 4
    if num == 0:
        term_final_C = ""
    else:
        g = math.gcd(abs(num), den)
        num_sim = num // g
        den_sim = den // g
        if den_sim == 1:
            if num_sim > 0: term_final_C = f"+ {num_sim}"
            else: term_final_C = f"- {-num_sim}"
        else:
            if num_sim > 0: term_final_C = f"+ \\frac{{{num_sim}}}{{{den_sim}}}"
            else: term_final_C = f"- \\frac{{{-num_sim}}}{{{den_sim}}}"

    # =============== 出力ロジック (Easy/Normal) ===============
    if mode in ["Easy", "Normal"]:
        line1 = f"{term_sq} - {term_sub_sq} {term_C}".strip()
        line2 = f"{term_sq} {term_final_C}".strip()

        if step == 1: return f"y = {line1}"
        else:
            return "\\begin{aligned}\n" f"y &= {line1} \\\\\n" f"  &= {line2}\n" "\\end{aligned}"

    # =============== 出力ロジック (Hard) ===============
    else:
        # 1行目: a(x^2 + px) + c
        if p == 1: term_px = "+ x"
        elif p == -1: term_px = "- x"
        elif p > 0: term_px = f"+ {p}x"
        else: term_px = f"- {-p}x"
        line1 = f"{A_str}(x^2 {term_px}) {term_C}".strip()

        # 2行目: a{ (x+p/2)^2 - (p/2)^2 } + c
        line2 = f"{A_str}\\left\\{{ {term_sq} - {term_sub_sq} \\right\\}} {term_C}".strip()

        # 3行目: a(x+p/2)^2 - a*(p/2)^2 + c
        # (分配法則で計算した - a*(p/2)^2 の部分を約分して出力)
        num_val = A * (p ** 2)
        den_val = 4
        g2 = math.gcd(abs(num_val), den_val)
        ns = num_val // g2
        ds = den_val // g2
        
        if ns == 0: term_Ap2 = ""
        elif ds == 1:
            if ns > 0: term_Ap2 = f"- {ns}"
            else: term_Ap2 = f"+ {-ns}"
        else:
            if ns > 0: term_Ap2 = f"- \\frac{{{ns}}}{{{ds}}}"
            else: term_Ap2 = f"+ \\frac{{{-ns}}}{{{ds}}}"

        line3 = f"{A_str}{term_sq} {term_Ap2} {term_C}".strip()

        # 4行目: a(x+p/2)^2 + 最終定数
        line4 = f"{A_str}{term_sq} {term_final_C}".strip()

        if step == 1:
            return f"y = {line1}"
        elif step == 2:
            return "\\begin{aligned}\n" f"y &= {line1} \\\\\n" f"  &= {line2}\n" "\\end{aligned}"
        elif step == 3:
            return "\\begin{aligned}\n" f"y &= {line1} \\\\\n" f"  &= {line2} \\\\\n" f"  &= {line3}\n" "\\end{aligned}"
        else:
            return "\\begin{aligned}\n" f"y &= {line1} \\\\\n" f"  &= {line2} \\\\\n" f"  &= {line3} \\\\\n" f"  &= {line4}\n" "\\end{aligned}"

st.radio(
    "モード選択", 
    ["Easy", "Normal", "Hard"], 
    horizontal=True, 
    key="mode_selector", 
    on_change=on_mode_change
)

# 1. 問題の表示
st.markdown("### 問題")
st.latex(get_question_latex(st.session_state.A, st.session_state.B, st.session_state.C))
st.markdown("---")

# 2. ボタンの表示
max_steps = get_max_steps(st.session_state.mode)
if st.session_state.step == 0: button_label = "答"
elif st.session_state.step == max_steps: button_label = "次"
elif st.session_state.step == max_steps - 1: button_label = "結果"
else: button_label = "続き"

st.button(button_label, on_click=handle_button_click)

# 3. 解答の表示
if st.session_state.step >= 1:
    st.markdown("### 解答")
    st.latex(get_answer_latex(st.session_state.A, st.session_state.B, st.session_state.C, st.session_state.step, st.session_state.mode))
