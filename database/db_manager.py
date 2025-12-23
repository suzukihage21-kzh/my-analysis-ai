"""
データベース管理

SQLiteを使用した永続化処理を提供します。
"""

import os
import streamlit as st
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

from models.data_models import (
    DimensionScore,
    JournalEntry,
    PersonalityResult,
    Dimension,
    DynamicTypeProfile,
)


# データベースファイルのパス (SQLite用)
DB_PATH = Path(__file__).parent.parent / "self_analysis.db"


def _get_db_url() -> Optional[str]:
    """
    データベースURLを取得 (PostgreSQL)
    Secrets または 環境変数から取得
    """
    # 1. Streamlit Secrets
    if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]
    
    # 2. Environment Variable
    return os.getenv("DATABASE_URL")


def is_cloud_environment() -> bool:
    """Streamlit Cloud環境かどうかを判定"""
    # Streamlit CloudではSTREAMLIT環境変数またはSecretsが存在
    return (
        os.getenv("STREAMLIT_SHARING_MODE") is not None or
        os.getenv("STREAMLIT_RUNTIME_ENV") is not None or
        (hasattr(st, "secrets") and len(st.secrets) > 0)
    )


def get_db_type() -> str:
    """現在使用中のデータベースタイプを返す"""
    db_url = _get_db_url()
    if db_url and psycopg2:
        return "PostgreSQL"
    return "SQLite (Local)"


def get_connection():
    """データベース接続を取得 (Dual DB support with safeguards)"""
    db_url = _get_db_url()
    
    if db_url and psycopg2:
        # PostgreSQL (Cloud)
        try:
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            if is_cloud_environment():
                # クラウド環境ではフォールバックせずエラー
                raise ConnectionError(
                    f"PostgreSQLへの接続に失敗しました。データが永続化されません。: {e}"
                )
            else:
                # ローカル開発ではフォールバックを許可
                print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
    
    # クラウド環境でDB URLがない場合はエラー
    if is_cloud_environment() and not db_url:
        raise ConnectionError(
            "Cloud環境でDATABASE_URLが設定されていません。Secretsを確認してください。"
        )

    # SQLite (Local only)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _execute(cursor, query: str, params: tuple = ()) -> None:
    """
    クエリ実行ラッパー
    SQLite (?) と PostgreSQL (%s) のプレースホルダの違いを吸収
    """
    # PostgreSQL接続判定 (psycopg2のカーソルかどうか)
    is_postgres = hasattr(cursor, "query") 
    
    if is_postgres:
        # SQLite形式(?) を Postgres形式(%s) に変換
        query = query.replace("?", "%s")
    
    cursor.execute(query, params)


def _execute_and_get_id(conn, cursor, query: str, params: tuple = ()) -> int:
    """
    INSERT実行後にIDを取得するラッパー
    """
    is_postgres = hasattr(cursor, "query")
    
    if is_postgres:
        # SQLite形式(?) を Postgres形式(%s) に変換
        query = query.replace("?", "%s")
        # RETURNING id を追加 (ただし既に含まれていない場合)
        if "RETURNING" not in query.upper():
            query += " RETURNING id"
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row["id"] if row else 0
    else:
        # SQLite
        cursor.execute(query, params)
        return cursor.lastrowid if cursor.lastrowid else 0



def init_database() -> None:
    """データベースとテーブルを初期化"""
    conn = get_connection()
    cursor = conn.cursor()

    # 性格診断結果テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            personality_type TEXT NOT NULL,
            dimension_scores TEXT NOT NULL,
            diagnosed_at TIMESTAMP NOT NULL
        )
    """)

    # ジャーナルエントリーテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TIMESTAMP NOT NULL,
            content TEXT NOT NULL,
            tags TEXT NOT NULL,
            emotion_score INTEGER NOT NULL,
            personality_type TEXT
        )
    """)

    # AI分析結果テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            behavior_patterns TEXT NOT NULL,
            thinking_patterns TEXT NOT NULL,
            emotional_triggers TEXT NOT NULL,
            values_and_beliefs TEXT NOT NULL,
            strengths TEXT NOT NULL,
            growth_areas TEXT NOT NULL,
            actionable_advice TEXT NOT NULL,
            overall_summary TEXT NOT NULL,
            analyzed_at TIMESTAMP NOT NULL
        )
    """)

    # ダイナミック・タイプ・プロファイルテーブル
    if _get_db_url():
        # PostgreSQL
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_profiles (
                user_id TEXT PRIMARY KEY,
                base_type TEXT NOT NULL,
                refined_description TEXT NOT NULL,
                validated_strengths TEXT NOT NULL,
                observed_challenges TEXT NOT NULL,
                estimated_axis_scores TEXT,
                last_updated TIMESTAMP NOT NULL
            )
        """)
    else:
        # SQLite
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_profiles (
                user_id TEXT PRIMARY KEY,
                base_type TEXT NOT NULL,
                refined_description TEXT NOT NULL,
                validated_strengths TEXT NOT NULL,
                observed_challenges TEXT NOT NULL,
                estimated_axis_scores TEXT,
                last_updated TIMESTAMP NOT NULL
            )
        """)

    conn.commit()
    conn.close()


def save_personality_result(result: PersonalityResult) -> int:
    """
    性格診断結果を保存

    Args:
        result: 診断結果

    Returns:
        int: 保存されたレコードのID
    """
    conn = get_connection()
    cursor = conn.cursor()

    # DimensionScoreをJSON文字列に変換
    dimension_scores_json = json.dumps(
        [
            {
                "dimension": score.dimension.value,
                "first_type": score.first_type,
                "second_type": score.second_type,
                "first_score": score.first_score,
                "second_score": score.second_score,
                "dominant_type": score.dominant_type,
                "strength_percent": score.strength_percent,
            }
            for score in result.dimension_scores
        ],
        ensure_ascii=False,
    )

    query = """
        INSERT INTO personality_results (user_id, personality_type, dimension_scores, diagnosed_at)
        VALUES (?, ?, ?, ?)
        """
    
    inserted_id = _execute_and_get_id(
        conn, cursor, query,
        (
            result.user_id,
            result.personality_type,
            dimension_scores_json,
            result.diagnosed_at.isoformat(),
        )
    )

    conn.commit()
    conn.close()

    return inserted_id


def get_latest_personality(user_id: str) -> Optional[PersonalityResult]:
    """
    最新の性格診断結果を取得

    Args:
        user_id: ユーザーID

    Returns:
        Optional[PersonalityResult]: 診断結果（存在しない場合はNone）
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        SELECT * FROM personality_results
        WHERE user_id = ?
        ORDER BY diagnosed_at DESC
        LIMIT 1
        """,
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    # JSON文字列からDimensionScoreを復元
    dimension_scores_data = json.loads(row["dimension_scores"])
    dimension_scores = [
        DimensionScore(
            dimension=Dimension(score["dimension"]),
            first_type=score["first_type"],
            second_type=score["second_type"],
            first_score=score["first_score"],
            second_score=score["second_score"],
            dominant_type=score["dominant_type"],
            strength_percent=score["strength_percent"],
        )
        for score in dimension_scores_data
    ]

    return PersonalityResult(
        user_id=row["user_id"],
        personality_type=row["personality_type"],
        dimension_scores=dimension_scores,
        diagnosed_at=datetime.fromisoformat(row["diagnosed_at"]),
    )


def save_journal_entry(entry: JournalEntry) -> int:
    """
    ジャーナルエントリーを保存

    Args:
        entry: ジャーナルエントリー

    Returns:
        int: 保存されたレコードのID
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO journal_entries (user_id, date, content, tags, emotion_score, personality_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
    
    inserted_id = _execute_and_get_id(
        conn, cursor, query,
        (
            entry.user_id,
            entry.date.isoformat(),
            entry.content,
            json.dumps(entry.tags, ensure_ascii=False),
            entry.emotion_score,
            entry.personality_type,
        )
    )

    conn.commit()
    conn.close()

    return inserted_id


def get_journal_entries(
    user_id: str,
    limit: int = 50,
) -> list[JournalEntry]:
    """
    ジャーナルエントリーを取得

    Args:
        user_id: ユーザーID
        limit: 取得件数上限

    Returns:
        list[JournalEntry]: ジャーナルエントリーのリスト
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        SELECT * FROM journal_entries
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        entries.append(
            JournalEntry(
                id=row["id"],
                user_id=row["user_id"],
                date=datetime.fromisoformat(row["date"]),
                content=row["content"],
                tags=json.loads(row["tags"]),
                emotion_score=row["emotion_score"],
                personality_type=row["personality_type"],
            )
        )

    return entries


def get_all_personality_results(user_id: str) -> list[PersonalityResult]:
    """
    全ての性格診断結果を取得

    Args:
        user_id: ユーザーID

    Returns:
        list[PersonalityResult]: 診断結果のリスト
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        SELECT * FROM personality_results
        WHERE user_id = ?
        ORDER BY diagnosed_at DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        dimension_scores_data = json.loads(row["dimension_scores"])
        dimension_scores = [
            DimensionScore(
                dimension=Dimension(score["dimension"]),
                first_type=score["first_type"],
                second_type=score["second_type"],
                first_score=score["first_score"],
                second_score=score["second_score"],
                dominant_type=score["dominant_type"],
                strength_percent=score["strength_percent"],
            )
            for score in dimension_scores_data
        ]

        results.append(
            PersonalityResult(
                user_id=row["user_id"],
                personality_type=row["personality_type"],
                dimension_scores=dimension_scores,
                diagnosed_at=datetime.fromisoformat(row["diagnosed_at"]),
            )
        )

    return results


def delete_journal_entry(entry_id: int) -> bool:
    """
    ジャーナルエントリーを削除

    Args:
        entry_id: エントリーID

    Returns:
        bool: 削除成功時はTrue
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        _execute(cursor, "DELETE FROM journal_entries WHERE id = ?", (entry_id,))
        conn.commit()
        deleted = True # Rowcount logic differs, assuming successful exec means true for now
    except Exception:
        deleted = False
    finally:
        conn.close()

    return deleted


def update_journal_entry(entry: JournalEntry) -> bool:
    """
    ジャーナルエントリーを更新
    
    Args:
        entry: 更新するジャーナルエントリー（ID必須）
        
    Returns:
        bool: 更新成功時はTrue
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE journal_entries 
        SET content = ?, tags = ?, emotion_score = ?
        WHERE id = ?
    """
    
    try:
        _execute(
            cursor, 
            query, 
            (
                entry.content,
                json.dumps(entry.tags, ensure_ascii=False),
                entry.emotion_score,
                entry.id
            )
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Update error: {e}")
        success = False
    finally:
        conn.close()
        
    return success


def get_all_tags(user_id: str) -> list[str]:
    """
    使用されている全てのタグを取得

    Args:
        user_id: ユーザーID

    Returns:
        list[str]: ユニークなタグのリスト（アルファベット順）
    """
    entries = get_journal_entries(user_id, limit=1000)
    all_tags = set()
    
    for entry in entries:
        for tag in entry.tags:
            if tag:
                all_tags.add(tag)
    
    return sorted(list(all_tags))


def save_ai_analysis_result(
    user_id: str,
    result_data: dict,
) -> int:
    """
    AI分析結果を保存

    Args:
        user_id: ユーザーID
        result_data: 分析結果の辞書

    Returns:
        int: 保存されたレコードのID
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO ai_analysis_results (
            user_id, behavior_patterns, thinking_patterns, emotional_triggers,
            values_and_beliefs, strengths, growth_areas, actionable_advice,
            overall_summary, analyzed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    inserted_id = _execute_and_get_id(conn, cursor, query, (
            user_id,
            json.dumps(result_data.get("behavior_patterns", []), ensure_ascii=False),
            json.dumps(result_data.get("thinking_patterns", []), ensure_ascii=False),
            json.dumps(result_data.get("emotional_triggers", []), ensure_ascii=False),
            json.dumps(result_data.get("values_and_beliefs", []), ensure_ascii=False),
            json.dumps(result_data.get("strengths", []), ensure_ascii=False),
            json.dumps(result_data.get("growth_areas", []), ensure_ascii=False),
            json.dumps(result_data.get("actionable_advice", []), ensure_ascii=False),
            result_data.get("overall_summary", ""),
            result_data.get("analyzed_at", datetime.now()).isoformat(),
    ))

    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return inserted_id if inserted_id else 0


def get_latest_ai_analysis(user_id: str) -> dict | None:
    """
    最新のAI分析結果を取得

    Args:
        user_id: ユーザーID

    Returns:
        dict | None: 分析結果（存在しない場合はNone）
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        SELECT * FROM ai_analysis_results
        WHERE user_id = ?
        ORDER BY analyzed_at DESC
        LIMIT 1
        """,
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "behavior_patterns": json.loads(row["behavior_patterns"]),
        "thinking_patterns": json.loads(row["thinking_patterns"]),
        "emotional_triggers": json.loads(row["emotional_triggers"]),
        "values_and_beliefs": json.loads(row["values_and_beliefs"]),
        "strengths": json.loads(row["strengths"]),
        "growth_areas": json.loads(row["growth_areas"]),
        "actionable_advice": json.loads(row["actionable_advice"]),
        "overall_summary": row["overall_summary"],
        "analyzed_at": datetime.fromisoformat(row["analyzed_at"]),
    }


def save_dynamic_profile(profile: DynamicTypeProfile) -> None:
    """
    ダイナミック・タイプ・プロファイルを保存（Upsert）

    Args:
        profile: ダイナミック・タイプ・プロファイル
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        INSERT INTO dynamic_profiles (
            user_id, base_type, refined_description, 
            validated_strengths, observed_challenges, estimated_axis_scores, last_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            base_type=excluded.base_type,
            refined_description=excluded.refined_description,
            validated_strengths=excluded.validated_strengths,
            observed_challenges=excluded.observed_challenges,
            estimated_axis_scores=excluded.estimated_axis_scores,
            last_updated=excluded.last_updated
        """,
        (
            profile.user_id,
            profile.base_type,
            profile.refined_description,
            json.dumps(profile.validated_strengths, ensure_ascii=False),
            json.dumps(profile.observed_challenges, ensure_ascii=False),
            json.dumps(profile.estimated_axis_scores, ensure_ascii=False),
            profile.last_updated.isoformat(),
        )
    )

    conn.commit()
    conn.close()


def get_dynamic_profile(user_id: str) -> Optional[DynamicTypeProfile]:
    """
    ダイナミック・タイプ・プロファイルを取得

    Args:
        user_id: ユーザーID

    Returns:
        Optional[DynamicTypeProfile]: プロファイル（存在しない場合はNone）
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        "SELECT * FROM dynamic_profiles WHERE user_id = ?",
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    estimated_axis_scores = {}
    if "estimated_axis_scores" in row.keys() and row["estimated_axis_scores"]:
        estimated_axis_scores = json.loads(row["estimated_axis_scores"])

    return DynamicTypeProfile(
        user_id=row["user_id"],
        base_type=row["base_type"],
        refined_description=row["refined_description"],
        validated_strengths=json.loads(row["validated_strengths"]),
        observed_challenges=json.loads(row["observed_challenges"]),
        estimated_axis_scores=estimated_axis_scores,
        last_updated=datetime.fromisoformat(row["last_updated"]),
    )


def get_all_ai_analyses(user_id: str, limit: int = 10) -> list[dict]:
    """
    AI分析結果の履歴を取得

    Args:
        user_id: ユーザーID
        limit: 取得件数の上限

    Returns:
        list[dict]: 分析結果のリスト
    """
    conn = get_connection()
    cursor = conn.cursor()

    _execute(
        cursor,
        """
        SELECT * FROM ai_analysis_results
        WHERE user_id = ?
        ORDER BY analyzed_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "behavior_patterns": json.loads(row["behavior_patterns"]),
            "thinking_patterns": json.loads(row["thinking_patterns"]),
            "emotional_triggers": json.loads(row["emotional_triggers"]),
            "values_and_beliefs": json.loads(row["values_and_beliefs"]),
            "strengths": json.loads(row["strengths"]),
            "growth_areas": json.loads(row["growth_areas"]),
            "actionable_advice": json.loads(row["actionable_advice"]),
            "overall_summary": row["overall_summary"],
            "analyzed_at": datetime.fromisoformat(row["analyzed_at"]),
        })

    return results

