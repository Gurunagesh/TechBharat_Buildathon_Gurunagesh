"""
services/business/sync_service.py
──────────────────────────────────
External Tool Synchronization Service.

Coordinates sending APPROVED action items to external tool integrations (GitHub Issues).

Rules:
- ONLY items with status == APPROVED are eligible for sync.
- Zero unapproved actions rule is strictly enforced.
- Updates GitHubSync table with ticket URL/number.
- Transitions ActionItem status: APPROVED -> SYNCED via StateMachine.
- Records GITHUB_SUCCESS or GITHUB_FAILURE in audit log.
- Respects settings.enable_github kill switch for demo safety.
"""

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.models import ActionItem, GitHubSync, Meeting
from app.models.enums import ActionStatus, SyncStatus, AuditEventType, AuditActor
from app.workflow.state_machine import StateMachine
from app.services.business.audit_service import AuditService
from app.integrations.github_service import GitHubService
from app.core.config import settings
from app.core.exceptions import ActionItemNotFoundError, MeetingNotFoundError, GitHubSyncError
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class SyncService:
    """Service orchestrating external tool integrations (GitHub Issues)."""

    @staticmethod
    def sync_meeting_approved_items(
        db: Session, meeting_id: str, actor: str = "Human Approver"
    ) -> List[Dict[str, Any]]:
        """
        Sync all APPROVED action items for a meeting to GitHub Issues.

        Returns list of sync result summary dicts.
        """
        meeting = db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first()
        if not meeting:
            raise MeetingNotFoundError(meeting_id)

        # Retrieve strictly APPROVED items (Zero Unapproved Actions guardrail)
        approved_items = (
            db.query(ActionItem)
            .filter(
                ActionItem.meeting_id == meeting_id,
                ActionItem.status == ActionStatus.APPROVED,
            )
            .all()
        )

        if not approved_items:
            logger.info(f"[SYNC] No APPROVED action items to sync for meeting '{meeting_id[:8]}'")
            return []

        results = []
        for item in approved_items:
            res = SyncService.sync_single_action_item(db=db, item=item, actor=actor)
            results.append(res)

        return results

    @staticmethod
    def sync_single_action_item(
        db: Session, item: ActionItem, actor: str = "Human Approver"
    ) -> Dict[str, Any]:
        """
        Sync one APPROVED action item to GitHub Issues.

        Updates GitHubSync table, transitions item state to SYNCED, and writes audit log.
        """
        if item.status != ActionStatus.APPROVED:
            logger.warning(
                f"[SYNC_BLOCKED] Action item '{item.action_item_id[:8]}' "
                f"cannot sync — status is '{item.status.value}', not 'APPROVED'"
            )
            return {
                "action_item_id": item.action_item_id,
                "status": "BLOCKED",
                "reason": f"Item status is {item.status.value}, not APPROVED",
            }

        # Check feature kill switch
        if not settings.enable_github:
            logger.warning("[SYNC_DISABLED] ENABLE_GITHUB is False in settings — mock sync mode")
            return SyncService._mock_sync_success(db, item, actor)

        # Fetch or create GitHubSync record
        sync_record = (
            db.query(GitHubSync)
            .filter(GitHubSync.action_item_id == item.action_item_id)
            .first()
        )
        if not sync_record:
            sync_record = GitHubSync(
                action_item_id=item.action_item_id,
                sync_status=SyncStatus.PENDING,
            )
            db.add(sync_record)

        try:
            # Invoke PyGithub integration service
            issue_data = GitHubService.create_issue_for_action_item(
                title=item.title,
                description=item.description,
                owner=item.owner,
                due_date=item.due_date,
                priority=item.priority.value,
                evidence_quote=item.evidence_quote,
            )

            # Update sync record
            sync_record.github_issue_number = issue_data["number"]
            sync_record.github_issue_url = issue_data["url"]
            sync_record.github_issue_title = issue_data["title"]
            sync_record.sync_status = SyncStatus.SUCCESS
            sync_record.synced_at = datetime.utcnow()
            sync_record.error_message = None

            # Transition ActionItem status APPROVED -> SYNCED via StateMachine
            StateMachine.transition_action_item(item, ActionStatus.SYNCED)

            # Audit event
            AuditService.log_event(
                db=db,
                meeting_id=item.meeting_id,
                action_item_id=item.action_item_id,
                event_type=AuditEventType.GITHUB_SUCCESS,
                actor=AuditActor.HUMAN_USER,
                payload={
                    "issue_number": issue_data["number"],
                    "issue_url": issue_data["url"],
                    "synced_by": actor,
                },
            )

            db.commit()
            db.refresh(item)
            logger.info(
                f"[{LogEvent.GITHUB_SUCCESS}] Action item '{item.action_item_id[:8]}' "
                f"synced to GitHub Issue #{issue_data['number']} ({issue_data['url']})"
            )
            return {
                "action_item_id": item.action_item_id,
                "status": "SUCCESS",
                "issue_number": issue_data["number"],
                "issue_url": issue_data["url"],
            }

        except Exception as exc:
            db.rollback()
            sync_record.sync_status = SyncStatus.FAILED
            sync_record.error_message = str(exc)
            db.add(sync_record)

            AuditService.log_event(
                db=db,
                meeting_id=item.meeting_id,
                action_item_id=item.action_item_id,
                event_type=AuditEventType.GITHUB_FAILURE,
                actor=AuditActor.SYSTEM,
                payload={"error": str(exc)},
            )
            db.commit()
            logger.error(f"[{LogEvent.GITHUB_FAILURE}] GitHub sync failed for item '{item.action_item_id[:8]}': {exc}")
            return {
                "action_item_id": item.action_item_id,
                "status": "FAILED",
                "error": str(exc),
            }

    @staticmethod
    def _mock_sync_success(db: Session, item: ActionItem, actor: str) -> Dict[str, Any]:
        """Mock sync response when ENABLE_GITHUB = False."""
        mock_number = 999
        mock_url = f"https://github.com/mock/{settings.github_repo}/issues/{mock_number}"

        sync_record = (
            db.query(GitHubSync)
            .filter(GitHubSync.action_item_id == item.action_item_id)
            .first()
        )
        if not sync_record:
            sync_record = GitHubSync(action_item_id=item.action_item_id)
            db.add(sync_record)

        sync_record.github_issue_number = mock_number
        sync_record.github_issue_url = mock_url
        sync_record.github_issue_title = item.title
        sync_record.sync_status = SyncStatus.SUCCESS
        sync_record.synced_at = datetime.utcnow()

        StateMachine.transition_action_item(item, ActionStatus.SYNCED)
        AuditService.log_event(
            db=db,
            meeting_id=item.meeting_id,
            action_item_id=item.action_item_id,
            event_type=AuditEventType.GITHUB_SUCCESS,
            actor=AuditActor.HUMAN_USER,
            payload={"mock": True, "issue_url": mock_url},
        )
        db.commit()
        return {
            "action_item_id": item.action_item_id,
            "status": "SUCCESS",
            "issue_number": mock_number,
            "issue_url": mock_url,
            "mock": True,
        }
