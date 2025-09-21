import streamlit as st
import pandas as pd
from flo_finance import flo_finance  # Direct import

# -------------------------
# Load CSVs
# -------------------------
@st.cache_data
def load_health_systems():
	df = pd.read_csv("health_system.csv")
	df = df.sort_values(by="Health_System_Name")
	return df.set_index("Health_System_ID").to_dict(orient="index")

@st.cache_data
def load_hospitals():
	df = pd.read_csv("all_hospitals.csv")
	df = df.sort_values(by="Hospital_Name")
	return df.set_index("CCN#").to_dict(orient="index")

health_systems = load_health_systems()
hospitals = load_hospitals()

# -------------------------
# Streamlit UI
# -------------------------
st.title("Florence Financial Impact")

mode = st.radio("Select a Health System or an Individual Hospital", ["Health System", "Individual Hospital"])

# -------------------------
# Health System Mode
# -------------------------
if mode == "Health System":
	name_lookup = {v["Health_System_Name"]: k for k, v in health_systems.items()}
	choice_name = st.selectbox(
		"Choose a health system (type to search)",
		sorted(name_lookup.keys())
	)
	choice_key = name_lookup[choice_name]
	defaults = health_systems[choice_key]
	
	st.subheader("Health System Information")
	st.text_input("Health System Name", value=defaults["Health_System_Name"], disabled=True)
	st.text_input("Bed Size", value=str(defaults["Bed_Size"]), disabled=True)
	st.text_area("States", value=defaults["State(s)"], disabled=True)
	st.text_input("Affiliated Hospitals", value=str(defaults["Affiliated_Hospitals"]), disabled=True)
	
	col1, col2, col3 = st.columns(3)
	with col1:
		staff_rate = round(st.number_input("Staff Labor Rate", value=float(defaults["Staff_Labor_Rate"])), 2)
	with col2:
		agency_rate = round(st.number_input("Agency Labor Rate", value=float(defaults["Agency_Labor_Rate"])), 2)
	with col3:
		rn_needed = round(st.number_input("Estimated RN Need", value=float(defaults["Estimated_RN_Need"])), 2)
		
# -------------------------
# Individual Hospital Mode
# -------------------------
else:
	states = sorted(set(v["State"] for v in hospitals.values()))
	chosen_state = st.selectbox("Choose a state", states)
	
	hospitals_in_state = {k: v for k, v in hospitals.items() if v["State"] == chosen_state}
	sorted_hospitals = dict(sorted(hospitals_in_state.items(), key=lambda item: item[1]["Hospital_Name"]))
	
	name_lookup = {v["Hospital_Name"]: k for k, v in sorted_hospitals.items()}
	choice_name = st.selectbox(
		"Choose a hospital (type to search)",
		sorted(name_lookup.keys())
	)
	choice_key = name_lookup[choice_name]
	defaults = hospitals[choice_key]
	
	st.subheader("Hospital Information")
	st.text_input("Hospital Name", value=defaults["Hospital_Name"], disabled=True)
	st.text_input("Bed Size", value=str(defaults["Bed_Size"]), disabled=True)
	st.text_input("State", value=defaults["State"], disabled=True)
	
	col1, col2, col3 = st.columns(3)
	with col1:
		staff_rate = round(st.number_input("Staff Labor Rate", value=float(defaults["Staff_Labor_Rate"])), 2)
	with col2:
		agency_rate = round(st.number_input("Agency Labor Rate", value=float(defaults["Agency_Labor_Rate"])), 2)
	with col3:
		rn_needed = round(st.number_input("Estimated RN Need", value=float(defaults["Estimated_RN_Need"])), 2)
		
# -------------------------
# Call model function
# -------------------------
result = flo_finance(staff_rate, agency_rate, rn_needed)

# -------------------------
# Display result + inputs in a styled box
# -------------------------
st.markdown("### 🔮 Model Output")
st.markdown(
	f"""
	<div style="
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 15px;
		margin-top: 10px;
		font-size: 18px;
		background-color: #f9f9f9;">
		<b>Model Result:</b> ${result:,.2f} <br>
		<b>Inputs:</b> Staff Labor Rate: ${staff_rate:,.2f}, Agency Labor Rate: ${agency_rate:,.2f}, Estimated RN Need: {rn_needed:,.2f}
	</div>
	""",
	unsafe_allow_html=True
)


