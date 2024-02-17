#!/bin/bash

IMAGE_NAME=local
NAMESPACE=carefirst

# remove image in case this script was run before
docker image rm ${IMAGE_NAME}

# Start up Minikube
minikube start --kubernetes-version=v1.25.4

echo "Set kubernetes context"
kubectl config use-context minikube

echo "Setup your docker daemon to build with Minikube"
eval $(minikube docker-env)

# Run pytest within poetry virtualenv
poetry env remove python3.11
poetry install
poetry run pytest -vv -s

echo "Build your docker container"
# rebuild and run the new image
docker build -t ${IMAGE_NAME} .

echo "Apply your namespace"
kubectl apply -f namespace.yaml
kubectl config set-context --current --namespace=$NAMESPACE

echo "Apply Kustomize Files"
kubectl apply -k .k8s/bases
kubectl apply -k .k8s/overlays/dev
kubectl get all -n $NAMESPACE

echo "Start minikube tunnel"
minikube tunnel &
TUNNEL_ID=$!
export TUNNEL_ID
echo $TUNNEL_ID

echo "Wait for API to be accessible"
# # wait for the /health endpoint to return a 200 and then move on
finished=false
while ! $finished; do
    health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8001/health")
    if [ $health_status == "200" ]; then
        finished=true
        echo "API is ready"
    else
        echo "API not responding yet"
        sleep 1
    fi
done

echo "curl the defined endpoints and return status codes (same format as lab_1 requirement)"
echo "testing '/hello' endpoint with ?name=Winegar. Expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8001/hello?name=Winegar"

echo "testing '/' endpoint. Expect status code of 404 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8001/"

echo "testing '/docs' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8001/docs"

echo "testing '/health' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8001/health"

# # echo "testing '/predict' endpoint. expect status code of 200 returned"
# curl -X POST -H 'Content-Type: application/json' localhost:8000/predict -d \
# '{"houses":
# [{"AveRooms":"6.98","AveBedrms":"1.02","Population":"321","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"41","MedInc":"8.32"},
# {"AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"41","MedInc":"8.24"}]}
# '

# # echo "Kill minikube tunnel"
kill $TUNNEL_ID

echo "Delete deployments and services in namespace"
kubectl delete --all deployments --namespace=${NAMESPACE}
kubectl delete --all services --namespace=${NAMESPACE}
kubectl delete --all pods --namespace=${NAMESPACE}
kubectl delete --all horizontalpodautoscaler.autoscaling  --namespace=${NAMESPACE}

echo "Delete namespace"
kubectl delete namespace ${NAMESPACE}

# echo "Clean up docker resources"
docker image rm ${IMAGE_NAME}

# echo "minikube stop"
minikube stop