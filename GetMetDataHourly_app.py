import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
import AMD_Tools4 as amd
import folium
from streamlit_folium import st_folium

st.title("時別気象データ取得アプリ")
st.markdown("気温（TMP）、相対湿度（RH）、下向き長波放射量（DLR）の時別データを可視化します。")

# --- 要素選択 ---
element = st.selectbox("気象要素を選択してください", options=["TMP", "RH", "DLR"], format_func=lambda x: {
    "TMP": "気温 (TMP)",
    "RH": "相対湿度 (RH)",
    "DLR": "下向き長波放射量 (DLR)"
}[x])

# --- 今日の日付をデフォルトに設定 ---
today = datetime.today().date()
col1, col2 = st.columns(2)
start_date = col1.date_input("開始日", today)
end_date = col2.date_input("終了日", today)

# --- マップクリックで地点指定（ピン付き） ---
with st.container():
    st.subheader("地点の指定")
    m = folium.Map(location=[st.session_state["lat"], st.session_state["lon"]], zoom_start=6)
    folium.Marker(
        location=[st.session_state["lat"], st.session_state["lon"]],
        tooltip="選択地点",
        icon=folium.Icon(color="red")
    ).add_to(m)
    map_result = st_folium(m, height=400, returned_objects=["last_clicked"])
    st.caption("※ 終了日は9日先まで指定できます。")
    st.caption("※ マップをクリックすると、クリックした場所の緯度・経度が表示されます。")


if map_result["last_clicked"] is not None:
    st.session_state["lat"] = round(map_result["last_clicked"]["lat"], 4)
    st.session_state["lon"] = round(map_result["last_clicked"]["lng"], 4)

lat = st.session_state["lat"]
lon = st.session_state["lon"]
st.success(f"選択された地点: 緯度 {lat}, 経度 {lon}")

lalodomain = [lat, lat, lon, lon]

# --- 時別形式のタイムドメインに変換 ---
start_str = str(start_date)
end_str = str(end_date)
timedomain = [f"{start_str}T01", f"{end_str}T24"]

# --- データ取得 ---
if st.button("気象データを取得"):
    with st.spinner("時別データを取得中..."):
        try:
            # 時別気象データの取得
            obs, tim, lat_arr, lon_arr, name, unit = amd.GetMetDataHourly(element, timedomain, lalodomain, namuni=True)

            # 次元削減
            obs_1d = obs[:, 0, 0]
            tim = pd.to_datetime(tim)

            # --- 表形式で出力 ---
            df = pd.DataFrame({
                "日時": tim,
                "値": obs_1d,
                "緯度": lat,
                "経度": lon
            })
            st.subheader("データテーブル")
            st.dataframe(df)

            # --- 折れ線グラフ ---
            st.subheader("折れ線グラフ")
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(tim, obs_1d, 'b-', label=name)
            ax.set_xlabel("日時")
            ax.set_ylabel(f"{name} [{unit}]")
            ax.set_title(f"{name}（時別）: N{lat}, E{lon}")
            ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d %Hh'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"データ取得エラー: {e}")

