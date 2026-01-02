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
