import streamlit as st


def render_recommendation_page(state):
    st.markdown("## Recommendation Result")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='metric-label'>Predicted Enrollment</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='metric-value'>{state['final_enrollment']}%</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='metric-sub'>{state['enrollment_label']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with m2:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='metric-label'>Recommended Aid</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='metric-value'>${state['recommended_aid']:,}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='metric-sub'>Annual Award</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with m3:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown("<div class='metric-label'>Summary</div>", unsafe_allow_html=True)
        summary_html = "<ul class='summary-list'>" + "".join(
            [f"<li>{item}</li>" for item in state["summary_lines"]]
        ) + "</ul>"
        st.markdown(summary_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='help-box'>This screen shows a simple recommended aid amount, a predicted enrollment signal, and a short summary of why the result was generated.</div>",
        unsafe_allow_html=True,
    )