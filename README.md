# AWS Info Website

A comprehensive web application for displaying AWS information with infrastructure automation, containerization, and modern frontend technologies.

## 📋 Project Overview

This is a full-stack application that combines:
- **Backend**: NestJS API server with TypeScript
- **Frontend**: React application with Vite
- **Infrastructure**: Kubernetes (Helm), Terraform, and Docker
- **Metrics**: Prometheus metrics collection service
- **CI/CD**: Jenkins pipelines for build, validation, and deployment
- **Design**: Responsive web design with Pug templates and SCSS

## 🏗️ Project Structure

```
├── mainwebsite/           # Main NestJS backend + React frontend
├── design/                # Static design assets and templates
├── metrics/               # Prometheus metrics service
├── helm-dir/              # Kubernetes Helm charts
├── terraform/             # Infrastructure as Code (Terraform)
├── Jenkinsfile.*          # CI/CD pipeline definitions
└── LICENSE                # Project license
```

## 🚀 Quick Start

### Prerequisites
- Node.js (v16+)
- Docker & Docker Compose
- Kubernetes cluster (optional, for deployment)
- AWS credentials configured

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aws-info-website
   ```

2. **Install dependencies**
   ```bash
   cd mainwebsite
   npm install
   cd ../metrics
   npm install
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env` (if available)
   - Update AWS credentials and API endpoints

4. **Run the application**
   ```bash
   cd mainwebsite
   npm start
   ```

## 📚 Directory Details

### `/mainwebsite`
The core application with NestJS backend and React frontend.

- **Backend** (`src/`): NestJS application with authentication, captcha, logging, and contact services
- **Frontend** (`react/`): React app built with Vite
- **Public Assets** (`public/`): Static files, CSS, fonts, images, video
- **Documentation**: See [START_HERE.md](mainwebsite/START_HERE.md) and [DEPLOYMENT_GUIDE.md](mainwebsite/DEPLOYMENT_GUIDE.md)

### `/design`
Design assets and templates.

- **Site** (`site/`): HTML, CSS, JavaScript for the static website
- **Sources** (`sources/`): Pug templates and SCSS source files
- **Configuration** (`documentation.txt`): Design documentation

### `/helm-dir`
Kubernetes Helm charts for deployment.

- `deployment.yaml`: Main application deployment
- `service.yaml`: Kubernetes service definitions
- `ingress.yaml`: Ingress configuration
- `hpa-*.yaml`: Horizontal Pod Autoscalers
- `values-*.yaml`: Environment-specific values (dev, staging, prod)

See [TESTS_DOCUMENTATION.md](helm-dir/TESTS_DOCUMENTATION.md) for testing details.

### `/terraform`
Infrastructure as Code for AWS/cloud resources.

- `main.tf`: Primary infrastructure definitions
- `variables.tf`: Variable definitions
- `outputs.tf`: Output values
- `modules/`: Reusable Terraform modules (e.g., GKE deployment)
- `environments/`: Environment-specific configurations

See [SETUP.md](terraform/SETUP.md) and [TROUBLESHOOTING.md](terraform/TROUBLESHOOTING.md).

### `/metrics`
Prometheus metrics collection and monitoring service.

- `index.js`: Node.js metrics server
- `package.json`: Dependencies

## 🐳 Docker

Build and run containerized services:

```bash
# Build Docker images
docker build -t mainwebsite:latest ./mainwebsite
docker build -t metrics:latest ./metrics

# Run containers
docker run -p 3000:3000 mainwebsite:latest
docker run -p 9090:9090 metrics:latest
```

## ☸️ Kubernetes Deployment

Deploy to Kubernetes cluster using Helm:

```bash
# Add Helm repository (if applicable)
helm repo add <repo-name> <repo-url>

# Deploy to different environments
helm install aws-info-website ./helm-dir -f helm-dir/values-dev.yaml    # Dev
helm install aws-info-website ./helm-dir -f helm-dir/values-staging.yaml # Staging
helm install aws-info-website ./helm-dir -f helm-dir/values-prod.yaml    # Production

# Upgrade deployment
helm upgrade aws-info-website ./helm-dir -f helm-dir/values-prod.yaml
```

## 🔄 CI/CD Pipeline

Jenkins pipelines automate build, validation, and deployment:

- `Jenkinsfile.build`: Build stage
- `Jenkinsfile.validate`: Code validation and testing
- `Jenkinsfile.deploy`: Production deployment

## 🔧 AWS CI/CD Deployment (CodePipeline, CodeBuild, CodeDeploy)

This project can be deployed to AWS using CodePipeline, CodeBuild, and CodeDeploy for automated continuous integration and deployment.

### Prerequisites
- AWS account with appropriate IAM permissions
- CodePipeline, CodeBuild, and CodeDeploy services enabled
- GitHub repository connected to CodePipeline
- Amazon ECR repository for storing Docker images
- EC2 instances or ECS cluster for deployment targets
- CodeDeploy agent installed on EC2 instances (for EC2 deployments)

### AWS Services Overview

**CodePipeline**: Orchestrates the entire CI/CD workflow
- Monitors source code repository for changes
- Triggers CodeBuild for compilation and testing
- Deploys using CodeDeploy

**CodeBuild**: Builds, tests, and packages the application
- Compiles TypeScript/React code
- Runs unit and E2E tests
- Builds Docker images
- Pushes images to ECR

**CodeDeploy**: Automates application deployment
- Deploys to EC2 instances, on-premises servers, or auto-scaling groups
- Manages traffic shifting and health checks
- Supports rollback capabilities

### Setup Instructions

#### 1. Create CodePipeline

```bash
# Create an S3 bucket for pipeline artifacts
aws s3 mb s3://aws-info-website-pipeline-artifacts

# Create IAM role for CodePipeline
aws iam create-role --role-name CodePipelineServiceRole \
  --assume-role-policy-document file://trust-policy.json

# Attach required policies
aws iam attach-role-policy --role-name CodePipelineServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AWSCodePipelineFullAccess
```

#### 2. Create CodeBuild Project

Use the `buildspec.yml` file from [aws-ci-cd-config/buildspec.yml](aws-ci-cd-config/buildspec.yml). Place it in the project root or specify its location in CodeBuild project settings.

Create CodeBuild project via AWS CLI:

```bash
aws codebuild create-project \
  --name aws-info-website-build \
  --source type=GITHUB,location=https://github.com/your-org/aws-info-website \
  --artifacts type=S3,location=aws-info-website-pipeline-artifacts \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_LARGE,environmentVariables='[{"name":"AWS_DEFAULT_REGION","value":"us-east-1"},{"name":"AWS_ACCOUNT_ID","value":"123456789012"}]' \
  --service-role arn:aws:iam::123456789012:role/CodeBuildServiceRole
```

#### 3. Create CodeDeploy Application

```bash
# Create CodeDeploy application
aws deploy create-app --application-name aws-info-website

# Create deployment group for EC2 instances
aws deploy create-deployment-group \
  --application-name aws-info-website \
  --deployment-group-name aws-info-website-deployment \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --ec2-tag-filters Key=Environment,Value=production,Type=KEY_AND_VALUE
```

Use `appspec-ec2.yml` from [aws-ci-cd-config/appspec-ec2.yml](aws-ci-cd-config/appspec-ec2.yml). Rename it to `appspec.yml` and place in project root for EC2 deployment.

#### 4. Create CodePipeline

Use the `pipeline.json` file from [aws-ci-cd-config/pipeline.json](aws-ci-cd-config/pipeline.json):

```bash
aws codepipeline create-pipeline \
  --cli-input-json file://aws-ci-cd-config/pipeline.json
```

Update the following in `pipeline.json` before using:
- AWS Account ID (replace `123456789012`)
- GitHub organization and token
- AWS region

### ECS Deployment (Alternative)

For ECS deployment with CodeDeploy:

```bash
aws deploy create-deployment-group \
  --application-name aws-info-website \
  --deployment-group-name aws-info-website-ecs \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
  --deployment-config-name CodeDeployDefault.ECSAllAtOnce \
  --deployment-style deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL
```

Use `appspec-ecs.yml` from [aws-ci-cd-config/appspec-ecs.yml](aws-ci-cd-config/appspec-ecs.yml). Rename it to `appspec.yml` and place in project root. Update the following:
- Task definition name and version
- Container name and port
- Subnet IDs
- Security group IDs

### Monitoring and Troubleshooting

Monitor pipeline execution:
```bash
# Get pipeline status
aws codepipeline get-pipeline-state --name aws-info-website-pipeline

# Get build logs
aws codebuild batch-get-builds --ids <build-id>

# Get deployment status
aws deploy get-deployment --deployment-id <deployment-id>
```

View logs in CloudWatch:
- CodeBuild logs: `/aws/codebuild/aws-info-website-build`
- CodeDeploy logs: `/aws/codedeploy/aws-info-website`

### Environment-Specific Deployments

For staging and production:

```bash
# Create separate deployment groups
aws deploy create-deployment-group \
  --application-name aws-info-website \
  --deployment-group-name aws-info-website-staging \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
  --ec2-tag-filters Key=Environment,Value=staging,Type=KEY_AND_VALUE

aws deploy create-deployment-group \
  --application-name aws-info-website \
  --deployment-group-name aws-info-website-production \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
  --ec2-tag-filters Key=Environment,Value=production,Type=KEY_AND_VALUE
```

## 🛠️ Development

### Backend Development
```bash
cd mainwebsite
npm run start:dev      # Start in development mode
npm run build          # Build TypeScript
npm test               # Run unit tests
npm run test:e2e       # Run end-to-end tests
```

### Frontend Development
```bash
cd mainwebsite/react
npm run dev            # Start Vite dev server
npm run build          # Build for production
```

### Design/Template Development
- Edit Pug templates in `design/sources/pug/`
- Compile SCSS in `design/sources/scss/`
- Output to `design/site/`

## 🔐 Security

- **Authentication**: OAuth/JWT implemented in backend
- **Captcha**: reCAPTCHA integration for form protection
- **Contact Form**: Mail form with PHP backend for inquiries

## 📊 Monitoring

- **Metrics Service**: Prometheus-compatible metrics on port 9090
- **Health Checks**: Service health endpoints configured in Helm charts
- **Logging**: Centralized logging service in backend

## 📝 Configuration Files

- `helm-dir/values.yaml`: Default Helm values
- `helm-dir/values-dev.yaml`: Development environment
- `helm-dir/values-staging.yaml`: Staging environment
- `helm-dir/values-prod.yaml`: Production environment
- `terraform/backend.tf`: Terraform backend configuration
- `mainwebsite/tsconfig.json`: TypeScript configuration

## 🧪 Testing

- Unit tests: `npm test`
- E2E tests: `npm run test:e2e`
- Helm chart tests: See `helm-dir/TESTS_DOCUMENTATION.md`

## 🚢 Deployment Guides

- **Mainwebsite**: [DEPLOYMENT_GUIDE.md](mainwebsite/DEPLOYMENT_GUIDE.md)
- **Infrastructure**: [terraform/SETUP.md](terraform/SETUP.md)
- **Troubleshooting**: [terraform/TROUBLESHOOTING.md](terraform/TROUBLESHOOTING.md)
- **Helm**: [helm-dir/README.md](helm-dir/README.md)

## 📄 License

This project is licensed under the terms specified in [LICENSE](LICENSE).

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and validation
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check existing documentation in project subdirectories
2. Review CI/CD logs in Jenkins
3. Consult Terraform and Helm documentation for infrastructure issues

---

**Last Updated**: January 2, 2026
