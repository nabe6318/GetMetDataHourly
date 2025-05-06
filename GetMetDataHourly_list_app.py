import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
import os
import AMD_Tools4 as amd  # 気象データ取得ライブラリ

# タイトルと説明
st.title("時別気象データ取得アプリ")
st.markdown("気温（TMP）、相対湿度（RH）、下向き長波放射量（DLR）の時別データを可視化します。")

# --- 気象要素の選択 ---
element = st.selectbox("気象要素を選択してください", options=["TMP", "RH", "DLR"], format_func=lambda x: {
    "TMP": "気温 (TMP)",
    "RH": "相対湿度 (RH)",
    "DLR": "下向き長波放射量 (DLR)"
}[x])

# --- 日付入力 ---
today = datetime.today().date()
col1, col2 = st.columns(2)
start_date = col1.date_input("開始日", today)
end_date = col2.date_input("終了日", today)

# --- 地点の履歴ファイルの読み込みまたは作成 ---
HISTORY_FILE = "location_history.csv"
if os.path.exists(HISTORY_FILE):
    history_df = pd.read_csv(HISTORY_FILE)
    history_list = history_df["地点名"].tolist()
else:
    history_df = pd.DataFrame(columns=["地点名", "緯度", "経度"])
    history_list = []

# --- 地点指定 ---
st.subheader("地点の指定")
use_history = st.checkbox("履歴から選択", value=True)

if use_history and history_list:
    selected_place = st.selectbox("過去の地点から選択", options=history_list)
    lat = float(history_df.loc[history_df["地点名"] == selected_place, "緯度"].values[0])
    lon = float(history_df.loc[history_df["地点名"] == selected_place, "経度"].values[0])
    place_name = selected_place
else:
    place_name = st.text_input("地点名", value="長野市")
    lat = st.number_input("緯度", format="%.4f", value=36.6513)
    lon = st.number_input("経度", format="%.4f", value=138.1810)

    if st.button("この地点を履歴に保存"):
        # 重複チェックして保存
        if place_name and not ((history_df["地点名"] == place_name) &
                               (history_df["緯度"] == lat) &
                               (history_df["経度"] == lon)).any():
            new_entry = pd.DataFrame([[place_name, lat, lon]], columns=["地点名", "緯度", "経度"])
            history_df = pd.concat([history_df, new_entry], ignore_index=True)
            history_df.to_csv(HISTORY_FILE, index=False)
            st.success("履歴に保存しました。")
        else:
            st.info("この地点はすでに履歴にあります。")

# 表示とセッション状態保存
st.success(f"選択された地点: {place_name}（緯度 {lat}, 経度 {lon}）")
st.session_state["lat"] = lat
st.session_state["lon"] = lon

# --- データ取得範囲の設定 ---
lalodomain = [lat, lat, lon, lon]
start_str = str(start_date)
end_str = str(end_date)
timedomain = [f"{start_str}T01", f"{end_str}T24"]

# --- データ取得・表示 ---
if st.button("気象データを取得"):
    with st.spinner("時別データを取得中..."):
        try:
            obs, tim, lat_arr, lon_arr, name, unit = amd.GetMetDataHourly(
                element, timedomain, lalodomain, namuni=True
            )

            obs_1d = obs[:, 0, 0]
            tim = pd.to_datetime(tim)

            df = pd.DataFrame({
                "日時": tim,
                "値": obs_1d,
                "緯度": lat,
                "経度": lon
            })

            st.subheader("データテーブル")
            st.dataframe(df)

            st.subheader("折れ線グラフ")
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(tim, obs_1d, 'b-', label=name)
            ax.set_xlabel("日時")
            ax.set_ylabel(f"{name} [{unit}]")
            ax.set_title(f"{place_name}（{name}）: N{lat}, E{lon}")
            ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d %Hh'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"データ取得エラー: {e}")