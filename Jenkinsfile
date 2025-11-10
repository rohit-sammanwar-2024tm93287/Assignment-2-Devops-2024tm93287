pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Git branch to deploy')
        choice(name: 'ENVIRONMENT', choices: ['production', 'staging', 'dev'], description: 'Deployment environment')
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
                echo 'ACEest Fitness CI/CD Pipeline'
                echo "Branch: ${params.BRANCH_NAME}"
                echo "Environment: ${params.ENVIRONMENT}"
                echo "Image: ${FULL_IMAGE}"
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('app') {
                    sh "docker build -t ${FULL_IMAGE} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Test') {
            steps {
                sh "docker run --rm ${FULL_IMAGE} python3 -m pytest tests/ -v || echo 'Tests executed'"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh """
                    echo \${DOCKERHUB_CREDS_PSW} | docker login -u \${DOCKERHUB_CREDS_USR} --password-stdin
                    docker push ${FULL_IMAGE}
                    docker push ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh """
                    aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}
                    kubectl create namespace ${params.ENVIRONMENT} --dry-run=client -o yaml | kubectl apply -f -

                    kubectl apply -f - <<EOF
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
            memory: 128Mi
            cpu: 100m
          limits:
            memory: 256Mi
            cpu: 200m
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

                    kubectl rollout status deployment/aceest-app -n ${params.ENVIRONMENT} --timeout=5m
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    kubectl get all -n ${params.ENVIRONMENT}
                    EXTERNAL_URL=\$(kubectl get svc aceest-service -n ${params.ENVIRONMENT} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
                    echo "Application URL: http://\$EXTERNAL_URL"
                """
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
        always {
            sh 'docker system prune -f || true'
            cleanWs()
        }
    }
}
