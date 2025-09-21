import streamlit as st
import pandas as pd
from flo_finance import flo_finance

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
			background-color: #cfe2f3;
			color: black;
			padding: 10px 12px;
			border-radius: 5px;
			margin-bottom: 8px;
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
# Display read-only info
# -------------------------
st.subheader("Information")
for label, value in read_only_data.items():
	styled_readonly(label, value)
	
# -------------------------
# Editable inputs
# -------------------------
st.subheader("Editable Inputs")

def dollar_input(label, value):
	"""Input with $ and commas. Returns float."""
	formatted_value = f"${value:,.2f}"
	input_str = st.text_input(label, formatted_value)
	numeric_str = input_str.replace("$", "").replace(",", "")
	try:
		return round(float(numeric_str), 2)
	except:
		return value
	
# Emphasized RN Need Input
st.markdown(
	f"""
	<div style="
		border: 2px solid #444;
		padding: 8px 10px;
		border-radius: 5px;
		margin-bottom: 12px;
	">
		<label style="font-weight: bold; font-size: 18px;">Estimated RN Need (FTE)</label>
	</div>
	""",
	unsafe_allow_html=True
)
rn_input_str = st.text_input(
	"", f"{float(defaults['Estimated_RN_Need']):.1f}", label_visibility="collapsed"
)
try:
	rn_needed = round(float(rn_input_str), 1)
except:
	rn_needed = round(float(defaults["Estimated_RN_Need"]), 1)
	
# Staff and Agency Rates
staff_rate = dollar_input("Staff Labor Rate", float(defaults["Staff_Labor_Rate"]))
agency_rate = dollar_input("Agency Labor Rate", float(defaults["Agency_Labor_Rate"]))

# -------------------------
# Model output
# -------------------------
st.markdown(
	"""
	<div style="
		border: 2px solid #444;
		padding: 10px 12px;
		border-radius: 5px;
		margin-top: 20px;
		margin-bottom: 10px;
	">
		<span style="font-weight: bold; font-size: 18px;">🔮 Model Output</span>
	</div>
	""",
	unsafe_allow_html=True
)

result = flo_finance(staff_rate, agency_rate, rn_needed)

st.markdown(
	f"""
	<div style="
		background-color: #cfe2f3;
		color: black;
		padding: 15px 14px;
		border-radius: 5px;
		margin-bottom: 12px;
		font-size: 20px;
		font-weight: bold;
		word-wrap: break-word;">
		Model Result: ${result:,.2f}
	</div>
	<div style="
		background-color: #cfe2f3;
		color: black;
		padding: 10px 12px;
		border-radius: 5px;
		margin-bottom: 8px;
		font-size: 16px;
		word-wrap: break-word;">
		Inputs → Staff Labor Rate: ${staff_rate:,.2f}, Agency Labor Rate: ${agency_rate:,.2f}, Estimated RN Need: {rn_needed:.1f}
	</div>
	""",
	unsafe_allow_html=True
)


