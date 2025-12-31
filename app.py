import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(page_title="GTR Stock Cockpit", layout="wide")
st.title("🏎️ GTR Stock Cockpit")

# --- サイドバーで入力 ---
with st.sidebar:
    st.header("PIT ENTRY")
    ticker = st.text_input("ティッカー入力 (例: NVDA, TSLA, AAPL)", value="NVDA").upper()
    period = st.selectbox("データ期間", ["1d", "5d", "1mo"], index=0)

if ticker:
    # データ取得
    df = yf.download(ticker, period=period, interval="15m")
    
    if not df.empty:
        # 指標計算（簡易版）
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[0]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # --- メーター作成関数 ---
        def create_gauge(value, title, min_val, max_val, color):
            return go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': title, 'font': {'size': 24, 'color': "white"}},
                gauge={
                    'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': color},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [min_val, max_val*0.8], 'color': "rgba(255,255,255,0.1)"},
                        {'range': [max_val*0.8, max_val], 'color': "rgba(255,0,0,0.3)"} # レッドゾーン
                    ],
                }
            )).update_layout(paper_bgcolor='black', font={'color': "white"}, height=300, margin=dict(l=20, r=20, t=50, b=20))

        # --- レイアウト配置 ---
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            # タコメーター：株価の勢い（前日比％）
            st.plotly_chart(create_gauge(change_pct, "MOMENTUM (%)", -5, 5, "cyan"), use_container_width=True)

        with col2:
            # スピードメーター：単純な価格（目安）
            st.plotly_chart(create_gauge(current_price, "STOCK SPEED", 0, current_price*1.2, "orange"), use_container_width=True)

        with col3:
            # 液晶パネル風メッセージ
            st.markdown("""
            <div style="background-color: #111; padding: 20px; border: 2px solid #333; border-radius: 10px; height: 260px;">
                <h3 style="color: #00ff00; font-family: 'Courier New';">PIT COMMAND</h3>
                <p style="color: white; font-size: 18px;">Target: """ + ticker + """</p>
                <p style="color: yellow; font-size: 20px;">""" + 
                ("🔥 フル加速だ！前の株をぶち抜け！" if change_pct > 0 else "🛑 ブレーキ！路面状況（地合い）が悪い！") 
                + """</p>
                <hr style="border-color: #444;">
                <p style="color: gray;">Tire: Warm up<br>Oil: Optimal</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.line_chart(df['Close'])
    else:
        st.error("ティッカーが見つかりません。正しいシンボルを入力してください。")
