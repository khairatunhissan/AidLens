import streamlit as st

from config import APP_TITLE
from ui.styles import apply_styles
from logic.scoring import compute_recommendation
from logic.fairness import fairness_summary
from logic.ai_explainer import (
    get_llm_explanation,
    build_explanation_prompt,
    get_llm_decision_support,
    get_llm_numeric_policy,
)
from app_pages.input_page import render_input_page
from app_pages.recommendation_page import render_recommendation_page
from app_pages.explanation_page import render_explanation_page
from app_pages.fairness_page import render_fairness_page

st.set_page_config(page_title="AidLens", layout="wide")
apply_styles()


def init_state():
    defaults = {
        "gpa": 3.78,
        "residency": "In-state",
        "family_income": 42000,
        "financial_need": 18500,
        "requested_aid": 12000,
        "need_level": "High",
        "major": "Computer Science",
        "predicted_enrollment_probability": 72,
        "extracurricular_score": 4,
        "gender": "Female",
        "race": "Asian",
        "first_gen": "Yes",
        "recommended_aid": 8000,
        "final_enrollment": 72,
        "enrollment_label": "Likely to enroll",
        "summary_lines": [],
        "generated": False,
        "ai_explanation": "",
        "aid_with_sensitive": 0,
        "aid_without_sensitive": 0,
        "fairness_label": "stable",
        "fairness_title": "",
        "fairness_text": "",
        "llm_prompt": "",
        "raw_llm_output": "",
        "feature_importance_without_sensitive": {},
        "feature_importance_with_sensitive": {},
        "decision_support_prompt": "",
        "raw_decision_support_output": "",
        "ai_reviewer_note": "",
        "numeric_policy_without_sensitive": {},
        "numeric_policy_with_sensitive": {},
        "numeric_policy_prompt_without_sensitive": "",
        "numeric_policy_prompt_with_sensitive": "",
        "raw_numeric_policy_output_without_sensitive": "",
        "raw_numeric_policy_output_with_sensitive": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def current_input_data():
    return {
        "gpa": st.session_state["gpa"],
        "residency": st.session_state["residency"],
        "family_income": st.session_state["family_income"],
        "financial_need": st.session_state["financial_need"],
        "requested_aid": st.session_state["requested_aid"],
        "need_level": st.session_state["need_level"],
        "major": st.session_state["major"],
        "predicted_enrollment_probability": st.session_state["predicted_enrollment_probability"],
        "extracurricular_score": st.session_state["extracurricular_score"],
        "gender": st.session_state["gender"],
        "race": st.session_state["race"],
        "first_gen": st.session_state["first_gen"],
    }


def run_pipeline():
    data = current_input_data()

    numeric_policy_without = get_llm_numeric_policy(data, use_sensitive=False)
    numeric_policy_with = get_llm_numeric_policy(data, use_sensitive=True)

    aid_without, enroll, enrollment_label, remaining_need, summary_lines, contrib_without = compute_recommendation(
        data,
        use_sensitive=False,
        numeric_policy=numeric_policy_without,
    )
    aid_with, _, _, _, _, contrib_with = compute_recommendation(
        data,
        use_sensitive=True,
        numeric_policy=numeric_policy_with,
    )

    fairness = fairness_summary(aid_with, aid_without)
    fairness_delta = aid_with - aid_without

    llm_output = get_llm_explanation(
        data,
        aid_without,
        enroll,
        fairness_delta,
    )
    prompt = build_explanation_prompt(
        data,
        aid_without,
        enroll,
        fairness_delta,
    )

    sorted_features = sorted(
        contrib_without.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    top_features = [name for name, _ in sorted_features[:3]]

    decision_output = get_llm_decision_support(
        data=data,
        recommended_aid=aid_without,
        enrollment=enroll,
        remaining_need=remaining_need,
        top_features=top_features,
        fairness_delta=fairness_delta,
    )

    final_enrollment_label = (
        decision_output["enrollment_text"].strip()
        if decision_output["enrollment_text"]
        else enrollment_label
    )

    final_summary_lines = (
        decision_output["summary_lines"]
        if decision_output["summary_lines"]
        else summary_lines
    )

    st.session_state["recommended_aid"] = aid_without
    st.session_state["final_enrollment"] = enroll
    st.session_state["enrollment_label"] = final_enrollment_label
    st.session_state["summary_lines"] = final_summary_lines
    st.session_state["generated"] = True
    st.session_state["ai_explanation"] = llm_output["explanation"]
    st.session_state["aid_with_sensitive"] = aid_with
    st.session_state["aid_without_sensitive"] = aid_without
    st.session_state["fairness_label"] = fairness["label"]
    st.session_state["fairness_title"] = fairness["title"]
    st.session_state["fairness_text"] = llm_output["fairness_text"]
    st.session_state["llm_prompt"] = prompt
    st.session_state["raw_llm_output"] = llm_output["raw_output"]
    st.session_state["feature_importance_without_sensitive"] = contrib_without
    st.session_state["feature_importance_with_sensitive"] = contrib_with
    st.session_state["decision_support_prompt"] = decision_output["prompt"]
    st.session_state["raw_decision_support_output"] = decision_output["raw_output"]
    st.session_state["ai_reviewer_note"] = decision_output["review_note"]

    st.session_state["numeric_policy_without_sensitive"] = {
        "base_award": numeric_policy_without["base_award"],
        "max_extra_award": numeric_policy_without["max_extra_award"],
        "aid_adjustment": numeric_policy_without["aid_adjustment"],
        "enrollment_adjustment": numeric_policy_without["enrollment_adjustment"],
    }
    st.session_state["numeric_policy_with_sensitive"] = {
        "base_award": numeric_policy_with["base_award"],
        "max_extra_award": numeric_policy_with["max_extra_award"],
        "aid_adjustment": numeric_policy_with["aid_adjustment"],
        "enrollment_adjustment": numeric_policy_with["enrollment_adjustment"],
    }
    st.session_state["numeric_policy_prompt_without_sensitive"] = numeric_policy_without["prompt"]
    st.session_state["numeric_policy_prompt_with_sensitive"] = numeric_policy_with["prompt"]
    st.session_state["raw_numeric_policy_output_without_sensitive"] = numeric_policy_without["raw_output"]
    st.session_state["raw_numeric_policy_output_with_sensitive"] = numeric_policy_with["raw_output"]


init_state()

st.sidebar.markdown("### AidLens")
page = st.sidebar.radio(
    "Navigation",
    [
        "Application Input",
        "Recommendation",
        "Explanation",
        "Fairness Check",
        "AI Proof",
    ],
    label_visibility="collapsed",
)

st.markdown(f"<div class='title-text'>{APP_TITLE}</div>", unsafe_allow_html=True)

if page == "Application Input":
    clicked = render_input_page(st.session_state)
    if clicked:
        run_pipeline()

elif page == "Recommendation":
    if not st.session_state["generated"]:
        run_pipeline()
    render_recommendation_page(st.session_state)

elif page == "Explanation":
    if not st.session_state["generated"]:
        run_pipeline()
    render_explanation_page(st.session_state)
    if st.session_state["ai_reviewer_note"]:
        st.markdown("### Reviewer Note")
        st.info(st.session_state["ai_reviewer_note"])

elif page == "Fairness Check":
    if not st.session_state["generated"]:
        run_pipeline()
    render_fairness_page(st.session_state)

else:
    if not st.session_state["generated"]:
        run_pipeline()

    st.markdown("## AI Proof of Concept")
    st.write(
        "This page documents the real LLM components used in the prototype. "
        "The system uses Groq-hosted LLM calls for numeric policy generation, feature importance, explanation generation, "
        "fairness interpretation, enrollment wording, recommendation summary bullets, and reviewer support text."
    )

    st.markdown("**Prompt used for the explanation module**")
    st.code(st.session_state["llm_prompt"])

    st.markdown("**Generated explanation output**")
    st.write(st.session_state["ai_explanation"])

    st.markdown("**Generated fairness interpretation**")
    st.write(st.session_state["fairness_text"])

    st.markdown("**Feature importance without sensitive features**")
    st.json(st.session_state["feature_importance_without_sensitive"])

    st.markdown("**Feature importance with sensitive features**")
    st.json(st.session_state["feature_importance_with_sensitive"])

    st.markdown("**LLM numeric policy without sensitive features**")
    st.json(st.session_state["numeric_policy_without_sensitive"])

    st.markdown("**LLM numeric policy with sensitive features**")
    st.json(st.session_state["numeric_policy_with_sensitive"])

    st.markdown("**Prompt used for numeric policy without sensitive features**")
    st.code(st.session_state["numeric_policy_prompt_without_sensitive"])

    st.markdown("**Prompt used for numeric policy with sensitive features**")
    st.code(st.session_state["numeric_policy_prompt_with_sensitive"])

    st.markdown("**Raw model output (numeric policy without sensitive features)**")
    st.code(st.session_state["raw_numeric_policy_output_without_sensitive"])

    st.markdown("**Raw model output (numeric policy with sensitive features)**")
    st.code(st.session_state["raw_numeric_policy_output_with_sensitive"])

    st.markdown("**Raw model output (explanation module)**")
    st.code(st.session_state["raw_llm_output"])

    st.markdown("**Prompt used for recommendation wording / decision support**")
    st.code(st.session_state["decision_support_prompt"])

    st.markdown("**Generated enrollment wording**")
    st.write(st.session_state["enrollment_label"])

    st.markdown("**Generated recommendation summary bullets**")
    st.write(st.session_state["summary_lines"])

    st.markdown("**Generated reviewer note**")
    st.write(st.session_state["ai_reviewer_note"])

    st.markdown("**Raw model output (decision support module)**")
    st.code(st.session_state["raw_decision_support_output"])