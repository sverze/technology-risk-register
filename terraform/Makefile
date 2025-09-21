# Terraform Makefile for Technology Risk Register

.PHONY: help init plan apply destroy clean format validate

# Default target
help:
	@echo "Available targets:"
	@echo "  init      - Initialize Terraform"
	@echo "  plan      - Plan Terraform changes"
	@echo "  apply     - Apply Terraform changes"
	@echo "  destroy   - Destroy Terraform infrastructure"
	@echo "  clean     - Clean Terraform cache and lock files"
	@echo "  format    - Format Terraform files"
	@echo "  validate  - Validate Terraform configuration"
	@echo "  build     - Build and push Docker image"
	@echo "  deploy    - Build, push, and deploy to Cloud Run"

# Initialize Terraform
init:
	terraform init

# Plan Terraform changes
plan:
	terraform plan

# Apply Terraform changes
apply:
	terraform apply

# Destroy infrastructure
destroy:
	terraform destroy

# Clean Terraform cache
clean:
	rm -rf .terraform .terraform.lock.hcl terraform.tfstate.backup

# Format Terraform files
format:
	terraform fmt -recursive

# Validate Terraform configuration
validate:
	terraform validate

# Build and push Docker image
build:
	@if [ -z "$(shell terraform output -raw project_id 2>/dev/null)" ]; then \
		echo "Error: Terraform not applied yet. Run 'make apply' first."; \
		exit 1; \
	fi
	@PROJECT_ID=$$(terraform output -raw project_id) && \
	REGION=$$(terraform output -raw region) && \
	REGISTRY=$$(terraform output -raw container_registry) && \
	echo "Building and pushing to $$REGISTRY..." && \
	cd .. && \
	gcloud builds submit --tag $$REGISTRY/technology-risk-register:latest .

# Deploy to Cloud Run (build + update service)
deploy: build
	@echo "Updating Cloud Run service..."
	@PROJECT_ID=$$(terraform output -raw project_id) && \
	REGION=$$(terraform output -raw region) && \
	REGISTRY=$$(terraform output -raw container_registry) && \
	gcloud run deploy technology-risk-register \
		--image $$REGISTRY/technology-risk-register:latest \
		--platform managed \
		--region $$REGION \
		--project $$PROJECT_ID