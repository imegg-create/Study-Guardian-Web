import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import base64
import time

# --- 1. 標題與基本設定 ---
st.set_page_config(page_title="讀書監管者", page_icon="👹")
st.title("讀書監管者")
st.write("認真讀書，否則超市會超市你")

# --- 2. 數據初始化 ---
if 'study_data' not in st.session_state:
    st.session_state.study_data = {"國文": 0.0, "英文": 0.0, "數學": 0.0}
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False


# 將音效轉為網頁可讀格式
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
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

# --- 4. 監控開關 (把按鈕找回來了！) ---
if st.button("🚀 開始 / 停止 監控", type="primary"):
    st.session_state.monitoring = not st.session_state.monitoring
    st.rerun()

# --- 5. 核心監控邏輯 (JavaScript) ---
if st.session_state.monitoring:
    st.success(f"正在監控：{selected_subject} ... (請勿離開此分頁)")

    # 這裡注入 JavaScript：偵測離開分頁就放音樂
    js_code = f"""
    <script>
        const audio = new Audio("data:audio/mp3;base64,{audio_base64}");
        audio.loop = true;

        // 監聽網頁可見性變化
        document.addEventListener("visibilitychange", function() {{
            if (document.hidden) {{
                audio.play(); // 離開分頁，開始超市你
            }} else {{
                audio.pause(); // 回來了，停止警報
                audio.currentTime = 0;
            }}
        }});
    </script>
    """
    components.html(js_code, height=0)

    # 顯示老師圖片警告（在網頁上提示）
    st.image("teacher.png", caption="老師正在看著你...", use_container_width=True)
else:
    st.info("目前的監控已停止。按下按鈕開始專注！")

# --- 6. 結算圖表 (已修正 {{ 語法錯誤) ---
st.divider()
if st.button("📈 結算今日成果"):
    # 修正點：這裡原本是 {{ 現在改回 {
    df = pd.DataFrame({
        "科目": list(st.session_state.study_state.study_data.keys()),
        "秒數": list(st.session_state.study_state.study_data.values())
    })

    # 為了方便示範，網頁版時間累計需配合手動計時，這裡先檢查是否有數據
    if df["秒數"].sum() >= 0:
        fig = px.pie(df, values='秒數', names='科目', title='今日專注分佈')
        st.plotly_chart(fig)
    else:
        st.warning("目前還沒有計時紀錄。")