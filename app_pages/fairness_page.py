import streamlit as st


def render_fairness_page(state):
    st.markdown("## Fairness Check")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown("**Comparison**")
        left, right = st.columns(2)
        with left:
            st.markdown(
                f"<div class='compare-box-orange'>With sensitive features<br><br>${state['aid_with_sensitive']:,}</div>",
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                f"<div class='compare-box-green'>Without sensitive features<br><br>${state['aid_without_sensitive']:,}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='inner-card'>", unsafe_allow_html=True)
        st.markdown("**Stability Summary**")
        if state["fairness_label"] == "stable":
            st.success(state["fairness_title"])
        else:
            st.warning(state["fairness_title"])
        st.write(state["fairness_text"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='help-box'><b>What counts as sensitive features?</b><br>For this prototype, sensitive features are gender, race/ethnicity, and first-generation status. They are displayed only for fairness comparison and not for the main recommendation.</div>",
        unsafe_allow_html=True,
    )