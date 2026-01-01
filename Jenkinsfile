pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "kalpit191/ecommerce-flask-app"
        IMAGE_TAG = "latest"
        // Note: You defined GIT_USER/PASS here but overrode them in the last stage. 
        // Ensure 'github-username' and 'github-password' are valid Secret Text credentials if you keep this.
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // stage('Build and Push Docker Image') {
        //     when { branch 'main' }
        //     steps {
                
        //         script {
        //             def NEW_IMAGE_TAG = "build-${BUILD_NUMBER}"
                    
        //             withCredentials([usernamePassword(
        //                 credentialsId: 'dockerhub-creds', 
        //                 usernameVariable: 'DOCKER_USER',
        //                 passwordVariable: 'DOCKER_PASS'
        //             )]) {
        //                 //sh "docker login -u $DOCKER_USER -p $DOCKER_PASS"
        //                 sh "docker build -t $IMAGE_NAME:${NEW_IMAGE_TAG} ."
        //                 sh "docker push $IMAGE_NAME:${NEW_IMAGE_TAG}"
        //             }
                    
        //             // Update the environment variable so the next stage can see it
        //             env.IMAGE_TAG = NEW_IMAGE_TAG
        //         }
        //     }
        // }
        

        stage('Build and Push Docker Image') {
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
                            sh '''
                              mkdir -p /kaniko/.docker
                              cat <<'EOF' > /kaniko/.docker/config.json
                              {
                                "auths": {
                                  "https://index.docker.io/v1/": {
                                    "username": "'"$DOCKER_USER"'",
                                    "password": "'"$DOCKER_PASS"'"
                                  }
                                }
                              }
                              EOF
        
                              /kaniko/executor \
                                --context $WORKSPACE \
                                --dockerfile Dockerfile \
                                --destination '"$IMAGE_NAME:$NEW_IMAGE_TAG"'
                            '''
                        }
                    }
        
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
                        
                        # Ensure we are on the main branch
                        git checkout main
                        git pull origin main
                        
                        # Use env.IMAGE_TAG to access the variable set in the previous stage
                        sed -i "s|image: .*|image: ${IMAGE_NAME}:${env.IMAGE_TAG}|g" kube/deployment.yaml
                        
                        git add kube/deployment.yaml
                        
                        # Commit only if changes exist
                        git diff --cached --quiet || git commit -m "Updated image tag to ${env.IMAGE_TAG}"
                        
                        git push https://${GIT_USER}:${GIT_PASSWORD}@github.com/${GIT_USER}/app-gitops.git main
                    """
                }
            }
        }
    }
}
