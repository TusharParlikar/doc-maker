---
type: llm
weight: 2
focus: { source: file, path: generated-docs/INFRASTRUCTURE.md }
---

Ground truth:
- compose.yml services: proxy (Traefik), db (postgres:18), adminer, backend; volume app-db-data. compose.override.yml (local development) adds mailpit and playwright and overrides the others.
- Configuration comes from a committed .env file at the repo root and frontend/.env; backend settings use pydantic BaseSettings.
- CI/CD is GitHub Actions with 15 workflows, including test-backend, test-docker-compose, playwright, deploy (on push to master and workflow_dispatch) and deploy-docker-compose.
- There are no Kubernetes manifests and no Terraform, CloudFormation or Pulumi files. No autoscaling, alerting or backup configuration is present.

PASS if the document describes these services and the local versus deployed compose setup, describes the GitHub Actions pipeline including tests and the deploy trigger, and states (or does not contradict) that Kubernetes, IaC, autoscaling, alerting and backups are absent.
FAIL if it claims Kubernetes, Terraform, autoscaling, alerting or backups exist, invents services or cloud providers not in the repository, or prints values from the .env files.
