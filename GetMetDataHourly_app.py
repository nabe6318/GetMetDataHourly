import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
import AMD_Tools4 as amd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("時別気象データ取得アプリ")
st.markdown("気温（TMP）、相対湿度（RH）、下向き長波放射量（DLR）の時別データを可視化します。")

# --- 観測地点リスト ---
locations = {
    "KOA山1（洗馬）": (36.10615778, 137.8787694),
    "KOA山2（洗馬）": (36.10599167, 137.8787083),
    "KOA山3（洗馬）": (36.10616111, 137.8790889),
    "KOA山4（洗馬）": (36.10617778, 137.8789667),
    "KOA5WW（箕輪町）": (35.89755278, 137.9560553),
    "KOA6（手良）": (35.87172194, 138.0164028),
    "KOA7（手良）": (35.87127222, 138.0160833)
}

# --- 地点選択 ---
location_name = st.selectbox("観測地点を選択してください", list(locations.keys()))
lat, lon = locations[location_name]
st.session_state["lat"] = lat
st.session_state["lon"] = lon

# --- 気象要素の選択 ---
element = st.selectbox(
    "気象要素を選択してください",
    options=["TMP", "RH", "DLR"],
    format_func=lambda x: {
        "TMP": "気温 (TMP)",
        "RH": "相対湿度 (RH)",
        "DLR": "下向き長波放射量 (DLR)"
    }[x]
)

# --- 日付選択 ---
today = datetime.today().date()
col1, col2 = st.columns(2)
start_date = col1.date_input("開始日", today)
end_date = col2.date_input("終了日", today)

# --- 時別形式のタイムドメイン作成 ---
start_str = str(start_date)
end_str = str(end_date)
timedomain = [f"{start_str}T01", f"{end_str}T24"]

# --- データ取得 ---
if st.button("気象データを取得"):
    with st.spinner("時別データを取得中..."):
        try:
            lalodomain = [[lat, lat], [lon, lon]]  # 単一点指定
            obs, tim, lat_arr, lon_arr, name, unit = amd.GetMetDataHourly(
                element, timedomain, lalodomain, namuni=True
            )

            obs_1d = obs[:, 0, 0]
            tim = pd.to_datetime(tim)

            # 表示用データフレーム
            df = pd.DataFrame({
                "日時": tim,
                "値": obs_1d,
                "緯度": lat,
                "経度": lon
            })

            st.subheader("データテーブル")
            st.dataframe(df)

            # 折れ線グラフ
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