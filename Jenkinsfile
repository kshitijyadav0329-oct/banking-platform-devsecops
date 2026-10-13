pipeline {

    agent any

    environment {
        IMAGE_NAME = 'banking-api'
        DOCKER_HUB_REPO = 'kyadav2910/banking-api'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Skip GitOps-triggered builds') {
            steps {
                scmSkip(
                    deleteBuild: false,
                    skipPattern: '.*gitops: deploy banking-api build.*'
                )
            }
        }


        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "===== Setting Up Python Environment ====="
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                    echo "Python environment setup completed."
                '''
            }
        }

        stage('Check Trivy') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== Checking Trivy ====="
                    trivy --version
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    echo "===== Running Tests ====="
                    .venv/bin/python -m pytest application/tests -v
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                        echo "===== SonarQube Analysis ====="

                        sonar-scanner \
                            -Dsonar.projectKey=banking-platform-devsecops \
                            -Dsonar.sources=application \
                            -Dsonar.exclusions=application/tests/**

                        echo "SonarQube analysis completed."
                    '''
                }
            }
        }

        stage('Dependency Security Scan') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== Dependency Security Scan ====="

                    trivy fs \
                        --scanners vuln \
                        --format table \
                        --output dependency-report.txt \
                        --exit-code 0 \
                        .
                '''
            }
        }

        stage('Dockerfile Security Scan') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== Dockerfile and Kubernetes Configuration Scan ====="

                    trivy config \
                        --exit-code 1 \
                        .

                    echo "Configuration security scan passed."
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    export PATH="/usr/local/bin:$PATH"
                    echo "===== Building Docker Image ====="

                    docker build \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                        .

                    echo "Docker image ${IMAGE_NAME}:${BUILD_NUMBER} built successfully."
                '''
            }
        }

        stage('Run Container Test') {
            steps {
                sh '''
                    export PATH="/usr/local/bin:$PATH"
                    echo "===== Running Container Test ====="

                    docker rm -f banking-api-test 2>/dev/null || true

                    docker run -d \
                        --name banking-api-test \
                        -p 8000:8000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "Waiting for application to start..."
                    sleep 5

                    echo "Checking health endpoint..."
                    curl --fail http://localhost:8000/health

                    echo "Container test passed."
                    docker rm -f banking-api-test
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== Docker Image Security Scan ====="

                    trivy image \
                        --scanners vuln \
                        --format table \
                        --output trivy-report.txt \
                        --exit-code 0 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    trivy image \
                        --scanners vuln \
                        --format json \
                        --output trivy-report.json \
                        --exit-code 0 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('SBOM Generation') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== SBOM Generation ====="

                    trivy image \
                        --format cyclonedx \
                        --output sbom.cdx.json \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "SBOM generation completed."
                    ls -lh sbom.cdx.json
                '''
            }
        }

        stage('Security Gate') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
                    echo "===== Security Gate ====="

                    echo "Policy: Fail on CRITICAL vulnerabilities with available fixes."

                    trivy image \
                        --scanners vuln \
                        --severity CRITICAL \
                        --ignore-unfixed \
                        --exit-code 1 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "Security gate passed."
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-pat',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        export PATH="/usr/local/bin:$PATH"

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Docker Image ====="

                        docker tag \
                            ${IMAGE_NAME}:${BUILD_NUMBER} \
                            ${DOCKER_HUB_REPO}:${BUILD_NUMBER}

                        echo "===== Pushing Docker Image ====="

                        docker push \
                            ${DOCKER_HUB_REPO}:${BUILD_NUMBER}

                        docker logout
                        echo "Docker image pushed successfully."
                    '''
                }
            }
        }

        stage('Update GitOps Manifest') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-pat',
                        usernameVariable: 'GITHUB_USERNAME',
                        passwordVariable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "===== Preparing GitOps Update ====="

                        ASKPASS_SCRIPT="$(mktemp)"
                        trap 'rm -f "$ASKPASS_SCRIPT"' EXIT

                        cat > "$ASKPASS_SCRIPT" <<'ASKPASS_EOF'
#!/bin/sh
case "$1" in
    *Username*) printf '%s\\n' "$GITHUB_USERNAME" ;;
    *Password*) printf '%s\\n' "$GITHUB_TOKEN" ;;
    *) exit 1 ;;
esac
ASKPASS_EOF

                        chmod 700 "$ASKPASS_SCRIPT"

                        export GIT_ASKPASS="$ASKPASS_SCRIPT"
                        export GIT_TERMINAL_PROMPT=0

                        git config user.name "Jenkins GitOps Bot"
                        git config user.email "jenkins-gitops@users.noreply.github.com"

                        echo "===== Checking Remote Main Branch ====="

                        git fetch origin +refs/heads/main:refs/remotes/origin/main

                        CURRENT_COMMIT="$(git rev-parse HEAD)"
                        REMOTE_COMMIT="$(git rev-parse refs/remotes/origin/main)"

                        echo "Build source commit: $CURRENT_COMMIT"
                        echo "Remote main commit:  $REMOTE_COMMIT"

                        if [ "$CURRENT_COMMIT" != "$REMOTE_COMMIT" ]; then
                            echo "ERROR: Remote main changed during the build."
                            echo "Refusing to update the GitOps manifest."
                            exit 1
                        fi

                        echo "===== Updating Kubernetes Image Tag ====="

                        python3 - <<'PY'
import os
import re
from pathlib import Path

manifest = Path("k8s/deployment.yaml")
content = manifest.read_text()
build_number = os.environ["BUILD_NUMBER"]

pattern = re.compile(
    r"(?m)^([ \\t]*image:[ \\t]*kyadav2910/banking-api:)[^\\s]+([ \\t]*)$"
)

updated, count = pattern.subn(
    lambda match: f"{match.group(1)}{build_number}{match.group(2)}",
    content
)

if count != 1:
    raise SystemExit(
        f"ERROR: Expected exactly one banking-api image entry; found {count}."
    )

manifest.write_text(updated)
print(f"Updated {manifest} to image tag {build_number}.")
PY

                        echo "===== Reviewing Manifest Change ====="

                        git diff --check
                        git diff -- k8s/deployment.yaml
                        git add -- k8s/deployment.yaml

                        if git diff --cached --quiet; then
                            echo "ERROR: No GitOps manifest change detected."
                            exit 1
                        fi

                        echo "===== Committing GitOps Update ====="

                        git commit \
                            -m "gitops: deploy banking-api build ${BUILD_NUMBER}"

                        echo "===== Pushing GitOps Commit ====="

                        git push origin HEAD:main

                        echo "GitOps manifest committed and pushed successfully."
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'dependency-report.txt,trivy-report.txt,trivy-report.json,secret-report.json,sbom.cdx.json',
                allowEmptyArchive: true,
                fingerprint: true
            )

            sh '''
                docker rm -f banking-api-test 2>/dev/null || true
            '''
        }

        success {
            echo 'CI completed and GitOps update pushed successfully!'
        }
    }
}