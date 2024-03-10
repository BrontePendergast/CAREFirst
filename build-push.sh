#!/bin/bash


# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
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


# -- Set up initial variables
# -- ACR and Docker Registry
ACR_DOMAIN=w255mids.azurecr.io
# IMAGE_NAME=${PWD##*/}
IMAGE_NAME=carefirst
# TAG=$(git rev-parse --short HEAD)
TAG=latest
# IMAGE_PREFIX=$(az account list --all | jq '.[].user.name' | grep -i berkeley.edu | awk -F@ '{print $1}' | tr -d '"' | tr -d "." | tr '[:upper:]' '[:lower:]' | tr '_' '-' | uniq)
IMAGE_PREFIX=carefirst
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
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
json_data='{
    "MedInc" : 8.3252,
    "HouseAge" : 41,
    "AveRooms" : 6.98412698,
    "AveBedrms" : 1.02380952,
    "Population" : 322,
    "AveOccup" : 2.55555556,
    "Latitude" : 37.88,
    "Longitude" : -122.23
}'
bulk_json_data='{
    "houses": [
        {
            "MedInc": 8.3252,
            "HouseAge": 41,
            "AveRooms": 6.98412698,
            "AveBedrms": 1.02380952,
            "Population": 322,
            "AveOccup": 2.55555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        },
        {
            "MedInc": 8.3252,
            "HouseAge": 41,
            "AveRooms": 6.98412698,
            "AveBedrms": 1.02380952,
            "Population": 322,
            "AveOccup": 2.55555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }
    ]
}'


# Create TAG and feed it to deployment yaml # FQDN = Fully-Qualified Domain Name
echo " -- Create lab4 deployment yaml"
sed "s/\[TAG\]/${TAG}/g" .k8s/overlays/prod/patch-deployment-lab4_copy.yaml > .k8s/overlays/prod/patch-deployment-lab4.yaml

echo " -- Build and push ${IMAGE_NAME}:${TAG} to ${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"
az acr login --name w255mids &> /dev/null
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} .
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}:${TAG}
docker push ${IMAGE_FQDN}:${TAG}


# echo " -- Deploy ${IMAGE_NAME}:${TAG} on AKS"
# kustomize build .k8s/overlays/prod | kubectl apply -f -

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