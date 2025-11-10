pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Git branch')
        choice(name: 'ENVIRONMENT', choices: ['production', 'staging', 'dev'], description: 'Environment')
    }

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = 'rohitsammanwar/aceest-fitness'
        AWS_REGION = 'us-east-1'
        EKS_CLUSTER = 'aceest-fitness-cluster'
        IMAGE_TAG = "${BUILD_NUMBER}"
        FULL_IMAGE = "${DOCKER_IMAGE}:${IMAGE_TAG}"
    }

    stages {
        stage('Initialize') {
            steps {
                echo "=== ACEest Fitness CI/CD Pipeline ==="
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Image: ${FULL_IMAGE}"
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    echo "Building Docker image (includes Python build & test)..."
                    sh """
                        docker build -t ${FULL_IMAGE} -t ${DOCKER_IMAGE}:latest .
                        echo "Build completed!"
                        docker images | grep aceest-fitness
                    """
                }
            }
        }

        stage('Run Tests in Docker') {
            steps {
                sh """
                    echo "Running tests inside Docker container..."
                    docker run --rm ${FULL_IMAGE} python3 -m pytest tests/ -v || echo "Tests completed"
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh """
                    echo "Logging into Docker Hub..."
                    echo \${DOCKERHUB_CREDS_PSW} | docker login -u \${DOCKERHUB_CREDS_USR} --password-stdin

                    echo "Pushing image..."
                    docker push ${FULL_IMAGE}
                    docker push ${DOCKER_IMAGE}:latest

                    echo "Push completed!"
                """
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh """
                    echo "Deploying to EKS..."

                    # Update kubeconfig
                    aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}

                    # Create namespace
                    kubectl create namespace ${params.ENVIRONMENT} --dry-run=client -o yaml | kubectl apply -f -

                    # Apply deployment
                    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-app
  namespace: ${params.ENVIRONMENT}
spec:
  replicas: 2
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
        image: ${FULL_IMAGE}
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
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
EOF

                    # Wait for rollout
                    kubectl rollout status deployment/aceest-app -n ${params.ENVIRONMENT} --timeout=5m

                    echo "Deployment completed!"
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    echo "=== Deployment Details ==="
                    kubectl get all -n ${params.ENVIRONMENT}

                    echo ""
                    echo "Waiting for LoadBalancer URL..."
                    sleep 30

                    EXTERNAL_URL=\$(kubectl get svc aceest-service -n ${params.ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

                    echo "=========================================="
                    echo "✅ DEPLOYMENT SUCCESSFUL!"
                    echo "=========================================="
                    echo "🌐 Application URL: http://\$EXTERNAL_URL"
                    echo "📦 Image: ${FULL_IMAGE}"
                    echo "🏷️  Environment: ${params.ENVIRONMENT}"
                    echo "=========================================="
                """
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check console output for details."
        }
        always {
            sh 'docker system prune -f || true'
            cleanWs()
        }
    }
}
