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

                    echo "===== Dockerfile Security Scan ====="

                    echo "Policy: Fail on any Dockerfile misconfiguration."

                    trivy config \
                        --exit-code 1 \
                        .

                    echo "Dockerfile security scan passed."
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

                    echo "Generating CycloneDX SBOM for ${IMAGE_NAME}:${BUILD_NUMBER}..."

                    trivy image \
                        --format cyclonedx \
                        --output sbom.cdx.json \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "SBOM generation completed."

                    echo "===== SBOM File ====="

                    ls -lh sbom.cdx.json
                '''

            }

        }

        stage('Security Gate') {

            steps {

                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Security Gate ====="

                    echo "Policy: Fail only on CRITICAL vulnerabilities with available fixes."

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
                        export PATH="/usr/local/bin:$PATH"

                        echo "===== Docker Hub Login ====="

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        echo "Docker Hub authentication succeeded."

                        echo "===== Tagging Docker Image ====="

                        docker tag \
                            ${IMAGE_NAME}:${BUILD_NUMBER} \
                            ${DOCKER_HUB_REPO}:${BUILD_NUMBER}

                        echo "===== Pushing Docker Image ====="

                        docker push \
                            ${DOCKER_HUB_REPO}:${BUILD_NUMBER}

                        echo "Docker image pushed successfully."

                        docker logout

                        echo "Docker Hub logout completed."
                    '''

                }

            }

        }

        stage('Deploy to Kubernetes') {

            steps {

                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Kubernetes Deployment ====="

                    echo "Kubernetes context:"

                    kubectl config current-context

                    echo "Kubernetes nodes:"

                    kubectl get nodes

                    echo "===== Applying Kubernetes Manifests ====="

                    kubectl apply -f k8s/deployment.yaml

                    kubectl apply -f k8s/service.yaml

                    echo "===== Updating Deployment Image ====="

                    kubectl set image deployment/banking-api \
                        banking-api=${DOCKER_HUB_REPO}:${BUILD_NUMBER}

                    echo "===== Waiting for Kubernetes Rollout ====="

                    kubectl rollout status deployment/banking-api \
                        --timeout=180s

                    echo "Kubernetes rollout completed successfully."

                    echo "===== Deployment Status ====="

                    kubectl get deployment banking-api

                    echo "===== Pod Status ====="

                    kubectl get pods -l app=banking-api
                '''

            }

        }

        stage('Kubernetes Deployment Verification') {

            steps {

                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Kubernetes Deployment Verification ====="

                    AVAILABLE=$(kubectl get deployment banking-api \
                        -o jsonpath='{.status.availableReplicas}')

                    READY=$(kubectl get deployment banking-api \
                        -o jsonpath='{.status.readyReplicas}')

                    echo "Available replicas: ${AVAILABLE}"

                    echo "Ready replicas: ${READY}"

                    if [ "${AVAILABLE}" != "2" ]; then

                        echo "ERROR: Expected 2 available replicas."

                        kubectl get pods -l app=banking-api

                        exit 1

                    fi

                    if [ "${READY}" != "2" ]; then

                        echo "ERROR: Expected 2 ready replicas."

                        kubectl get pods -l app=banking-api

                        exit 1

                    fi

                    echo "Kubernetes deployment verification passed."
                '''

            }

        }

        stage('Kubernetes Health Check') {

            steps {

                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Kubernetes Application Health Check ====="

                    echo "Starting temporary port-forward..."

                    kubectl port-forward service/banking-api 8000:8000 \
                        > /tmp/banking-api-port-forward.log 2>&1 &

                    PORT_FORWARD_PID=$!

                    echo "Port-forward PID: ${PORT_FORWARD_PID}"

                    cleanup() {

                        echo "Stopping port-forward..."

                        kill ${PORT_FORWARD_PID} 2>/dev/null || true

                    }

                    trap cleanup EXIT

                    echo "Waiting for port-forward and application to become ready..."

                    HEALTH_CHECK_PASSED=false

                    for i in {1..15}; do

                        if curl --silent --fail \
                            http://127.0.0.1:8000/health \
                            > /tmp/banking-api-health.json; then

                            HEALTH_CHECK_PASSED=true

                            break

                        fi

                        echo "Health check attempt ${i}/15 failed. Retrying..."

                        sleep 2

                    done

                    if [ "$HEALTH_CHECK_PASSED" != "true" ]; then

                        echo "ERROR: Kubernetes application health check failed."

                        echo "===== Port Forward Log ====="

                        cat /tmp/banking-api-port-forward.log || true

                        exit 1

                    fi

                    echo "Health response:"

                    cat /tmp/banking-api-health.json

                    echo

                    echo "Kubernetes application health check passed."
                '''

            }

        }

    }

    post {

        always {

            archiveArtifacts artifacts: 'dependency-report.txt,trivy-report.txt,trivy-report.json,secret-report.json,sbom.cdx.json',

                allowEmptyArchive: true,

                fingerprint: true

            sh '''
                docker rm -f banking-api-test 2>/dev/null || true
            '''

        }

        success {

            echo 'Pipeline completed successfully!'

        }

        failure {

            echo 'Pipeline failed. Check the stage logs above.'

        }

    }

}