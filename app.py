import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="GTR Stock Cockpit", layout="wide")

# 背景を黒く設定
st.markdown("<style>.main {background-color: #000000;}</style>", unsafe_allow_html=True)

st.title("🏎️ GTR Stock Cockpit")

ticker = st.text_input("ENTER TICKER (e.g. NVDA, TSLA)", value="NVDA").upper()

if ticker:
    # データ取得
    data = yf.download(ticker, period="5d", interval="15m")
    
    if not data.empty and len(data) >= 2:
        # 【修正ポイント】値を確実に「1つの数字」として取り出す
        current_price = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2])
        change_pct = ((current_price - prev_close) / prev_close) * 100

        # タコメーターの値を計算 (0-9000回転)
        # 前日比+3%で約7000回転（レッドゾーン入口）
        tacho_value = 1000 + (change_pct * 2000)
        tacho_value = max(0, min(9000, float(tacho_value)))

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            # --- タコメーター (RPM) ---
            fig_tacho = go.Figure(go.Indicator(
                mode="gauge+number",
                value=tacho_value,
                title={'text': "RPM (MOMENTUM)", 'font': {'color': "white"}},
                gauge={
                    'axis': {'range': [0, 9000], 'tickcolor': "white"},
                    'bar': {'color': "red" if tacho_value > 7000 else "orange"},
                    'steps': [
                        {'range': [0, 7000], 'color': "rgba(255,255,255,0.1)"},
                        {'range': [7000, 9000], 'color': "rgba(255,0,0,0.5)"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 5}, 'thickness': 0.8, 'value': 7000}
                }
            ))
            fig_tacho.update_layout(paper_bgcolor='black', font={'color': "white"}, height=350)
            st.plotly_chart(fig_tacho, use_container_width=True)

        with col2:
            # --- スピードメーター (JUDGMENT) ---
            speed_value = 100 + (change_pct * 30)
            speed_value = max(0, min(300, float(speed_value)))
            
            fig_speed = go.Figure(go.Indicator(
                mode="gauge+number",
                value=speed_value,
                title={'text': "Km/h (JUDGMENT)", 'font': {'color': "white"}},
                gauge={
                    'axis': {'range': [0, 300], 'tickcolor': "white"},
                    'bar': {'color': "lime" if speed_value > 120 else "yellow"},
                }
            ))
            fig_speed.update_layout(paper_bgcolor='black', font={'color': "white"}, height=350)
            st.plotly_chart(fig_speed, use_container_width=True)

        with col3:
            # --- 液晶風パネル ---
            mode_text = "R-MODE" if change_pct > 1 else "COMFORT"
            color_code = "#ff0000" if change_pct > 1 else "#00ffff"
            
            st.markdown(f"""
                <div style="background-color: #111; padding: 25px; border: 3px solid {color_code}; border-radius: 10px; margin-top: 50px;">
                    <h2 style="color: {color_code}; font-family: 'Courier New'; margin:0;">{mode_text}</h2>
                    <p style="color: white; font-size: 20px; margin: 10px 0;">TARGET: {ticker}</p>
                    <p style="color: #00ff00; font-size: 30px; font-weight: bold;">${current_price:.2f}</p>
                    <p style="color: {'#00ff00' if change_pct > 0 else '#ff4444'}; font-size: 18px;">
                        { '▲' if change_pct > 0 else '▼' } {abs(change_pct):.2f}%
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.line_chart(data['Close'])
    else:
        st.info("データ待機中... 市場が開いているか確認してくれ！")
