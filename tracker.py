import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. Page Configuration
st.set_page_config(page_title="SA Anti-Venom Command", layout="wide")

# 2. PERSISTENCE LOGIC (Simulating a Database)
if 'hospitals' not in st.session_state:
    st.session_state.hospitals = pd.DataFrame({
        'name': ['Chris Hani Baragwanath', 'Tygerberg Hospital', 'Addington Hospital', "Grey's Hospital", 'Polokwane Provincial'],
        'province': ['Gauteng', 'Western Cape', 'KZN', 'KZN', 'Limpopo'],
        'lat': [-26.2625, -33.9145, -29.8601, -29.5826, -23.9100],
        'lon': [27.9405, 18.6110, 31.0425, 30.3472, 29.4500],
        'vials': [12, 0, 8, 15, 0], # Mock starting data
        'phone': ['011 933 8000', '021 938 4111', '031 327 2000', '033 897 3000', '015 287 5000']
    })

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🕹️ Control Panel")
show_only_available = st.sidebar.checkbox("Show only hospitals with stock", value=False)
show_heatmap = st.sidebar.checkbox("Show Snakebite Risk Heatmap", value=True)
st.sidebar.divider()
st.sidebar.info("This dashboard integrates NHLS supply data with real-time hospital reporting.")

# --- TOP SECTION: NATIONAL METRICS ---
st.title("🇿🇦 National Anti-Venom Command Center")
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total National Stock", f"{st.session_state.hospitals['vials'].sum()} Vials")
with m2:
    depleted = len(st.session_state.hospitals[st.session_state.hospitals['vials'] == 0])
    st.metric("Facilities Depleted", depleted, delta="-Critical" if depleted > 0 else "Clear", delta_color="inverse")
with m3:
    st.metric("System Status", "LIVE / SECURE")

st.divider()

# --- MAIN LAYOUT ---
col1, col2 = st.columns([2, 1]) # Map gets 2/3 of space

with col1:
    st.subheader("Interactive Crisis Map")
    
    # Apply Sidebar Filters to Data
    df = st.session_state.hospitals.copy()
    if show_only_available:
        df = df[df['vials'] > 0]
    
    df['color'] = df['vials'].apply(lambda x: [0, 255, 0, 160] if x > 0 else [255, 0, 0, 160])
    
    layers = []
    if show_heatmap:
        # High-risk heatmap data
        hotspots = pd.DataFrame({'lat': [-28.5, -23.5, -29.8], 'lon': [31.5, 29.8, 30.5], 'w': [0.9, 1.0, 0.8]})
        layers.append(pdk.Layer("HeatmapLayer", data=hotspots, get_position="[lon, lat]", get_weight="w", radius_pixels=80, opacity=0.3))
    
    layers.append(pdk.Layer('ScatterplotLayer', data=df, get_position='[lon, lat]', get_color='color', get_radius=30000, pickable=True))
    
    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=-28.47, longitude=24.67, zoom=4.5),
        tooltip={"text": "{name}\nStock: {vials} vials"}
    ))

with col2:
    st.subheader("🔐 Admin Portal")
    with st.expander("Update Facility Inventory", expanded=True):
        target_hosp = st.selectbox("Select Facility:", st.session_state.hospitals['name'])
        idx = st.session_state.hospitals.index[st.session_state.hospitals['name'] == target_hosp].tolist()[0]
        current_val = int(st.session_state.hospitals.at[idx, 'vials'])
        
        new_val = st.number_input(f"New Vial Count for {target_hosp}", min_value=0, value=current_val)
        
        if st.button("Save to National Registry"):
            st.session_state.hospitals.at[idx, 'vials'] = new_val
            st.success("✅ Database Updated!")
            st.rerun()

st.divider()
st.subheader("Detailed Facility Inventory")
st.dataframe(df[['name', 'province', 'vials', 'phone']], use_container_width=True, hide_index=True)
# --- FOOTER: MVP DISCLAIMER ---
st.divider()
with st.expander("ℹ️ Technical Note: Prototype Status"):
    st.write("""
    **This interface is a Functional MVP (Minimum Viable Product) developed for demonstration purposes.**
    
    Upon project approval, the production-grade system will feature:
    *   **Advanced UI/UX**: Transition to a high-performance **NextJS / React Native** mobile architecture.
    *   **Enterprise Security**: Full OAuth2 authentication and POPIA-compliant data encryption.
    *   **API Integration**: Direct live-sync with the National Health Laboratory Service (NHLS) and Provincial medical databases.
    *   **Offline Support**: Specialized 'low-connectivity' mode for rural medical officers.
    """)
