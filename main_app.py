# write an app that do the following:
# streamlit for UI
# each calcultaion in diffrent function
# Target function : QALY ( show also graphs in plotly )
# Suffer integral ( Show also graph in plotly )
# parameters to take into account in the calculation:
# Mirles
# Physical - weight, muscle strength, bone strength
# Activity - to quantify from articles
# Cancer characteristics - pace , direction, the bone strength, SFR - Zohar
# the final product - these are the parameters, this is the way inserted to the model , what parameter has highest impact
# we want to help doctors, the one that add data on peppole with this cancer. to emphsis the assumptions on things we don't know
#
# all the app should be on git and its environment should be declerd properly
import streamlit as st
import numpy as np

st.set_page_config(page_title="QALY Decision Support System", layout="wide")
st.title("🧠 QALY-Based Surgical Decision Support System")

# ----------------- Section: Model Weights ----------------- #
st.sidebar.header("⚖️ Model Weights")
alpha = st.sidebar.number_input("α (Weight for FRAX)", value=0.05)
beta = st.sidebar.number_input("β (Weight for SFR)", value=0.3)
gamma = st.sidebar.number_input("γ (Weight for Mirels)", value=0.2)
delta = st.sidebar.number_input("δ (Weight for Age)", value=0.02)
epsilon = st.sidebar.number_input("ε (Weight for Gender)", value=0.1)
xi = st.sidebar.number_input("ξ (Weight for Frailty)", value=0.15)
psi = st.sidebar.number_input("ψ (Weight for Nutrition)", value=0.1)

theta_H, theta_L = 0.3, -0.3
D_int = 0.05
Q_noFx = 0.85
Q_Fx = lambda age: 0.5 - 0.002 * age

# ----------------- Section: Patient Demographics ----------------- #
st.sidebar.header("👤 Patient Demographics")
age = st.sidebar.slider("Age", 40, 100, 65)
gender = st.sidebar.radio("Gender", ["Male", "Female"])
gender_numeric = 1 if gender == "Female" else 0

# ----------------- Section: FRAX ----------------- #
st.header("📊 FRAX Score")
st.markdown("**FRAX** estimates the 10-year probability of fracture using clinical risk factors. It influences how much the system expects the patient to benefit from surgery by estimating baseline risk.")

bmi = st.slider("BMI", 15.0, 40.0, 25.0)
prev_fracture = st.checkbox("Previous Fracture")
smoking = st.checkbox("Smoking")
steroids = st.checkbox("Steroid Use")
alcohol = st.checkbox("Alcohol Use")
rheumatoid = st.checkbox("Rheumatoid Arthritis")
secondary_osteoporosis = st.checkbox("Secondary Osteoporosis")

FRAX = (0.1 * age) + (0.05 * bmi) + (5 if prev_fracture else 0) + \
       (3 if smoking else 0) + (4 if steroids else 0) + (2 if alcohol else 0) + \
       (3 if rheumatoid else 0) + (2 if secondary_osteoporosis else 0)
st.success(f"Calculated FRAX Score: {FRAX:.2f}")

# ----------------- Section: SFR ----------------- #
st.header("🦴 SFR (Strain Fold Ratio)")
st.markdown("**SFR** is calculated from CT scans and reflects biomechanical stress. High SFR implies structural instability, contributing to surgery recommendation.")

strain_lesion = st.slider("Strain in Lesion Region", 0.0, 3.0, 1.5)
strain_healthy = st.slider("Strain in Healthy Bone", 0.1, 3.0, 1.0)
ct_machine_factor = st.slider("CT Machine Correction Factor", 0.5, 1.5, 1.0)

SFR_raw = strain_lesion / strain_healthy
SFR = SFR_raw * ct_machine_factor
st.success(f"Adjusted SFR: {SFR:.2f}")

# ----------------- Section: Mirels ----------------- #
st.header("📋 Mirels Score")
st.markdown("**Mirels Score** combines radiographic and clinical parameters to assess fracture risk. It includes pain, lesion type, size, bone destruction, and more.")

site = st.selectbox("Lesion Site", ["Upper Limb", "Lower Limb", "Trochanteric"])
lesion_type = st.selectbox("Lesion Type", ["Blastic", "Mixed", "Lytic"])
pain = st.selectbox("Pain Level", ["None", "Mild", "Severe"])
size = st.selectbox("Lesion Size", ["<1/3", "1/3-2/3", ">2/3"])
cortical_loss = st.checkbox("Cortical Loss")
neuro_deficit = st.checkbox("Neurological Deficit")
bone_destruction = st.checkbox("Extensive Bone Destruction")
multiple_lesions = st.checkbox("Multiple Lesions")
mobility_restriction = st.checkbox("Mobility Restriction")

mirels_score = {
    "Upper Limb": 1, "Lower Limb": 2, "Trochanteric": 3
}[site] + {
    "Blastic": 1, "Mixed": 2, "Lytic": 3
}[lesion_type] + {
    "None": 1, "Mild": 2, "Severe": 3
}[pain] + {
    "<1/3": 1, "1/3-2/3": 2, ">2/3": 3
}[size] + sum([
    cortical_loss, neuro_deficit, bone_destruction,
    multiple_lesions, mobility_restriction
])

st.success(f"Mirels Score: {mirels_score}")

# ----------------- Section: Frailty ----------------- #
st.header("🧓 Frailty Index")
st.markdown("**Frailty** is a multi-factor index assessing vulnerability based on common geriatric indicators.")

frailty_components = {
    "Unintentional weight loss": st.checkbox("Unintentional weight loss"),
    "Exhaustion": st.checkbox("Self-reported exhaustion"),
    "Weak grip strength": st.checkbox("Weak grip strength"),
    "Slow walking speed": st.checkbox("Slow walking speed"),
    "Low physical activity": st.checkbox("Low physical activity"),
    "Cognitive impairment": st.checkbox("Cognitive impairment"),
    "Polypharmacy (≥5 medications)": st.checkbox("Polypharmacy"),
    "Falls in past year": st.checkbox("Falls in past year"),
    "Incontinence": st.checkbox("Incontinence"),
    "Dependence in daily activities": st.checkbox("Dependence in ADLs")
}

frailty_score = sum(1 for v in frailty_components.values() if v) / 10.0
st.success(f"Frailty Index: {frailty_score:.2f}")

# ----------------- Section: Nutrition ----------------- #
st.header("🥗 Nutrition Score")
st.markdown("**Nutrition** impacts healing and recovery. Low values reduce expected post-surgical quality of life.")

albumin = st.slider("Albumin Level (g/dL)", 2.0, 5.0, 4.0)
weight_stability = st.selectbox("Weight Stability", ["Stable", "Mild Loss", "Significant Loss"])
oral_intake = st.selectbox("Oral Intake", ["Full", "Partial", "Minimal"])

nutrition_score = (0.4 * albumin) + {
    "Stable": 0.4, "Mild Loss": 0.2, "Significant Loss": 0.0
}[weight_stability] + {
    "Full": 0.4, "Partial": 0.2, "Minimal": 0.0
}[oral_intake]

st.success(f"Nutrition Score: {nutrition_score:.2f}")

# ----------------- Final QALY Calculation ----------------- #
st.header("📈 QALY & Decision Recommendation")
p_f = 1 - np.exp(-(alpha * FRAX + beta * SFR + gamma * mirels_score +
                   delta * age + epsilon * gender_numeric + xi * frailty_score + psi * nutrition_score))
p_f_star = p_f * 0.3

q_no = p_f * Q_Fx(age) + (1 - p_f) * Q_noFx
q_int = p_f_star * Q_Fx(age) + (1 - p_f_star) * Q_noFx - D_int
delta_q = q_int - q_no

st.metric("QALY (No Surgery)", round(q_no, 3))
st.metric("QALY (With Surgery)", round(q_int, 3))
st.metric("ΔQALY (Net Gain)", round(delta_q, 3))

# ----------------- Decision Logic ----------------- #
if delta_q > theta_H:
    st.success("✅ Recommendation: Proceed with Surgery (High Confidence)")
    st.markdown("**Explanation**: Surgery is predicted to offer significant improvement in quality-adjusted life expectancy. Confidence is high based on patient risk and benefit profile.")
elif delta_q < theta_L:
    st.error("🚫 Recommendation: Avoid Surgery (High Confidence)")
    st.markdown("**Explanation**: Risk factors suggest surgery may do more harm than good in terms of QALY outcomes.")
else:
    st.warning("⚠️ Recommendation: Requires Shared Decision (Moderate Confidence)")
    st.markdown("**Next Steps**:\n- Discuss risks and benefits with the care team.\n- Consider patient values and preferences.\n- Seek additional imaging or specialist consultation.")

