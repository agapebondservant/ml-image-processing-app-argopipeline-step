## Deployment
* Create a Docker secret for the target container registry:
```
source .env
REGISTRY_PASSWORD=$DATA_E2E_REGISTRY_PASSWORD kp secret create tbs-demo-docker-secret --dockerhub ${DATA_E2E_REGISTRY_USERNAME}
```

* Create a Git secret for the source git repository:
```
source .env
GIT_PASSWORD=$DATA_E2E_GITHUB_PW kp secret create tbs-demo-git-secret --git-url https://github.com --git-user ${DATA_E2E_REGISTRY_USERNAME}
```

* Build the images via manifest:
```
source .env
envsubst < config/ml-image-processing-container.in.yaml > config/ml-image-processing-container.yaml
kubectl apply -f config/ml-image-processing-container.yaml
```

* Tail the logs: (must install kp cli - see <a href="https://github.com/vmware-tanzu/kpack-cli/blob/v0.2.0/docs/kp.md">link</a>)
```
kp build logs imgprocessor
```

* Build the images via kp (alternative approach):
```
source .env
kp image create imgprocessor --tag ${DATA_E2E_REGISTRY_USERNAME}/ml-image-processor  \
        --namespace default \
        --wait \
        --env MLFLOW_TRACKING_URI_VAL=http://mlflow.${DATA_E2E_BASE_URL} \
        --git “https://github.com/agapebondservant/ml-image-processing-app-pipelines.git” \
        --git-revision "main"
```

* Build the images via docker (alternative approach):
```
source .env
docker build --build-arg MLFLOW_TRACKING_URI_VAL=http://mlflow.${DATA_E2E_BASE_URL} -t ${DATA_E2E_REGISTRY_USERNAME}/ml-image-processor .
docker push ${DATA_E2E_REGISTRY_USERNAME}/ml-image-processor
```

To delete the image:
```
kubectl delete -f config/ml-image-processing-container.yaml
```
