pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              # We use the 'debug' version of Kaniko because it includes a shell
              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command:
                - sleep
                - 9999999
                tty: true
            '''
        }
    }

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "kalpit191/ecommerce-flask-app"
        // We set the tag dynamically in the script
        IMAGE_TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push with Kaniko') {
            when { branch 'main' }
            steps {
                script {
                    def NEW_IMAGE_TAG = "build-${BUILD_NUMBER}"
                    
                    container('kaniko') {
                        withCredentials([usernamePassword(
                            credentialsId: 'dockerhub-creds', 
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            sh """
                                # 1. Create the auth file for Docker Hub
                                # Kaniko needs a config.json file to authenticate
                                echo "{\\"auths\\":{\\"https://index.docker.io/v1/\\":{\\"auth\\":\\"\$(echo -n ${DOCKER_USER}:${DOCKER_PASS} | base64)\\"}}}" > /kaniko/.docker/config.json
                                
                                # 2. Run Kaniko Executor
                                # This builds the image and pushes it in one step
                                /kaniko/executor \
                                    --context `pwd` \
                                    --destination ${IMAGE_NAME}:${NEW_IMAGE_TAG} \
                                    --force
                            """
                        }
                    }
                    
                    // Update env variable so the next stage knows the tag
                    env.IMAGE_TAG = NEW_IMAGE_TAG
                }
            }
        }

        stage('Update Kubernetes Manifests') {
            when { branch 'main' }
            steps {
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
                        
                        # Update deployment.yaml
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
