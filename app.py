"""
自己分析・内省支援アプリケーション

性格診断とジャーナリングを通じて、自己理解を深めるためのアプリケーションです。
"""

import streamlit as st

from logic.auth_manager import AuthManager
from database.db_manager import init_database
from ui.diagnostic_ui import render_diagnostic_page
from ui.journal_ui import render_journal_page
from ui.analysis_ui import render_analysis_page


# ページ設定
st.set_page_config(
    page_title="自己分析アプリ",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_app() -> None:
    """アプリケーションの初期化"""
    # データベースを初期化
    try:
        init_database()
    except ConnectionError as e:
        st.error(f"⚠️ データベース接続エラー: {e}")
        st.warning("管理者に連絡するか、Secretsの設定（DATABASE_URL）を確認してください。")
        st.info("このエラーが発生している間、データの保存・読み込みはできません。")
        st.stop()  # アプリを停止

    # セッション状態の初期化
    if "user_id" not in st.session_state:
        # デフォルトはゲスト（ログイン前）
        st.session_state.user_id = None
    if "current_view" not in st.session_state:
        st.session_state.current_view = "diagnostic"
    if "user_info" not in st.session_state:
        st.session_state.user_info = None

    # URLパラメータから認証コードを取得 (Callback)
    query_params = st.query_params
    if "code" in query_params:
        auth_manager = AuthManager()
        if auth_manager.is_configured():
            try:
                code = query_params["code"]
                credentials = auth_manager.get_token_from_code(code)
                user_info = auth_manager.get_user_info(credentials)
                
                if user_info:
                    st.session_state.user_info = user_info
                    st.session_state.user_id = user_info.get("email") # EmailをユーザーIDとして使用
                    st.success(f"ログインしました: {user_info.get('name')}")
                    # コード付きURLからクリーンなURLへリダイレクトしたほうが良いが、
                    # Streamlitでは rerun でパラメータが残る場合があるため、一旦このまま
            except Exception as e:
                st.error(f"認証エラー: {e}")
            finally:
                # パラメータをクリア
                st.query_params.clear()


def render_login_page(auth_manager: AuthManager):
    """ログイン画面を描画"""
    st.title("🔐 自己分析アプリにログイン")
    st.markdown("自分だけのデータを安全に管理するために、Googleアカウントでログインしてください。")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        auth_url = auth_manager.get_auth_url()
        if auth_url:
            st.link_button("Googleでログイン", auth_url, type="primary")
        else:
            st.error("認証設定が見つかりません。Secretsを設定してください。")
            st.info("ローカル開発の場合は .streamlit/secrets.toml を確認してください。")

    with col2:
        st.markdown("""
        **ログインするメリット**:
        - 📱 どの端末からでもアクセス可能
        - 🔒 データが消えずに永続化
        - 🤖 あなただけのAI分析モデル
        """)



def render_sidebar() -> str:
    """サイドバーをレンダリングして選択されたビューを返す"""
    with st.sidebar:
        st.title("🔮 自己分析アプリ")
        
        # ユーザー情報表示
        if st.session_state.user_info:
            st.caption(f"Login: {st.session_state.user_info.get('name')}")
            if st.button("ログアウト"):
                st.session_state.user_id = None
                st.session_state.user_info = None
                st.rerun()
        
        st.markdown("---")

        # ナビゲーション
        st.markdown("### 📍 ナビゲーション")

        if st.button("🔮 性格診断", use_container_width=True):
            st.session_state.current_view = "diagnostic"
            st.rerun()

        if st.button("📝 ジャーナル", use_container_width=True):
            st.session_state.current_view = "journal"
            st.rerun()

        if st.button("🔍 分析", use_container_width=True):
            st.session_state.current_view = "analysis"
            st.rerun()

        st.markdown("---")

        # アプリ情報
        st.markdown("### ℹ️ このアプリについて")
        st.markdown("""
        このアプリは、性格診断と日々のジャーナリングを通じて
        自己理解を深めるためのツールです。

        **機能**:
        - 30問の性格診断
        - パーソナライズされたジャーナル
        - 盲点・行動パターンの分析
        """)

        st.markdown("---")

        # 現在のビューを表示
        view_names = {
            "diagnostic": "🔮 性格診断",
            "journal": "📝 ジャーナル",
            "analysis": "🔍 分析",
        }
        current = view_names.get(st.session_state.current_view, "不明")
        st.info(f"現在の画面: {current}")

    return st.session_state.current_view


def main() -> None:
    """メイン関数"""
    # 初期化
    init_app()

    # 認証チェック
    auth_manager = AuthManager()
    
    # 認証が設定されていない場合（開発ローカル等）はスキップしてデフォルトユーザー
    if not auth_manager.is_configured():
        if not st.session_state.user_id:
            st.session_state.user_id = "default_user"
            st.warning("⚠️ Google認証が設定されていません。ゲストモードで実行中（データはローカル/共有DBに保存されます）")
    
    # 認証設定があるが、ログインしていない場合
    elif not st.session_state.user_id:
        render_login_page(auth_manager)
        return  # ログイン画面のみを表示して終了

    # --- 以下、ログイン済みまたはゲストモードの処理 ---

    # サイドバーを描画
    current_view = render_sidebar()

    # メインコンテンツを描画
    if current_view == "diagnostic":
        render_diagnostic_page()
    elif current_view == "journal":
        render_journal_page()
    elif current_view == "analysis":
        render_analysis_page()
    else:
        st.error("不明な画面です")


if __name__ == "__main__":
    main()
