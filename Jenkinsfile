pipeline {
    agent any

    environment {
        IMAGE_NAME = 'banking-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_HUB_REPO = 'kyadav2910/banking-api'
    }

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
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Running Tests ====="

                    python3 -m pytest application/tests -v
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
                            -Dsonar.tests=application/tests
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
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        .
                '''
            }
        }

        stage('Dockerfile Security Scan') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Dockerfile Security Scan ====="

                    trivy config \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        Dockerfile
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "===== Building Docker Image ====="

                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                '''
            }
        }

        stage('Run Container Test') {
            steps {
                sh '''
                    echo "===== Running Container Test ====="

                    docker rm -f banking-api-test 2>/dev/null || true

                    docker run -d \
                        --name banking-api-test \
                        -p 8000:8000 \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Waiting for application to start..."
                    sleep 10

                    curl -f http://localhost:8000/health

                    echo "Container test successful"

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
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('SBOM Generation') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Generating SBOM ====="

                    syft ${IMAGE_NAME}:${IMAGE_TAG} \
                        -o cyclonedx-json=sbom.json
                '''
            }
        }

        stage('Security Gate') {
            steps {
                sh '''
                    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

                    echo "===== Final Security Gate ====="

                    trivy image \
                        --severity CRITICAL \
                        --exit-code 1 \
                        ${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Security Gate Passed"
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-banking-api',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "===== Logging in to Docker Hub ====="

                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "===== Tagging Docker Image ====="

                        docker tag \
                            ${IMAGE_NAME}:${IMAGE_TAG} \
                            ${DOCKER_HUB_REPO}:${IMAGE_TAG}

                        docker tag \
                            ${IMAGE_NAME}:latest \
                            ${DOCKER_HUB_REPO}:latest

                        echo "===== Pushing Docker Images ====="

                        docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                        docker push ${DOCKER_HUB_REPO}:latest

                        echo "Docker images pushed successfully"
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'sbom.json', allowEmptyArchive: true

            sh '''
                echo "===== Cleaning Workspace ====="

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