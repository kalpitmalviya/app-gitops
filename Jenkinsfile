pipeline {
    // 1. Define the Kubernetes Pod with a 'docker' container
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: docker
                image: docker:latest
                command:
                - cat
                tty: true
                volumeMounts:
                - name: docker-sock
                  mountPath: /var/run/docker.sock
              volumes:
              - name: docker-sock
                hostPath:
                  path: /var/run/docker.sock
            '''
        }
    }

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "kalpit191/ecommerce-flask-app"
        // We will set this dynamically in the build stage
        IMAGE_TAG = "latest" 
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
                    def NEW_IMAGE_TAG = "build-${BUILD_NUMBER}"
                    
                    // 2. Run these commands inside the 'docker' container defined above
                    container('docker') {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub-creds', 
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            // Note: 'docker login' might warn about storing creds unencrypted, which is normal in CI
                            sh "docker login -u $DOCKER_USER -p $DOCKER_PASS"
                            sh "docker build -t $IMAGE_NAME:${NEW_IMAGE_TAG} ."
                            sh "docker push $IMAGE_NAME:${NEW_IMAGE_TAG}"
                        }
                    }
                    
                    // Update env variable for the next stage
                    env.IMAGE_TAG = NEW_IMAGE_TAG
                }
            }
        }

        stage('Update Kubernetes Manifests') {
            when { branch 'main' }
            steps {
                // This runs in the default 'jnlp' container, which has git
                withCredentials([usernamePassword(
                    credentialsId: 'github-creds',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASSWORD'
                )]) {
                    sh """
                        set -e 
                        git config user.email "${GIT_USER}@users.noreply.github.com"
                        git config user.name "${GIT_USER}"
                        
                        git checkout main
                        git pull origin main
                        
                        # Update the deployment yaml with the new tag
                        sed -i "s|image: .*|image: ${IMAGE_NAME}:${env.IMAGE_TAG}|g" kube/deployment.yaml
                        
                        git add kube/deployment.yaml
                        git diff --cached --quiet || git commit -m "Updated image tag to ${env.IMAGE_TAG}"
                        git push https://${GIT_USER}:${GIT_PASSWORD}@github.com/${GIT_USER}/app-gitops.git main
                    """
                }
            }
        }
    }
}
