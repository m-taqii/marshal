import httpx
from lib.config import get_settings

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
        await self.client.aclose()

    async def get_pr_diff(self, owner: str, repo: str, pr_number: int):
        res = await self.client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
        res.raise_for_status()
        return res.json()

    async def post_comment(self, owner: str, repo: str, issue_number: int, body: str):
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )
        res.raise_for_status()
        return res.json()

    async def merge_pr(self, owner: str, repo: str, pr_number: int):
        res = await self.client.put(f"/repos/{owner}/{repo}/pulls/{pr_number}/merge")
        res.raise_for_status()
        return res.json()

    async def close_pr(self, owner: str, repo: str, pull_number: int):
        res = await self.client.patch(
            f"/repos/{owner}/{repo}/pulls/{pull_number}", json={"state": "closed"}
        )
        res.raise_for_status()
        return res.json()

    async def assign_issue(self, owner: str, repo: str, issue_number: int, assignee: str):
        res = await self.client.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/assignees",
            json={"assignees": [assignee]},
        )
        res.raise_for_status()
        return res.json()

    async def get_issue(self, owner: str, repo: str, issue_number: int):
        res = await self.client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")
        res.raise_for_status()
        return res.json()

    async def list_issues(self, owner: str, repo: str, state: str = "open"):
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

    async def list_pulls(self, owner: str, repo: str, state: str = "open"):
        res = await self.client.get(
            f"/repos/{owner}/{repo}/pulls", params={"state": state}
        )
        res.raise_for_status()
        return res.json()

    async def get_repo_collaborators(self, owner: str, repo: str):
        res = await self.client.get(f"/repos/{owner}/{repo}/collaborators")
        res.raise_for_status()
        return res.json()

    async def get_user(self, username: str):
        res = await self.client.get(f"/users/{username}")
        res.raise_for_status()
        return res.json()