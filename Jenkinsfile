pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "kalpit191/ecommerce-flask-app"
        GIT_USER   = "kalpitmalviya"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push Docker Image') {
            when { branch 'main' }
            steps {
                script {
                    env.IMAGE_TAG = "build-${BUILD_NUMBER}"
                }

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        set -e
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Deploy to EKS (GitOps)') {
            when { branch 'main' }
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'github-creds',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_TOKEN'
                    )]) {
                        sh """
                            set -e
                            git config user.name "${GIT_USER}"
                            git config user.email "jenkins@ci.local"

                            git fetch origin
                            git checkout main
                            git reset --hard origin/main

                            sed -i 's|image:.*|image: ${IMAGE_NAME}:${IMAGE_TAG}|' kube/deployment.yaml

                            git add kube/deployment.yaml

                            if ! git diff --cached --quiet; then
                              git commit -m "Update image to ${IMAGE_TAG}"
                              git push https://${GIT_USERNAME}:${GIT_TOKEN}@github.com/kalpitmalviya/app-gitops.git main
                            else
                              echo "No changes to commit"
                            fi
                        """
                    }
                }
            }
        }
    }
}
