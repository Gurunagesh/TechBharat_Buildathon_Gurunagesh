"""
integrations/github_service.py
──────────────────────────────
GitHub Issues Integration Service.

Uses PyGithub library to create Issues on the configured GitHub repository.
Called exclusively by SyncService — never directly from an API endpoint.

Environment Requirements:
- GITHUB_TOKEN: Personal Access Token with `repo` scope
- GITHUB_REPO: "owner/repo" format
"""

from typing import Optional, Dict, Any
from datetime import date
from github import Github, GithubException

from app.core.config import settings
from app.core.logging import get_logger, LogEvent

logger = get_logger(__name__)


class GitHubService:
    """Service for creating GitHub Issues from approved action items."""

    @staticmethod
    def create_issue_for_action_item(
        title: str,
        description: Optional[str] = None,
        owner: str = "UNASSIGNED",
        due_date: Optional[date] = None,
        priority: str = "MEDIUM",
        evidence_quote: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a GitHub Issue for a single approved action item.

        Args:
            title: Issue title (action item task title).
            description: Extended description (optional).
            owner: Assigned owner name.
            due_date: ISO due date.
            priority: Priority level string (HIGH, MEDIUM, LOW).
            evidence_quote: Transcript evidence quote for traceability.

        Returns:
            Dict with keys: number, url, title

        Raises:
            Exception: On GitHub API failure (caught by SyncService).
        """
        if not settings.github_token or not settings.github_repo:
            raise ValueError("GITHUB_TOKEN or GITHUB_REPO is not configured.")

        # Build the Issue body with structured markdown
        body_parts = [
            f"## Action Item: {title}",
            "",
            f"**Assigned To:** {owner}",
            f"**Priority:** {priority}",
            f"**Due Date:** {due_date if due_date else 'Not specified'}",
        ]

        if description:
            body_parts.extend(["", "### Description", description])

        if evidence_quote:
            body_parts.extend([
                "",
                "### 📎 Transcript Evidence",
                f"> {evidence_quote}",
            ])

        body_parts.extend([
            "",
            "---",
            "*Created by [AI Meeting Assistant](https://github.com/TechBharat) — TechBharat Buildathon*",
        ])

        issue_body = "\n".join(body_parts)

        # Determine labels
        labels = [f"priority:{priority.lower()}"]
        labels.append("ai-generated")

        try:
            g = Github(settings.github_token)
            repo = g.get_repo(settings.github_repo)

            issue = repo.create_issue(
                title=f"[Action Item] {title}",
                body=issue_body,
                labels=labels,
            )

            logger.info(
                f"[{LogEvent.GITHUB_SUCCESS}] Created GitHub Issue #{issue.number}: {issue.html_url}"
            )

            return {
                "number": issue.number,
                "url": issue.html_url,
                "title": issue.title,
            }

        except GithubException as gh_err:
            logger.error(f"[{LogEvent.GITHUB_FAILURE}] GitHub API error: {gh_err}")
            raise Exception(f"GitHub API error ({gh_err.status}): {gh_err.data.get('message', str(gh_err))}")
        except Exception as exc:
            logger.error(f"[{LogEvent.GITHUB_FAILURE}] GitHub integration error: {exc}")
            raise
