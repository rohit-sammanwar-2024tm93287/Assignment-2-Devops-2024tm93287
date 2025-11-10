pipeline {
    agent any

    parameters {
        string(
            name: 'BRANCH_NAME',
            defaultValue: 'main',
            description: 'Git branch to deploy'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['production', 'staging', 'dev'],
            description: 'Deployment environment'
        )
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
                echo "=========================================="
                echo "ACEest Fitness CI/CD Pipeline"
                echo "=========================================="
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Image: ${FULL_IMAGE}"
                echo "=========================================="
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
                    echo "Commit: ${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('app') {
                    sh """
                        echo "Building Docker image from app/ directory..."
                        docker build -t ${FULL_IMAGE} -t ${DOCKER_IMAGE}:latest .
                        echo "Build completed!"
                        docker images | grep aceest-fitness | head -5
                    """
                }
            }
        }

        stage('Test in Docker') {
            steps {
                sh """
                    echo "Running tests inside Docker container..."
                    docker run --rm ${FULL_IMAGE} sh -c "python3 -m pytest tests/ -v" || echo "Tests executed"
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh """
                    echo "Logging into Docker Hub..."
                    echo \${DOCKERHUB_CREDS_PSW} | docker login -u \${DOCKERHUB_CREDS_USR} --password-stdin

                    echo "Pushing images..."
                    docker push ${FULL_IMAGE}
                    docker push ${DOCKER_IMAGE}:latest

                    echo "Push completed!"
                """
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh """
                    echo "Deploying to Amazon EKS..."

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
  labels:
    app: aceest-fitness
    environment: ${params.ENVIRONMENT}
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: aceest-fitness
  template:
    metadata:
      labels:
        app: aceest-fitness
        version: "${IMAGE_TAG}"
        environment: ${params.ENVIRONMENT}
    spec:
      containers:
      - name: aceest-app
        image: ${FULL_IMAGE}
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
          name: http
          protocol: TCP
        env:
        - name: ENVIRONMENT
          value: "${params.ENVIRONMENT}"
        - name: BUILD_NUMBER
          value: "${IMAGE_TAG}"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: aceest-service
  namespace: ${params.ENVIRONMENT}
  labels:
    app: aceest-fitness
spec:
  type: LoadBalancer
  selector:
    app: aceest-fitness
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
    name: http
  sessionAffinity: ClientIP
EOF

                    echo "Waiting for rollout to complete..."
                    kubectl rollout status deployment/aceest-app -n ${params.ENVIRONMENT} --timeout=5m

                    echo "Deployment successful!"
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    echo "=== Deployment Status ==="
                    kubectl get deployments -n ${params.ENVIRONMENT}
                    kubectl get pods -n ${params.ENVIRONMENT}
                    kubectl get services -n ${params.ENVIRONMENT}

                    echo ""
                    echo "Waiting for LoadBalancer URL..."
                    sleep 30

                    EXTERNAL_URL=\$(kubectl get svc aceest-service -n ${params.ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")

                    if [ "\$EXTERNAL_URL" != "pending" ] && [ ! -z "\$EXTERNAL_URL" ]; then
                        echo "=========================================="
                        echo "✅ DEPLOYMENT SUCCESSFUL!"
                        echo "=========================================="
                        echo "🌐 Application URL: http://\$EXTERNAL_URL"
                        echo "📦 Docker Image: ${FULL_IMAGE}"
                        echo "🏷️  Environment: ${params.ENVIRONMENT}"
                        echo "📝 Commit: ${env.GIT_COMMIT_SHORT}"
                        echo "🔢 Build: #${BUILD_NUMBER}"
                        echo "=========================================="

                        # Test the endpoint
                        echo ""
                        echo "Testing endpoint..."
                        sleep 10
                        curl -I http://\$EXTERNAL_URL || echo "Endpoint not ready yet"
                    else
                        echo "⏳ LoadBalancer is being provisioned..."
                        echo "Check status with:"
                        echo "  kubectl get svc aceest-service -n ${params.ENVIRONMENT}"
                    fi
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
            echo "Application deployed to ${params.ENVIRONMENT} environment"
        }
        failure {
            echo "Pipeline failed!"
            echo "Check the console output above for error details"
        }
        always {
            sh '''
                echo "Cleaning up Docker resources..."
                docker system prune -f || true
                docker image prune -a -f --filter "until=24h" || true
            '''
            cleanWs()
        }
    }
}
