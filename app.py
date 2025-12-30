import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import base64

# --- 1. 標題與基本設定 ---
st.set_page_config(page_title="讀書監管者", page_icon="👹")
st.title("讀書監管者")
st.write("認真讀書，否則超市會超市你")

# --- 2. 數據初始化 ---
if 'study_data' not in st.session_state:
    st.session_state.study_data = {"國文": 0.0, "英文": 0.0, "數學": 0.0}
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False


# 讀取音效轉為 Base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""


audio_base64 = get_base64_of_bin_file('alert.mp3')

# --- 3. 側邊欄 ---
st.sidebar.title("📊 學習管理")
new_subj = st.sidebar.text_input("新增科目：")
if st.sidebar.button("➕ 新增"):
    if new_subj and new_subj not in st.session_state.study_data:
        st.session_state.study_data[new_subj] = 0.0
        st.rerun()

selected_subject = st.sidebar.selectbox("🎯 目前科目：", list(st.session_state.study_data.keys()))

# --- 4. 監控控制按鈕 ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 開始監控", type="primary", use_container_width=True):
        st.session_state.monitoring = True
        st.rerun()
with col2:
    if st.button("🛑 停止監控", use_container_width=True):
        st.session_state.monitoring = False
        st.rerun()

# --- 5. 監控邏輯 ---
if st.session_state.monitoring:
    st.warning(f"正在監控：{selected_subject} ... 請勿切換視窗！")

    # JavaScript 偵測離開頁面
    js_code = f"""
    <script>
        const audio = new Audio("data:audio/mp3;base64,{audio_base64}");
        audio.loop = true;
        document.addEventListener("visibilitychange", function() {{
            if (document.hidden) {{
                audio.play();
            }} else {{
                audio.pause();
                audio.currentTime = 0;
            }}
        }});
    </script>
    """
    components.html(js_code, height=0)
    st.image("teacher.png", caption="老師盯著你讀書...", use_container_width=True)
else:
    st.info("監控未啟動，請點擊「開始監控」按鈕。")

# --- 6. 結算圖表 ---
st.divider()
if st.button("📈 結算今日成果"):
    # 這裡已經修正為正確的 st.session_state.study_data
    data_dict = {
        "科目": list(st.session_state.study_data.keys()),
        "秒數": list(st.session_state.study_data.values())
    }
    df = pd.DataFrame(data_dict)

    if df["秒數"].sum() >= 0:
        fig = px.pie(df, values='秒數', names='科目', title='今日讀書時間比例')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("目前還沒有計時數據紀錄！")