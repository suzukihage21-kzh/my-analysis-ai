"""
分析画面UIコンポーネント

診断結果の詳細と盲点インサイトを表示します。
"""

import streamlit as st
import altair as alt

from database.db_manager import (
    delete_journal_entry,
    get_all_personality_results,
    get_journal_entries,
    get_latest_personality,
    save_ai_analysis_result,
    get_latest_ai_analysis,
    get_latest_ai_analysis,
    get_all_ai_analyses,
    get_dynamic_profile,
)
from logic.analysis import (
    detect_blind_spots,
    get_potential_challenges,
    get_type_strengths,
)
from logic.diagnostic import get_dimension_explanation
from logic.ai_analyzer import (
    analyze_journals_with_ai,
    is_api_configured,
    AIAnalysisResult,
    generate_comprehensive_profile,
)
from models.data_models import PersonalityResult


def render_analysis_page() -> None:
    """分析画面をレンダリング"""
    st.title("🔍 分析・インサイト")

    user_id = st.session_state.get("user_id", "default_user")

    # 最新の診断結果を取得
    personality = get_latest_personality(user_id)

    if personality is None:
        st.warning("まだ性格診断を受けていません。")
        if st.button("🔮 診断を受ける", type="primary"):
            st.session_state.current_view = "diagnostic"
            st.rerun()
        return

    # タブで分析内容を分ける（AI分析とタイプ詳細を統合）
    tab1, tab2, tab3 = st.tabs(["📊 総合分析", "🎯 盲点検知", "📚 ジャーナル記録"])

    with tab1:
        render_unified_analysis(user_id, personality)

    with tab2:
        render_blind_spots(user_id, personality)

    with tab3:
        render_journal_summary(user_id)


def render_unified_analysis(user_id: str, personality: PersonalityResult) -> None:
    """統合された分析画面をレンダリング"""
    st.markdown("## 📊 総合分析レポート")
    
    st.markdown("""
    あなたのジャーナル履歴と性格診断結果を統合し、
    AIが「現在のあなた」を深く分析します。
    """)
    
    # API設定状況を確認
    if not is_api_configured():
        st.warning("⚠️ Google Gemini APIキーの設定が必要です")
        return
    
    # ジャーナルを取得
    journals = get_journal_entries(user_id, limit=50)
    
    if not journals:
        st.info("📝 分析を行うには、まずジャーナルを書いてください。")
        if st.button("📝 ジャーナルを書く", key="write_journal_ai"):
            st.session_state.current_view = "journal"
            st.rerun()
        return
    
    # セッション状態で分析結果を管理
    if "ai_analysis_result" not in st.session_state:
        st.session_state.ai_analysis_result = None
    if "ai_analysis_error" not in st.session_state:
        st.session_state.ai_analysis_error = None
    
    # 分析実行エリア
    st.info(f"✅ {len(journals)}件のジャーナルをもとに分析します")
    
    if st.button("🚀 最新の状態で分析を実行", type="primary", use_container_width=True):
        with st.spinner("AIが分析中です...（ジャーナル量により30秒〜1分程度かかります）"):
            # 1. 一般的な分析
            result, error = analyze_journals_with_ai(
                journals,
                personality.personality_type
            )
            
            # 2. ダイナミック・プロファイルの再生成
            if not error:
                _, profile_error = generate_comprehensive_profile(
                    user_id,
                    personality.personality_type,
                    journals
                )
                if profile_error:
                    print(f"Profile generation error: {profile_error}")
            
            # 結果保存
            st.session_state.ai_analysis_result = result
            st.session_state.ai_analysis_error = error
            
            if result and not error:
                save_ai_analysis_result(
                    user_id,
                    {
                        "behavior_patterns": result.behavior_patterns,
                        "thinking_patterns": result.thinking_patterns,
                        "emotional_triggers": result.emotional_triggers,
                        "values_and_beliefs": result.values_and_beliefs,
                        "strengths": result.strengths,
                        "growth_areas": result.growth_areas,
                        "actionable_advice": result.actionable_advice,
                        "overall_summary": result.overall_summary,
                        "analyzed_at": result.analyzed_at,
                    }
                )
            st.rerun()
    
    if st.session_state.ai_analysis_error:
        st.error(st.session_state.ai_analysis_error)
        return

    # --- 分析結果の表示 ---
    
    # 1. ダイナミック・タイプ・プロファイル（最優先表示）
    dynamic_profile = get_dynamic_profile(user_id)
    if dynamic_profile:
        st.markdown("---")
        st.subheader(f"🔄 {personality.personality_type}のあなた：パーソナライズ分析")
        st.caption(f"最終更新: {dynamic_profile.last_updated.strftime('%Y/%m/%d %H:%M')}")
        
        st.info(dynamic_profile.refined_description)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("#### ✅ 実践で発揮された強み")
            for s in dynamic_profile.validated_strengths:
                st.markdown(f"- {s}")
        with col_d2:
            st.markdown("#### 🔍 直面している課題")
            for c in dynamic_profile.observed_challenges:
                st.markdown(f"- {c}")

        # --- タイプ変化の可視化 ---
        if dynamic_profile.estimated_axis_scores:
            st.markdown("---")
            st.subheader("📉 性格タイプの「ゆらぎ」")
            st.caption("診断結果（理想/基本）と、日記に見られる実際の振る舞い（実態）の比較")
            
            # 各軸の比較を表示
            _render_axis_comparison(personality, dynamic_profile.estimated_axis_scores)

    # 2. 直近のAI分析結果（あれば）
    result = st.session_state.ai_analysis_result
    if not result:
        # セッションになければDBから最新を取得
        latest = get_latest_ai_analysis(user_id)
        if latest:
            # 辞書からオブジェクトに変換
            result = AIAnalysisResult(**latest)
            # analyzed_atが文字列なら変換（念のため）
            if isinstance(result.analyzed_at, str):
                from datetime import datetime
                result.analyzed_at = datetime.fromisoformat(result.analyzed_at)
    
    if result:
        st.markdown("---")
        st.subheader("📊 深層心理・行動分析")
        st.caption(f"分析日時: {result.analyzed_at.strftime('%Y/%m/%d %H:%M')}")

        st.success(f"**総合サマリー**: {result.overall_summary}")

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("#### 🧠 思考・判断の癖")
            for item in result.thinking_patterns:
                st.markdown(f"- {item}")
            st.markdown("#### 🔄 行動パターン")
            for item in result.behavior_patterns:
                st.markdown(f"- {item}")
        with col_a2:
            st.markdown("#### 💎 価値観・信念")
            for item in result.values_and_beliefs:
                st.markdown(f"- {item}")
            st.markdown("#### ❤️ 感情トリガー")
            for item in result.emotional_triggers:
                st.markdown(f"- {item}")

        st.markdown("#### 🎯 具体的なネクストアクション")
        for i, advice in enumerate(result.actionable_advice, 1):
            st.info(f"{i}. {advice}")

    # 3. 基本診断データの詳細（参考情報として下部に配置）
    with st.expander("📊 基本診断データの詳細（スコア・理論値）を見る"):
        _render_static_type_details(personality)


def _render_axis_comparison(
    personality: PersonalityResult, 
    estimated_scores: dict[str, float]
) -> None:
    """診断結果と推定スコアの比較を表示"""
    
    axes = [
        ("内向(I) / 外向(E)", "EI", "E", "I"),
        ("直感(N) / 感覚(S)", "SN", "S", "N"),
        ("感情(F) / 思考(T)", "TF", "T", "F"),
        ("知覚(P) / 判断(J)", "JP", "J", "P"),
    ]
    
    for label, code, left, right in axes:
        # 1. 診断スコアの計算 (0.0=Left, 1.0=Right)
        # 該当するDimensionScoreを探す
        diag_val = 0.5
        for ds in personality.dimension_scores:
            if ds.dimension.name == code:
                # dominant_typeがLeft側(E, S, T, J)なら 0.5 - (percent/200)
                # Right側(I, N, F, P)なら 0.5 + (percent/200)
                if ds.dominant_type == left:
                    diag_val = 0.5 - (ds.strength_percent / 200)
                else:
                    diag_val = 0.5 + (ds.strength_percent / 200)
                break
        
        # 2. 推定スコア
        est_val = estimated_scores.get(code, 0.5)
        
        # 3. 差分表示
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.markdown(f"**{left}**")
        with col3:
            st.markdown(f"**{right}**")
        
        with col2:
            # プログレスバー風の可視化をAltairで行うか、簡易的に文字で表示するか
            # ここではst.progressは1つの値しか出せないので、HTML/CSSでカスタムバーを作るのが見やすい
            
            # バーの背景
            st.markdown(f"""
            <div style="position: relative; width: 100%; height: 24px; background-color: #f0f2f6; border-radius: 12px; margin-bottom: 8px;">
                <!-- 中心線 -->
                <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background-color: #ccc;"></div>
                
                <!-- 診断スコア (青) -->
                <div style="position: absolute; left: {diag_val*100}%; top: 4px; width: 16px; height: 16px; 
                            background-color: #4c7bf4; border-radius: 50%; transform: translateX(-50%); 
                            border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"
                     title="診断結果"></div>
                     
                <!-- 日記スコア (赤) -->
                <div style="position: absolute; left: {est_val*100}%; top: 4px; width: 16px; height: 16px; 
                            background-color: #ff6b6b; border-radius: 50%; transform: translateX(-50%);
                            border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"
                     title="最近の日記傾向"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # 変化の解説
            diff = est_val - diag_val
            if abs(diff) > 0.2:
                # 20%以上のズレがある場合
                direction = right if diff > 0 else left
                st.caption(f"📢 最近は **{direction}** の傾向が強く出ています")


def _render_static_type_details(personality: PersonalityResult) -> None:
    """タイプ詳細を表示"""
    st.markdown(f"""
    ## あなたのタイプ: **{personality.personality_type}**
    ### {personality.type_description}

    診断日時: {personality.diagnosed_at.strftime('%Y年%m月%d日 %H:%M')}
    """)

    # 各指標の詳細
    st.markdown("### 📊 指標別スコア")

    for score in personality.dimension_scores:
        st.markdown(f"#### {score.dimension.value}: {score.first_type} vs {score.second_type}")

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            st.markdown(f"**{score.first_type}**")
            st.markdown(f"{score.first_score:.1f}")

        with col2:
            # 中心を50%として表示
            if score.dominant_type == score.first_type:
                progress_value = 50 + (score.strength_percent / 2)
            else:
                progress_value = 50 - (score.strength_percent / 2)
            st.progress(progress_value / 100)

        with col3:
            st.markdown(f"**{score.second_type}**")
            st.markdown(f"{score.second_score:.1f}")

        # 説明
        explanation = get_dimension_explanation(score.dimension, score.dominant_type)
        with st.expander("詳細を見る"):
            st.info(explanation)
            st.markdown(f"**強度**: {score.strength_percent:.1f}%")

    # --- ダイナミック・プロファイルの表示 ---
    dynamic_profile = get_dynamic_profile(personality.user_id)
    if dynamic_profile:
        st.markdown("---")
        st.markdown("### 🔄 AIによる性格詳細（日記分析ベース）")
        st.info(f"""
        **AIからのインサイト ({dynamic_profile.last_updated.strftime('%Y/%m/%d 更新')})**
        
        {dynamic_profile.refined_description}
        """)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("#### ✅ 実践で確認された強み")
            if dynamic_profile.validated_strengths:
                for s in dynamic_profile.validated_strengths:
                    st.markdown(f"- {s}")
            else:
                st.caption("まだ十分なデータがありません")
        
        with col_d2:
            st.markdown("#### 🔍 観察された課題")
            if dynamic_profile.observed_challenges:
                for c in dynamic_profile.observed_challenges:
                    st.markdown(f"- {c}")
            else:
                st.caption("まだ十分なデータがありません")
    else:
        st.markdown("---")
        st.info("💡 日記を書くと、あなたの性格プロフィールがより詳細にアップデートされます。")

    # 強みと課題（理論値）
    st.markdown("---")
    st.markdown(f"### 💪 {personality.personality_type}タイプの一般的な強み")
    strengths = get_type_strengths(personality.personality_type)
    strength_chips = " ".join([f"`{s}`" for s in strengths])
    st.markdown(strength_chips)

    st.markdown(f"### ⚠️ {personality.personality_type}タイプの一般的な課題")
    challenges = get_potential_challenges(personality.personality_type)
    challenge_chips = " ".join([f"`{c}`" for c in challenges[:6]])
    st.markdown(challenge_chips)


def render_blind_spots(user_id: str, personality: PersonalityResult) -> None:
    """盲点インサイトを表示"""
    st.markdown("## 🎯 盲点検知")

    # ジャーナルを取得
    journals = get_journal_entries(user_id, limit=50)

    if not journals:
        st.info("""
        盲点を検知するには、ジャーナルのデータが必要です。

        日記を書き続けることで、あなたの性格タイプと実際の行動・感情との
        ギャップ（盲点）を発見できるようになります。
        """)

        if st.button("📝 ジャーナルを書く", key="write_journal_blindspot"):
            st.session_state.current_view = "journal"
            st.rerun()
        return

    st.markdown(f"📝 分析対象: {len(journals)}件のジャーナルエントリー")

    # 盲点検知を実行
    insights = detect_blind_spots(personality, journals)

    if not insights:
        st.success("""
        ✨ 現時点で明確な盲点は検出されませんでした！

        これは良い兆候ですが、以下の可能性もあります：
        - ジャーナルのデータがまだ少ない
        - 自己認識と行動が一致している

        引き続きジャーナルを書き続けることで、より深い分析が可能になります。
        """)
    else:
        st.markdown(f"### 🔎 {len(insights)}件のインサイトが見つかりました")

        for i, insight in enumerate(insights, 1):
            severity_color = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴",
            }.get(insight.severity, "⚪")

            with st.expander(f"{severity_color} インサイト {i}: {insight.category}", expanded=True):
                st.markdown(f"**💡 発見**: {insight.description}")

                if insight.evidence:
                    st.markdown("**📝 関連する日記の記述**:")
                    for evidence in insight.evidence:
                        st.markdown(f"- {evidence}")

                st.markdown(f"**🎯 提案**: {insight.recommendation}")

    # ヒント
    st.markdown("---")
    st.markdown("""
    ### 💡 盲点検知を最大限に活用するヒント

    1. **継続的に書く**: 毎日少しでもジャーナルを書くことで、パターンが見えてきます
    2. **正直に書く**: ネガティブな感情も含めて正直に記録しましょう
    3. **具体的に書く**: 「イライラした」だけでなく、何に対してどうイライラしたかを詳しく
    4. **定期的に振り返る**: 週に1回はこの画面で分析結果を確認しましょう
    """)


def render_journal_summary(user_id: str) -> None:
    """ジャーナルの要約と履歴を表示"""
    import pandas as pd
    from collections import Counter

    st.markdown("## 📚 ジャーナル記録・要約")

    # 全ジャーナルを取得（limitを大きく設定）
    entries = get_journal_entries(user_id, limit=1000)

    if not entries:
        st.info("まだジャーナルエントリーがありません。")
        if st.button("📝 最初のエントリーを書く", type="primary", key="write_first_journal"):
            st.session_state.current_view = "journal"
            st.rerun()
        return

    # DataFrame作成
    df = pd.DataFrame([
        {
            "date": e.date,
            "emotion": e.emotion_score,
            "length": len(e.content),
            "tags": e.tags
        }
        for e in entries
    ])
    # dateをdatetime型に変換
    df["date"] = pd.to_datetime(df["date"])
    # 日付ごとの平均（同日に複数ある場合）
    daily_df = df.groupby(df["date"].dt.date)["emotion"].mean().reset_index()
    daily_df["date"] = pd.to_datetime(daily_df["date"])

    # --- 統計情報 ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("総エントリー数", f"{len(entries)}件")
    
    with col2:
        avg_emotion = df["emotion"].mean()
        st.metric("平均気分スコア", f"{avg_emotion:.1f} / 10")
    
    with col3:
        first_date = df["date"].min().date()
        days_since = (pd.Timestamp.now().date() - first_date).days + 1
        st.metric("記録期間", f"{days_since}日間")

    with col4:
        total_chars = df["length"].sum()
        st.metric("総文字数", f"{total_chars}文字")

    st.markdown("---")

    # --- 可視化 ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📈 気分の推移")
        
        # Altairチャートの作成
        chart = alt.Chart(daily_df).mark_line(point=True).encode(
            x=alt.X("date:T", title="日付", axis=alt.Axis(format="%Y/%m/%d")),
            y=alt.Y("emotion:Q", title="気分 (1-10)", scale=alt.Scale(domain=[1, 10])),
            tooltip=[alt.Tooltip("date:T", title="日付", format="%Y/%m/%d"), alt.Tooltip("emotion:Q", title="気分", format=".1f")]
        ).properties(
            title="日々の気分推移"
        )
        # interactive() を呼ばなければ拡大縮小不可になる
        st.altair_chart(chart, use_container_width=True)

    with col_chart2:
        st.markdown("### 🏷️ よく使うタグ")
        all_tags = [tag for tags in df["tags"] for tag in tags if tag]
        if all_tags:
            tag_counts = Counter(all_tags)
            st.bar_chart(pd.Series(tag_counts).sort_values(ascending=False).head(10))
        else:
            st.caption("タグが使用されていません")

    st.markdown("---")

    # --- 全履歴リスト ---
    st.markdown("### 📝 全エントリー一覧")
    
    # フィルタリング機能
    search_query = st.text_input("🔍 キーワード検索", placeholder="内容やタグで検索...")
    
    filtered_entries = entries
    if search_query:
        query = search_query.lower()
        filtered_entries = [
            e for e in entries 
            if query in e.content.lower() or 
            any(query in t.lower() for t in e.tags)
        ]
        st.caption(f"{len(filtered_entries)}件が見つかりました")

    # リスト表示
    for entry in filtered_entries:
        date_str = entry.date.strftime('%Y/%m/%d (%a)')
        emotion_emoji = get_emotion_emoji(entry.emotion_score)
        
        with st.expander(f"{date_str} {emotion_emoji} (気分: {entry.emotion_score})"):
            st.markdown(entry.content)
            
            if entry.tags:
                st.markdown(f"🏷️ **タグ**: {', '.join(entry.tags)}")
            
            if entry.personality_type:
                st.caption(f"当時のタイプ: {entry.personality_type}")
            
            # 削除ボタン
            if st.button("🗑️ このエントリーを削除", key=f"del_summary_{entry.id}"):
                if delete_journal_entry(entry.id):
                    st.success("エントリーを削除しました")
                    st.rerun()
                else:
                    st.error("削除に失敗しました")


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
