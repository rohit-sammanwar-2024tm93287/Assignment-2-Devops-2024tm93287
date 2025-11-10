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
        K8S_NAMESPACE = "${params.ENVIRONMENT}"
        IMAGE_TAG = "${BUILD_NUMBER}"
        FULL_IMAGE = "${DOCKER_IMAGE}:${IMAGE_TAG}"
    }

    stages {
        stage('Initialize') {
            steps {
                echo "Building ${params.BRANCH_NAME} for ${params.ENVIRONMENT}"
                echo "Image: ${FULL_IMAGE}"
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

        stage('Build') {
            steps {
                sh '''
                    cd app
                    echo "Building application..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    cd app
                    echo "Running tests..."
                    . venv/bin/activate
                    pytest tests/ -v --junitxml=test-results.xml --cov=app
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    cd app
                    docker build -t ${FULL_IMAGE} -t ${DOCKER_IMAGE}:latest .
                    docker images | grep aceest-fitness
                """
            }
        }

        stage('Docker Push') {
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
                    kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

                    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aceest-app
  namespace: ${K8S_NAMESPACE}
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
  - port: 80
    targetPort: 5000
EOF

                    kubectl rollout status deployment/aceest-app -n ${K8S_NAMESPACE}
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    kubectl get all -n ${K8S_NAMESPACE}
                    EXTERNAL_URL=\$(kubectl get svc aceest-service -n ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
                    echo "Application URL: http://\$EXTERNAL_URL"
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
        always {
            cleanWs()
        }
    }
}
