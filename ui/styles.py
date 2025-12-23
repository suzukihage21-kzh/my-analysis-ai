"""
グローバルUIスタイル定義

モダンでプレミアムなデザインを実現するためのCSSスタイルを提供します。
"""

import streamlit as st


def inject_custom_css() -> None:
    """グローバルカスタムCSSを注入"""
    st.markdown("""
    <style>
    /* ========================================
       カラーパレット（CSS変数）
    ======================================== */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        
        --bg-dark: #0e1117;
        --bg-card: rgba(26, 27, 38, 0.8);
        --bg-glass: rgba(255, 255, 255, 0.05);
        
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --text-muted: #718096;
        
        --border-color: rgba(255, 255, 255, 0.1);
        --shadow-color: rgba(0, 0, 0, 0.3);
    }
    
    /* ========================================
       グローバルスタイル
    ======================================== */
    
    /* メインコンテナの余白調整 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* タイトルスタイル */
    h1 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    h3 {
        color: #cbd5e0 !important;
        font-weight: 500 !important;
    }
    
    /* ========================================
       サイドバースタイル
    ======================================== */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1b26 0%, #0e1117 100%) !important;
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--primary-gradient) !important;
        border-color: transparent !important;
        transform: translateX(5px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* ========================================
       ボタンスタイル
    ======================================== */
    
    /* プライマリボタン */
    .stButton > button[kind="primary"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* セカンダリボタン */
    .stButton > button[kind="secondary"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* ========================================
       インプットスタイル
    ======================================== */
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* セレクトボックス */
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    
    /* マルチセレクト */
    .stMultiSelect > div > div {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    
    /* ========================================
       カードスタイル
    ======================================== */
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(26, 27, 38, 0.5) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    /* タブ */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-glass);
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient) !important;
    }
    
    /* ========================================
       メトリクスカード
    ======================================== */
    
    [data-testid="stMetric"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 1.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px var(--shadow-color) !important;
    }
    
    [data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }
    
    /* ========================================
       プログレスバー
    ======================================== */
    
    .stProgress > div > div > div > div {
        background: var(--primary-gradient) !important;
        border-radius: 10px !important;
    }
    
    .stProgress > div > div > div {
        background: var(--bg-glass) !important;
        border-radius: 10px !important;
    }
    
    /* ========================================
       アラートスタイル
    ======================================== */
    
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Info */
    [data-testid="stAlert"][data-baseweb="notification-info"] {
        background: rgba(79, 172, 254, 0.15) !important;
        border-left: 4px solid #4facfe !important;
    }
    
    /* Success */
    [data-testid="stAlert"][data-baseweb="notification-success"] {
        background: rgba(56, 239, 125, 0.15) !important;
        border-left: 4px solid #38ef7d !important;
    }
    
    /* Warning */
    [data-testid="stAlert"][data-baseweb="notification-warning"] {
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    /* Error */
    [data-testid="stAlert"][data-baseweb="notification-negative"] {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    /* ========================================
       スライダー
    ======================================== */
    
    .stSlider > div > div > div > div {
        background: var(--primary-gradient) !important;
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: var(--primary-gradient) !important;
        font-weight: 600;
    }
    
    /* ========================================
       ラジオボタン
    ======================================== */
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio [data-testid="stMarkdownContainer"] {
        background: var(--bg-glass);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stRadio [data-testid="stMarkdownContainer"]:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* ========================================
       スピナー
    ======================================== */
    
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* ========================================
       ディバイダー
    ======================================== */
    
    hr {
        border-color: var(--border-color) !important;
        margin: 2rem 0 !important;
    }
    
    /* ========================================
       トースト
    ======================================== */
    
    [data-testid="stToast"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* ========================================
       アニメーション
    ======================================== */
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    .animate-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    </style>
    """, unsafe_allow_html=True)


def get_hero_card(title: str, subtitle: str, icon: str = "✨") -> str:
    """ヒーローカードのHTMLを返す"""
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <h1 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        ">{title}</h1>
        <p style="
            color: #a0aec0;
            font-size: 1.1rem;
            margin: 0;
        ">{subtitle}</p>
    </div>
    """


def get_feature_card(icon: str, title: str, description: str) -> str:
    """フィーチャーカードのHTMLを返す"""
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    ">
        <div style="
            font-size: 2rem;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">{icon}</div>
        <h4 style="
            color: #e2e8f0;
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        ">{title}</h4>
        <p style="
            color: #718096;
            font-size: 0.875rem;
            margin: 0;
            line-height: 1.5;
        ">{description}</p>
    </div>
    """


def get_metric_card(icon: str, label: str, value: str, color: str = "#667eea") -> str:
    """メトリクスカードのHTMLを返す"""
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="
            font-size: 0.875rem;
            color: #718096;
            margin-bottom: 0.25rem;
        ">{label}</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, {color} 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">{value}</div>
    </div>
    """


def get_result_type_card(personality_type: str, description: str) -> str:
    """性格タイプ結果カードのHTMLを返す"""
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        border: 2px solid rgba(102, 126, 234, 0.5);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        "></div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <div style="
                font-size: 0.875rem;
                color: #a0aec0;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 0.5rem;
            ">あなたのタイプは</div>
            <div style="
                font-size: 4rem;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
                letter-spacing: 4px;
            ">{personality_type}</div>
            <div style="
                font-size: 1.25rem;
                color: #e2e8f0;
                font-weight: 500;
            ">{description}</div>
        </div>
    </div>
    """


def get_question_card(question_id: int, question_text: str) -> str:
    """質問カードのHTMLを返す"""
    return f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 1rem;
        ">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.875rem;
                flex-shrink: 0;
            ">Q{question_id}</div>
            <div style="
                color: #e2e8f0;
                font-size: 1rem;
                line-height: 1.6;
            ">{question_text}</div>
        </div>
    </div>
    """


def get_section_header(icon: str, title: str, subtitle: str = "") -> str:
    """セクションヘッダーのHTMLを返す"""
    subtitle_html = f'<p style="color: #718096; font-size: 0.9rem; margin: 0;">{subtitle}</p>' if subtitle else ""
    return f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    ">
        <div style="
            font-size: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">{icon}</div>
        <div>
            <h2 style="
                color: #e2e8f0;
                font-size: 1.5rem;
                font-weight: 600;
                margin: 0;
            ">{title}</h2>
            {subtitle_html}
        </div>
    </div>
    """


def get_info_banner(icon: str, title: str, message: str, color: str = "#4facfe") -> str:
    """情報バナーのHTMLを返す"""
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        border: 1px solid {color}30;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.5rem;
    ">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div>
            <div style="
                color: #e2e8f0;
                font-weight: 600;
                margin-bottom: 0.25rem;
            ">{title}</div>
            <div style="
                color: #a0aec0;
                font-size: 0.9rem;
                line-height: 1.5;
            ">{message}</div>
        </div>
    </div>
    """
