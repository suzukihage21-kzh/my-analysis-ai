"""
AI分析モジュール

Google Gemini APIを使用してジャーナル内容を深く分析し、
ユーザーの人間性に関するインサイトを提供します。
"""

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import streamlit as st


from database.db_manager import get_dynamic_profile, save_dynamic_profile
from models.data_models import DynamicTypeProfile, JournalEntry, get_jst_now

# 環境変数を読み込み
load_dotenv()


class AIAnalysisResult(BaseModel):
    """AI分析結果"""
    behavior_patterns: list[str] = Field(
        default_factory=list,
        description="繰り返し現れる行動パターン"
    )
    thinking_patterns: list[str] = Field(
        default_factory=list,
        description="思考・意思決定の傾向"
    )
    emotional_triggers: list[str] = Field(
        default_factory=list,
        description="感情のトリガーとなる状況"
    )
    values_and_beliefs: list[str] = Field(
        default_factory=list,
        description="価値観・信念"
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="強み・才能"
    )
    growth_areas: list[str] = Field(
        default_factory=list,
        description="成長の余地がある領域"
    )
    actionable_advice: list[str] = Field(
        default_factory=list,
        description="具体的で実行可能なアドバイス"
    )
    overall_summary: str = Field(
        default="",
        description="人間性の総合的なサマリー"
    )
    analyzed_at: datetime = Field(
        default_factory=get_jst_now,
        description="分析日時"
    )


def get_gemini_client() -> Optional[object]:
    """
    Gemini APIクライアントを取得
    
    Returns:
        クライアントオブジェクト（設定されていない場合はNone）
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Streamlit CloudのSecretsも確認
    if (not api_key or api_key == "your_api_key_here") and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if not api_key or api_key == "your_api_key_here":
        return None
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except ImportError:
        return None
    except Exception:
        return None


def build_analysis_prompt(
    journals_text: str,
    personality_type: Optional[str] = None,
    emotion_stats: Optional[dict[str, float]] = None,
) -> str:
    """
    AI分析用のプロンプトを構築
    
    Args:
        journals_text: ジャーナルエントリーのテキスト
        personality_type: 性格タイプ（あれば）
        emotion_stats: 感情統計情報（あれば）
    
    Returns:
        構造化されたプロンプト
    """
    personality_context = ""
    if personality_type:
        personality_context = f"""【性格タイプ】
このユーザーの性格診断結果は「{personality_type}」です。
性格タイプの一般的な特徴と、日記から見える実際の姿を比較し、
一致している点、意外な点、成長の可能性を見出してください。"""

    emotion_context = ""
    if emotion_stats:
        emotion_context = f"""【感情の傾向】
- 平均気分スコア: {emotion_stats.get('avg', 0):.1f}/10
- 最高: {emotion_stats.get('max', 0)}/10、最低: {emotion_stats.get('min', 0)}/10
- 変動幅: {emotion_stats.get('range', 0)}
これらの傾向も考慮に入れてください。"""

    prompt = f"""あなたは20年以上の経験を持つ臨床心理士であり、人間の内面を深く理解する専門家です。
クライアントが書いた日記を読み、その方の人間性について温かく、かつ鋭い洞察を提供してください。

{personality_context}
{emotion_context}

【分析対象の日記】
{journals_text}

【分析の視点 - 深さを重視】

表面的なキーワード抽出ではなく、日記の「行間」を読んでください。
以下の5つの視点から、具体的かつ深い洞察を提供してください：

1. **行動と思考のパターン**
   - 繰り返し現れるテーマや行動傾向
   - 意思決定の仕方、問題への向き合い方
   - 日記に書かれていないが推測される習慣

2. **感情の源泉**
   - 何がこの人を本当に喜ばせるか
   - ストレスや不安の根本にあるもの
   - 感情と行動の関係性

3. **価値観と強み**
   - 無意識に大切にしているもの
   - 本人が気づいていない潜在的な才能
   - 人柄の魅力的な側面

4. **成長のチャンス**
   - より幸せになれる可能性のある領域
   - 批判ではなく、可能性としての提案
   - 性格タイプを活かした成長の方向性

5. **明日からのアクション**
   - 小さく始められる具体的な一歩
   - この人の性格に合った実践方法
   - 継続しやすい形での提案

【回答形式】
必ず以下のJSON形式で回答してください。
各項目は「具体的」で「その人だけに当てはまる」内容にしてください。
一般論や抽象的な表現は避けてください。

```json
{{
    "behavior_patterns": ["日記から読み取れる具体的なパターン（3-4個）"],
    "thinking_patterns": ["思考・判断の傾向（3-4個）"],
    "emotional_triggers": ["喜び・ストレスの具体的なトリガー（3-4個）"],
    "values_and_beliefs": ["大切にしている価値観（3-4個）"],
    "strengths": ["強み・才能。できれば本人が気づいていなさそうなもの（3-4個）"],
    "growth_areas": ["成長の余地。批判ではなく可能性として（2-3個）"],
    "actionable_advice": ["明日から実践できる具体的なアクション（3個）"],
    "overall_summary": "200-300文字で、この人の魅力と可能性を温かく表現してください"
}}
```

【重要な注意点】
- 温かみを持ちながらも、表面的なお世辞は避けてください
- 批判や否定ではなく、常に成長と可能性の視点で書いてください
- 日記に書かれた具体的なエピソードを根拠にしてください"""

    return prompt


def parse_ai_response(response_text: str) -> AIAnalysisResult:
    """
    AIのレスポンスをパースしてAIAnalysisResultに変換
    
    Args:
        response_text: AIからのレスポンステキスト
    
    Returns:
        AIAnalysisResult オブジェクト
    """
    import json
    import re
    
    # JSONブロックを抽出
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(1)
    else:
        # JSONブロックがない場合、全体をJSONとして解析を試みる
        json_str = response_text
    
    try:
        data = json.loads(json_str)
        return AIAnalysisResult(
            behavior_patterns=data.get("behavior_patterns", []),
            thinking_patterns=data.get("thinking_patterns", []),
            emotional_triggers=data.get("emotional_triggers", []),
            values_and_beliefs=data.get("values_and_beliefs", []),
            strengths=data.get("strengths", []),
            growth_areas=data.get("growth_areas", []),
            actionable_advice=data.get("actionable_advice", []),
            overall_summary=data.get("overall_summary", ""),
            analyzed_at=get_jst_now(),
        )
    except (json.JSONDecodeError, KeyError):
        # パースに失敗した場合はデフォルト値を返す
        return AIAnalysisResult(
            overall_summary="分析結果のパースに失敗しました。再度お試しください。",
            analyzed_at=get_jst_now(),
        )


def analyze_journals_with_ai(
    journals: list,
    personality_type: Optional[str] = None,
) -> tuple[Optional[AIAnalysisResult], Optional[str]]:
    """
    ジャーナルをAIで分析する
    
    Args:
        journals: JournalEntryのリスト
        personality_type: 性格タイプ（あれば）
    
    Returns:
        (AIAnalysisResult, エラーメッセージ) のタプル
        成功時はエラーメッセージがNone、失敗時は結果がNone
    """
    # クライアントを取得
    client = get_gemini_client()
    
    if client is None:
        return None, "APIキーが設定されていません。.envファイルにGEMINI_API_KEYを設定してください。"
    
    if not journals:
        return None, "分析するジャーナルがありません。先に日記を書いてください。"
    
    # ジャーナルをテキストに変換
    journals_text = ""
    for journal in journals:
        date_str = journal.date.strftime("%Y年%m月%d日")
        emotion_str = f"気分: {journal.emotion_score}/10"
        tags_str = f"タグ: {', '.join(journal.tags)}" if journal.tags else ""
        
        journals_text += f"""
---
【{date_str}】{emotion_str} {tags_str}
{journal.content}
"""
    
    # 感情統計を計算
    emotion_stats = calculate_emotion_stats(journals)
    
    # プロンプトを構築
    prompt = build_analysis_prompt(journals_text, personality_type, emotion_stats)
    
    try:
        # Gemini APIを呼び出し
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        
        # レスポンスをパース
        result = parse_ai_response(response.text)
        return result, None
        
    except Exception as e:
        error_msg = f"AI分析中にエラーが発生しました: {str(e)}"
        return None, error_msg


def is_api_configured() -> bool:
    """
    APIキーが設定されているかチェック
    
    Returns:
        設定されている場合True
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if (not api_key or api_key == "your_api_key_here") and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        
    return bool(api_key and api_key != "your_api_key_here")


def get_journal_feedback(
    content: str,
    emotion_score: int,
    personality_type: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    """
    ジャーナル入力に対する即時AIフィードバックを取得
    
    Args:
        content: ジャーナルの内容
        emotion_score: 感情スコア（1-10）
        personality_type: 性格タイプ（あれば）
    
    Returns:
        (フィードバックメッセージ, エラーメッセージ) のタプル
    """
    client = get_gemini_client()
    
    if client is None:
        return None, None  # APIが設定されていなくてもエラーにしない
    
    if not content or len(content.strip()) < 20:
        return None, None  # 内容が短すぎる場合はスキップ
    
    # 性格タイプ別のパーソナライズされたアプローチ
    personality_guidance = _get_personality_feedback_guidance(personality_type)
    
    # 感情状態に応じたトーン調整
    emotion_tone = _get_emotion_aware_tone(emotion_score)
    
    prompt = f"""あなたは豊かな経験を持つ心理カウンセラーです。
クライアントの日記を読み、心に響く温かいフィードバックを提供してください。

【クライアント情報】
- 性格タイプ: {personality_type if personality_type else '未診断'}
- 今日の気分: {emotion_score}/10
{personality_guidance}

【今日の日記】
{content}

【フィードバック作成の指針】
{emotion_tone}

1. **共感と承認**: まず日記の内容に対する共感を示してください
2. **具体的な気づき**: 日記の中から1つ、ポジティブな点や気づきを具体的に指摘してください
3. **明日へのヒント**: 1つだけ、すぐに実践できる小さな提案をしてください

【出力形式】
- 180〜220文字程度
- 温かみのある自然な日本語
- 「〜ですね」「〜かもしれませんね」など寄り添う表現を使用
- 相手を否定したり、説教をしたりしない
- 絵文字は使わない

フィードバックメッセージのみを返してください。"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)


def generate_comprehensive_profile(
    user_id: str,
    base_type: str,
    journals: list[JournalEntry],
) -> tuple[Optional[DynamicTypeProfile], Optional[str]]:
    """
    全ジャーナルに基づいて包括的なプロフィールを生成する（一括更新用）

    Args:
        user_id: ユーザーID
        base_type: 基本性格タイプ
        journals: ジャーナルエントリーのリスト

    Returns:
        (NewProfile, ErrorMessage)
    """
    client = get_gemini_client()
    if client is None:
        return None, "APIキーが設定されていません"

    if not journals:
        return None, "分析するジャーナルがありません"

    # ジャーナルをテキストに変換（最新のものから最大20件程度を使用）
    # トークン数を考慮して、内容を結合
    sorted_journals = sorted(journals, key=lambda j: j.date, reverse=True)[:30]
    journals_text = ""
    for journal in sorted_journals:
        date_str = journal.date.strftime("%Y/%m/%d")
        journals_text += f"\n--- {date_str} ---\n{journal.content}\n"

    prompt = f"""あなたは性格分析の専門家です。
ユーザーの基本性格タイプは「{base_type}」です。
以下の過去の日記ログ（最大30件）を分析し、このユーザーの「詳細な性格プロフィール」をゼロから作成してください。

【日記ログ】
{journals_text}

【指示】
1. 基本タイプ「{base_type}」の枠組みを使いつつ、日記から読み取れる**このユーザー独自の**特徴、価値観、行動パターンを深く分析してください。
2. 一般的な{base_type}の説明ではなく、日記のエビデンスに基づいた「生きた」人物像を描写してください。
3. 強みと課題についても、日記の中で具体的に現れているものを抽出してください。
4. 【重要】日記の内容から、4つの指標（EI, SN, TF, JP）に対する「現在の実際の傾向」を0.0〜1.0の数値で推定してください。
   - 0.0に近いほど左側（E, S, T, J）、1.0に近いほど右側（I, N, F, P）の性質が強く出ています。
   - 0.5は中立です。

【回答形式】
JSON形式で返答してください。
```json
{{
    "refined_description": "詳細な人物像説明（400-500文字）。三人称（このユーザーは...）で記述。",
    "validated_strengths": ["日記で確認された具体的な強み（5-7個）"],
    "observed_challenges": ["日記で確認された具体的な課題（5-7個）"],
    "estimated_axis_scores": {{
        "EI": 0.3,
        "SN": 0.7,
        "TF": 0.4,
        "JP": 0.6
    }}
}}
```
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        
        # Parse JSON
        import json
        import re
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.text
            
        data = json.loads(json_str)
        
        new_profile = DynamicTypeProfile(
            user_id=user_id,
            base_type=base_type,
            refined_description=data.get("refined_description", ""),
            validated_strengths=data.get("validated_strengths", []),
            observed_challenges=data.get("observed_challenges", []),
            estimated_axis_scores=data.get("estimated_axis_scores", {}),
            last_updated=get_jst_now()
        )
        
        save_dynamic_profile(new_profile)
        return new_profile, None

    except Exception as e:
        return None, str(e)


def _get_personality_feedback_guidance(personality_type: Optional[str]) -> str:
    """性格タイプに基づくフィードバック指針を生成"""
    if not personality_type:
        return ""
    
    guidance_map: dict[str, str] = {
        "E": "外向型: 人との繋がりや活動に焦点を当てた言葉が響きやすい",
        "I": "内向型: 内省や深い思考を認める言葉が響きやすい",
        "S": "感覚型: 具体的な事実や実践的な提案が響きやすい",
        "N": "直観型: 可能性や意味に焦点を当てた言葉が響きやすい",
        "T": "思考型: 論理的な観点や客観的な気づきが響きやすい",
        "F": "感情型: 感情を受け止め、価値観を尊重する言葉が響きやすい",
        "J": "判断型: 達成や進歩に焦点を当てた言葉が響きやすい",
        "P": "知覚型: 柔軟性や可能性を認める言葉が響きやすい",
    }
    
    guides = []
    for char in personality_type:
        if char in guidance_map:
            guides.append(f"- {guidance_map[char]}")
    
    if guides:
        return "【この方へのアプローチのヒント】\n" + "\n".join(guides)
    return ""


def _get_emotion_aware_tone(emotion_score: int) -> str:
    """感情スコアに応じたトーンのガイダンスを生成"""
    if emotion_score <= 3:
        return """【特に重要】今日は辛い一日だったようです。
- まずは「大変でしたね」「頑張りましたね」と労いの言葉を
- 無理にポジティブにせず、今の気持ちに寄り添う
- 具体的な解決策より、気持ちの受容を優先"""
    elif emotion_score <= 5:
        return """今日は普通か少し落ち着いた日のようです。
- 日常の中の小さな良い点を見つけて伝える
- バランスの取れた穏やかなトーンで"""
    elif emotion_score <= 7:
        return """今日は良い一日だったようです。
- ポジティブな点を一緒に喜ぶ
- その良い状態を続けるヒントがあれば提案"""
    else:
        return """今日はとても良い一日だったようです！
- 喜びを一緒に分かち合う
- 何がその良い気分につながったか気づきがあれば指摘"""


def get_weekly_insight(
    journals: list,
    personality_type: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    """
    週間のジャーナルから気づきを生成
    
    Args:
        journals: 過去1週間のジャーナルリスト
        personality_type: 性格タイプ
    
    Returns:
        (週間インサイト, エラーメッセージ) のタプル
    """
    client = get_gemini_client()
    
    if client is None:
        return None, "APIキーが設定されていません"
    
    if len(journals) < 3:
        return None, "週間インサイトには最低3件の日記が必要です"
    
    # 感情スコアの統計を計算
    emotion_scores = [j.emotion_score for j in journals]
    avg_emotion = sum(emotion_scores) / len(emotion_scores)
    min_emotion = min(emotion_scores)
    max_emotion = max(emotion_scores)
    
    # 感情の傾向を分析（上昇・下降・安定）
    emotion_trend = _analyze_emotion_trend(emotion_scores)
    
    # ジャーナルを日付順にソートしてテキストに変換（全文を含める）
    sorted_journals = sorted(journals, key=lambda j: j.date)
    journals_text = ""
    for journal in sorted_journals:
        date_str = journal.date.strftime("%m/%d(%a)")
        tags_str = f" [タグ: {', '.join(journal.tags)}]" if journal.tags else ""
        # 内容は500文字まで（200文字から拡張）
        content_preview = journal.content[:500] + "..." if len(journal.content) > 500 else journal.content
        journals_text += f"\n【{date_str}】気分: {journal.emotion_score}/10{tags_str}\n{content_preview}\n"
    
    personality_context = ""
    if personality_type:
        personality_context = f"""この方の性格タイプは「{personality_type}」です。
このタイプの特徴を踏まえたアドバイスを含めてください。"""
    
    prompt = f"""あなたは経験豊富な心理カウンセラーです。
クライアントの1週間の日記を振り返り、深い洞察と温かい励ましを提供してください。

{personality_context}

【感情データ】
- 平均気分: {avg_emotion:.1f}/10
- 最高の日: {max_emotion}/10
- 最低の日: {min_emotion}/10  
- 傾向: {emotion_trend}

【今週の日記】
{journals_text}

【分析の視点】
1. 1週間を通じた感情の流れ（どんな時に上がり、どんな時に下がったか）
2. 繰り返し現れるテーマや関心事
3. この1週間で見られた小さな成長や良い変化
4. 来週をより良くするための具体的な提案

【回答形式】
以下の形式で、合計300〜400文字程度で回答してください。
温かみがありながらも、具体的な洞察を含めてください。

📊 **今週の振り返り**
（1週間の感情の流れと主なテーマを2-3文で）

✨ **見つけた光**
（今週の良かった点、成長を1-2文で）

💡 **気づき**
（深い洞察や発見を1-2文で）

🌱 **来週へのヒント**
（具体的で実践しやすい提案を1-2つ。その人の性格に合った形で）"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)


def generate_comprehensive_profile(
    user_id: str,
    base_type: str,
    journals: list[JournalEntry],
) -> tuple[Optional[DynamicTypeProfile], Optional[str]]:
    """
    全ジャーナルに基づいて包括的なプロフィールを生成する（一括更新用）

    Args:
        user_id: ユーザーID
        base_type: 基本性格タイプ
        journals: ジャーナルエントリーのリスト

    Returns:
        (NewProfile, ErrorMessage)
    """
    client = get_gemini_client()
    if client is None:
        return None, "APIキーが設定されていません"

    if not journals:
        return None, "分析するジャーナルがありません"

    # ジャーナルをテキストに変換（最新のものから最大20件程度を使用）
    # トークン数を考慮して、内容を結合
    sorted_journals = sorted(journals, key=lambda j: j.date, reverse=True)[:30]
    journals_text = ""
    for journal in sorted_journals:
        date_str = journal.date.strftime("%Y/%m/%d")
        journals_text += f"\n--- {date_str} ---\n{journal.content}\n"

    prompt = f"""あなたは性格分析の専門家です。
ユーザーの基本性格タイプは「{base_type}」です。
以下の過去の日記ログ（最大30件）を分析し、このユーザーの「詳細な性格プロフィール」をゼロから作成してください。

【日記ログ】
{journals_text}

【指示】
1. 基本タイプ「{base_type}」の枠組みを使いつつ、日記から読み取れる**このユーザー独自の**特徴、価値観、行動パターンを深く分析してください。
2. 一般的な{base_type}の説明ではなく、日記のエビデンスに基づいた「生きた」人物像を描写してください。
3. 強みと課題についても、日記の中で具体的に現れているものを抽出してください。
4. 【重要】日記の内容から、4つの指標（EI, SN, TF, JP）に対する「現在の実際の傾向」を0.0〜1.0の数値で推定してください。
   - 0.0に近いほど左側（E, S, T, J）、1.0に近いほど右側（I, N, F, P）の性質が強く出ています。
   - 0.5は中立です。

【回答形式】
JSON形式で返答してください。
```json
{{
    "refined_description": "詳細な人物像説明（400-500文字）。三人称（このユーザーは...）で記述。",
    "validated_strengths": ["日記で確認された具体的な強み（5-7個）"],
    "observed_challenges": ["日記で確認された具体的な課題（5-7個）"],
    "estimated_axis_scores": {{
        "EI": 0.3,
        "SN": 0.7,
        "TF": 0.4,
        "JP": 0.6
    }}
}}
```
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        
        # Parse JSON
        import json
        import re
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.text
            
        data = json.loads(json_str)
        
        new_profile = DynamicTypeProfile(
            user_id=user_id,
            base_type=base_type,
            refined_description=data.get("refined_description", ""),
            validated_strengths=data.get("validated_strengths", []),
            observed_challenges=data.get("observed_challenges", []),
            estimated_axis_scores=data.get("estimated_axis_scores", {}),
            last_updated=get_jst_now()
        )
        
        save_dynamic_profile(new_profile)
        return new_profile, None

    except Exception as e:
        return None, str(e)


def _analyze_emotion_trend(scores: list[int]) -> str:
    """感情スコアのトレンドを分析"""
    if len(scores) < 2:
        return "データ不足"
    
    # 前半と後半の平均を比較
    mid = len(scores) // 2
    first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
    second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
    
    diff = second_half_avg - first_half_avg
    
    if diff > 1:
        return "上昇傾向 📈 週の後半に向けて気分が上向いています"
    elif diff < -1:
        return "下降傾向 📉 週の後半に気分が下がっています"
    else:
        # 変動の大きさをチェック
        variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
        if variance > 4:
            return "変動あり 🎢 日によって気分の波があります"
        else:
            return "安定 ➡️ 比較的安定した1週間でした"


def calculate_emotion_stats(journals: list) -> dict[str, float]:
    """ジャーナルリストから感情統計を計算"""
    if not journals:
        return {}
    
    scores = [j.emotion_score for j in journals]
    return {
        "avg": sum(scores) / len(scores),
        "min": min(scores),
        "max": max(scores),
        "range": max(scores) - min(scores),
    }

def refine_profile_with_journal(
    user_id: str,
    base_type: str,
    journal_entry: JournalEntry,
) -> tuple[Optional[DynamicTypeProfile], Optional[str]]:
    """
    ジャーナルに基づいてプロフィールを詳細化・更新する

    Args:
        user_id: ユーザーID
        base_type: 基本性格タイプ
        journal_entry: 新しいジャーナルエントリー

    Returns:
        (UpdatedProfile, ErrorMessage)
    """
    client = get_gemini_client()
    if client is None:
        return None, "APIキーが設定されていません"

    # 現在の動的プロフィールを取得
    current_profile = get_dynamic_profile(user_id)
    
    # プロフィールの初期化（まだ存在しない場合）
    if current_profile is None:
        current_description = "まだ十分なデータがありません。"
        current_strengths = []
        current_challenges = []
    else:
        current_description = current_profile.refined_description
        current_strengths = current_profile.validated_strengths
        current_challenges = current_profile.observed_challenges

    prompt = f"""あなたは性格分析の専門家です。
ユーザーの基本性格タイプは「{base_type}」です。
これまでの観察（プロフィール）と、新しい日記のエビデンスに基づいて、
このユーザーの「個人化された性格プロフィール」を更新してください。

【現在のプロフィール】
- 詳細説明: {current_description}
- 確認された強み: {', '.join(current_strengths) if current_strengths else 'なし'}
- 観察された課題: {', '.join(current_challenges) if current_challenges else 'なし'}

【新しい日記】
日付: {journal_entry.date.strftime('%Y/%m/%d')}
内容: {journal_entry.content}

【指示】
1. この日記が、ユーザーの性格（強み・課題・特徴）について何を明らかにしているか分析してください。
2. 「{base_type}」の一般的な特徴と照らし合わせ、このユーザー独自のニュアンスを捉えてください。
3. 以前の説明を維持しつつ、新しい発見を統合して説明を洗練させてください。
4. 強みや課題リストも必要に応じて更新・追加してください。
5. 【重要】日記の内容から、4つの指標（EI, SN, TF, JP）に対する「現在の実際の傾向」を0.0〜1.0の数値で推定してください。
   - 0.0に近いほど左側（E, S, T, J）、1.0に近いほど右側（I, N, F, P）の性質が強く出ています。
   - 0.5は中立です。

【回答形式】
JSON形式で返答してください。
```json
{{
    "refined_description": "更新された詳細説明（300-400文字）。三人称（このユーザーは...）で記述。",
    "validated_strengths": ["リスト（最大5-7個）"],
    "observed_challenges": ["リスト（最大5-7個）"],
    "estimated_axis_scores": {{
        "EI": 0.3,
        "SN": 0.7,
        "TF": 0.4,
        "JP": 0.6
    }}
}}
```
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        
        # Parse JSON
        import json
        import re
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.text
            
        data = json.loads(json_str)
        
        new_profile = DynamicTypeProfile(
            user_id=user_id,
            base_type=base_type,
            refined_description=data.get("refined_description", current_description),
            validated_strengths=data.get("validated_strengths", current_strengths),
            observed_challenges=data.get("observed_challenges", current_challenges),
            estimated_axis_scores=data.get("estimated_axis_scores", {}),
            last_updated=get_jst_now()
        )
        
        save_dynamic_profile(new_profile)
        return new_profile, None

    except Exception as e:
        return None, str(e)


def generate_comprehensive_profile(
    user_id: str,
    base_type: str,
    journals: list[JournalEntry],
) -> tuple[Optional[DynamicTypeProfile], Optional[str]]:
    """
    全ジャーナルに基づいて包括的なプロフィールを生成する（一括更新用）

    Args:
        user_id: ユーザーID
        base_type: 基本性格タイプ
        journals: ジャーナルエントリーのリスト

    Returns:
        (NewProfile, ErrorMessage)
    """
    client = get_gemini_client()
    if client is None:
        return None, "APIキーが設定されていません"

    if not journals:
        return None, "分析するジャーナルがありません"

    # ジャーナルをテキストに変換（最新のものから最大20件程度を使用）
    # トークン数を考慮して、内容を結合
    sorted_journals = sorted(journals, key=lambda j: j.date, reverse=True)[:30]
    journals_text = ""
    for journal in sorted_journals:
        date_str = journal.date.strftime("%Y/%m/%d")
        journals_text += f"\n--- {date_str} ---\n{journal.content}\n"

    prompt = f"""あなたは性格分析の専門家です。
ユーザーの基本性格タイプは「{base_type}」です。
以下の過去の日記ログ（最大30件）を分析し、このユーザーの「詳細な性格プロフィール」をゼロから作成してください。

【日記ログ】
{journals_text}

【指示】
1. 基本タイプ「{base_type}」の枠組みを使いつつ、日記から読み取れる**このユーザー独自の**特徴、価値観、行動パターンを深く分析してください。
2. 一般的な{base_type}の説明ではなく、日記のエビデンスに基づいた「生きた」人物像を描写してください。
3. 強みと課題についても、日記の中で具体的に現れているものを抽出してください。
4. 【重要】日記の内容から、4つの指標（EI, SN, TF, JP）に対する「現在の実際の傾向」を0.0〜1.0の数値で推定してください。
   - 0.0に近いほど左側（E, S, T, J）、1.0に近いほど右側（I, N, F, P）の性質が強く出ています。
   - 0.5は中立です。

【回答形式】
JSON形式で返答してください。
```json
{{
    "refined_description": "詳細な人物像説明（400-500文字）。三人称（このユーザーは...）で記述。",
    "validated_strengths": ["日記で確認された具体的な強み（5-7個）"],
    "observed_challenges": ["日記で確認された具体的な課題（5-7個）"],
    "estimated_axis_scores": {{
        "EI": 0.3,
        "SN": 0.7,
        "TF": 0.4,
        "JP": 0.6
    }}
}}
```
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
        )
        
        # Parse JSON
        import json
        import re
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response.text
            
        data = json.loads(json_str)
        
        new_profile = DynamicTypeProfile(
            user_id=user_id,
            base_type=base_type,
            refined_description=data.get("refined_description", ""),
            validated_strengths=data.get("validated_strengths", []),
            observed_challenges=data.get("observed_challenges", []),
            estimated_axis_scores=data.get("estimated_axis_scores", {}),
            last_updated=get_jst_now()
        )
        
        save_dynamic_profile(new_profile)
        return new_profile, None

    except Exception as e:
        return None, str(e)
