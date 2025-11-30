# CI/CD Pipeline Setup Guide

This guide walks through setting up the GitHub Actions CI/CD pipeline and Harness integration for the Technology Risk Register application.

## Overview

The CI/CD pipeline consists of two workflows:
1. **CI Pipeline** (`.github/workflows/ci.yml`) - Validates pull requests
2. **CD Pipeline** (`.github/workflows/cd.yml`) - Builds and deploys to production

## Architecture

```
┌─────────────────┐
│  Pull Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  CI Workflow (PR Validation)        │
│  • Lint Backend (Black/Ruff/MyPy)   │
│  • Test Backend (90% coverage)      │
│  • Lint Frontend (ESLint/TS)        │
│  • Build Backend (Docker)           │
│  • Build Frontend (Vite)            │
└─────────────────────────────────────┘

┌─────────────────┐
│  Push to main   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  CD Workflow (Build & Deploy)       │
│  • All CI checks                    │
│  • Push to ghcr.io                  │
│  • Upload frontend artifact         │
│  • Trigger Harness webhook          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Harness Deployment                 │
│  • Pull image from ghcr.io          │
│  • Download frontend artifact       │
│  • Deploy to GCP Cloud Run          │
└─────────────────────────────────────┘
```

## Initial Setup

### 1. Configure GitHub Repository Settings

#### Enable Package Permissions
1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

This allows workflows to push Docker images to GitHub Container Registry (ghcr.io).

### 2. Add Repository Secrets

#### Required Secrets
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `HARNESS_WEBHOOK_URL` | Harness deployment webhook endpoint | `https://app.harness.io/gateway/api/webhooks/...` |

#### Optional Secrets (if needed)
| Secret Name | Description |
|------------|-------------|
| `HARNESS_API_KEY` | If Harness requires authentication header |

### 3. Verify Workflows

The workflows should already be committed in `.github/workflows/`:
- `.github/workflows/ci.yml` - PR validation
- `.github/workflows/cd.yml` - Build and deploy

## Using the CI/CD Pipeline

### Pull Request Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes and commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/my-new-feature
   ```

3. **Open a pull request**
   - Go to GitHub and create a PR targeting `main`
   - The CI workflow automatically runs
   - All checks must pass before merging

4. **Review CI results**
   - **Backend Code Quality**: Black, Ruff, MyPy checks
   - **Backend Tests**: Pytest with 90% coverage requirement
   - **Frontend Code Quality**: ESLint, TypeScript checks
   - **Build Verification**: Docker and frontend builds

### Deployment Workflow

#### Automatic Deployment (Recommended)
1. **Merge PR to main**
   ```bash
   # After PR approval, merge via GitHub UI or:
   git checkout main
   git merge feature/my-new-feature
   git push origin main
   ```

2. **CD workflow runs automatically**
   - Runs all quality checks and tests
   - Builds Docker image
   - Pushes to `ghcr.io/sverze/technology-risk-register:latest`
   - Uploads frontend artifact
   - Triggers Harness webhook

3. **Monitor deployment**
   - Check GitHub Actions tab for workflow status
   - View Harness for deployment progress
   - Verify deployment at your Cloud Run URL

#### Manual Deployment
1. Go to **Actions** → **CD** workflow
2. Click **Run workflow**
3. Select environment (production/staging)
4. Click **Run workflow**

## Container Registry

### Image Tags
The CD pipeline creates multiple tags for each build:

| Tag Format | Example | Purpose |
|-----------|---------|---------|
| `latest` | `ghcr.io/sverze/technology-risk-register:latest` | Always points to latest main build |
| `main-{sha}` | `ghcr.io/sverze/technology-risk-register:main-a1b2c3d` | Specific commit reference |
| `sha-{full-sha}` | `ghcr.io/sverze/technology-risk-register:sha-a1b2c3d4...` | Full SHA for auditability |

### Accessing Images
Images are stored in GitHub Container Registry and can be pulled with:

```bash
# Authenticate to ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull latest image
docker pull ghcr.io/sverze/technology-risk-register:latest

# Pull specific commit
docker pull ghcr.io/sverze/technology-risk-register:main-a1b2c3d
```

## Harness Integration

### Webhook Payload
The CD workflow sends the following JSON to Harness:

```json
{
  "event": "github_deployment",
  "repository": "sverze/technology-risk-register",
  "commit_sha": "abc1234567890...",
  "commit_message": "feat: add new feature",
  "triggered_by": "username",
  "backend_image": "ghcr.io/sverze/technology-risk-register:main-abc1234",
  "backend_image_tag": "main-abc1234",
  "frontend_artifact_run_id": "1234567890",
  "frontend_artifact_name": "frontend-dist-abc1234567890...",
  "frontend_artifact_url": "https://api.github.com/repos/sverze/technology-risk-register/actions/runs/1234567890/artifacts",
  "timestamp": "2025-11-28T10:30:00Z",
  "workflow_run_url": "https://github.com/sverze/technology-risk-register/actions/runs/1234567890",
  "environment": "production"
}
```

### Harness Configuration

#### Backend Deployment (Docker Image)
1. **Artifact Source**: GitHub Container Registry
2. **Image Path**: `ghcr.io/sverze/technology-risk-register`
3. **Tag**: Use `backend_image_tag` from webhook payload
4. **Authentication**: Create GitHub PAT with `read:packages` scope

#### Frontend Deployment (Artifact)
1. **Artifact Source**: GitHub Actions Artifacts
2. **Download URL**: Use `frontend_artifact_url` from webhook payload
3. **Authentication**: Use GitHub PAT with `repo` scope
4. **Extract**: Unzip artifact to Cloud Storage bucket or serve via CDN

Example artifact download with GitHub CLI:
```bash
# Download frontend artifact
gh run download $ARTIFACT_RUN_ID -n frontend-dist-$COMMIT_SHA

# Or with curl (requires token)
curl -L \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "$FRONTEND_ARTIFACT_URL" \
  -o frontend.zip
```

## Pipeline Optimization

### Caching
The workflows use caching to speed up builds:

| Cache | Key | Speedup |
|-------|-----|---------|
| UV dependencies | `uv.lock` | ~30 seconds |
| Docker layers | GitHub Actions cache | ~60 seconds |
| npm modules | `frontend/package-lock.json` | ~20 seconds |

### Estimated Build Times
- **CI Workflow** (PR validation): ~3-4 minutes
- **CD Workflow** (build & deploy): ~4-5 minutes
- **Total time** (commit to deployed): ~5-7 minutes

## Troubleshooting

### CI Workflow Failures

#### "Black check failed"
```bash
# Fix locally
uv run black .
git add .
git commit -m "fix: format code with Black"
git push
```

#### "Ruff linting failed"
```bash
# Fix automatically
uv run ruff check --fix .
git add .
git commit -m "fix: lint with Ruff"
git push
```

#### "MyPy type check failed"
```bash
# Run locally to see errors
uv run mypy app/

# Fix type issues and commit
git add .
git commit -m "fix: type annotations"
git push
```

#### "Tests failed" or "Coverage below 90%"
```bash
# Run tests locally
uv run pytest --ignore=tests/integration -v --cov=app --cov-report=term-missing

# Add tests or fix failures
git add .
git commit -m "test: improve test coverage"
git push
```

### CD Workflow Failures

#### "Failed to push Docker image"
**Cause**: Insufficient permissions

**Solution**: Verify GitHub Settings → Actions → Workflow permissions is set to "Read and write permissions"

#### "Harness webhook failed"
**Cause**: Invalid webhook URL or Harness service down

**Solution**:
1. Verify `HARNESS_WEBHOOK_URL` secret is correct
2. Test webhook manually:
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"test": "payload"}' \
     "$HARNESS_WEBHOOK_URL"
   ```
3. Check Harness service status

#### "Frontend build failed"
**Cause**: TypeScript errors or missing dependencies

**Solution**:
```bash
cd frontend
npm ci
npm run build
# Fix any errors shown
```

### Image Pull Errors

#### "unauthorized: access denied"
**Solution**: Authenticate to ghcr.io
```bash
# Create GitHub PAT with read:packages scope
# Settings → Developer settings → Personal access tokens

echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

## Security Best Practices

### Secrets Management
- ✅ **DO**: Store sensitive values in GitHub Secrets
- ✅ **DO**: Use minimal permission tokens
- ❌ **DON'T**: Commit secrets to repository
- ❌ **DON'T**: Log sensitive data in workflow outputs

### Container Registry
- ✅ **DO**: Use private repositories for production images
- ✅ **DO**: Scan images for vulnerabilities (optional: add Trivy to workflow)
- ✅ **DO**: Use specific tags in production (not `latest`)

### Workflow Permissions
- ✅ **DO**: Use least-privilege permissions
- ✅ **DO**: Review workflow changes in PRs
- ❌ **DON'T**: Allow workflows to approve PRs automatically (unless needed)

## Advanced Configuration

### Add Code Quality Badges
Add to README.md:
```markdown
[![CI](https://github.com/sverze/technology-risk-register/actions/workflows/ci.yml/badge.svg)](https://github.com/sverze/technology-risk-register/actions/workflows/ci.yml)
[![CD](https://github.com/sverze/technology-risk-register/actions/workflows/cd.yml/badge.svg)](https://github.com/sverze/technology-risk-register/actions/workflows/cd.yml)
```

### Enable Dependabot (Optional)
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Add Security Scanning (Optional)
Add to CD workflow after Docker build:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/${{ github.repository }}:latest
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy results to GitHub Security
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: 'trivy-results.sarif'
```

## Monitoring and Metrics

### Key Metrics to Track
- Build success rate (target: >95%)
- Average build time (target: <5 minutes)
- Test coverage (target: >90%)
- Deployment frequency
- Time to production (commit → deployed)

### GitHub Actions Insights
View metrics at: **Insights** → **Actions**
- Workflow run history
- Success/failure rates
- Build duration trends

## Next Steps

1. ✅ Set up GitHub repository settings
2. ✅ Add Harness webhook URL secret
3. ✅ Test CI workflow with a sample PR
4. ✅ Test CD workflow by merging to main
5. ✅ Configure Harness to consume artifacts
6. ✅ Verify end-to-end deployment
7. ⬜ Add monitoring and alerting
8. ⬜ Document rollback procedures
9. ⬜ Set up staging environment (optional)

## Support

For issues or questions:
- Check GitHub Actions logs for error details
- Review this guide's troubleshooting section
- Open an issue in the repository
- Contact the DevOps team

---

**Last Updated**: 2025-11-28
**Pipeline Version**: 1.0
