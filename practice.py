import streamlit as st
import random

# --- ページ設定（一番最初に） ---
st.set_page_config(page_title="平方完成しろ", layout="wide")

# ===============================================
# ★【微調整】数式を大きくしつつ、見切れを防ぐCSS
# ===============================================
st.markdown(
    """
    <style>
    /* 数式全体のベースサイズを拡大（比率を壊さないように * は外す） */
    .katex {
        font-size: 2.2em !important;
    }
    /* 指数などが上下にはみ出しても見切れないように余白を作る */
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
# ===============================================

# --- 状態の初期化 ---
if 'a' not in st.session_state:
    st.session_state.a = random.choice([i for i in range(-9, 10) if i != 0])
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- コールバック関数 ---
def handle_button_click():
    if st.session_state.step == 0:
        st.session_state.step = 1
    elif st.session_state.step == 1:
        st.session_state.step = 2
    elif st.session_state.step == 2:
        st.session_state.a = random.choice([i for i in range(-9, 10) if i != 0])
        st.session_state.step = 0

# --- 数式の整形関数 ---
def get_question_latex(a):
    if a == 1:
        return "y = x^2 + x"
    elif a == -1:
        return "y = x^2 - x"
    elif a > 0:
        return f"y = x^2 + {a}x"
    else:
        return f"y = x^2 - {-a}x"

def get_answer_latex(a, step):
    # --- 前半 ---
    if a % 2 == 0:
        p = abs(a) // 2
        sign = "+" if a > 0 else "-"
        term1 = f"(x {sign} {p})^2"
    else:
        p = abs(a)
        sign = "+" if a > 0 else "-"
        term1 = f"\\left(x {sign} \\frac{{{p}}}{{2}}\\right)^2"

    # --- 後半1 (途中式) ---
    if a % 2 != 0:
        if a > 0:
            term2_step = f"\\left(\\frac{{{a}}}{{2}}\\right)^2"
        else:
            term2_step = f"\\left(-\\frac{{{-a}}}{{2}}\\right)^2"
    elif a > 0:
        term2_step = f"{a // 2}^2"
    else:
        term2_step = f"({a // 2})^2"

    # --- 後半2 (最終結果) ---
    if a % 2 == 0:
        term2_final = f"{(a // 2) ** 2}"
    else:
        term2_final = f"\\frac{{{a ** 2}}}{{4}}"

    if step == 1:
        return f"y = {term1} - {term2_step}"
    else:
        return (
            "\\begin{aligned}\n"
            f"y &= {term1} - {term2_step} \\\\\n"
            f"  &= {term1} - {term2_final}\n"
            "\\end{aligned}"
        )

# --- UIの描画 ---
st.title("平方完成の練習アプリ")

# 1. 問題の表示
st.markdown("### 問題")
st.latex(get_question_latex(st.session_state.a))

st.markdown("---")

# 2. ボタンの表示
if st.session_state.step == 0:
    button_label = "答"
elif st.session_state.step == 1:
    button_label = "結果"
else:
    button_label = "次"

st.button(button_label, on_click=handle_button_click)

# 3. 解答の表示
if st.session_state.step >= 1:
    st.markdown("### 解答")
    st.latex(get_answer_latex(st.session_state.a, st.session_state.step))
