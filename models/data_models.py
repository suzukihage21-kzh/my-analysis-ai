"""
データモデル定義

Pydanticを使用した型安全なデータ構造を定義します。
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Dimension(str, Enum):
    """性格診断の4つの指標"""
    EI = "EI"  # 外向(E) vs 内向(I)
    SN = "SN"  # 感覚(S) vs 直観(N)
    TF = "TF"  # 思考(T) vs 感情(F)
    JP = "JP"  # 判断(J) vs 知覚(P)


class Direction(str, Enum):
    """質問のスコア方向"""
    POSITIVE = "positive"  # 高いスコアが第1タイプ(E, S, T, J)を示す
    NEGATIVE = "negative"  # 高いスコアが第2タイプ(I, N, F, P)を示す


class Question(BaseModel):
    """診断質問"""
    id: int = Field(..., description="質問ID")
    text: str = Field(..., description="質問文")
    dimension: Dimension = Field(..., description="測定する指標")
    direction: Direction = Field(..., description="スコアの方向")


class UserResponse(BaseModel):
    """ユーザーの回答"""
    user_id: str = Field(..., description="ユーザーID")
    question_id: int = Field(..., description="質問ID")
    score: int = Field(..., ge=1, le=5, description="回答スコア（1-5）")
    timestamp: datetime = Field(default_factory=datetime.now, description="回答日時")


class DimensionScore(BaseModel):
    """各指標のスコア詳細"""
    dimension: Dimension = Field(..., description="指標")
    first_type: str = Field(..., description="第1タイプ（E, S, T, J）")
    second_type: str = Field(..., description="第2タイプ（I, N, F, P）")
    first_score: float = Field(..., description="第1タイプのスコア")
    second_score: float = Field(..., description="第2タイプのスコア")
    dominant_type: str = Field(..., description="優勢なタイプ")
    strength_percent: float = Field(..., ge=0, le=100, description="強度（%）")


class PersonalityResult(BaseModel):
    """性格診断結果"""
    user_id: str = Field(..., description="ユーザーID")
    personality_type: str = Field(..., min_length=4, max_length=4, description="4文字タイプ（例: INTJ）")
    dimension_scores: list[DimensionScore] = Field(..., description="各指標の詳細スコア")
    diagnosed_at: datetime = Field(default_factory=datetime.now, description="診断日時")

    @property
    def type_description(self) -> str:
        """タイプの簡易説明を返す"""
        type_names: dict[str, str] = {
            "INTJ": "建築家",
            "INTP": "論理学者",
            "ENTJ": "指揮官",
            "ENTP": "討論者",
            "INFJ": "提唱者",
            "INFP": "仲介者",
            "ENFJ": "主人公",
            "ENFP": "広報運動家",
            "ISTJ": "管理者",
            "ISFJ": "擁護者",
            "ESTJ": "幹部",
            "ESFJ": "領事官",
            "ISTP": "巨匠",
            "ISFP": "冒険家",
            "ESTP": "起業家",
            "ESFP": "エンターテイナー",
        }
        return type_names.get(self.personality_type, "不明")


class JournalEntry(BaseModel):
    """ジャーナルエントリー"""
    id: Optional[int] = Field(None, description="エントリーID")
    user_id: str = Field(..., description="ユーザーID")
    date: datetime = Field(default_factory=datetime.now, description="日付")
    content: str = Field(..., min_length=1, description="日記内容")
    tags: list[str] = Field(default_factory=list, description="タグリスト")
    emotion_score: int = Field(..., ge=1, le=10, description="感情スコア（1-10）")
    personality_type: Optional[str] = Field(None, description="作成時の性格タイプ")


class BlindSpotInsight(BaseModel):
    """盲点インサイト"""
    category: str = Field(..., description="盲点のカテゴリ")
    description: str = Field(..., description="盲点の説明")
    evidence: list[str] = Field(default_factory=list, description="日記からの根拠")
    recommendation: str = Field(..., description="改善のための提案")
    severity: str = Field(..., description="深刻度（low/medium/high）")


class DynamicTypeProfile(BaseModel):
    """ダイナミック・タイプ・プロファイル"""
    user_id: str = Field(..., description="ユーザーID")
    base_type: str = Field(..., description="基本性格タイプ")
    refined_description: str = Field(..., description="AIにより詳細化された説明")
    validated_strengths: list[str] = Field(default_factory=list, description="日記で確認された強み")
    observed_challenges: list[str] = Field(default_factory=list, description="日記で観察された課題")
    estimated_axis_scores: dict[str, float] = Field(default_factory=dict, description="AI推定の指標スコア (0.0-1.0)")
    last_updated: datetime = Field(default_factory=datetime.now, description="最終更新日時")
