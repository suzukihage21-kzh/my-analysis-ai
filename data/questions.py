"""
診断質問データ

30問の性格診断質問を定義します。
各指標（E/I, S/N, T/F, J/P）に対して7〜8問を均等に配分。
"""

from models.data_models import Dimension, Direction, Question

# 30問の診断質問データ
DIAGNOSTIC_QUESTIONS: list[Question] = [
    # ===== E/I（外向/内向）: 8問 =====
    Question(
        id=1,
        text="パーティーや大人数の集まりに参加すると、エネルギーが湧いてくる",
        dimension=Dimension.EI,
        direction=Direction.POSITIVE,  # 高スコア = E
    ),
    Question(
        id=2,
        text="一人で過ごす時間が、自分をリフレッシュさせてくれる",
        dimension=Dimension.EI,
        direction=Direction.NEGATIVE,  # 高スコア = I
    ),
    Question(
        id=3,
        text="初対面の人とでも、すぐに打ち解けて話すことができる",
        dimension=Dimension.EI,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=4,
        text="深い話ができる少数の友人関係を、広い交友関係より好む",
        dimension=Dimension.EI,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=5,
        text="考えをまとめるとき、人と話しながら整理することが多い",
        dimension=Dimension.EI,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=6,
        text="行動する前に、じっくり考える時間が必要だ",
        dimension=Dimension.EI,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=7,
        text="グループでの活動やチームワークを楽しめる",
        dimension=Dimension.EI,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=8,
        text="自分の内面世界や想像の世界に没頭することが多い",
        dimension=Dimension.EI,
        direction=Direction.NEGATIVE,
    ),

    # ===== S/N（感覚/直観）: 7問 =====
    Question(
        id=9,
        text="具体的な事実やデータに基づいて判断することを好む",
        dimension=Dimension.SN,
        direction=Direction.POSITIVE,  # 高スコア = S
    ),
    Question(
        id=10,
        text="将来の可能性やパターンを想像することが得意だ",
        dimension=Dimension.SN,
        direction=Direction.NEGATIVE,  # 高スコア = N
    ),
    Question(
        id=11,
        text="実践的で現実的なアプローチを重視する",
        dimension=Dimension.SN,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=12,
        text="抽象的なアイデアや理論について考えることが好きだ",
        dimension=Dimension.SN,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=13,
        text="詳細を正確に把握することに長けている",
        dimension=Dimension.SN,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=14,
        text="全体像やビジョンを描くことを優先する",
        dimension=Dimension.SN,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=15,
        text="過去の経験や実績を重要な判断材料にする",
        dimension=Dimension.SN,
        direction=Direction.POSITIVE,
    ),

    # ===== T/F（思考/感情）: 8問 =====
    Question(
        id=16,
        text="決定を下すとき、論理的な分析を最も重視する",
        dimension=Dimension.TF,
        direction=Direction.POSITIVE,  # 高スコア = T
    ),
    Question(
        id=17,
        text="他者の感情や価値観を考慮して判断することが多い",
        dimension=Dimension.TF,
        direction=Direction.NEGATIVE,  # 高スコア = F
    ),
    Question(
        id=18,
        text="批判的なフィードバックを、改善の機会として受け止められる",
        dimension=Dimension.TF,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=19,
        text="人間関係のハーモニーを保つことを優先する",
        dimension=Dimension.TF,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=20,
        text="公平で客観的な判断ができると自負している",
        dimension=Dimension.TF,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=21,
        text="共感力が高く、他者の立場に立って考えることができる",
        dimension=Dimension.TF,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=22,
        text="問題解決において、感情より効率を優先する",
        dimension=Dimension.TF,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=23,
        text="人を助けたり励ましたりすることに喜びを感じる",
        dimension=Dimension.TF,
        direction=Direction.NEGATIVE,
    ),

    # ===== J/P（判断/知覚）: 7問 =====
    Question(
        id=24,
        text="計画を立てて、その通りに物事を進めることを好む",
        dimension=Dimension.JP,
        direction=Direction.POSITIVE,  # 高スコア = J
    ),
    Question(
        id=25,
        text="状況に応じて柔軟に対応することが得意だ",
        dimension=Dimension.JP,
        direction=Direction.NEGATIVE,  # 高スコア = P
    ),
    Question(
        id=26,
        text="締め切りより前に、早めに仕事を終わらせたい",
        dimension=Dimension.JP,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=27,
        text="最後の瞬間まで選択肢を残しておきたい",
        dimension=Dimension.JP,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=28,
        text="決断を下すことで、スッキリした気持ちになる",
        dimension=Dimension.JP,
        direction=Direction.POSITIVE,
    ),
    Question(
        id=29,
        text="新しい情報が入れば、計画を変更することに抵抗がない",
        dimension=Dimension.JP,
        direction=Direction.NEGATIVE,
    ),
    Question(
        id=30,
        text="整理整頓された環境で作業することを好む",
        dimension=Dimension.JP,
        direction=Direction.POSITIVE,
    ),
]


def get_questions_by_dimension(dimension: Dimension) -> list[Question]:
    """指定された指標の質問を取得"""
    return [q for q in DIAGNOSTIC_QUESTIONS if q.dimension == dimension]


def get_question_by_id(question_id: int) -> Question | None:
    """IDで質問を取得"""
    for q in DIAGNOSTIC_QUESTIONS:
        if q.id == question_id:
            return q
    return None


def get_total_questions() -> int:
    """総質問数を取得"""
    return len(DIAGNOSTIC_QUESTIONS)
