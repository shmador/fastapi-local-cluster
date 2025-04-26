# Directory structure
# .
# ├── app
# │   └── main.py
# ├── requirements.txt
# └── .env.example

# app/main.py
import os
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

# Load your GitHub personal access token from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("Please set the GITHUB_TOKEN environment variable")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Default GitHub Actions workflow for Python linting on PRs
DEFAULT_WORKFLOW = '''name: CI Lint
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install flake8
      - name: Lint with flake8
        run: flake8 .
'''

class RepoCreate(BaseModel):
    name: str
    description: str = ""
    private: bool = False
    readme_content: str = "# Hello World"
    workflow_content: str = DEFAULT_WORKFLOW

@app.post("/repos/")
async def create_repo(repo: RepoCreate):
    async with httpx.AsyncClient() as client:
        # 1. Create the repository
        create_payload = {
            "name": repo.name,
            "description": repo.description,
            "private": repo.private,
            "auto_init": False
        }
        resp = await client.post(
            "https://api.github.com/user/repos",
            json=create_payload,
            headers=HEADERS
        )
        if resp.status_code >= 300:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        owner = data["owner"]["login"]

        # 2. Create README.md
        readme_encoded = base64.b64encode(repo.readme_content.encode()).decode()
        readme_payload = {
            "message": "Add README.md",
            "content": readme_encoded
        }
        resp2 = await client.put(
            f"https://api.github.com/repos/{owner}/{repo.name}/contents/README.md",
            json=readme_payload,
            headers=HEADERS
        )
        if resp2.status_code >= 300:
            raise HTTPException(status_code=resp2.status_code, detail=resp2.text)

        # 3. Create GitHub Actions workflow
        workflow_path = ".github/workflows/lint.yml"
        workflow_encoded = base64.b64encode(repo.workflow_content.encode()).decode()
        workflow_payload = {
            "message": "Add CI workflow",
            "content": workflow_encoded
        }
        resp3 = await client.put(
            f"https://api.github.com/repos/{owner}/{repo.name}/contents/{workflow_path}",
            json=workflow_payload,
            headers=HEADERS
        )
        if resp3.status_code >= 300:
            raise HTTPException(status_code=resp3.status_code, detail=resp3.text)

    return {
        "repo_url": data["html_url"],
        "readme_url": resp2.json().get("content", {}).get("html_url"),
        "workflow_url": resp3.json().get("content", {}).get("html_url")
    }

# requirements.txt
# ----------------
# fastapi
# uvicorn[standard]
# httpx

# .env.example
# ----------------
# GITHUB_TOKEN=ghp_your_personal_access_token_here

