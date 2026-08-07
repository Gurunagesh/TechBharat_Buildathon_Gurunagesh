"""
components/sync_panel.py
────────────────────────
GitHub Sync Panel Component.

Renders:
- Synchronization stats (Approved, Synced, Pending)
- "Sync Approved Items to GitHub" button
- List of created GitHub Issue URLs
"""

import streamlit as st
from typing import Dict, Any
from utils.api_client import APIClient


def render_github_sync_tab(meeting_id: str):
    """Render GitHub Integration sync panel."""
    st.subheader("🐙 GitHub Integration Sync")
    st.caption(
        "Zero Unapproved Actions Rule: Only items marked **APPROVED** during human review "
        "will be sent to GitHub Issues."
    )

    items = APIClient.get_action_items(meeting_id)

    approved = [i for i in items if i.get("status") == "APPROVED"]
    synced = [i for i in items if i.get("status") == "SYNCED"]
    pending = [i for i in items if i.get("status") == "PENDING_REVIEW"]

    # Stats Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Approved (Ready to Sync)", len(approved))
    with c2:
        st.metric("Already Synced to GitHub", len(synced))
    with c3:
        st.metric("Pending Review", len(pending))

    st.divider()

    # Sync Action Panel
    if approved:
        st.success(f"**{len(approved)}** task(s) are approved and ready to be created as GitHub Issues.")
        if st.button("🚀 Sync Approved Items to GitHub", type="primary", key="btn_sync_github"):
            with st.spinner("Creating GitHub Issues..."):
                ok, data, msg = APIClient.sync_meeting_github(meeting_id)
                if ok:
                    st.balloons()
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    else:
        st.info("No tasks are currently approved for sync. Review and approve pending tasks in the **Action Items** tab first.")

    # Show existing synced GitHub issues list
    if synced:
        st.markdown("### 🔗 Created GitHub Issues")
        for item in synced:
            sync_info = item.get("github_sync") or {}
            issue_url = sync_info.get("github_issue_url") or "#"
            issue_num = sync_info.get("github_issue_number") or "Issue"
            st.markdown(
                f"- **{item.get('title')}** → "
                f"[Issue #{issue_num}]({issue_url}) "
                f"*(Owner: {item.get('owner')})*"
            )
