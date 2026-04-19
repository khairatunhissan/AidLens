import streamlit as st
from config import MAJOR_OPTIONS, RACE_OPTIONS, GENDER_OPTIONS


def render_input_page(state):
    st.markdown("## Applicant Input")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown("**Academic + Basic Information**")
        state["gpa"] = st.slider("High School GPA", 0.0, 4.0, float(state["gpa"]), 0.01)
        state["residency"] = st.selectbox(
            "Residency",
            ["In-state", "Out-of-state"],
            index=0 if state["residency"] == "In-state" else 1,
        )
        major_index = (
            MAJOR_OPTIONS.index(state["major"])
            if state["major"] in MAJOR_OPTIONS
            else 0
        )
        state["major"] = st.selectbox("Intended Major", MAJOR_OPTIONS, index=major_index)
        state["predicted_enrollment_probability"] = st.slider(
            "Predicted Enrollment Probability",
            0,
            100,
            int(state["predicted_enrollment_probability"]),
            1,
        )
        state["extracurricular_score"] = st.slider(
            "Extracurricular Strength",
            1,
            5,
            int(state["extracurricular_score"]),
            1,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown("**Financial Information**")
        state["family_income"] = st.number_input(
            "Family Income",
            min_value=0,
            value=int(state["family_income"]),
            step=1000,
        )
        state["financial_need"] = st.number_input(
            "Financial Need",
            min_value=0,
            value=int(state["financial_need"]),
            step=500,
        )
        state["requested_aid"] = st.number_input(
            "Requested Aid",
            min_value=0,
            value=int(state["requested_aid"]),
            step=500,
        )
        need_level_options = ["Low", "Medium", "High"]
        need_index = (
            need_level_options.index(state["need_level"])
            if state["need_level"] in need_level_options
            else 2
        )
        state["need_level"] = st.selectbox(
            "Need Level",
            need_level_options,
            index=need_index,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='help-box'><b>Fairness-only fields</b><br>These are displayed for fairness comparison and transparency. They are not used in the main recommendation.</div>",
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        gender_index = (
            GENDER_OPTIONS.index(state["gender"])
            if state["gender"] in GENDER_OPTIONS
            else 0
        )
        state["gender"] = st.selectbox("Gender", GENDER_OPTIONS, index=gender_index)

    with f2:
        race_index = (
            RACE_OPTIONS.index(state["race"])
            if state["race"] in RACE_OPTIONS
            else 0
        )
        state["race"] = st.selectbox("Race / Ethnicity", RACE_OPTIONS, index=race_index)

    with f3:
        first_gen_options = ["Yes", "No"]
        fg_index = (
            first_gen_options.index(state["first_gen"])
            if state["first_gen"] in first_gen_options
            else 0
        )
        state["first_gen"] = st.selectbox(
            "First-generation status",
            first_gen_options,
            index=fg_index,
        )

    st.markdown(
        "<div class='help-box'>Enter or adjust applicant input, then click the button to generate a recommendation.</div>",
        unsafe_allow_html=True,
    )

    clicked = st.button("Generate Result")
    return clicked