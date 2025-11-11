# ACEest Fitness - CI/CD Deployment Guide

Complete Jenkins CI/CD pipeline for deploying ACEest Fitness application to AWS EKS with multi-version support.

## Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Version Management](#-version-management)
- [Setup Instructions](#-setup-instructions)
- [Deployment Guide](#-deployment-guide)
- [Accessing the Application](#-accessing-the-application)
- [Troubleshooting](#-troubleshooting)
- [Cost Optimization](#-cost-optimization)
- [Cleanup](#-cleanup)

## Project Overview

ACEest Fitness is a Flask-based fitness tracking application with multiple versions deployed through a Jenkins CI/CD pipeline to AWS EKS (Elastic Kubernetes Service).

### Key Features

✅ Automated CI/CD pipeline with Jenkins  
✅ Containerized deployment using Docker  
✅ Kubernetes orchestration on AWS EKS  
✅ Multi-version support (V1.0 → V1.3)  
✅ Branch-based deployment strategy  
✅ Automated testing and building  
✅ LoadBalancer for external access

### Jenkins Credentials (Intentionally sharing the credentials and not the URL)

The URL for the jenkins can be found in the submitted document along with the Assignment.
- **Username**: admin
- **Password**: Admin@123

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Application | Python 3.11, Flask 3.0.0, Gunicorn |
| Containerization | Docker |
| CI/CD | Jenkins |
| Orchestration | Kubernetes (AWS EKS) |
| Cloud Provider | AWS (EC2, EKS, VPC) |
| Version Control | Git, GitHub |
| Container Registry | Docker Hub |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  main    │  │ develop  │  │ feature  │  │ hotfix   │       │
│  │ (v1.0)   │  │ (v1.1)   │  │ (v1.3)   │  │ (v1.2.x) │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │    Jenkins Pipeline      │
        │  ┌───────────────────┐  │
        │  │ 1. Checkout       │  │
        │  │ 2. Build Docker   │  │
        │  │ 3. Test           │  │
        │  │ 4. Push to Hub    │  │
        │  │ 5. Deploy to EKS  │  │
        │  │ 6. Verify         │  │
        │  └───────────────────┘  │
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │      Docker Hub          │
        │  aceest-fitness:latest   │
        │  aceest-fitness:24       │
        │  aceest-fitness:25       │
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │       AWS EKS Cluster    │
        │  ┌───────────────────┐  │
        │  │ Production Pods   │  │
        │  │ ┌──┐ ┌──┐ ┌──┐  │  │
        │  │ │v1│ │v2│ │v3│  │  │
        │  │ └──┘ └──┘ └──┘  │  │
        │  └───────────────────┘  │
        │  LoadBalancer → Internet │
        └─────────────────────────┘
```

## ✅ Prerequisites

### AWS Account Requirements
- AWS account with admin access
- AWS CLI installed and configured
- IAM user with EKS, EC2, VPC permissions

### Local Machine Requirements
- Git
- AWS CLI
- kubectl
- eksctl
- SSH client

### Services Used
- **GitHub**: Source code repository
- **Docker Hub**: Container registry
- **AWS EC2**: Jenkins server
- **AWS EKS**: Kubernetes cluster
- **AWS VPC**: Networking

## 📁 Project Structure

```
Assignment-2-Devops-2024tm93287/
├── app/
│   ├── app.py                    # Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Container image definition
│   ├── templates/
│   │   └── index.html           # Web UI
│   ├── static/
│   │   └── css/
│   │       └── style.css        # Styling
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_app.py          # Unit tests
├── Jenkinsfile                   # CI/CD pipeline definition
└── README.md                     # This file
```

## 🔄 Version Management

### Application Versions

| Version | Branch                | Features | Status |
|--------|-----------------------|----------|--------|
| V1.0   | ACEest_Fitness-V1.0   | Basic workout tracking | ✅ Stable |
| V1.1   | ACEest_Fitness-V1.1   | User authentication | ✅ Stable |
| V1.2  | ACEest_Fitness-V1.2   | Bug fixes | ✅ Stable |
| V1.2.1 | ACEest_Fitness-V1.2.1 | Performance improvements | ✅ Stable |
| V1.3   | ACEest_Fitness-V1.3   | Advanced reporting | ✅ Stable |

### Deployment Strategy

**Single Jenkinsfile for All Versions** ✅

The Jenkins pipeline uses the `BRANCH_NAME` parameter to deploy any version:

```groovy
parameters {
    string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Git branch to deploy')
    choice(name: 'ENVIRONMENT', choices: ['production', 'staging', 'dev'], description: 'Environment')
}
```

**How it works:**
1. Select version by choosing the branch name
2. Jenkins checks out that specific branch
3. Builds Docker image with that code
4. Deploys to selected environment

**Example Deployments:**

```bash
# Deploy V1.0 (main) to production
BRANCH_NAME: main
ENVIRONMENT: production

# Deploy V1.3 (feature) to staging
BRANCH_NAME: feature/v1.3
ENVIRONMENT: staging

# Deploy V1.2.1 (hotfix) to dev
BRANCH_NAME: hotfix/v1.2.1
ENVIRONMENT: dev
```

## 🚀 Setup Instructions

### Step 1: Create AWS EKS Cluster

```bash
# Install eksctl (if not already installed)
# Windows: choco install eksctl
# Linux: curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp && sudo mv /tmp/eksctl /usr/local/bin

# Create EKS cluster
eksctl create cluster \
  --name aceest-fitness-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.micro \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name aceest-fitness-cluster

# Verify cluster
kubectl get nodes
```

**Expected output:**
```
NAME                            STATUS   ROLES    AGE   VERSION
ip-xxx-xxx-xxx-xxx.ec2.internal Ready    <none>   2m    v1.28.x
ip-xxx-xxx-xxx-xxx.ec2.internal Ready    <none>   2m    v1.28.x
```

### Step 2: Create Jenkins EC2 Instance

```bash
# Create security group
aws ec2 create-security-group \
  --group-name jenkins-sg \
  --description "Jenkins Security Group" \
  --region us-east-1

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups --group-names jenkins-sg --query 'SecurityGroups[0].GroupId' --output text --region us-east-1)

# Allow SSH
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Allow Jenkins
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Create key pair
aws ec2 create-key-pair \
  --key-name jenkins-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > jenkins-key.pem

chmod 400 jenkins-key.pem

# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name jenkins-key \
  --security-group-ids $SG_ID \
  --region us-east-1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=jenkins-master}]'
```

### Step 3: Install Jenkins

```bash
# SSH into instance
JENKINS_IP=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=jenkins-master" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region us-east-1)
ssh -i jenkins-key.pem ec2-user@$JENKINS_IP

# Install Jenkins
sudo yum update -y
sudo amazon-linux-extras install java-openjdk11 -y
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum install jenkins -y
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Install Docker
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user
sudo usermod -aG docker jenkins

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Configure AWS for jenkins user
sudo su - jenkins
aws configure
# Enter your AWS credentials
aws eks update-kubeconfig --region us-east-1 --name aceest-fitness-cluster
kubectl get nodes
exit

# Get Jenkins password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# Restart Jenkins
sudo systemctl restart jenkins
exit
```

### Step 4: Configure Jenkins

1. Access Jenkins: `http://<JENKINS_IP>:8080`
2. Enter initial password
3. Install suggested plugins
4. Create admin user
5. Install additional plugins:
    - Docker Pipeline
    - Kubernetes
    - Kubernetes CLI
    - AWS Steps

### Step 5: Add Credentials

**Docker Hub:**
```
Manage Jenkins → Manage Credentials → Add Credentials
Kind: Username with password
ID: dockerhub-credentials
Username: <your-dockerhub-username>
Password: <your-dockerhub-password>
```

**AWS:**
```
Add Credentials
Kind: AWS Credentials
ID: aws-credentials
Access Key ID: <your-aws-access-key>
Secret Access Key: <your-aws-secret-key>
```

**GitHub:**
```
Add Credentials
Kind: Username with password
ID: github-credentials
Username: <your-github-username>
Password: <github-personal-access-token>
```

### Step 6: Create Pipeline

```
1. New Item → Pipeline → Name: "ACEest-Fitness-EKS-Deploy"
2. Pipeline section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: https://github.com/<username>/Assignment-2-Devops-2024tm93287.git
   - Credentials: github-credentials
   - Branches: */main
   - Script Path: Jenkinsfile
3. Save
```

## 📦 Deployment Guide

### Deploy Any Version

1. Go to Jenkins → ACEest-Fitness-EKS-Deploy
2. Click "Build with Parameters"
3. Select version:

| Version | BRANCH_NAME           | ENVIRONMENT |
|---------|-----------------------|-------------|
| V1.0    | ACEest_Fitness-V1.0   | production |
| V1.1    | ACEest_Fitness-V1.1   | staging |
| V1.2    | ACEest_Fitness-V1.2   | dev |
| V1.2.1  | ACEest_Fitness-V1.2.1 | staging |
| V1.3    | ACEest_Fitness-V1.3   | staging |

4. Click "Build"
5. Monitor progress in Console Output

### Pipeline Stages

```
1. Initialize     → Display build info
2. Checkout       → Clone specified branch
3. Build          → Create Docker image
4. Push           → Upload to Docker Hub
5. Deploy         → Apply to EKS cluster
6. Verify         → Check deployment status
```

### Expected Build Time

- Checkout: 10 seconds
- Build: 60-90 seconds
- Push: 30 seconds
- Deploy: 60 seconds
- **Total: ~3 minutes**

## 🌐 Accessing the Application

### Get Application URL

```bash
# Method 1: kubectl
kubectl get svc aceest-service -n production

# Method 2: AWS CLI
aws elbv2 describe-load-balancers --region us-east-1

# Method 3: From Jenkins Console Output
# Look for: "Application URL: http://..."
```

### Test the Application

```bash
# Get URL
EXTERNAL_URL=$(kubectl get svc aceest-service -n production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test
curl http://$EXTERNAL_URL

# Or open in browser
echo "http://$EXTERNAL_URL"
```

### Application Endpoints

```
/ (or /home)          → Home page
/workouts             → Workout list
/workout/<id>         → Workout details
/api/workouts         → API endpoint
/health               → Health check
```