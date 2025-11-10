pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Git branch')
        choice(name: 'ENVIRONMENT', choices: ['production', 'staging', 'dev'], description: 'Environment')
    }

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = '2024tm93287/aceest-fitness'
        AWS_REGION = 'us-east-1'
        EKS_CLUSTER = 'aceest-fitness-cluster'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Initialize') {
            steps {
                echo '=========================================='
                echo 'ACEest Fitness CI/CD Pipeline - t3.micro optimized'
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                echo '=========================================='
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('app') {
                    sh """
                        echo 'Building lightweight Docker image...'
                        docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest .
                        echo 'Build completed'
                        docker images | grep aceest-fitness | head -3
                    """
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh """
                    echo 'Pushing to Docker Hub...'
                    echo \${DOCKERHUB_CREDS_PSW} | docker login -u \${DOCKERHUB_CREDS_USR} --password-stdin
                    docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE}:latest
                    echo 'Push completed'
                """
            }
        }

        stage('Deploy to EKS') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                    sh """
                        echo 'Deploying to EKS (t3.micro optimized)...'

                        aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}
                        kubectl create namespace ${params.ENVIRONMENT} --dry-run=client -o yaml | kubectl apply -f -

                        # Clean up old deployment
                        kubectl delete deployment aceest-app -n ${params.ENVIRONMENT} --ignore-not-found=true
                        sleep 5

                        cat <<'EOFK8S' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-app
  namespace: ${params.ENVIRONMENT}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aceest-fitness
  template:
    metadata:
      labels:
        app: aceest-fitness
    spec:
      containers:
      - name: aceest-app
        image: ${DOCKER_IMAGE}:${IMAGE_TAG}
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: 32Mi
            cpu: 25m
          limits:
            memory: 64Mi
            cpu: 100m
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
---
apiVersion: v1
kind: Service
metadata:
  name: aceest-service
  namespace: ${params.ENVIRONMENT}
spec:
  type: LoadBalancer
  selector:
    app: aceest-fitness
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
EOFK8S

                        echo 'Waiting for pod to start...'
                        kubectl wait --for=condition=ready pod -l app=aceest-fitness -n ${params.ENVIRONMENT} --timeout=3m || echo 'Still starting...'

                        echo 'Current status:'
                        kubectl get pods -n ${params.ENVIRONMENT}
                        kubectl get svc -n ${params.ENVIRONMENT}
                    """
                }
            }
        }

        stage('Verify') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                    sh """
                        echo 'Verifying deployment...'
                        kubectl get all -n ${params.ENVIRONMENT}

                        sleep 30

                        EXTERNAL_URL=\$(kubectl get svc aceest-service -n ${params.ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo 'pending')

                        if [ "\$EXTERNAL_URL" != "pending" ] && [ ! -z "\$EXTERNAL_URL" ]; then
                            echo '=========================================='
                            echo 'DEPLOYMENT SUCCESSFUL!'
                            echo '=========================================='
                            echo "Application URL: http://\$EXTERNAL_URL"
                            echo "Docker Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
                            echo "Environment: ${params.ENVIRONMENT}"
                            echo "Commit: ${env.GIT_COMMIT_SHORT}"
                            echo '=========================================='
                        else
                            echo 'LoadBalancer provisioning in progress...'
                            echo 'Check with: kubectl get svc aceest-service -n ${params.ENVIRONMENT}'
                        fi
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed - check logs above'
        }
        always {
            sh 'docker system prune -f || true'
            cleanWs()
        }
    }
}
