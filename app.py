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
from ui.styles import inject_custom_css, get_hero_card, get_feature_card


# ページ設定
st.set_page_config(
    page_title="自己分析アプリ",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# グローバルスタイルを注入
inject_custom_css()


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


def render_login_page(auth_manager: AuthManager) -> None:
    """ログイン画面を描画"""
    # ヒーローセクション
    st.markdown(get_hero_card(
        title="自己分析アプリ",
        subtitle="性格診断とジャーナリングで、あなた自身をもっと深く理解しよう",
        icon="🔮"
    ), unsafe_allow_html=True)
    
    # メリットカード
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(get_feature_card(
            icon="📱",
            title="どの端末からでも",
            description="スマホ・PC・タブレット、どこからでもアクセス可能"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(get_feature_card(
            icon="🔒",
            title="安全なデータ保護",
            description="あなたのデータは暗号化され、永続的に保存"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(get_feature_card(
            icon="🤖",
            title="AIパーソナル分析",
            description="あなただけのカスタマイズされたAI分析を提供"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ログインボタン
    auth_url = auth_manager.get_auth_url()
    if auth_url:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            st.link_button(
                "🚀 Googleでログインして始める",
                auth_url,
                type="primary",
                use_container_width=True
            )
    else:
        st.error("⚠️ 認証設定が見つかりません。Secretsを設定してください。")
        st.info("ローカル開発の場合は `.streamlit/secrets.toml` を確認してください。")



def render_sidebar() -> str:
    """サイドバーをレンダリングして選択されたビューを返す"""
    with st.sidebar:
        # ロゴ/タイトル
        st.markdown("""
        <div style="
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔮</div>
            <div style="
                font-size: 1.25rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">自己分析アプリ</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ユーザー情報カード
        if st.session_state.user_info:
            user_name = st.session_state.user_info.get('name', 'ユーザー')
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 0.75rem 1rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            ">
                <div style="
                    width: 36px;
                    height: 36px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1rem;
                ">👤</div>
                <div>
                    <div style="font-size: 0.75rem; color: #718096;">ログイン中</div>
                    <div style="font-size: 0.9rem; color: #e2e8f0; font-weight: 500;">{user_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 ログアウト", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_info = None
                st.rerun()

        st.markdown("---")

        # ナビゲーション
        current_view = st.session_state.current_view
        
        nav_items = [
            ("diagnostic", "🔮", "性格診断"),
            ("journal", "📝", "ジャーナル"),
            ("analysis", "🔍", "分析"),
        ]
        
        for view_id, icon, label in nav_items:
            is_active = current_view == view_id
            btn_label = f"{icon} {label}"
            
            if is_active:
                # アクティブ状態の強調表示
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span>{icon}</span>
                    <span>{label}</span>
                    <span style="margin-left: auto; font-size: 0.75rem;">●</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(btn_label, key=f"nav_{view_id}", use_container_width=True):
                    st.session_state.current_view = view_id
                    st.rerun()

        st.markdown("---")

        # アプリ情報（コンパクト版）
        st.markdown("""
        <div style="
            font-size: 0.8rem;
            color: #718096;
            text-align: center;
            padding: 0.5rem;
        ">
            <div style="margin-bottom: 0.5rem;">💡 機能一覧</div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; justify-content: center;">
                <span style="
                    background: rgba(255,255,255,0.05);
                    padding: 0.25rem 0.5rem;
                    border-radius: 6px;
                    font-size: 0.7rem;
                ">性格診断</span>
                <span style="
                    background: rgba(255,255,255,0.05);
                    padding: 0.25rem 0.5rem;
                    border-radius: 6px;
                    font-size: 0.7rem;
                ">ジャーナル</span>
                <span style="
                    background: rgba(255,255,255,0.05);
                    padding: 0.25rem 0.5rem;
                    border-radius: 6px;
                    font-size: 0.7rem;
                ">AI分析</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
