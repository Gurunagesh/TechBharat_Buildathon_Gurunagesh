"""
components/action_table.py
───────────────────────────
Human Review Action Items Component.

Features:
- Visual separation by state tabs: Pending Review, Approved, Rejected, Synced
- Inline editing of Owner, Due Date, and Priority
- Per-item Approve / Reject action buttons
- Evidence Quote Inspection Drawer (transcript snippet + confidence score indicator)
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import date
from utils.api_client import APIClient
from components.status_badges import render_action_status_badge, render_priority_badge


def render_action_items_tab(meeting_id: str):
    """Render the human review action items tab."""
    items = APIClient.get_action_items(meeting_id)

    if not items:
        st.info("No action items extracted for this meeting.")
        return

    # Categorize items by status
    pending = [i for i in items if i.get("status") == "PENDING_REVIEW"]
    approved = [i for i in items if i.get("status") == "APPROVED"]
    rejected = [i for i in items if i.get("status") == "REJECTED"]
    synced = [i for i in items if i.get("status") == "SYNCED"]

    # Tabbed sections for review clarity
    t_pending, t_approved, t_synced, t_rejected = st.tabs([
        f"⏳ Pending Review ({len(pending)})",
        f"✅ Approved ({len(approved)})",
        f"🐙 Synced ({len(synced)})",
        f"❌ Rejected ({len(rejected)})",
    ])

    with t_pending:
        if pending:
            st.markdown("##### ⏳ Action Items Awaiting Your Review")
            st.caption("Edit owner or date if needed, then click **Approve** or **Reject**.")
            for item in pending:
                _render_single_action_card(item, meeting_id, allow_review=True)
        else:
            st.success("🎉 All items have been reviewed!")

    with t_approved:
        if approved:
            st.markdown("##### ✅ Approved Action Items (Ready to Sync)")
            st.caption("These items are approved and will be created as GitHub Issues when you sync.")
            for item in approved:
                _render_single_action_card(item, meeting_id, allow_review=False)
        else:
            st.info("No items currently approved. Review pending items above.")

    with t_synced:
        if synced:
            st.markdown("##### 🐙 Action Items Synced to GitHub")
            for item in synced:
                _render_single_action_card(item, meeting_id, allow_review=False)
        else:
            st.caption("No items synced yet.")

    with t_rejected:
        if rejected:
            st.markdown("##### ❌ Rejected Action Items")
            for item in rejected:
                _render_single_action_card(item, meeting_id, allow_review=False)
        else:
            st.caption("No items rejected.")


def _render_single_action_card(item: Dict[str, Any], meeting_id: str, allow_review: bool):
    """Render a single action item review card with inline edit and evidence drawer."""
    item_id = item["action_item_id"]

    with st.container(border=True):
        col_title, col_status = st.columns([3, 1])

        with col_title:
            st.markdown(f"#### 📌 {item.get('title')}")
        with col_status:
            render_action_status_badge(item.get("status", "PENDING_REVIEW"))

        # Metadata Row
        col_owner, col_date, col_prio, col_conf = st.columns(4)

        with col_owner:
            owner_val = item.get("owner", "UNASSIGNED")
            if owner_val == "UNASSIGNED":
                st.markdown("👤 Owner: :red[**UNASSIGNED**]")
            else:
                st.markdown(f"👤 Owner: **{owner_val}**")

        with col_date:
            due = item.get("due_date")
            st.markdown(f"📅 Due Date: `{due if due else 'Not set'}`")

        with col_prio:
            st.markdown(f"⚡ Priority: {render_priority_badge(item.get('priority', 'MEDIUM'))}")

        with col_conf:
            conf = item.get("confidence_score", 0.0)
            conf_percent = int(conf * 100)
            if conf >= 0.70:
                st.markdown(f"🎯 AI Confidence: :green[**{conf_percent}%**]")
            else:
                st.markdown(f"🎯 AI Confidence: :red[**{conf_percent}% (Low)**]")

        # ── Evidence Quote Inspection Drawer ───────────────────────────
        quote = item.get("evidence_quote")
        if quote:
            with st.expander("🔍 View Transcript Evidence Quote"):
                st.info(f'"{quote}"')
                if item.get("github_sync") and item["github_sync"].get("github_issue_url"):
                    st.markdown(
                        f"🔗 **GitHub Issue:** [{item['github_sync']['github_issue_url']}]"
                        f"({item['github_sync']['github_issue_url']})"
                    )

        # ── Inline Edit & Review Actions ──────────────────────────────
        if allow_review:
            st.divider()
            with st.expander("✏️ Edit Task Details"):
                with st.form(key=f"edit_form_{item_id}"):
                    e_col1, e_col2, e_col3 = st.columns(3)
                    with e_col1:
                        new_owner = st.text_input("Owner Name", value=item.get("owner", ""))
                    with e_col2:
                        current_due = date.fromisoformat(item["due_date"]) if item.get("due_date") else None
                        new_date = st.date_input("Due Date", value=current_due)
                    with e_col3:
                        prio_opts = ["HIGH", "MEDIUM", "LOW"]
                        curr_prio_idx = prio_opts.index(item.get("priority", "MEDIUM"))
                        new_prio = st.selectbox("Priority", options=prio_opts, index=curr_prio_idx)

                    submit_edit = st.form_submit_button("Save Edits")
                    if submit_edit:
                        date_str = str(new_date) if new_date else None
                        ok, _, msg = APIClient.edit_action_item(
                            action_id=item_id,
                            owner=new_owner,
                            due_date=date_str,
                            priority=new_prio,
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            # Approve / Reject Button Row
            btn_col1, btn_col2, _ = st.columns([1, 1, 2])
            with btn_col1:
                if st.button("✅ Approve Task", key=f"btn_approve_{item_id}", type="primary"):
                    ok, _, msg = APIClient.approve_action_item(item_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with btn_col2:
                if st.button("❌ Reject Task", key=f"btn_reject_{item_id}"):
                    ok, _, msg = APIClient.reject_action_item(item_id)
                    if ok:
                        st.info(msg)
                        st.rerun()
                    else:
                        st.error(msg)
