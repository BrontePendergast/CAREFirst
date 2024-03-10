#!/bin/bash
BACKEND_FOLDER=carefirst
FRONTEND_FOLDER=webapp
NAMESPACE=carefirst

# ### BACKEND DOCKERFILE
cd ${BACKEND_FOLDER}
pwd

IMAGE_NAME_BACKEND=demo

# # remove image in case this script was run before
# docker image rm ${IMAGE_NAME_BACKEND}:latest

# # Start up Minikube
minikube start --kubernetes-version=v1.25.4

# # Setup your docker daemon to build with Minikube
eval $(minikube docker-env)

# echo "Pytest"
# poetry env remove python3.11
# poetry install
# poetry run pytest tests/test.py -vv -s

echo "Build your docker container"
# rebuild and run the new image
docker build -t ${IMAGE_NAME_BACKEND} .

## FRONTEND DOCKERFILE
cd ../${FRONTEND_FOLDER}/client
pwd
IMAGE_NAME_FRONTEND=frontend

# # remove image in case this script was run before
# docker image rm ${IMAGE_NAME_FRONTEND}:latest

echo "Build your docker container"
# https://dev.to/pawankm21/create-docker-container-for-react-application-e0g
docker build -t ${IMAGE_NAME_FRONTEND} .

### Deploy
cd ../..
pwd

# echo "Apply your Deployments and Services"
kubectl apply -f infra/namespace.yaml --namespace=${NAMESPACE}
kubectl config set-context --current --namespace=${NAMESPACE}

echo "Apply your k8s namespace"
kubectl apply -f infra --namespace=${NAMESPACE}
kubectl get all --namespace=${NAMESPACE}

# # echo "Start minikube tunnel"
# minikube tunnel &
# TUNNEL_ID=$!
# export TUNNEL_ID
# echo $TUNNEL_ID

# echo "Wait for backend to be accessible"
# # # wait for the /health endpoint to return a 200 and then move on
# finished=false
# while ! $finished; do
#     health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health")
#     if [ $health_status == "200" ]; then
#         finished=true
#         echo "Backend is ready"
#     else
#         echo "Backend not responding yet"
#         sleep 1
#     fi
# done

# echo "Wait for frontend to be accessible"
# # # wait for the /health endpoint to return a 200 and then move on
# finished=false
# while ! $finished; do
#     health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:3000")
#     if [ $health_status == "200" ]; then
#         finished=true
#         echo "Frontend is ready"
#     else
#         echo "Frontend not responding yet"
#         sleep 1
#     fi
# done

# echo "curl the defined endpoints and return status codes"
# echo "testing '/hello' endpoint with ?name=Winegar. Expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar"

# echo "testing '/docs' endpoint. expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs"

# echo "testing '/health' endpoint. expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health"

# echo "testing '/conversations' endpoint. expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X POST "http://localhost:8000/conversations/999" -H 'Content-Type: application/json' -d \
# '{"query": "bee sting"}'

# # echo "testing '/messages' endpoint. expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X POST "http://localhost:8000/messages/555" -H 'Content-Type: application/json' -d \
# '{"feedback": "True"}'

# echo "testing '/frontend' endpoint. expect status code of 200 returned"
# curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:3000"

# echo "Kill minikube tunnel"
# kill $TUNNEL_ID

# echo "Delete deployments and services in namespace w255"
# kubectl delete --all deployments --namespace=${NAMESPACE}
# kubectl delete --all services --namespace=${NAMESPACE}

# echo "Delete namespace"
# kubectl delete namespace ${NAMESPACE}

# echo "Clean up docker resources"
# docker image rm ${IMAGE_NAME_BACKEND}
# docker image rm ${IMAGE_NAME_FRONTEND}

# echo "minikube stop"
# minikube stop
# minikube delete

