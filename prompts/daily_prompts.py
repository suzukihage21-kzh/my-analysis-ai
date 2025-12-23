"""
動的プロンプト

性格タイプに応じた日記の問いかけを提供します。
"""

import random
from typing import Optional


# 性格タイプ別のプロンプト
TYPE_PROMPTS: dict[str, list[str]] = {
    # 外向型 (E) 向けプロンプト
    "E": [
        "今日はどんな人と交流しましたか？その会話でどんな発見がありましたか？",
        "今日のコミュニケーションで、特に印象に残ったやり取りは何ですか？",
        "今日、誰かと一緒にいて楽しかった瞬間を思い出してみましょう。",
        "今日、あなたのアイデアを誰かに共有できましたか？反応はどうでしたか？",
    ],
    # 内向型 (I) 向けプロンプト
    "I": [
        "今日、じっくり考えることができた時間はありましたか？何を考えていましたか？",
        "一人で過ごした時間に、どんな気づきがありましたか？",
        "今日の出来事を振り返って、最も印象的だったことは何ですか？",
        "静かな時間の中で、どんなアイデアが浮かびましたか？",
    ],
    # 感覚型 (S) 向けプロンプト
    "S": [
        "今日実際に経験したことの中で、最も学びになったことは何ですか？",
        "今日の具体的な成果や達成したことを書き出してみましょう。",
        "五感で感じた今日の印象的な瞬間は何ですか？",
        "今日取り組んだ作業の詳細を振り返ってみてください。",
    ],
    # 直観型 (N) 向けプロンプト
    "N": [
        "今日の出来事から、将来への可能性やパターンが見えましたか？",
        "今日浮かんだ新しいアイデアや閃きはありましたか？",
        "もし今日を違う方法でやり直せるなら、どうしたいですか？",
        "今日の経験から、より大きなビジョンに繋がる気づきはありましたか？",
    ],
    # 思考型 (T) 向けプロンプト
    "T": [
        "今日の課題解決プロセスを振り返ってみてください。何がうまくいきましたか？",
        "今日直面した問題と、それに対するあなたの分析を書いてみましょう。",
        "今日学んだ最も論理的な洞察は何ですか？",
        "改善できる点があるとすれば、何をどう変えますか？",
    ],
    # 感情型 (F) 向けプロンプト
    "F": [
        "今日の出来事で、どんな感情が湧きましたか？その理由を探ってみましょう。",
        "今日、誰かの役に立てたと感じた瞬間はありましたか？",
        "今日の人間関係で、心に残ったやり取りは何ですか？",
        "今日感謝したいと思った人や出来事はありますか？",
    ],
    # 判断型 (J) 向けプロンプト
    "J": [
        "今日の計画と実際の結果を比較してみてください。どうでしたか？",
        "今日達成できたことと、明日に持ち越すことを整理してみましょう。",
        "今日の時間の使い方で、効果的だった点は何ですか？",
        "今日の決断で、よかったと思えるものはありましたか？",
    ],
    # 知覚型 (P) 向けプロンプト
    "P": [
        "今日、予想外の展開に柔軟に対応できた瞬間はありましたか？",
        "今日探索した新しいことや発見したことは何ですか？",
        "計画にとらわれず、その場で判断したことでうまくいったことは？",
        "今日、オープンマインドでいられた瞬間を思い出してみましょう。",
    ],
}

# デフォルトプロンプト
DEFAULT_PROMPTS: list[str] = [
    "今日一日を振り返って、最も印象に残った出来事は何ですか？",
    "今日の自分を一言で表すと何ですか？その理由は？",
    "今日学んだことや気づいたことがあれば書いてみましょう。",
    "今日の自分に点数をつけるなら何点？その理由は？",
]


def get_daily_prompt(personality_type: Optional[str] = None) -> str:
    """
    性格タイプに応じた日記プロンプトを取得

    Args:
        personality_type: 4文字の性格タイプ（例: "INTJ"）

    Returns:
        str: 日記の問いかけ
    """
    if personality_type is None:
        return random.choice(DEFAULT_PROMPTS)

    # 最も強調すべきタイプを選択（ランダムに1つ）
    available_types = [char for char in personality_type if char in TYPE_PROMPTS]

    if not available_types:
        return random.choice(DEFAULT_PROMPTS)

    selected_type = random.choice(available_types)
    prompts = TYPE_PROMPTS[selected_type]

    return random.choice(prompts)


def get_prompts_for_type(type_char: str) -> list[str]:
    """
    特定のタイプ文字に対する全プロンプトを取得

    Args:
        type_char: 1文字のタイプ（E, I, S, N, T, F, J, P）

    Returns:
        list[str]: プロンプトのリスト
    """
    return TYPE_PROMPTS.get(type_char, DEFAULT_PROMPTS)


def get_balanced_prompt(personality_type: str) -> str:
    """
    タイプのバランスを考慮したプロンプトを取得
    （弱い指標を意識的に刺激する）

    Args:
        personality_type: 4文字の性格タイプ

    Returns:
        str: 日記の問いかけ
    """
    # 反対のタイプのプロンプトをたまに提示する
    opposite_types = {
        "E": "I", "I": "E",
        "S": "N", "N": "S",
        "T": "F", "F": "T",
        "J": "P", "P": "J",
    }

    # 20%の確率で反対タイプのプロンプトを提示
    if random.random() < 0.2:
        selected_type = random.choice(list(personality_type))
        opposite = opposite_types.get(selected_type)
        if opposite and opposite in TYPE_PROMPTS:
            return random.choice(TYPE_PROMPTS[opposite])

    return get_daily_prompt(personality_type)
