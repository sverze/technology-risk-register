# Environment Variables Setup

This guide explains how to set up environment variables for the Technology Risk Register application.

## Quick Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your Anthropic API key:**
   ```bash
   # Open in your preferred editor
   nano .env
   # or
   vim .env
   # or
   code .env
   ```

3. **Get your Anthropic API key:**
   - Visit https://console.anthropic.com/settings/keys
   - Create a new API key
   - Copy the key and paste it into your `.env` file:
     ```
     ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

4. **Restart your Docker containers:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Environment Variables

### Required for Risk SME Chat

- **`ANTHROPIC_API_KEY`** - Your Anthropic API key for Claude
  - Required for the Risk SME Chat feature
  - Get it from: https://console.anthropic.com/settings/keys
  - Format: `sk-ant-api03-...`

### Database Configuration

- **`DATABASE_URL`** - SQLite database connection string
  - Default: `sqlite:///./risk_register.db`
  - Can be changed to point to a different database file

### Authentication

- **`AUTH_USERNAME`** - Admin username for login
  - Default: `admin`
  - Change this in production!

- **`AUTH_PASSWORD`** - Admin password for login
  - Default: `changeme123`
  - **IMPORTANT:** Change this in production!

- **`AUTH_SECRET_KEY`** - Secret key for JWT token signing
  - Default: `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7`
  - **IMPORTANT:** Generate a new key for production:
    ```bash
    openssl rand -hex 32
    ```

### CORS Configuration

- **`ALLOWED_ORIGINS`** - List of allowed frontend origins
  - Default: `["http://localhost:3000", "http://127.0.0.1:3000", "http://frontend:3000"]`
  - Add your production frontend URL here

## Security Notes

⚠️ **NEVER commit `.env` files to version control!**

The `.env` file is already listed in `.gitignore` to prevent accidental commits. The file contains:
- API keys (Anthropic)
- Authentication credentials
- Secret keys for encryption

If you accidentally commit secrets:
1. **Immediately revoke/regenerate the compromised credentials**
2. Remove the file from Git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (if working on a shared repository, coordinate with your team)

## Production Deployment

For production deployments (GCP Cloud Run), set environment variables via:

1. **GCP Console:**
   - Navigate to Cloud Run > Your Service > Edit & Deploy New Revision
   - Add environment variables in the "Variables & Secrets" section

2. **gcloud CLI:**
   ```bash
   gcloud run services update technology-risk-register \
     --set-env-vars ANTHROPIC_API_KEY=your_key_here \
     --region us-central1
   ```

3. **Terraform:**
   - Use Secret Manager for sensitive values
   - Reference in your `main.tf`:
     ```hcl
     resource "google_cloud_run_service" "app" {
       template {
         spec {
           containers {
             env {
               name = "ANTHROPIC_API_KEY"
               value_from {
                 secret_key_ref {
                   name = google_secret_manager_secret.anthropic_key.secret_id
                   key  = "latest"
                 }
               }
             }
           }
         }
       }
     }
     ```

## Troubleshooting

### Error: "Could not resolve authentication method"

**Symptom:** Chat requests fail with authentication error about `api_key` or `auth_token`

**Cause:** `ANTHROPIC_API_KEY` environment variable is not set or not being passed to the container

**Solution:**
1. Check that `.env` file exists and contains `ANTHROPIC_API_KEY`
2. Restart Docker containers: `docker-compose down && docker-compose up -d`
3. Verify the variable is set inside the container:
   ```bash
   docker-compose exec backend printenv | grep ANTHROPIC
   ```
   Should output: `ANTHROPIC_API_KEY=sk-ant-api03-...`

### Error: Container fails to start

**Symptom:** Backend container exits immediately

**Cause:** Missing required environment variables or invalid values

**Solution:**
1. Check Docker logs: `docker-compose logs backend`
2. Verify all required variables are set in `.env`
3. Ensure no syntax errors in `.env` (no spaces around `=`)

## Example `.env` File

```bash
# Database
DATABASE_URL=sqlite:///./risk_register.db

# Authentication (CHANGE IN PRODUCTION!)
AUTH_USERNAME=admin
AUTH_PASSWORD=SecurePassword123!
AUTH_SECRET_KEY=your_generated_secret_key_here

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-your_actual_key_here
```

## Development vs Production

### Development (Local)
- Use `.env` file (not committed)
- Default authentication credentials are fine for local testing
- Keep CORS open to localhost

### Production (GCP)
- Use GCP Secret Manager for sensitive values
- Generate new `AUTH_SECRET_KEY`
- Use strong `AUTH_PASSWORD`
- Restrict `ALLOWED_ORIGINS` to your production frontend URL
- Enable HTTPS only
