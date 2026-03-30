"""
ml.t3.medium	2	4 GB	Burstable, cheap, low traffic/short jobs
ml.t3.large	2	8 GB	More memory
ml.m5.large	2	8 GB	Standard general purpose
ml.m5.xlarge	4	16 GB	Larger
ml.m5.2xlarge	8	32 GB	Only if dataset is bigger
"""
"""SageMaker v3 training job script using ModelTrainer and ModelBuilder for deployment.
https://sagemaker.readthedocs.io/en/stable/api/training/model_trainer.html
"""



import os
import logging
import argparse
import sagemaker
from sagemaker.train import ModelTrainer
from sagemaker.core.training.configs import Compute, InputData, S3DataSource, StoppingCondition
from sagemaker.serve import ModelBuilder
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

image_uri = os.environ.get("IMAGE_URI", "473587278533.dkr.ecr.us-east-1.amazonaws.com/sklearn-train:latest")
role = os.environ.get("SAGEMAKER_ROLE", "arn:aws:iam::473587278533:role/service-role/AmazonSageMaker-ExecutionRole-20251112T173851")
s3_bucket = os.environ.get("S3_BUCKET", "sagemakeroheneralov")
s3_model_key = os.environ.get("S3_MODEL_KEY", "models/feedforward/model_evenodd.pth")


def deploy_model(s3_model_uri, logger):
    """Deploy the trained model using SageMaker v3 ModelBuilder"""
    try:
        deploy_endpoint = os.environ.get("DEPLOY_ENDPOINT", "false").lower() == "true"
        
        if not deploy_endpoint:
            logger.info("Model deployment disabled. Set DEPLOY_ENDPOINT=true to deploy.")
            return None
        
        logger.info("Creating SageMaker ModelBuilder for deployment")
        sagemaker_session = sagemaker.Session()
        
        # Get deployment parameters
        instance_type = os.environ.get("DEPLOY_INSTANCE_TYPE", "ml.t3.medium")
        instance_count = int(os.environ.get("DEPLOY_INSTANCE_COUNT", "1"))
        
        logger.info(f"Deploying model to SageMaker endpoint")
        logger.info(f"  Model URI: {s3_model_uri}")
        logger.info(f"  Instance Type: {instance_type}")
        logger.info(f"  Instance Count: {instance_count}")
        
        # Create ModelBuilder with the model artifact
        model_builder = ModelBuilder(
            s3_model_data_url=s3_model_uri,
            image_uri=image_uri,
            role_arn=role,
            sagemaker_session=sagemaker_session,
        )
        
        # Build the model (creates SageMaker Model resource)
        model = model_builder.build(model_name=f"evenodd-classifier-model")
        
        # Deploy to endpoint using v3 API
        endpoint_name = os.environ.get("DEPLOY_ENDPOINT_NAME", "evenodd-classifier")
        
        endpoint = model_builder.deploy(
            endpoint_name=endpoint_name,
            initial_instance_count=instance_count,
            instance_type=instance_type,
            wait=True,
        )
        
        logger.info(f"Model deployed successfully!")
        logger.info(f"  Endpoint Name: {endpoint_name}")
        logger.info(f"  Endpoint Status: In Service")
        
        return endpoint_name
        
    except Exception as e:
        logger.error(f"Failed to deploy model: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Run SageMaker training job.")
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--deploy', action='store_true', help='Deploy model after training')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("Setting AWS region for SageMaker")
    os.environ["AWS_DEFAULT_REGION"] = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    logger.info("Initializing ModelTrainer")
    trainer = ModelTrainer(
        training_image=image_uri,
        role=role,
        compute=Compute(
            instance_type="ml.m5.large",
            instance_count=1,
            volume_size_in_gb=30,
            enable_managed_spot_training=True,
        ),
        stopping_condition=StoppingCondition(
            max_runtime_in_seconds=3600,
            max_wait_time_in_seconds=7200,
        ),
    )

    logger.info("Configuring training data input")
    train_data = InputData(
        channel_name="train",
        data_source=S3DataSource(
            s3_uri=f"s3://{s3_bucket}/train",
            s3_data_type="S3Prefix",
            s3_data_distribution_type="FullyReplicated",
        ),
    )

    logger.info("Starting training job")
    training_job = trainer.train(input_data_config=[train_data])
    logger.info("Training job submitted.")
    
    # Deploy model if requested
    if args.deploy or os.environ.get("DEPLOY_ENDPOINT", "false").lower() == "true":
        logger.info("\nStarting model deployment...")
        
        # Get the trained model output from the training job
        if hasattr(training_job, 'output_path') and training_job.output_path:
            s3_model_uri = f"{training_job.output_path}/output/model.tar.gz"
        else:
            # Fallback to default output path pattern for SageMaker training jobs
            training_job_name = training_job if isinstance(training_job, str) else getattr(training_job, 'name', None)
            if training_job_name:
                s3_model_uri = f"s3://{s3_bucket}/sagemaker-output/{training_job_name}/output/model.tar.gz"
            else:
                s3_model_uri = f"s3://{s3_bucket}/{s3_model_key}"
        
        logger.info(f"Model S3 URI: {s3_model_uri}")
        
        endpoint_name = deploy_model(s3_model_uri, logger)
        if endpoint_name:
            logger.info(f"\nDeployment completed! Endpoint: {endpoint_name}")
    else:
        logger.info("\nModel deployment not requested. Use --deploy flag or set DEPLOY_ENDPOINT=true to deploy.")


if __name__ == "__main__":
    main()
