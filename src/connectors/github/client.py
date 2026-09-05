import httpx
from strands import tool
from src.lib.config import get_settings

GITHUB_API = "https://api.github.com"

class GithubClient:
    def __init__(self):
        settings = get_settings()
        self.client = httpx.AsyncClient(
            base_url=GITHUB_API,
            headers={
                "Authorization": f"Bearer {settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    async def close(self):
        """Close the underlying HTTP client session."""
        await self.client.aclose()

    async def get_authenticated_user(self):
        """Get the authenticated GitHub user profile."""
        res = await self.client.get("/user")
        res.raise_for_status()
        return res.json()

    @tool
    async def create_issue(self, owner: str, repo: str, title: str, body: str = ""):
        """Create a new issue in a GitHub repository.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            title: The title of the issue.
            body: The description or body content of the issue.
        """
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues",
            json={"title": title, "body": body},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def close_issue(self, owner: str, repo: str, issue_number: int):
        """Close an existing GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The number of the issue to close.
        """
        res = await self.client.patch(
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            json={"state": "closed"},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def reopen_issue(self, owner: str, repo: str, issue_number: int):
        """Reopen a closed GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The number of the issue to reopen.
        """
        res = await self.client.patch(
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            json={"state": "open"},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def post_comment(self, owner: str, repo: str, issue_number: int, body: str):
        """Post a comment on a GitHub issue or pull request.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue or pull request number.
            body: The text content of the comment.
        """
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def get_issue(self, owner: str, repo: str, issue_number: int):
        """Get details of a specific GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue number to retrieve.
        """
        res = await self.client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")
        res.raise_for_status()
        return res.json()

    @tool
    async def list_issues(self, owner: str, repo: str, state: str = "open"):
        """List issues in a GitHub repository (excludes pull requests).

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            state: Filter issues by state: 'open', 'closed', or 'all'. Defaults to 'open'.
        """
        items = []
        url = f"/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": 100}
        while url:
            res = await self.client.get(url, params=params)
            res.raise_for_status()
            items.extend(item for item in res.json() if "pull_request" not in item)
            url = res.links.get("next", {}).get("url")
            params = None
        return items

    @tool
    async def list_pulls(self, owner: str, repo: str, state: str = "open"):
        """List pull requests in a GitHub repository.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            state: Filter pull requests by state: 'open', 'closed', or 'all'. Defaults to 'open'.
        """
        res = await self.client.get(
            f"/repos/{owner}/{repo}/pulls", params={"state": state}
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def get_pr_diff(self, owner: str, repo: str, pr_number: int):
        """Get list of changed files and diff information for a pull request.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            pr_number: The pull request number.
        """
        res = await self.client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
        res.raise_for_status()
        return res.json()

    @tool
    async def merge_pr(self, owner: str, repo: str, pr_number: int):
        """Merge a pull request into the base branch.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            pr_number: The pull request number to merge.
        """
        res = await self.client.put(f"/repos/{owner}/{repo}/pulls/{pr_number}/merge")
        res.raise_for_status()
        return res.json()

    @tool
    async def close_pr(self, owner: str, repo: str, pull_number: int):
        """Close a pull request without merging it.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            pull_number: The pull request number to close.
        """
        res = await self.client.patch(
            f"/repos/{owner}/{repo}/pulls/{pull_number}", json={"state": "closed"}
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def assign_issue(self, owner: str, repo: str, issue_number: int, assignee: str):
        """Assign a user to a GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue number.
            assignee: The GitHub username to assign.
        """
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/assignees",
            json={"assignees": [assignee]},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def unassign_issue(self, owner: str, repo: str, issue_number: int, assignee: str):
        """Remove an assigned user from a GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue number.
            assignee: The GitHub username to unassign.
        """
        res = await self.client.request(
            "DELETE",
            f"/repos/{owner}/{repo}/issues/{issue_number}/assignees",
            json={"assignees": [assignee]},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def add_label(self, owner: str, repo: str, issue_number: int, label: str):
        """Add a label to a GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue number.
            label: The name of the label to add.
        """
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
            json={"labels": [label]},
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def remove_label(self, owner: str, repo: str, issue_number: int, label: str):
        """Remove a label from a GitHub issue.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
            issue_number: The issue number.
            label: The name of the label to remove.
        """
        res = await self.client.delete(
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}"
        )
        res.raise_for_status()
        return res.json()

    @tool
    async def get_repo_collaborators(self, owner: str, repo: str):
        """List collaborators for a GitHub repository.

        Args:
            owner: The repository owner or organization.
            repo: The repository name.
        """
        res = await self.client.get(f"/repos/{owner}/{repo}/collaborators")
        res.raise_for_status()
        return res.json()

    @tool
    async def get_user(self, username: str):
        """Get public profile information for a GitHub user.

        Args:
            username: The GitHub username.
        """
        res = await self.client.get(f"/users/{username}")
        res.raise_for_status()
        return res.json()

    def get_tools(self) -> list:
        """Return the list of tool-decorated methods for Strands Agent."""
        return [
            self.create_issue,
            self.close_issue,
            self.reopen_issue,
            self.post_comment,
            self.get_issue,
            self.list_issues,
            self.list_pulls,
            self.merge_pr,
            self.close_pr,
            self.assign_issue,
            self.unassign_issue,
            self.add_label,
            self.remove_label,
            self.get_pr_diff,
            self.get_repo_collaborators,
            self.get_user,
        ]