# Banking Platform DevSecOps

A production-oriented DevSecOps project demonstrating how application code moves from source control through automated testing, security validation, containerization, and Kubernetes deployment.

The project is being developed incrementally across multiple phases. The current implementation establishes a secure and automated Continuous Integration foundation with Kubernetes deployment validation.

---

## Project Overview

This project demonstrates a DevSecOps workflow for a Python-based banking API.

The current implementation integrates:

- GitHub for source control
- Jenkins for CI automation
- Python and Pytest for application testing
- SonarQube for static code analysis
- Trivy for security scanning
- Docker for containerization
- CycloneDX for Software Bill of Materials (SBOM) generation
- Kubernetes for container orchestration
- Docker Hub for container image distribution

The CI pipeline is designed to identify code quality issues, dependency vulnerabilities, infrastructure/configuration misconfigurations, and container vulnerabilities before the application image is promoted for deployment.

---

## Architecture

```text
                    ┌─────────────────┐
                    │      GitHub     │
                    │  Source Control │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Jenkins     │
                    │   CI Pipeline   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌───────────┐   ┌──────────┐
        │  Pytest  │   │ SonarQube │   │  Trivy   │
        │   Tests  │   │    SAST   │   │ Security │
        └──────────┘   └───────────┘   └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Docker Build   │
                    │ + Runtime Test  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Trivy Image Scan│
                    │  + Security     │
                    │      Gate       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Docker Hub   │
                    │ Container Image │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Kubernetes    │
                    │    Deployment   │
                    └─────────────────┘

CI/CD Pipeline
The current Jenkins pipeline implements the Continuous Integration and security validation portion of the workflow.
Pipeline Stages
1. Source Checkout
   - Retrieves the application source code from GitHub.
2. Python Environment Setup
   - Creates an isolated Python environment.
   - Installs the application dependencies.
3. Test Execution
   - Runs the application test suite using Pytest.
4. SonarQube Analysis
   - Performs static code analysis.
   - Evaluates code quality and potential issues.
5. Dependency Security Scan
   - Uses Trivy to scan project dependencies for known vulnerabilities.
6. Dockerfile / Kubernetes Configuration Scan
   - Uses Trivy configuration scanning to identify infrastructure and container configuration misconfigurations.
7. Docker Image Build
   - Builds the banking API container image.
8. Container Runtime Test
   - Starts the built image as a container.
   - Validates the application health endpoint.
9. Container Image Security Scan
   - Scans the final container image for known vulnerabilities.
10. Security Gate
    - Fails the pipeline when configured critical vulnerabilities with available fixes are detected.
11. SBOM Generation
    - Generates a CycloneDX Software Bill of Materials for the container image.
12. Docker Hub Push
    - Publishes the validated container image to Docker Hub.
Security Controls
Security is integrated directly into the CI workflow rather than being treated as a separate final step.
Implemented Security Controls
- Static Application Security Testing using SonarQube
- Dependency vulnerability scanning using Trivy
- Dockerfile security scanning
- Kubernetes manifest security scanning
- Container image vulnerability scanning
- Critical vulnerability security gate
- SBOM generation using CycloneDX
- Docker image runtime validation
- Docker Hub authentication using Jenkins credentials
The pipeline is configured to prevent promotion when critical vulnerabilities with available fixes are detected.
Kubernetes Deployment
The application is containerized and deployed to Kubernetes using Kubernetes manifests.
Current Kubernetes resources include:
- Deployment
- Service
The Kubernetes deployment has been validated locally using Minikube.
The application service was exposed and tested successfully, confirming that the containerized banking API can run successfully within Kubernetes.
Current Deployment Flow
Docker Image
     │
     ▼
Docker Hub
     │
     ▼
Kubernetes Deployment
     │
     ▼
Kubernetes Service
     │
     ▼
Banking API

The Kubernetes deployment is currently validated as a deployment target. Continuous Delivery and automated GitOps-based synchronization are planned for the next phase.
Project Structure
.
├── application/
│   ├── main.py
│   ├── __init__.py
│   └── tests/
│
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
│
├── terraform/
│
├── helm/
│
├── jenkins/
│
├── scripts/
│
├── docs/
│
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
├── .dockerignore
├── .gitignore
├── .trivyignore
├── sbom.cdx.json
├── trivy-image.json
└── README.md

Some project directories are reserved for subsequent phases of the implementation.
Local Development
Prerequisites
The project currently uses:
- Python 3
- Docker
- Kubernetes / Minikube
- kubectl
- Jenkins
- SonarQube
- Trivy
- Git
Run the Application
Create a Python virtual environment:
python3 -m venv .venv

Activate it:
source .venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Run the application:
uvicorn application.main:app --host 0.0.0.0 --port 8000

Health endpoint:
http://localhost:8000/health

Run Tests
pytest application/tests -v

Docker
Build the image:
docker build -t banking-api:local .

Run the container:
docker run -d \
  --name banking-api \
  -p 8000:8000 \
  banking-api:local

Test the health endpoint:
curl http://localhost:8000/health

Expected response:
{"status":"healthy"}

Kubernetes
Start Minikube:
minikube start

Deploy the application:
kubectl apply -f k8s/

Verify the resources:
kubectl get pods
kubectl get services

The Kubernetes deployment can then be exposed locally using the appropriate Minikube service mechanism.
Current Status
Phase 1 — CI & DevSecOps Foundation
Status: Completed
Implemented and validated:
- GitHub source control
- Jenkins CI pipeline
- Automated Pytest execution
- SonarQube analysis
- Trivy dependency scanning
- Trivy configuration scanning
- Docker image build
- Container runtime testing
- Container vulnerability scanning
- Critical vulnerability security gate
- CycloneDX SBOM generation
- Docker Hub image publishing
- Kubernetes deployment manifests
- Local Kubernetes deployment validation
The Jenkins pipeline has been successfully executed end-to-end with all configured security gates passing.
Roadmap
Phase 2 — Continuous Delivery & GitOps
Status: Planned
Planned technologies and capabilities:
- Argo CD
- GitOps-based deployment
- Automated Kubernetes synchronization
- Image promotion from CI to CD
- Deployment health monitoring
- Declarative application delivery
The goal is to extend the current CI workflow into a complete CI/CD pipeline.
Phase 3 — Advanced DevSecOps & Observability
Status: Planned
Potential areas include:
- Prometheus
- Grafana
- Helm
- Kustomize
- Canary deployments
- Advanced Kubernetes deployment strategies
- Application and infrastructure observability
- Additional security and compliance controls
The roadmap will evolve as subsequent phases are implemented.
Project Goals
The objective of this project is to demonstrate a realistic DevSecOps workflow rather than simply showcase individual tools.
The implementation focuses on:
- Automation
- Security integrated into CI/CD
- Containerized application delivery
- Infrastructure and configuration security
- Kubernetes orchestration
- Reproducible deployments
- GitOps-based delivery
- Observability and operational readiness
The project is intentionally being developed incrementally to demonstrate how a DevSecOps platform can evolve from Continuous Integration into a complete automated delivery platform.