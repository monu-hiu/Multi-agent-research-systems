import streamlit as st
from agents import build_search_agent, build_reader_agent, writter_chain, critic_chain

st.set_page_config(page_title="Research Pipeline", layout="wide")
st.title("🔎 AI Research Pipeline")

topic = st.text_input("Enter a research topic", placeholder="e.g. Impact of AI on climate modeling")
run_btn = st.button("Run Pipeline", type="primary", disabled=not topic)

if run_btn:
    state = {}

    # ---------- Step 1: Search agent ----------
    with st.status("Step 1 — Search agent gathering information...", expanded=True) as status:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_result["messages"][-1].content
        status.update(label="Step 1 — Search complete ✅", state="complete")

    with st.expander("🔍 Raw Search Results", expanded=True):
        st.markdown(state["search_results"])

    # ---------- Step 2: Reader agent ----------
    with st.status("Step 2 — Reader agent scraping deeper content...", expanded=True) as status:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )]
        })
        state["scraped_content"] = reader_result["messages"][-1].content
        status.update(label="Step 2 — Scraping complete ✅", state="complete")

    with st.expander("📄 Raw Scraped Content", expanded=True):
        st.markdown(state["scraped_content"])

    # ---------- Step 3: Writer chain ----------
    with st.status("Step 3 — Writer drafting the report...", expanded=True) as status:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = writter_chain.invoke({"topic": topic, "research": research_combined})
        status.update(label="Step 3 — Report drafted ✅", state="complete")

    st.subheader("📝 Final Report")
    st.markdown(state["report"])

    # ---------- Step 4: Critic chain ----------
    with st.status("Step 4 — Critic reviewing the report...", expanded=True) as status:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        status.update(label="Step 4 — Review complete ✅", state="complete")

    st.subheader("🧐 Critic Feedback")
    st.markdown(state["feedback"])

    st.success("Pipeline finished!")