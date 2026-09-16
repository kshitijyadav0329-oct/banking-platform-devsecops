pipeline {

    agent any

    environment {
        IMAGE_NAME = 'banking-api'
        IMAGE_TAG = 'ci'
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
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        .
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
                        ${IMAGE_NAME}:${IMAGE_TAG}

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
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    trivy image \
                        --scanners vuln \
                        --format json \
                        --output trivy-report.json \
                        --exit-code 0 \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('SBOM Generation') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== SBOM Generation ====="

                    echo "Generating CycloneDX SBOM for ${IMAGE_NAME}:${IMAGE_TAG}..."

                    trivy image \
                        --format cyclonedx \
                        --output sbom.cdx.json \
                        ${IMAGE_NAME}:${IMAGE_TAG}

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
                        ${IMAGE_NAME}:${IMAGE_TAG}

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
                            ${IMAGE_NAME}:${IMAGE_TAG} \
                            ${DOCKER_HUB_REPO}:1.0

                        echo "===== Pushing Docker Image ====="

                        docker push \
                            ${DOCKER_HUB_REPO}:1.0

                        echo "Docker image pushed successfully."

                        docker logout

                        echo "Docker Hub logout completed."
                    '''
                }
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