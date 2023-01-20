## Deployment
kp secret create tbs-harbor-secret --registry harbor.haas-436.pez.vmware.com --registry-user admin
kp secret create tbs-git-secret --git-url https://gitlab.com --git-user oawofolu
kp image create tbsdemo --tag oawofolu/image-analytics-training --namespace default --wait --git “https://gitlab.com/oawofolu/tbs-demo.git”

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

* Build the images via kp:
```
kp image create tbsdemo --tag ${DATA_E2E_REGISTRY_USERNAME}/ml-image-processor  \
        --namespace default \
        --wait \
        --git “https://github.com/agapebondservant/ml-image-processing-app-pipelines.git”
        --git-revision "main"
```