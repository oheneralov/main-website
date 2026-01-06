# AWS CI/CD Configuration Files

This directory contains configuration files for AWS CodePipeline, CodeBuild, and CodeDeploy.

## Files

- **buildspec.yml** - CodeBuild specification file for building, testing, and pushing Docker images to ECR
- **appspec-ec2.yml** - CodeDeploy specification for EC2 instance deployments
- **appspec-ecs.yml** - CodeDeploy specification for ECS service deployments
- **pipeline.json** - CodePipeline configuration for orchestrating the CI/CD workflow

## Usage

1. Place `buildspec.yml` in the project root or specify its location in CodeBuild project settings
2. Use `appspec-ec2.yml` or `appspec-ecs.yml` based on your deployment target (rename to `appspec.yml` and place in project root)
3. Use `pipeline.json` when creating the CodePipeline via AWS CLI

## Configuration

Before using these files:

- Update AWS Account ID in files (replace `123456789012`)
- Update GitHub organization and token in `pipeline.json`
- Update AWS region (`us-east-1`)
- Update subnet and security group IDs in `appspec-ecs.yml`
- Configure EC2 instance tags for targeting in deployment groups

## References

See [README.md](../README.md#-aws-cicd-deployment-codepipeline-codebuild-codedeploy) for detailed setup instructions.
