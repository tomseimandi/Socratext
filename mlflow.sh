# Set MLFLOW_TRACKING_URI environment variable
export MLFLOW_S3_ENDPOINT_URL='https://minio.lab.sspcloud.fr'
export MLFLOW_TRACKING_URI="https://projet-socratext-588729.user.lab.sspcloud.fr"
export MLFLOW_EXPERIMENT_NAME="ticket_extraction"

mlflow run ~/work/Socratext/ --entry-point ticket_extraction --env-manager=local -P remote_server_uri=$MLFLOW_TRACKING_URI
