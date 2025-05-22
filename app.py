import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Fungsi untuk mengambil data dari API liveList/v2
def fetch_live_sessions(cookies):
    # Generate endDate dengan tanggal terbaru
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Bangun URL secara manual
    api_url = (
        f"https://creator.shopee.co.id/supply/api/lm/sellercenter/liveList/v2?"
        f"page=1&pageSize=1000&name=&orderBy=&sort=&timeDim=30d&endDate={end_date}"
    )
    
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "referer": "https://creator.shopee.co.id/insight/live/list ",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "x-env": "live",
        "x-region": "id",
        "x-region-domain": "co.id",
        "x-region-timezone": "+0700",
        "x-traceid": "hL2clMOkW_wsPs_-TzJHl"
    }

    try:
        response = requests.get(api_url, headers=headers, cookies=cookies)
        print("Request URL:", response.url)  # Debugging: Cetak URL lengkap
        response.raise_for_status()  # Memastikan tidak ada error HTTP
        data = response.json()
        print("Response Data:", data)  # Debugging: Cetak respons JSON
        if data.get("code") == 0:  # Cek apakah respons sukses
            return data["data"]["list"]
        else:
            st.error(f"Error fetching live sessions: {data.get('msg')}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Fungsi untuk mengambil data dari API realtime/dashboard/overview
def fetch_dashboard_data(cookies, session_id):
    # Bangun URL secara manual
    api_url = (
        f"https://creator.shopee.co.id/supply/api/lm/sellercenter/realtime/dashboard/overview?"
        f"sessionId={session_id}"
    )
    
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "referer": "https://creator.shopee.co.id/insight/live/list ",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "x-env": "live",
        "x-region": "id",
        "x-region-domain": "co.id",
        "x-region-timezone": "+0700",
        "x-traceid": "hL2clMOkW_wsPs_-TzJHl"
    }

    try:
        response = requests.get(api_url, headers=headers, cookies=cookies)
        print("Request URL:", response.url)  # Debugging: Cetak URL lengkap
        response.raise_for_status()  # Memastikan tidak ada error HTTP
        data = response.json()
        print("Response Data:", data)  # Debugging: Cetak respons JSON
        if data.get("code") == 0:  # Cek apakah respons sukses
            return data["data"]
        else:
            st.error(f"Error fetching dashboard data: {data.get('msg')}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Main App
st.title("Shopee Live Real-Time Dashboard")

# Inisialisasi session state untuk cookie
if "cookies" not in st.session_state:
    st.session_state.cookies = {}

# Input Cookie
st.subheader("Masukkan Cookie Anda")
cookie_input = st.text_area("Paste Cookie di Bawah Ini", height=150)

if cookie_input:
    # Parse cookie input into a dictionary
    cookies = {}
    for line in cookie_input.split(";"):
        if "=" in line:
            key, value = line.strip().split("=", 1)
            cookies[key] = value

    # Validasi cookie
    if not cookies:
        st.warning("Cookie tidak valid. Pastikan formatnya benar (contoh: key=value).")
    else:
        # Simpan cookie ke session state
        st.session_state.cookies = cookies
        st.success("Cookie berhasil disimpan!")

# Fetch live sessions jika cookie tersedia
if st.session_state.cookies:
    live_sessions = fetch_live_sessions(st.session_state.cookies)
    if live_sessions:
        # Buat dropdown untuk memilih sesi
        session_options = {session["title"]: session["sessionId"] for session in live_sessions}
        selected_title = st.selectbox("Pilih Sesi Live Streaming", list(session_options.keys()))

        # Dapatkan sessionId dari sesi yang dipilih
        session_id = session_options[selected_title]

        # Fetch dashboard data untuk sessionId yang dipilih
        dashboard_data = fetch_dashboard_data(st.session_state.cookies, session_id)
        if dashboard_data:
            # Display overview metrics
            st.subheader("Overview Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Viewers", dashboard_data.get("viewers", "N/A"))
            with col2:
                st.metric("Confirmed Buyers", dashboard_data.get("confirmedBuyers", "N/A"))
            with col3:
                st.metric("Confirmed GMV", f"Rp{dashboard_data.get('confirmedGmv', 'N/A'):,.2f}")

            # Display engagement data
            st.subheader("Engagement Data")
            engagement_data = dashboard_data.get("engagementData", {})
            st.write(f"**Likes:** {engagement_data.get('likes', 'N/A')}")
            st.write(f"**Comments:** {engagement_data.get('comments', 'N/A')}")
            st.write(f"**Shares:** {engagement_data.get('shares', 'N/A')}")
            st.write(f"**New Followers:** {engagement_data.get('newFollowers', 'N/A')}")

            # Visualize data with charts
            st.subheader("Performance Metrics")
            fig, ax = plt.subplots(figsize=(10, 5))
            metrics = {
                "Placed Orders": dashboard_data.get("placedOrder", 0),
                "Confirmed Orders": dashboard_data.get("confirmedOrder", 0),
                "Placed GMV": dashboard_data.get("placedGmv", 0),
                "Confirmed GMV": dashboard_data.get("confirmedGmv", 0)
            }
            ax.bar(metrics.keys(), metrics.values(), color=["blue", "green", "orange", "purple"])
            ax.set_title("Order and GMV Performance")
            ax.set_ylabel("Value")
            st.pyplot(fig)

            # Display additional metrics
            st.subheader("Additional Metrics")
            st.write(f"**Avg View Time:** {dashboard_data.get('avgViewTime', 'N/A')} ms")
            st.write(f"**CTR:** {dashboard_data.get('ctr', 'N/A')}%")
            st.write(f"**Engaged Viewers:** {dashboard_data.get('engagedViewers', 'N/A')}")
        else:
            st.warning("No data found for the selected session.")
    else:
        st.warning("No live sessions found.")
else:
    st.info("Silakan masukkan cookie untuk melanjutkan.")
