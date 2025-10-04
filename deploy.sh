#!/bin/bash
# Deployment script for Stock Market Analyzer
# This script is intended to be run by the CI/CD pipeline for production deployments

set -e  # Exit on any error

# Deployment environment configuration
ENVIRONMENT=${DEPLOY_ENV:-production}
TAG=${GITHUB_SHA:-latest}
IMAGE_NAME="stock-analyzer:${TAG}"

echo "Starting deployment for ${ENVIRONMENT} environment"
echo "Using image: ${IMAGE_NAME}"
echo "Git SHA: ${GITHUB_SHA}"

# Function to validate deployment environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "staging" ]]; then
        echo "Error: Invalid environment $ENVIRONMENT. Use 'production' or 'staging'."
        exit 1
    fi
}

# Function to run pre-deployment checks
pre_deployment_checks() {
    echo "Running pre-deployment checks..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker image exists
    if [[ $(docker images -q ${IMAGE_NAME} | wc -l) -eq 0 ]]; then
        echo "Error: Docker image ${IMAGE_NAME} does not exist"
        exit 1
    fi
    
    echo "Pre-deployment checks passed"
}

# Function to deploy to specified environment
deploy_to_environment() {
    echo "Deploying to ${ENVIRONMENT} environment..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.yml down --remove-orphans || true
    
    # Set environment variables for deployment
    export APP_VERSION=${TAG}
    export DEPLOY_ENVIRONMENT=${ENVIRONMENT}
    
    # Start the services with docker-compose
    docker-compose -f docker-compose.yml up -d --no-build
    
    # Wait for services to be healthy
    echo "Waiting for services to be healthy..."
    sleep 30
    
    # Check if services are running properly
    if docker-compose -f docker-compose.yml ps | grep -q "Up"; then
        echo "Services deployed successfully!"
        
        # Run health check
        echo "Running health check..."
        sleep 10
        if curl -f http://localhost:8501/_stcore/health 2>/dev/null; then
            echo "Health check passed"
        else
            echo "Warning: Health check failed"
        fi
    else
        echo "Error: Services failed to start properly"
        docker-compose -f docker-compose.yml logs
        exit 1
    fi
}

# Function to rollback deployment if needed
rollback() {
    echo "Rolling back deployment..."
    # In a real scenario, you might rollback to a previous version
    docker-compose -f docker-compose.yml down
    echo "Rollback completed"
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    
    validate_environment
    pre_deployment_checks
    deploy_to_environment
    
    echo "Deployment completed successfully!"
    echo "Application is now running at http://localhost:8501"
}

# Error handling
error_handler() {
    echo "Deployment failed at line $1"
    rollback
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Run main deployment process
main

echo "Deployment script completed"