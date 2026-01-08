import streamlit as st
import pandas as pd
from flo_finance import flo_finance

# -------------------------
# Page Config (must come first)
# -------------------------
st.set_page_config(
	page_title="Florence Financial Impact",
	layout="wide",  # nice wide layout for desktop
	initial_sidebar_state="collapsed"  # collapsed by default on mobile
)

# -------------------------
# Global CSS (mobile friendly tweaks)
# -------------------------
st.markdown(
	"""
	<style>
	/* Apply only on smaller screens */
	@media (max-width: 768px) {
		.block-container {
			padding-left: 0.5rem !important;
			padding-right: 0.5rem !important;
		}
		div[role="radiogroup"] label {
			font-size: 14px !important;
		}
		div[data-testid="stMarkdownContainer"] {
			font-size: 14px !important;
		}
		input[type="text"], input[type="number"] {
			font-size: 14px !important;
			padding: 4px !important;
		}
	}
	</style>
	""",
	unsafe_allow_html=True
)

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
st.caption("Note: If hospital or health system does not appear in the dropdown, there was no publicly reported Contracted Labor data to the HCRIS for that organization") 
mode = st.radio("Search for Health System or Hospital", ["Health System", "Individual Hospital"])

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
		"Bed Size": round(float(defaults["Bed_Size"])),
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
		"Bed Size": round(float(defaults["Bed_Size"])),
		"State": defaults["State"],
		"Health Care Affiliation": defaults.get("Health_System_Name", "N/A")
	}
	
# -------------------------
# Sidebar with Notations
# -------------------------
with st.sidebar.expander("ℹ️ Data & Calculation Notes", expanded=False):
	agency_fte = defaults.get("Agency_Labor_FTE", "N/A")
	try:
		agency_fte = round(float(agency_fte), 1)
	except:
		agency_fte = agency_fte
		
	st.markdown(
		f"""
		<div style="
			background-color: #b2dfdb;
			color: black;
			padding: 10px;
			border-radius: 5px;
			font-style: italic;
			line-height: 1.5;">
			<p>1. All rate and staffing information pulled from the Healthcare Cost Report Information System (HCRIS) FY2024. The reported Agency FTE use ({agency_fte}) was used to estimate the RN need (assuming 80% of the Agency FTEs were RNs working 1872 hours annually).</p>
			<p>2. Estimated savings is a 3 year calculation, measured using the difference between the current reported agency hourly rate and the one-time Florence fee amortized over that 3 year period added to the current reported staff hourly rate.</p>
		</div>
		""",
		unsafe_allow_html=True
	)
	
# -------------------------
# RN Need Display (always present)
# -------------------------
rn_needed = round(float(defaults.get("Estimated_RN_Need", 0)), 1)

# -------------------------
# Conditional Display Based on Agency>Staff
# -------------------------
agency_gt_staff = str(defaults.get("Agency>Staff", True)).lower() == "true"

if agency_gt_staff:
	# Staffing section
	st.subheader("Current Rates/Staffing (Can Edit)")
	
	st.markdown(
		"""
		<label style="font-weight: bold; font-size: 20px;">Estimated RN Need</label>
		""",
		unsafe_allow_html=True
	)
	rn_input_str = st.text_input(
		"", f"{rn_needed:.1f}", label_visibility="collapsed"
	)
	try:
		rn_needed = round(float(rn_input_str), 1)
	except:
		rn_needed = round(float(defaults["Estimated_RN_Need"]), 1)
		
	st.markdown(
		"""
		<style>
		input[type="text"] {
			font-weight: bold !important;
			font-size: 20px !important;
		}
		</style>
		""",
		unsafe_allow_html=True
	)
	
	staff_rate = st.number_input(
		"Staff Labor Rate ($)",
		value=float(defaults["Staff_Labor_Rate"]),
		step=0.01,
		format="%.2f"
	)
	agency_rate = st.number_input(
		"Agency Labor Rate ($)",
		value=float(defaults["Agency_Labor_Rate"]),
		step=0.01,
		format="%.2f"
	)
	
	st.markdown(
		"""
		<div style="
			border: 2px solid #444;
			padding: 10px 12px;
			border-radius: 5px;
			margin-top: 20px;
			margin-bottom: 10px;">
			<span style="font-weight: bold; font-size: 18px;">Florence Financial Savings</span>
		</div>
		""",
		unsafe_allow_html=True
	)
	
	result = flo_finance(staff_rate, agency_rate, rn_needed)
	
	st.markdown(
		f"""
		<div style="
			background-color: #d4edda;
			color: black;
			padding: 15px 14px;
			border-radius: 5px;
			margin-bottom: 12px;
			font-size: 20px;
			font-weight: bold;
			word-wrap: break-word;">
			Estimated Financial Savings Over Standard Agency: ${result:,.2f}
		</div>
		<div style="
			background-color: #d4edda;
			color: black;
			padding: 10px 12px;
			border-radius: 5px;
			margin-bottom: 8px;
			font-size: 16px;
			font-style: italic;
			word-wrap: break-word;">
			Inputs → Staff Labor Rate: ${staff_rate:,.2f}, Agency Labor Rate: ${agency_rate:,.2f}, Estimated RN Need: {rn_needed:.1f}
		</div>
		""",
		unsafe_allow_html=True
	)
	
else:
	st.markdown(
		f"""
		<div style="
			font-weight: bold;
			font-size: 28px;
			color: #0b6623;
			margin-bottom: 16px;">
			Estimated RN Need: {rn_needed:.1f}
		</div>
		<div style="
			font-size: 18px;
			font-weight: bold;
			color: #155724;
			background-color: #d4edda;
			padding: 12px;
			border-radius: 5px;
			line-height: 1.5;">
			For a one-time fee, Florence can fill your RN needs for 3 years, not just 12 weeks. Contact us today!
		</div>
		""",
		unsafe_allow_html=True
	)
	
# -------------------------
# Information Section (always at bottom)
# -------------------------
st.subheader("Information")
for label, value in read_only_data.items():
	styled_readonly(label, value)
	

	