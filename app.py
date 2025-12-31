import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- ページ設定 ---
st.set_page_config(page_title="GTR Stock Cockpit", layout="wide")

# CSSで背景を黒く、よりコックピット風にする
st.markdown("""
    <style>
    .main { background-color: #000000; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ GTR Stock Cockpit")

# --- 入力部 ---
ticker = st.text_input("ティッカー入力 (例: NVDA, TSLA, AAPL)", value="AAPL").upper()

if ticker:
    try:
        # データ取得 (期間を1ヶ月にして確実にデータを取る)
        data = yf.download(ticker, period="1mo", interval="1d")
        
        if len(data) > 1:
            # 最新の価格と前日比
            current_price = float(data['Close'].iloc[-1])
            prev_price = float(data['Close'].iloc[-2])
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            # --- レイアウト ---
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                # タコメーター
                fig_tacho = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=abs(change_pct),
                    title={'text': "MOMENTUM (%)", 'font': {'color': "white"}},
                    gauge={'axis': {'range': [0, 10]}, 'bar': {'color': "red" if change_pct < 0 else "lime"}}
                ))
                fig_tacho.update_layout(paper_bgcolor='black', font={'color': "white"}, height=300)
                st.plotly_chart(fig_tacho, use_container_width=True)

            with col2:
                # スピードメーター（RSIの代わりに前日比を速度に見立てる）
                speed = 100 + (change_pct * 10)
                fig_speed = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=speed,
                    title={'text': "JUDGMENT SPEED", 'font': {'color': "white"}},
                    gauge={'axis': {'range': [0, 200]}, 'bar': {'color': "gold"}}
                ))
                fig_speed.update_layout(paper_bgcolor='black', font={'color': "white"}, height=300)
                st.plotly_chart(fig_speed, use_container_width=True)

            with col3:
                # 液晶パネル
                status = "FULL THROTTLE!" if change_pct > 0 else "EMERGENCY BRAKE!"
                st.markdown(f"""
                    <div style="background-color: #111; padding: 20px; border: 2px solid #333; border-radius: 10px;">
                        <h3 style="color: #00ff00; font-family: 'Courier New';">PIT COMMAND</h3>
                        <p style="font-size: 24px; color: white;">{ticker}</p>
                        <p style="font-size: 20px; color: yellow;">{status}</p>
                        <p style="color: gray;">Price: ${current_price:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.line_chart(data['Close'])
        else:
            st.warning("データ収集中... ティッカーが正しいか確認してくれ！")
            
    except Exception as e:
        st.error(f"メカニックからの報告: マシンの準備ができていないようだ (エラー: {e})")
