# FastAPI GitHub Repo Creator

This project creates a FastAPI app that allows you to:
1. Create a GitHub repository with a README file.
2. Add a workflow for checking Python code errors (using `flake8` in this case).
3. Deploy the FastAPI app to a local Kubernetes cluster using Kind or Minikube.

## How to Use

1. **Build the image:**
   ```bash
   docker build -t fastapi .
   ```

2. **Configure `k8s/secret.yaml`:**
   Update the GitHub token with your actual token.

3. **Create a local cluster (with Kind):**
   ```bash
   kind create cluster --name kind
   ```

4. **Apply manifests:**
   ```bash
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

5. **Run port forwarding:**
   ```bash
   kubectl port-forward svc/fastapi-service 8000:80
   ```

6. **Now you can access the API at `http://localhost:8000` or run a curl command:**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/repos/' \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -d '{
   "name": "string",
   "description": "",
   "private": false,
   "readme_content": "# Hello World",
   "workflow_content": "name: CI Lint\non: [pull_request]\njobs:\n  lint:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v3\n      - name: Set up Python\n        uses: actions/setup-python@v4\n        with:\n          python-version: '\''3.x'\''\n      - name: Install dependencies\n        run: pip install flake8\n      - name: Lint with flake8\n        run: flake8 .\n"
   }'
   ```

