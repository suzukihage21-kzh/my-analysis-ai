"""
分析・盲点検知ロジック

性格タイプと日記の内容を照合し、盲点を検出するスケルトン実装。
"""

from models.data_models import BlindSpotInsight, JournalEntry, PersonalityResult


# 性格タイプごとの強みキーワード
TYPE_STRENGTHS: dict[str, list[str]] = {
    "E": ["コミュニケーション", "チームワーク", "社交", "積極的", "発信"],
    "I": ["集中力", "深い思考", "独立性", "慎重", "観察力"],
    "S": ["現実的", "詳細", "実践的", "経験", "安定"],
    "N": ["創造", "ビジョン", "可能性", "革新", "直感"],
    "T": ["論理", "分析", "効率", "客観", "問題解決"],
    "F": ["共感", "調和", "人間関係", "価値観", "思いやり"],
    "J": ["計画", "組織", "締切", "決断", "秩序"],
    "P": ["柔軟", "適応", "即興", "探索", "オープン"],
}

# 性格タイプごとの苦手・ストレスパターン
TYPE_VULNERABILITIES: dict[str, list[str]] = {
    "E": ["疲れた", "一人になりたい", "静かにしたい", "うるさい"],
    "I": ["もっと話したい", "孤独", "存在感がない", "発言できなかった"],
    "S": ["見通しが立たない", "変化についていけない", "抽象的すぎる"],
    "N": ["細かい", "退屈", "ルーティン", "現実的すぎる"],
    "T": ["感情的になった", "理解されない", "非論理的", "感情に振り回された"],
    "F": ["冷たい", "合理的すぎる", "批判された", "人間関係が辛い"],
    "J": ["予定が崩れた", "計画通りにいかない", "不確実", "決められない"],
    "P": ["締め切り", "プレッシャー", "追われている", "決めなければならない"],
}

# 盲点パターン（タイプと矛盾する記述）
BLIND_SPOT_PATTERNS: dict[str, dict[str, str]] = {
    "P_planning_stress": {
        "type": "P",
        "keywords": ["計画通りにいかない", "予定が崩れた", "イライラ"],
        "insight": "柔軟性が強みですが、無意識に計画への期待を持っているようです。",
        "recommendation": "「計画」ではなく「方向性」を設定することで、自分らしい柔軟さを活かせるかもしれません。",
    },
    "J_spontaneous_desire": {
        "type": "J",
        "keywords": ["もっと自由に", "縛られている", "窮屈"],
        "insight": "秩序を好む一方で、自発性への欲求も持っているようです。",
        "recommendation": "計画の中に「予定外の余白時間」を意図的に設けてみましょう。",
    },
    "T_emotional_struggle": {
        "type": "T",
        "keywords": ["感情的になった", "気持ちを抑えられなかった", "怒り"],
        "insight": "論理的であることを重視していますが、感情も大切な情報源です。",
        "recommendation": "感情を「データ」として観察することで、自分をより深く理解できます。",
    },
    "F_logic_frustration": {
        "type": "F",
        "keywords": ["論理的に考えられない", "合理的になれない", "効率が悪い"],
        "insight": "共感を大切にしながらも、論理的であることへの憧れがありそうです。",
        "recommendation": "「人を助けるための論理」という視点で、分析力を活かしてみましょう。",
    },
    "E_social_exhaustion": {
        "type": "E",
        "keywords": ["人疲れ", "一人になりたい", "静かにしたい"],
        "insight": "社交的でも、内省の時間は必要です。",
        "recommendation": "「充電のための一人時間」を罪悪感なく取り入れましょう。",
    },
    "I_connection_desire": {
        "type": "I",
        "keywords": ["もっと話したかった", "繋がりたい", "孤独"],
        "insight": "内向的でも、人との繋がりを求めるのは自然なことです。",
        "recommendation": "少人数での深い対話の機会を意識的に作ってみましょう。",
    },
}


def detect_blind_spots(
    personality: PersonalityResult,
    journals: list[JournalEntry],
) -> list[BlindSpotInsight]:
    """
    性格タイプと日記から盲点を検出する

    Args:
        personality: 性格診断結果
        journals: ジャーナルエントリーリスト

    Returns:
        list[BlindSpotInsight]: 検出された盲点のリスト
    """
    insights: list[BlindSpotInsight] = []

    if not journals:
        return insights

    # 全日記の内容を結合
    all_content = " ".join([j.content for j in journals])

    # 各盲点パターンをチェック
    for pattern_id, pattern in BLIND_SPOT_PATTERNS.items():
        pattern_type = pattern["type"]

        # このパターンが適用されるタイプかチェック
        if pattern_type not in personality.personality_type:
            continue

        # キーワードマッチング
        keywords: list[str] = pattern["keywords"]  # type: ignore
        matched_keywords = [kw for kw in keywords if kw in all_content]

        if matched_keywords:
            # 関連する日記エントリーを抽出
            evidence = []
            for journal in journals:
                for kw in matched_keywords:
                    if kw in journal.content:
                        # 日記の抜粋（最初の50文字）
                        excerpt = journal.content[:50] + "..." if len(journal.content) > 50 else journal.content
                        evidence.append(f"[{journal.date.strftime('%Y-%m-%d')}] {excerpt}")
                        break

            insight = BlindSpotInsight(
                category=f"{pattern_type}タイプの盲点",
                description=pattern["insight"],  # type: ignore
                evidence=evidence[:3],  # 最大3件
                recommendation=pattern["recommendation"],  # type: ignore
                severity="medium" if len(matched_keywords) >= 2 else "low",
            )
            insights.append(insight)

    return insights


def get_type_strengths(personality_type: str) -> list[str]:
    """
    性格タイプの強みを取得

    Args:
        personality_type: 4文字の性格タイプ

    Returns:
        list[str]: 強みのリスト
    """
    strengths: list[str] = []
    for char in personality_type:
        if char in TYPE_STRENGTHS:
            strengths.extend(TYPE_STRENGTHS[char])
    return strengths


def get_potential_challenges(personality_type: str) -> list[str]:
    """
    性格タイプの潜在的な課題を取得

    Args:
        personality_type: 4文字の性格タイプ

    Returns:
        list[str]: 課題キーワードのリスト
    """
    challenges: list[str] = []
    for char in personality_type:
        if char in TYPE_VULNERABILITIES:
            challenges.extend(TYPE_VULNERABILITIES[char])
    return challenges
