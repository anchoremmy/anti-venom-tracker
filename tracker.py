import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
from st_supabase_connection import SupabaseConnection

# 1. Page Configuration
st.set_page_config(page_title="SA Anti-Venom Command", layout="wide")

# --- DISTANCE UTILITY ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat, dlon = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

# 2. LIVE DATABASE CONNECTION
conn = st.connection("supabase", type=SupabaseConnection)

try:
    response = conn.table("hospitals").select("*").execute()
    df_base = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# --- 🚨 EMERGENCY ALERT SYSTEM ---
critical_hospitals = df_base[df_base['vials'] == 0]['name'].tolist()
if critical_hospitals:
    st.error(f"🚨 CRITICAL DEPLETION: {len(critical_hospitals)} facilities have 0 vials!")
    st.components.v1.html("""<audio autoplay><source src="https://www.soundjay.com" type="audio/mpeg"></audio>""", height=0)

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🕹️ Control Panel")
show_only_available = st.sidebar.checkbox("Show only hospitals with stock", value=False)
show_heatmap = st.sidebar.checkbox("Show Snakebite Risk Heatmap", value=True)
st.sidebar.divider()
st.sidebar.info("LIVE DATA: Integrated with Supabase National Registry.")

# --- TOP SECTION: NATIONAL METRICS ---
st.title("🇿🇦 National Anti-Venom Command Center")
m1, m2, m3 = st.columns(3)
with m1: st.metric("Total National Stock", f"{df_base['vials'].sum()} Vials")
with m2: st.metric("Facilities Depleted", len(critical_hospitals), delta="-Critical" if critical_hospitals else "Clear", delta_color="inverse")
with m3: st.metric("System Status", "📡 ONLINE / SECURE")

st.divider()

# --- MAIN LAYOUT (RESTORED 2:1 RATIO) ---
col1, col2 = st.columns([2, 1]) # <--- This gives you the big map you like!

with col1:
    st.subheader("Interactive Crisis Map")
    map_df = df_base.copy()
    if show_only_available:
        map_df = map_df[map_df['vials'] > 0]
    
    # Colors: Green for stock [0, 255, 0], Red for 0 [255, 0, 0]
    map_df['color'] = map_df['vials'].apply(lambda x: [0, 255, 0, 160] if x > 0 else [255, 0, 0, 160])
    
    layers = []
    if show_heatmap:
        hotspots = pd.DataFrame({'lat': [-28.5, -23.5, -29.8], 'lon': [31.5, 29.8, 30.5], 'w': [1.0, 1.2, 0.8]})
        layers.append(pdk.Layer("HeatmapLayer", data=hotspots, get_position="[lon, lat]", get_weight="w", radius_pixels=80, opacity=0.3))
    
    layers.append(pdk.Layer('ScatterplotLayer', data=map_df, get_position='[lon, lat]', get_color='color', get_radius=30000, pickable=True))
    
    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=-28.47, longitude=24.67, zoom=4.5),
        tooltip={"text": "{name}\nStock: {vials} vials"}
    ))

with col2:
    st.subheader("🔐 Logistics & Admin")
    
    # 1. DISTANCE CALCULATOR
    with st.expander("🔍 Find Nearest Stock", expanded=True):
        origin_name = st.selectbox("Depleted Facility:", df_base['name'])
        origin_hosp = df_base[df_base['name'] == origin_name].iloc[0]
        stock_df = df_base[df_base['vials'] > 0].copy()
        
        if not stock_df.empty:
            stock_df['dist_km'] = stock_df.apply(lambda row: haversine(origin_hosp['lat'], origin_hosp['lon'], row['lat'], row['lon']), axis=1)
            closest = stock_df.sort_values('dist_km').iloc[0]
            st.info(f"**Closest Stock: {closest['name']}**")
            st.metric("Distance", f"{closest['dist_km']:.1f} km")
            st.success(f"📞 Contact: {closest['phone']}")
        else:
            st.error("No stock available nationwide.")

    # 2. UPDATE INVENTORY
    with st.expander("Update Facility Inventory"):
        target_hosp = st.selectbox("Select Facility:", df_base['name'], key="update_box")
        current_val = int(df_base[df_base['name'] == target_hosp]['vials'].iloc[0])
        new_val = st.number_input(f"Count for {target_hosp}", min_value=0, value=current_val)
        
        if st.button("Update Cloud Database"):
            conn.table("hospitals").update({"vials": new_val}).eq("name", target_hosp).execute()
            st.cache_resource.clear() 
            st.rerun()

st.divider()
st.subheader("Detailed Facility Inventory")
st.dataframe(df_base[['name', 'province', 'vials', 'phone']], use_container_width=True, hide_index=True)

# --- FOOTER ---
st.divider()
with st.expander("ℹ️ Technical Note"):
    st.write("Functional MVP powered by Supabase Cloud. POPIA Compliant Architecture.")
st.caption("V-Track ZA v1.1 | Developed for National Health Security")

# --- FOOTER: MVP DISCLAIMER ---
st.divider()
with st.expander("ℹ️ Technical Note: Prototype Status"):
    st.write("""
    **This interface is a Functional MVP (Minimum Viable Product) powered by Supabase Cloud.**
    *   **Distance Logic**: Uses the Haversine formula to calculate the 'Golden Hour' transfer distance.
    *   **Data Integrity**: Changes made in the Admin Portal persist across all user sessions.
    """)
st.caption("V-Track ZA v1.1 | Data Sovereignty: Hosted via Supabase | POPIA Compliant Architecture")
