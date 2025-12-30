import streamlit as st
import streamlit.components.v1 as components
import time
import pandas as pd
import plotly.express as px
import base64

# --- 1. 標題與基本設定 ---
st.set_page_config(page_title="讀書監管者", page_icon="👹")
st.title("讀書監管者")
st.write("認真讀書，否則超市會超市你")

# --- 2. 讀取素材並轉為 Base64 (為了讓網頁能直接播放) ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    audio_base64 = get_base64_of_bin_file('alert.mp3')
except:
    audio_base64 = ""

# --- 3. 數據初始化 ---
if 'study_data' not in st.session_state:
    st.session_state.study_data = {"國文": 0.0, "英文": 0.0, "數學": 0.0}
if 'is_distracted' not in st.session_state:
    st.session_state.is_distracted = False

# --- 4. 側邊欄與科目管理 ---
st.sidebar.title("📊 學習統計")
new_subj = st.sidebar.text_input("新增科目：")
if st.sidebar.button("➕ 新增"):
    if new_subj and new_subj not in st.session_state.study_data:
        st.session_state.study_data[new_subj] = 0.0
        st.rerun()

selected_subject = st.sidebar.selectbox("目前科目：", list(st.session_state.study_data.keys()))

# --- 5. JavaScript 核心監控邏輯 ---
# 這段程式碼會嵌入瀏覽器，當使用者「切換分頁」或「縮小視窗」時會發動攻擊
st.info("💡 只要離開這個網頁分頁，警報就會響起！")

js_code = f"""
<script>
    const audio = new Audio("data:audio/mp3;base64,{audio_base64}");
    audio.loop = true;

    document.addEventListener("visibilitychange", function() {{
        if (document.hidden) {{
            // 使用者離開了分頁
            audio.play();
            // 發送訊息給 Streamlit (這需要一點點時間處理)
            window.parent.postMessage({{type: 'distracted', value: true}}, '*');
        }} else {{
            // 使用者回來了
            audio.pause();
            audio.currentTime = 0;
        }}
    }});
</script>
"""
components.html(js_code, height=0)

# --- 6. 主畫面顯示 ---
if st.session_state.is_distracted:
    st.error("🚨 抓到了！你剛剛跑去哪裡了？")
    st.image("teacher.png", use_container_width=True)
    if st.button("我錯了，我會認真讀書"):
        st.session_state.is_distracted = False
        st.rerun()
else:
    st.success(f"✅ 正在專注於：{selected_subject}")
    st.write("請保持在這個網頁，不要切換視窗。")

# --- 7. 結算圖表 ---
if st.button("📈 結算今日成果"):
    df = pd.DataFrame({{
        "科目": list(st.session_state.study_data.keys()),
        "秒數": list(st.session_state.study_data.values())
    }})
    if df["秒數"].sum() > 0:
        fig = px.pie(df, values='秒數', names='科目', title='讀書時間分佈')
        st.plotly_chart(fig)
    else:
        st.warning("還沒累積時間喔！")