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
        // Docker Hub credentials
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = '2024tm93287/aceest-fitness'

        // AWS/EKS configuration
        AWS_REGION = 'us-east-1'
        EKS_CLUSTER = 'aceest-fitness-cluster'
        K8S_NAMESPACE = "${params.ENVIRONMENT}"

        // Image tag
        IMAGE_TAG = "${BUILD_NUMBER}-${params.BRANCH_NAME.replaceAll('/', '-')}"
        FULL_IMAGE = "${DOCKER_IMAGE}:${IMAGE_TAG}"
    }

    stages {
        stage('📋 Initialize') {
            steps {
                echo "=========================================="
                echo "🚀 ACEest Fitness CI/CD Pipeline - AWS EKS"
                echo "=========================================="
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Image: ${FULL_IMAGE}"
                echo "EKS Cluster: ${EKS_CLUSTER}"
                echo "=========================================="
            }
        }

        stage('🔽 Checkout from GitHub') {
            steps {
                script {
                    echo "Checking out branch: ${params.BRANCH_NAME}"
                    checkout scmGit(
                        branches: [[name: "*/${params.BRANCH_NAME}"]],
                        userRemoteConfigs: [[
                            url: 'https://github.com/rohit-sammanwar-2024tm93287/Assignment-2-Devops-2024tm93287.git',
                            credentialsId: 'github-credentials'
                        ]]
                    )

                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()

                    echo "✅ Checked out commit: ${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('🔨 Build Application') {
            steps {
                sh '''
                    echo "Installing Python dependencies..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "✅ Build completed"
                '''
            }
        }

        stage('🧪 Run Tests') {
            steps {
                sh '''
                    echo "Running pytest tests..."
                    . venv/bin/activate
                    pytest tests/ -v --junitxml=test-results.xml --cov=app --cov-report=xml
                    echo "✅ All tests passed"
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('🐳 Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh """
                        docker build -t ${FULL_IMAGE} -t ${DOCKER_IMAGE}:latest .
                        echo "✅ Docker image built"
                        docker images | grep aceest-fitness
                    """
                }
            }
        }

        stage('📤 Push to Docker Hub') {
            steps {
                sh """
                    echo "Pushing to Docker Hub..."
                    echo ${DOCKERHUB_CREDS_PSW} | docker login -u ${DOCKERHUB_CREDS_USR} --password-stdin
                    docker push ${FULL_IMAGE}
                    docker push ${DOCKER_IMAGE}:latest
                    echo "✅ Image pushed: ${FULL_IMAGE}"
                """
            }
        }

        stage('☸️ Deploy to AWS EKS') {
            steps {
                script {
                    echo "Deploying to EKS cluster..."
                    sh """
                        # Update kubeconfig
                        aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}

                        # Create namespace if doesn't exist
                        kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

                        # Deploy application
                        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-app
  namespace: ${K8S_NAMESPACE}
  labels:
    app: aceest-fitness
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aceest-fitness
  template:
    metadata:
      labels:
        app: aceest-fitness
        version: ${IMAGE_TAG}
    spec:
      containers:
      - name: aceest-app
        image: ${FULL_IMAGE}
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /api/workouts
            port: 5000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/workouts
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: aceest-service
  namespace: ${K8S_NAMESPACE}
spec:
  type: LoadBalancer
  selector:
    app: aceest-fitness
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
EOF

                        # Wait for rollout
                        kubectl rollout status deployment/aceest-app -n ${K8S_NAMESPACE} --timeout=5m
                        echo "✅ Deployment completed"
                    """
                }
            }
        }

        stage('✅ Verify Deployment') {
            steps {
                sh """
                    echo "Verifying deployment..."
                    kubectl get deployments -n ${K8S_NAMESPACE}
                    kubectl get pods -n ${K8S_NAMESPACE}
                    kubectl get service aceest-service -n ${K8S_NAMESPACE}

                    # Get external URL
                    echo "Waiting for LoadBalancer URL..."
                    sleep 30
                    EXTERNAL_URL=\$(kubectl get service aceest-service -n ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

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
            echo "❌ Pipeline failed!"
        }
        always {
            cleanWs()
        }
    }
}
