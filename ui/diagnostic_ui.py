"""
診断画面UIコンポーネント

30問の性格診断をページネーションで表示します。
"""

from datetime import datetime

import streamlit as st

from data.questions import DIAGNOSTIC_QUESTIONS, get_total_questions
from logic.diagnostic import calculate_personality_type, get_dimension_explanation
from models.data_models import UserResponse
from database.db_manager import save_personality_result


QUESTIONS_PER_PAGE = 5


def init_diagnostic_state() -> None:
    """診断用セッション状態を初期化"""
    if "diagnostic_started" not in st.session_state:
        st.session_state.diagnostic_started = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "diagnostic_complete" not in st.session_state:
        st.session_state.diagnostic_complete = False
    if "personality_result" not in st.session_state:
        st.session_state.personality_result = None


def reset_diagnostic() -> None:
    """診断をリセット"""
    st.session_state.diagnostic_started = False
    st.session_state.current_page = 0
    st.session_state.responses = {}
    st.session_state.diagnostic_complete = False
    st.session_state.personality_result = None


def render_diagnostic_page() -> None:
    """診断画面をレンダリング"""
    init_diagnostic_state()

    st.title("🔮 性格診断")

    if st.session_state.diagnostic_complete:
        render_result_page()
        return

    if not st.session_state.diagnostic_started:
        render_start_page()
        return

    render_questions_page()


def render_start_page() -> None:
    """診断開始ページ"""
    st.markdown("""
    ## 自己分析のための性格診断

    この診断は、あなたの性格特性を4つの指標で分析します：

    - **E/I** - 外向型 vs 内向型
    - **S/N** - 感覚型 vs 直観型
    - **T/F** - 思考型 vs 感情型
    - **J/P** - 判断型 vs 知覚型

    ### 診断について

    - **問題数**: 30問
    - **所要時間**: 約5〜10分
    - **回答方式**: 5段階評価

    各質問に対して、あなたに最も当てはまると思う選択肢を選んでください。
    正解・不正解はありません。直感的に答えることをお勧めします。
    """)

    if st.button("🚀 診断を開始する", type="primary", use_container_width=True):
        st.session_state.diagnostic_started = True
        st.rerun()


def render_questions_page() -> None:
    """質問ページ"""
    total_questions = get_total_questions()
    total_pages = (total_questions + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE
    current_page = st.session_state.current_page

    # プログレスバー
    answered_count = len(st.session_state.responses)
    progress = answered_count / total_questions
    st.progress(progress, text=f"進捗: {answered_count}/{total_questions}問完了")

    # 現在のページの質問を取得
    start_idx = current_page * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, total_questions)
    page_questions = DIAGNOSTIC_QUESTIONS[start_idx:end_idx]

    # ページ情報
    st.markdown(f"### ページ {current_page + 1} / {total_pages}")

    # 質問を表示
    for question in page_questions:
        st.markdown(f"**Q{question.id}.** {question.text}")

        options = [
            "1: 全く当てはまらない",
            "2: あまり当てはまらない",
            "3: どちらとも言えない",
            "4: やや当てはまる",
            "5: 非常に当てはまる",
        ]

        # 既存の回答があれば取得
        current_value = st.session_state.responses.get(question.id, None)
        default_index = current_value - 1 if current_value else None

        response = st.radio(
            label=f"質問{question.id}への回答",
            options=options,
            index=default_index,
            key=f"q_{question.id}",
            horizontal=True,
            label_visibility="collapsed",
        )

        if response:
            score = int(response[0])  # "1: ..." から 1 を抽出
            st.session_state.responses[question.id] = score

        st.markdown("---")

    # ナビゲーションボタン
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_page > 0:
            if st.button("⬅️ 前のページ", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()

    with col2:
        st.markdown(f"<div style='text-align: center;'>ページ {current_page + 1}/{total_pages}</div>", unsafe_allow_html=True)

    with col3:
        if current_page < total_pages - 1:
            if st.button("次のページ ➡️", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
        else:
            # 最終ページ
            all_answered = len(st.session_state.responses) == total_questions
            if st.button(
                "📊 結果を見る" if all_answered else f"未回答: {total_questions - len(st.session_state.responses)}問",
                use_container_width=True,
                disabled=not all_answered,
                type="primary" if all_answered else "secondary",
            ):
                submit_diagnostic()


def submit_diagnostic() -> None:
    """診断を提出して結果を計算"""
    user_id = st.session_state.get("user_id", "default_user")

    # UserResponseオブジェクトのリストを作成
    responses: list[UserResponse] = []
    for question_id, score in st.session_state.responses.items():
        responses.append(
            UserResponse(
                user_id=user_id,
                question_id=question_id,
                score=score,
            )
        )

    # 性格タイプを計算
    result = calculate_personality_type(responses, user_id)

    # データベースに保存
    save_personality_result(result)

    # セッション状態を更新
    st.session_state.personality_result = result
    st.session_state.diagnostic_complete = True
    st.rerun()


def render_result_page() -> None:
    """結果ページ"""
    result = st.session_state.personality_result

    if result is None:
        st.error("診断結果が見つかりません")
        return

    # タイプ表示
    st.markdown(f"""
    # 🎉 あなたのタイプは **{result.personality_type}** です！

    ## {result.type_description}
    """)

    # 各指標の詳細
    st.markdown("### 📊 各指標の詳細")

    for score in result.dimension_scores:
        col1, col2 = st.columns([3, 1])

        with col1:
            # プログレスバーで強度を表示
            if score.dominant_type == score.first_type:
                # 第1タイプが優勢
                display_value = 50 + (score.strength_percent / 2)
            else:
                # 第2タイプが優勢
                display_value = 50 - (score.strength_percent / 2)

            st.markdown(f"**{score.first_type} ← → {score.second_type}**")
            st.progress(display_value / 100)

        with col2:
            st.markdown(f"**{score.dominant_type}** ({score.strength_percent:.1f}%)")

        # 説明
        explanation = get_dimension_explanation(score.dimension, score.dominant_type)
        st.info(explanation)

    # アクションボタン
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 もう一度診断する", use_container_width=True):
            reset_diagnostic()
            st.rerun()

    with col2:
        if st.button("📝 ジャーナルを書く", use_container_width=True):
            st.session_state.current_view = "journal"
            st.rerun()
