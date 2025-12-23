"""
診断ロジック

ユーザーの回答から性格タイプと各指標の強度を計算します。
"""

from models.data_models import (
    Dimension,
    DimensionScore,
    Direction,
    PersonalityResult,
    UserResponse,
)
from data.questions import DIAGNOSTIC_QUESTIONS, get_question_by_id


def calculate_dimension_score(
    responses: list[UserResponse],
    dimension: Dimension,
) -> DimensionScore:
    """
    特定の指標のスコアを計算する

    Args:
        responses: ユーザーの回答リスト
        dimension: 計算対象の指標

    Returns:
        DimensionScore: 指標のスコア詳細
    """
    # 指標に対応するタイプ名
    type_mapping: dict[Dimension, tuple[str, str]] = {
        Dimension.EI: ("E", "I"),
        Dimension.SN: ("S", "N"),
        Dimension.TF: ("T", "F"),
        Dimension.JP: ("J", "P"),
    }

    first_type, second_type = type_mapping[dimension]

    # この指標の質問に対する回答を抽出
    dimension_questions = [q for q in DIAGNOSTIC_QUESTIONS if q.dimension == dimension]
    question_ids = {q.id for q in dimension_questions}

    dimension_responses = [r for r in responses if r.question_id in question_ids]

    # スコア計算
    first_score = 0.0
    second_score = 0.0

    for response in dimension_responses:
        question = get_question_by_id(response.question_id)
        if question is None:
            continue

        # スコアを0-4の範囲に正規化（1-5 → 0-4）
        normalized_score = response.score - 1

        if question.direction == Direction.POSITIVE:
            # 正方向: 高スコアが第1タイプ
            first_score += normalized_score
            second_score += 4 - normalized_score
        else:
            # 逆方向: 高スコアが第2タイプ
            second_score += normalized_score
            first_score += 4 - normalized_score

    # 強度の計算（%）
    total_score = first_score + second_score
    if total_score > 0:
        strength_percent = abs(first_score - second_score) / total_score * 100
    else:
        strength_percent = 0.0

    # 優勢なタイプの決定
    dominant_type = first_type if first_score >= second_score else second_type

    return DimensionScore(
        dimension=dimension,
        first_type=first_type,
        second_type=second_type,
        first_score=first_score,
        second_score=second_score,
        dominant_type=dominant_type,
        strength_percent=round(strength_percent, 1),
    )


def calculate_personality_type(
    responses: list[UserResponse],
    user_id: str = "default_user",
) -> PersonalityResult:
    """
    全回答から性格タイプを計算する

    Args:
        responses: ユーザーの全回答リスト
        user_id: ユーザーID

    Returns:
        PersonalityResult: 性格診断結果
    """
    # 各指標のスコアを計算
    dimension_scores: list[DimensionScore] = []
    personality_type_chars: list[str] = []

    for dimension in [Dimension.EI, Dimension.SN, Dimension.TF, Dimension.JP]:
        score = calculate_dimension_score(responses, dimension)
        dimension_scores.append(score)
        personality_type_chars.append(score.dominant_type)

    # 4文字タイプを構築
    personality_type = "".join(personality_type_chars)

    return PersonalityResult(
        user_id=user_id,
        personality_type=personality_type,
        dimension_scores=dimension_scores,
    )


def get_dimension_explanation(dimension: Dimension, dominant_type: str) -> str:
    """
    指標と優勢タイプに基づく説明を取得

    Args:
        dimension: 指標
        dominant_type: 優勢なタイプ

    Returns:
        str: タイプの説明
    """
    explanations: dict[str, str] = {
        "E": "外向型：人との交流からエネルギーを得ます。社交的で、考えを話しながら整理する傾向があります。",
        "I": "内向型：一人の時間からエネルギーを得ます。深く考えてから行動し、少数の深い関係を好みます。",
        "S": "感覚型：具体的な事実や詳細を重視します。現実的で実践的なアプローチを好みます。",
        "N": "直観型：可能性やパターンを重視します。抽象的なアイデアや将来のビジョンに関心があります。",
        "T": "思考型：論理と客観性を重視して判断します。公平さと効率を大切にします。",
        "F": "感情型：価値観と人間関係を重視して判断します。調和と共感を大切にします。",
        "J": "判断型：計画と秩序を好みます。決断を下すことで安心感を得ます。",
        "P": "知覚型：柔軟性と適応力を好みます。選択肢を残しておくことを好みます。",
    }

    return explanations.get(dominant_type, "説明がありません")
