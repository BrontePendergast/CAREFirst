#!/bin/bash
# -- Set up initial variables
BACKEND_FOLDER=carefirst
FRONTEND_FOLDER=webapp
NAMESPACE=rmarin
ACR_DOMAIN=w255mids.azurecr.io
TAG=latest
IMAGE_PREFIX=rmarin
# -- Virtual Service HOST and URL
export KNS=$IMAGE_PREFIX
# export VSVC_HOST=$(kubectl get virtualservice -n $KNS $IMAGE_NAME -o jsonpath='{.spec.hosts[0]}')
export VSVC_HOST=$KNS.mids255.com
export VSVC_URL=https://$VSVC_HOST
export HEALTH_URL=$VSVC_URL/health
# -- Misc Variables
timeout_seconds=120
wait_seconds=5
total_seconds=0
request_count=0

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -q|--quit) # stop and delete
            echo "kustomize delete"
            kubectl config use-context w255-aks
            kustomize build .k8s/overlays/prod | kubectl delete -f -
            # minikube stop
            # minikube delete
            exit 1
            ;;
        -i|--infra) # apply infra
            echo "kustomize apply"
            kubectl config use-context w255-aks
            kustomize build .k8s/overlays/prod | kubectl apply -f -
            # minikube delete
            exit 1
            ;;
        -f|--frontend) # apply infra
            echo " -- Build Frontend Only"
            kubectl config use-context w255-aks
            kustomize build .k8s/overlays/prod | kubectl apply -f -
            # minikube delete
            exit 1
            ;;
        -v|--verbose) # Verbose mode, display responses on console
            VERBOSE=true
            ;;
        *) # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# acr login
# echo " -- acr login"
# az acr login --name w255mids &> /dev/null

# Build pythonapi image
cd ${BACKEND_FOLDER}
IMAGE_NAME=pythonapi
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
echo " -- Build and push ${IMAGE_NAME}:${TAG} to ${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} . 
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}:${TAG}
docker push ${IMAGE_FQDN}:${TAG}

# Build frontend image
cd ../${FRONTEND_FOLDER}/client
IMAGE_NAME=frontend
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
echo " -- Build and push ${IMAGE_NAME}:${TAG} to ${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} . 
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}:${TAG}
docker push ${IMAGE_FQDN}:${TAG}

# Go back to root
cd ../../


#  -- Deploy ${IMAGE_NAME}:${TAG} on AKS
echo " -- Deploy ${IMAGE_NAME}:${TAG} on AKS"
kubectl config use-context w255-aks
kustomize build .k8s/overlays/prod | kubectl apply -f -

# # -- Test if service is Up
# echo " -- Test if service is up on: $HEALTH_URL"
# while [ $total_seconds -lt $timeout_seconds ]; do
#     response=$(curl -o /dev/null -s -w "%{http_code}" -X GET $HEALTH_URL)
#     if [ $response -eq 200 ]; then
#         echo " -- Total seconds taken: $total_seconds seconds"
#         break
#     else
#         sleep $wait_seconds
#         total_seconds=$((total_seconds + wait_seconds))
#         request_count=$((request_count + 1))
#         if [ $((request_count % 2)) -eq 0 ]; then
#             echo " ---- Still trying... | Total seconds: $total_seconds | Total Requests: $request_count | Last response status: $response"
#             if [[ "$VERBOSE" = true ]]; then
#                 kubectl -n $KNS get pods
#             fi
#         fi
#     fi
# done


# #  -- Testing service
# echo " -- Testing service ${IMAGE_NAME}:${TAG} on $VSVC_URL"
# echo " -- testing '/hello' endpoint with ?name=Winegar"
# echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/hello?name=Winegar")
# echo " -- testing '/' endpoint"
# echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/")
# echo " -- testing '/docs' endpoint"
# echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/docs")
# echo " -- testing '/predict' endpoint"
# echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$json_data" "$VSVC_URL/predict")
# echo " -- testing '/bulk_predict' endpoint"
# echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$bulk_json_data" "$VSVC_URL/bulk_predict")


# echo " -- Done"