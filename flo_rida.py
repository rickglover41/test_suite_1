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
mode = st.radio("Select mode", ["Health System", "Individual Hospital"])

# -------------------------
# Function to display styled read-only fields
# -------------------------
def styled_readonly(label, value):
	st.markdown(
		f"""
		<div style="
			background-color: #f2f2f2;
			padding: 8px 12px;
			border-radius: 5px;
			margin-bottom: 5px;
			font-size: 16px;
			word-wrap: break-word;">
			<b>{label}:</b> {value}
		</div>
		""",
		unsafe_allow_html=True
	)
	
# -------------------------
# Get defaults based on mode
# -------------------------
if mode == "Health System":
	name_lookup = {v["Health_System_Name"]: k for k, v in health_systems.items()}
	choice_name = st.selectbox("Choose a health system (type to search)", sorted(name_lookup.keys()))
	choice_key = name_lookup[choice_name]
	defaults = health_systems[choice_key]
	
	read_only_data = {
		"Health System Name": defaults["Health_System_Name"],
		"Bed Size": defaults["Bed_Size"],
		"States": defaults["State(s)"],
		"Affiliated Hospitals": defaults["Affiliated_Hospitals"]
	}
	
else:
	states = sorted(set(v["State"] for v in hospitals.values()))
	chosen_state = st.selectbox("Choose a state", states)
	hospitals_in_state = {k: v for k, v in hospitals.items() if v["State"] == chosen_state}
	sorted_hospitals = dict(sorted(hospitals_in_state.items(), key=lambda item: item[1]["Hospital_Name"]))
	name_lookup = {v["Hospital_Name"]: k for k, v in sorted_hospitals.items()}
	choice_name = st.selectbox("Choose a hospital (type to search)", sorted(name_lookup.keys()))
	choice_key = name_lookup[choice_name]
	defaults = hospitals[choice_key]
	
	read_only_data = {
		"Hospital Name": defaults["Hospital_Name"],
		"Bed Size": defaults["Bed_Size"],
		"State": defaults["State"]
	}
	
# -------------------------
# Layout: responsive columns
# -------------------------
with st.container():
	cols = st.columns([2, 2, 3])
	
	# Column 1: Read-only info
	with cols[0]:
		st.subheader("Information")
		for label, value in read_only_data.items():
			styled_readonly(label, value)
			
	# Column 2: Editable inputs
	with cols[1]:
		st.subheader("Editable Inputs")
		staff_rate = st.number_input(
			"Staff Labor Rate", 
			value=float(defaults["Staff_Labor_Rate"]), 
			format="$%.2f"
		)
		agency_rate = st.number_input(
			"Agency Labor Rate", 
			value=float(defaults["Agency_Labor_Rate"]), 
			format="$%.2f"
		)
		rn_needed = round(st.number_input(
			"Estimated RN Need", 
			value=float(defaults["Estimated_RN_Need"])
		), 1)
		
	# Column 3: Model output
	with cols[2]:
		st.subheader("🔮 Model Output")
		result = flo_finance(staff_rate, agency_rate, rn_needed)
		st.markdown(
			f"""
			<div style="
				border: 1px solid #ddd;
				border-radius: 8px;
				padding: 15px;
				font-size: 18px;
				background-color: #f9f9f9;
				word-wrap: break-word;">
				<b>Model Result:</b> ${result:,.2f} <br>
				<b>Inputs:</b> Staff Labor Rate: ${staff_rate:,.2f}, Agency Labor Rate: ${agency_rate:,.2f}, Estimated RN Need: {rn_needed:.1f}
			</div>
			""",
			unsafe_allow_html=True
		)
		
		