pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
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
                        -t banking-api:ci \
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
                        banking-api:ci

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
                        banking-api:ci

                    trivy image \
                        --scanners vuln \
                        --format json \
                        --output trivy-report.json \
                        --exit-code 0 \
                        banking-api:ci
                '''
            }
        }

        stage('SBOM Generation') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== SBOM Generation ====="
                    echo "Generating CycloneDX SBOM for banking-api:ci..."

                    trivy image \
                        --format cyclonedx \
                        --output sbom.cdx.json \
                        banking-api:ci

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
                        banking-api:ci

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
                            banking-api:ci \
                            kyadav2910/banking-api:1.0

                        echo "===== Pushing Docker Image ====="

                        docker push \
                            kyadav2910/banking-api:1.0

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
        }
    }
}