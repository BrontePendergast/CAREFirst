#!/bin/bash

IMAGE_NAME=demo

# remove image in case this script was run before
docker image rm ${IMAGE_NAME}

# Start up Minikube
minikube start --kubernetes-version=v1.25.4

# Setup your docker daemon to build with Minikube
eval $(minikube docker-env)

# Run pytest within poetry virtualenv
poetry env remove python3.11
poetry install
poetry run pytest tests/test.py -vv -s

echo "Build your docker container"
# rebuild and run the new image
docker build -t ${IMAGE_NAME} .

echo "Apply your Deployments and Services"
kubectl apply -f infra/namespace.yaml --namespace=carefirst

echo "Apply your k8s namespace"
kubectl apply -f infra --namespace=carefirst
kubectl config set-context --current --namespace=carefirst

echo "Start minikube tunnel"
minikube tunnel &
TUNNEL_ID=$!
export TUNNEL_ID

echo $TUNNEL_ID
echo "Wait for API to be accessible"
# # wait for the /health endpoint to return a 200 and then move on
finished=false
while ! $finished; do
    health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health")
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
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar"

echo "testing '/' endpoint. Expect status code of 404 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/"

echo "testing '/docs' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs"

echo "testing '/health' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health"

# # echo "testing '/conversations' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X POST "http://localhost:8000/conversations/9999" -H 'Content-Type: application/json' -d \
'{"question": "cut"}'

# # echo "Kill minikube tunnel"
kill $TUNNEL_ID

echo "Delete deployments and services in namespace w255"
kubectl delete --all deployments --namespace=carefirst
kubectl delete --all services --namespace=carefirst

echo "Delete namespace"
kubectl delete namespace carefirst

# echo "Clean up docker resources"
docker image rm ${IMAGE_NAME}

# echo "minikube stop"
minikube stop