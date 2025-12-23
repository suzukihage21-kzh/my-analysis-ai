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
from ui.styles import (
    get_hero_card,
    get_feature_card,
    get_question_card,
    get_result_type_card,
    get_section_header,
)


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

    if st.session_state.diagnostic_complete:
        render_result_page()
        return

    if not st.session_state.diagnostic_started:
        render_start_page()
        return

    render_questions_page()


def render_start_page() -> None:
    """診断開始ページ"""
    # ヒーローセクション
    st.markdown(get_hero_card(
        title="性格診断",
        subtitle="30問の質問であなたの性格特性を4つの指標で分析します",
        icon="🔮"
    ), unsafe_allow_html=True)
    
    # 4つの指標カード
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(get_feature_card(
            icon="🔄",
            title="E/I",
            description="外向型 vs 内向型"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(get_feature_card(
            icon="💭",
            title="S/N",
            description="感覚型 vs 直観型"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(get_feature_card(
            icon="🧠",
            title="T/F",
            description="思考型 vs 感情型"
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(get_feature_card(
            icon="📋",
            title="J/P",
            description="判断型 vs 知覚型"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 診断情報カード
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    ">
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">📝</div>
                <div style="color: #a0aec0; font-size: 0.8rem;">問題数</div>
                <div style="color: #e2e8f0; font-weight: 600;">30問</div>
            </div>
            <div>
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">⏱️</div>
                <div style="color: #a0aec0; font-size: 0.8rem;">所要時間</div>
                <div style="color: #e2e8f0; font-weight: 600;">約5〜10分</div>
            </div>
            <div>
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">⭐</div>
                <div style="color: #a0aec0; font-size: 0.8rem;">回答方式</div>
                <div style="color: #e2e8f0; font-weight: 600;">5段階評価</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ヒント
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.05) 100%);
        border: 1px solid rgba(79, 172, 254, 0.2);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    ">
        <div style="font-size: 1.5rem;">💡</div>
        <div style="color: #a0aec0; font-size: 0.9rem;">
            各質問に対して、最も当てはまると思う選択肢を選んでください。<br>
            正解・不正解はありません。<strong style="color: #e2e8f0;">直感的に答えること</strong>をお勧めします。
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 開始ボタン
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🚀 診断を開始する", type="primary", use_container_width=True):
            st.session_state.diagnostic_started = True
            st.rerun()


def render_questions_page() -> None:
    """質問ページ"""
    total_questions = get_total_questions()
    total_pages = (total_questions + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE
    current_page = st.session_state.current_page

    # ページヘッダー
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    ">
        <div>
            <h2 style="margin: 0; color: #e2e8f0; font-size: 1.5rem;">
                🔮 性格診断
            </h2>
            <div style="color: #718096; font-size: 0.9rem;">
                ページ {current_page + 1} / {total_pages}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # プログレスバー（モダン版）
    answered_count = len(st.session_state.responses)
    progress_percent = (answered_count / total_questions) * 100
    
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        ">
            <span style="color: #a0aec0;">進捗状況</span>
            <span style="color: #e2e8f0; font-weight: 600;">{answered_count} / {total_questions} 問完了</span>
        </div>
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100%;
                width: {progress_percent}%;
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 現在のページの質問を取得
    start_idx = current_page * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, total_questions)
    page_questions = DIAGNOSTIC_QUESTIONS[start_idx:end_idx]

    # 質問を表示
    for question in page_questions:
        # 質問カード
        st.markdown(get_question_card(question.id, question.text), unsafe_allow_html=True)

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

        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # ナビゲーションボタン
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_page > 0:
            if st.button("⬅️ 前のページ", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()

    with col2:
        # ページインジケーター
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
        ">
        """, unsafe_allow_html=True)
        
        for i in range(total_pages):
            is_current = i == current_page
            color = "#667eea" if is_current else "rgba(255,255,255,0.2)"
            size = "10px" if is_current else "8px"
            st.markdown(f"""
            <span style="
                display: inline-block;
                width: {size};
                height: {size};
                background: {color};
                border-radius: 50%;
            "></span>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

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

    # タイプ表示（モダンカード）
    st.markdown(get_result_type_card(
        result.personality_type,
        result.type_description
    ), unsafe_allow_html=True)

    # 各指標の詳細
    st.markdown(get_section_header("📊", "各指標の詳細", "あなたの性格タイプの内訳"), unsafe_allow_html=True)

    for score in result.dimension_scores:
        # プログレスバーで強度を表示
        if score.dominant_type == score.first_type:
            # 第1タイプが優勢
            display_value = 50 + (score.strength_percent / 2)
        else:
            # 第2タイプが優勢
            display_value = 50 - (score.strength_percent / 2)

        # モダンなスコアバー
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.75rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: {'#667eea' if score.dominant_type == score.first_type else '#a0aec0'};
                    ">{score.first_type}</span>
                    <span style="color: #718096;">←→</span>
                    <span style="
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: {'#667eea' if score.dominant_type == score.second_type else '#a0aec0'};
                    ">{score.second_type}</span>
                </div>
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: white;
                ">{score.dominant_type} ({score.strength_percent:.0f}%)</div>
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                height: 12px;
                overflow: hidden;
                position: relative;
            ">
                <div style="
                    position: absolute;
                    left: 50%;
                    top: 0;
                    bottom: 0;
                    width: 2px;
                    background: rgba(255, 255, 255, 0.2);
                "></div>
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100%;
                    width: {display_value}%;
                    border-radius: 10px;
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 説明
        explanation = get_dimension_explanation(score.dimension, score.dominant_type)
        with st.expander(f"💡 {score.dominant_type}タイプの特徴を見る"):
            st.markdown(explanation)

    # アクションボタン
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 もう一度診断する", use_container_width=True):
            reset_diagnostic()
            st.rerun()

    with col2:
        if st.button("📝 ジャーナルを書く", type="primary", use_container_width=True):
            st.session_state.current_view = "journal"
            st.rerun()
