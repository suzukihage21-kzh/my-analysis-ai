"""
ジャーナル画面UIコンポーネント

日記の入力と履歴表示を提供します。
"""

from datetime import datetime

import streamlit as st

from database.db_manager import (
    delete_journal_entry,
    get_all_tags,
    get_journal_entries,
    get_latest_personality,
    save_journal_entry,
    update_journal_entry,
)
from logic.tagging import suggest_tags
from logic.ai_analyzer import get_journal_feedback, is_api_configured, refine_profile_with_journal
from models.data_models import JournalEntry
from prompts.daily_prompts import get_daily_prompt, get_balanced_prompt


def init_journal_state() -> None:
    """ジャーナル用セッション状態を初期化"""
    if "journal_saved" not in st.session_state:
        st.session_state.journal_saved = False
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "editing_entry_id" not in st.session_state:
        st.session_state.editing_entry_id = None


def render_journal_page() -> None:
    """ジャーナル画面をレンダリング"""
    init_journal_state()

    st.title("📝 ジャーナル")

    user_id = st.session_state.get("user_id", "default_user")

    # タブで入力と履歴を切り替え
    tab1, tab2 = st.tabs(["✍️ 新規エントリー", "📚 履歴"])

    with tab1:
        render_journal_form(user_id)

    with tab2:
        render_journal_history(user_id)


def render_journal_form(user_id: str) -> None:
    """ジャーナル入力フォーム"""
    # AIフィードバックがあれば表示（改善されたカード形式）
    if "ai_feedback" in st.session_state and st.session_state.ai_feedback:
        st.markdown("""
        <style>
        .ai-feedback-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            color: white;
        }
        .ai-feedback-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        .ai-feedback-content {
            font-size: 15px;
            line-height: 1.7;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="ai-feedback-card">
            <div class="ai-feedback-title">💬 AIカウンセラーからのメッセージ</div>
            <div class="ai-feedback-content">{st.session_state.ai_feedback}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ メッセージを閉じる", key="close_feedback"):
            st.session_state.ai_feedback = None
            st.rerun()
        st.markdown("---")
    
    # 最新の性格タイプを取得
    personality_result = get_latest_personality(user_id)
    personality_type = personality_result.personality_type if personality_result else None

    # 動的プロンプトの表示
    if personality_type:
        prompt = get_balanced_prompt(personality_type)
        st.info(f"💭 **今日の問いかけ**: {prompt}")
        st.caption(f"あなたのタイプ「{personality_type}」に基づいたプロンプトです")
    else:
        st.info("💭 **ヒント**: 性格診断を受けると、あなたに合った問いかけが表示されます")

    # 既存の全タグを取得
    existing_tags = get_all_tags(user_id)

    # 日付選択（key追加）
    st.date_input(
        "📅 日付",
        value=datetime.now().date(),
        max_value=datetime.now().date(),
        key="journal_entry_date"
    )

    # 内容入力
    st.text_area(
        "📖 今日の振り返り",
        height=200,
        placeholder="今日あったこと、感じたこと、考えたことを自由に書いてください...",
        key="journal_content_area"
    )

    st.markdown("---")
    st.markdown("🏷️ **タグ設定**")

    # タグ提案ボタン
    content_for_suggest = st.session_state.get("journal_content_area", "")
    if st.button("🤖 本文からタグを自動提案", help="入力された本文を解析してタグを提案します"):
        if content_for_suggest:
            suggestions = suggest_tags(content_for_suggest, existing_tags)
            if suggestions:
                current_selection = st.session_state.get("selected_tags_widget", [])
                new_selection = sorted(list(set(current_selection + suggestions)))
                st.session_state.selected_tags_widget = new_selection
                st.toast(f"タグを提案しました: {', '.join(suggestions)}", icon="🤖")
            else:
                st.toast("提案できるタグが見つかりませんでした", icon="🤔")
        else:
            st.toast("先に本文を入力してください", icon="⚠️")

    col1, col2 = st.columns(2)
    
    with col1:
        # 既存タグから選択
        st.multiselect(
            "既存のタグから選択",
            options=existing_tags,
            placeholder="タグを選択...",
            key="selected_tags_widget"
        )
    
    with col2:
        # 新規タグ入力
        st.text_input(
            "新規タグを追加（カンマ区切り）",
            placeholder="例: 新しいプロジェクト, 挑戦",
            key="new_tags_input"
        )

    # 感情スコア（key追加）
    st.slider(
        "😊 今日の気分（1: とても悪い ← → 10: とても良い）",
        min_value=1,
        max_value=10,
        value=5,
        key="journal_emotion_score"
    )

    st.markdown("---")

    # 保存処理のコールバック関数
    def handle_save_journal():
        content = st.session_state.journal_content_area
        date_val = st.session_state.journal_entry_date
        emotion_val = st.session_state.journal_emotion_score
        
        if not content.strip():
            st.error("内容を入力してください")
            return

        # タグを結合して整理
        tags = list(st.session_state.selected_tags_widget)
        new_tags_str = st.session_state.new_tags_input
        if new_tags_str:
            new_tags = [tag.strip() for tag in new_tags_str.split(",") if tag.strip()]
            tags.extend(new_tags)
        
        # 重複除去
        tags = sorted(list(set(tags)))

        # エントリーを作成
        entry = JournalEntry(
            user_id=user_id,
            date=datetime.combine(date_val, datetime.min.time()),
            content=content.strip(),
            tags=tags,
            emotion_score=emotion_val,
            personality_type=personality_type,
        )

        try:
            # 保存
            save_journal_entry(entry)
            st.toast("✅ ジャーナルを保存しました！", icon="💾")
            
            # AIフィードバックを取得（APIが設定されている場合）
            # 注意: コールバック内での spinner 表示は動作しない場合があるため、
            # 次回のレンダリングで処理するか、ここではシンプルに実行する
            if is_api_configured():
                try:
                    # 同期的に実行（spinnerなし）
                    feedback, error_msg = get_journal_feedback(
                        content.strip(),
                        emotion_val,
                        personality_type,
                    )
                    if feedback:
                        st.session_state.ai_feedback = feedback
                    elif error_msg:
                        st.session_state.ai_feedback_error = error_msg
                except Exception as e:
                    st.session_state.ai_feedback_error = str(e)
            
            # ダイナミック・プロファイルの更新（バックグラウンド的に実行）
            if is_api_configured() and personality_type:
                try:
                    # ユーザーに処理中であることを伝える（トースト）
                    st.toast("性格プロフィールを更新中...", icon="🔄")
                    _, ref_error = refine_profile_with_journal(
                        user_id,
                        personality_type,
                        entry
                    )
                    if not ref_error:
                        st.toast("性格プロフィールが詳細化されました！", icon="✨")
                except Exception as e:
                    # プロファイル更新のエラーはユーザー体験を阻害しないようログのみ（または無視）
                    print(f"Profile update error: {e}")

            # フォームクリア
            st.session_state.journal_content_area = ""
            st.session_state.selected_tags_widget = []
            st.session_state.new_tags_input = ""
            # 日付とスコアは維持するか、リセットするか。ここでは維持する。

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

    # 送信ボタン（コールバックを使用）
    st.button("💾 保存する", type="primary", use_container_width=True, on_click=handle_save_journal)
    
    # AIエラーがあれば表示
    if "ai_feedback_error" in st.session_state and st.session_state.ai_feedback_error:
        st.warning(f"⚠️ AIフィードバックエラー: {st.session_state.ai_feedback_error}")
        # 一度表示したら消す
        del st.session_state.ai_feedback_error


def render_journal_history(user_id: str) -> None:
    """ジャーナル履歴表示"""
    entries = get_journal_entries(user_id, limit=30)
    existing_tags = get_all_tags(user_id) # 編集用

    if not entries:
        st.info("まだジャーナルエントリーがありません。最初のエントリーを書いてみましょう！")
        return

    st.markdown(f"### 📚 最近のエントリー（{len(entries)}件）")

    # 感情の推移グラフ
    if len(entries) >= 2:
        render_emotion_chart(entries)

    # エントリー一覧
    for entry in entries:
        is_editing = st.session_state.get("editing_entry_id") == entry.id
        
        # エキスパンダーのラベル
        label = f"📅 {entry.date.strftime('%Y年%m月%d日')} - 気分: {'😃' if entry.emotion_score >= 7 else '😐' if entry.emotion_score >= 4 else '😔'} ({entry.emotion_score}/10)"
        if is_editing:
            label = f"✏️ 編集モード: {entry.date.strftime('%Y年%m月%d日')}"
            
        with st.expander(label, expanded=is_editing):
            
            if is_editing:
                # --- 編集モード ---
                # フォーム外でタグ提案ボタンを配置（フォームの前に）
                st.markdown("🏷️ **タグ設定**")
                
                # セッション状態キーを動的に生成
                suggest_key = f"suggest_tags_edit_{entry.id}"
                content_key = f"temp_content_{entry.id}"
                suggested_tags_key = f"suggested_tags_{entry.id}"
                
                # 現在の本文を一時保存（提案ボタン用）
                if content_key not in st.session_state:
                    st.session_state[content_key] = entry.content
                
                # 提案されたタグを保持
                if suggested_tags_key not in st.session_state:
                    st.session_state[suggested_tags_key] = []
                
                if st.button("🤖 本文からタグを自動提案", key=suggest_key, help="入力された本文を解析してタグを提案します"):
                    temp_content = st.session_state.get(content_key, entry.content)
                    if temp_content:
                        suggestions = suggest_tags(temp_content, existing_tags)
                        if suggestions:
                            st.session_state[suggested_tags_key] = suggestions
                            st.toast(f"タグを提案しました: {', '.join(suggestions)}", icon="🤖")
                        else:
                            st.toast("提案できるタグが見つかりませんでした", icon="🤔")
                    else:
                        st.toast("先に本文を入力してください", icon="⚠️")
                
                with st.form(key=f"edit_form_{entry.id}"):
                    # 本文編集
                    new_content = st.text_area("本文", value=entry.content, height=150, key=f"edit_content_{entry.id}")
                    
                    # 本文の変更をセッション状態に反映（次回の提案用）
                    st.session_state[content_key] = new_content
                    
                    # 気分編集
                    new_emotion = st.slider(
                        "気分", min_value=1, max_value=10, value=entry.emotion_score
                    )
                    
                    # タグ編集（既存タグの選択）
                    current_tags = [t for t in entry.tags if t in existing_tags]
                    # 提案されたタグを追加
                    suggested = st.session_state.get(suggested_tags_key, [])
                    if suggested:
                        current_tags = sorted(list(set(current_tags + suggested)))
                    
                    custom_tags_val = ", ".join([t for t in entry.tags if t not in existing_tags])
                    
                    col_tag1, col_tag2 = st.columns(2)
                    with col_tag1:
                        new_selected_tags = st.multiselect(
                            "既存タグ", existing_tags, default=current_tags
                        )
                    with col_tag2:
                        new_custom_tags_str = st.text_input(
                            "新規タグ（カンマ区切り）", value=custom_tags_val
                        )
                    
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                         if st.form_submit_button("💾 保存", type="primary", use_container_width=True):
                            # タグの結合
                            final_tags = list(new_selected_tags)
                            if new_custom_tags_str:
                                extra_tags = [t.strip() for t in new_custom_tags_str.split(",") if t.strip()]
                                final_tags.extend(extra_tags)
                            final_tags = sorted(list(set(final_tags)))
                            
                            # 更新オブジェクト
                            updated_entry = JournalEntry(
                                id=entry.id,
                                user_id=entry.user_id,
                                date=entry.date, # 日付は変更しない
                                content=new_content,
                                tags=final_tags,
                                emotion_score=new_emotion,
                                personality_type=entry.personality_type
                            )
                            
                            if update_journal_entry(updated_entry):
                                st.session_state.editing_entry_id = None
                                st.success("更新しました！")
                                st.rerun()
                            else:
                                st.error("更新に失敗しました")
                                
                    with col_btn2:
                        # フォーム内でのキャンセルは難しい（submitボタンしかイベント発火しないため）
                        # フォーム外に設置するか、submitボタンの一つとして実装しstateで分岐する
                        # ここでは「キャンセル」ボタンもsubmit扱いにして、処理せずにstate戻す
                        if st.form_submit_button("❌ キャンセル", use_container_width=True):
                            st.session_state.editing_entry_id = None
                            st.rerun()

            else:
                # --- 表示モード ---
                st.markdown(entry.content)

                if entry.tags:
                    tag_str = " ".join([f"`{tag}`" for tag in entry.tags])
                    st.markdown(f"🏷️ {tag_str}")

                if entry.personality_type:
                    st.caption(f"タイプ: {entry.personality_type}")
                
                # 操作ボタンエリア
                col_op1, col_op2 = st.columns([1, 4])
                with col_op1:
                    if st.button("✏️ 編集", key=f"edit_btn_{entry.id}"):
                        st.session_state.editing_entry_id = entry.id
                        st.rerun()
                with col_op2:
                    if st.button("🗑️ 削除", key=f"del_{entry.id}"):
                        if delete_journal_entry(entry.id):
                            st.success("エントリーを削除しました")
                            st.rerun()
                        else:
                            st.error("削除に失敗しました")


def render_emotion_chart(entries: list[JournalEntry]) -> None:
    """感情推移グラフ"""
    import pandas as pd

    # データを整形（日付昇順に）
    sorted_entries = sorted(entries, key=lambda e: e.date)

    data = {
        "日付": [e.date.strftime("%m/%d") for e in sorted_entries],
        "気分": [e.emotion_score for e in sorted_entries],
    }
    df = pd.DataFrame(data)

    st.markdown("#### 📈 気分の推移")
    st.line_chart(df.set_index("日付"))


def get_emotion_emoji(score: int) -> str:
    """感情スコアに対応する絵文字を取得"""
    if score >= 9:
        return "🎉"
    elif score >= 7:
        return "😃"
    elif score >= 5:
        return "🙂"
    elif score >= 3:
        return "😐"
    else:
        return "😔"
