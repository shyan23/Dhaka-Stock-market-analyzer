# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Stock Market Analyzer project.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and includes the following stages:
- Code Quality Checks
- Automated Testing
- Security Scanning
- Docker Image Building
- Deployment

## Pipeline Structure

The pipeline consists of three separate workflow files:

### 1. CI/CD Pipeline (`ci-cd.yml`)
This is the main pipeline that runs on every push and pull request. It includes:
- Testing across multiple Python versions (3.8, 3.9, 3.10)
- Code quality checks (linting)
- Security scanning
- Docker image building (only on main branch)
- Deployment (only when merged to main)

### 2. Docker Pipeline (`docker.yml`)
This pipeline runs when a new tag is pushed (e.g., `v1.2.3`) and:
- Builds multi-platform Docker images
- Pushes images to GitHub Container Registry (GHCR)
- Creates Docker image tags based on the Git tag

### 3. Quality Pipeline (`quality.yml`)
This pipeline runs on every push and pull request and:
- Checks code formatting with Black
- Performs type checking with MyPy
- Runs CodeQL security analysis
- Performs dependency review

## Triggers

### Push Events
- `ci-cd.yml`: Runs on pushes to `main` and `develop` branches, excluding markdown files
- `quality.yml`: Runs on pushes to `main` and `develop` branches
- `docker.yml`: Runs on Git tag pushes

### Pull Request Events
- `ci-cd.yml`: Runs on PRs to `main`, excluding markdown files
- `quality.yml`: Runs on PRs to `main`

## Testing Strategy

The pipeline runs all tests in the `test/` directory using pytest with the following configuration:
- Tests are run across multiple Python versions for compatibility
- Code coverage is calculated and uploaded to Codecov
- Tests include unit tests, integration tests, and edge case tests

## Security Scanning

The pipeline includes security scanning using:
- Bandit for Python code vulnerability scanning
- CodeQL for comprehensive code analysis
- Dependency review for known vulnerabilities in dependencies

## Deployment Process

Deployment occurs automatically when changes are merged to the `main` branch:
1. All tests must pass
2. Security scans must complete without critical issues
3. Docker image is built and scanned
4. Application is deployed to the production environment

## Configuration

The pipeline is configured in the `.github/workflows/` directory with the following files:
- `ci-cd.yml` - Main CI/CD workflow
- `docker.yml` - Docker build and publishing workflow
- `quality.yml` - Code quality and security checks

## Secrets and Variables

The pipeline uses the following GitHub Secrets (configured in repository settings):
- `GITHUB_TOKEN` - Automatically provided by GitHub for authentication
- Any additional secrets required for deployment

## Status and Coverage Reports

- Test coverage is reported to Codecov
- Security scan results are available in workflow artifacts
- Build status is shown in pull requests and on the repository page

## Manual Deployment

If needed, deployments can be triggered manually through GitHub Actions or by creating Git tags in the format `vX.Y.Z`.

## Troubleshooting

If the pipeline fails:
1. Check the workflow logs in GitHub Actions
2. Verify all tests pass locally with `python -m pytest test/`
3. Ensure code formatting is correct with `black src/ test/`
4. Check for any new security vulnerabilities introduced