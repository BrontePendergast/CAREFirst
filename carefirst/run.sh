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


#  -- Setting up variables. Set version and project nmae based on Git
ENV="$(git symbolic-ref HEAD 2>/dev/null)" ||
ENV="(unnamed branch)"
ENV=${ENV##refs/heads/}
ENVName=''
timestamp=$(date +%Y%m%d)
projectName=${PWD##*/}
commitID=$(git rev-parse --short HEAD)
version=$ENVName$timestamp-$commitID
versionLatest="latest"


# -- Set Runtime Variabels
model_path="./model_pipeline.pkl"
timeout_seconds=120
wait_seconds=5
total_seconds=0
LOCAL_PORT=8000
APP_PORT=8000
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
health_url="http://localhost:$APP_PORT/health"
request_count=0


if [[ "$VERBOSE" = true ]]; then
    # -- Startup Minikube
    echo " -- Starting up Minikube"
    minikube start --kubernetes-version=v1.27.3


    # -- Setup dockerdaemon in minikube and default kubectl namespace as w255
    echo " -- Setup dockerdaemon to minikube"
    eval $(minikube -p minikube docker-env)


    # -- Train Model 
    if [ -f "$model_path" ]; then
        echo " -- Model found in $model_path. Skipping training."
    else
        echo " -- Model not found in local folder. Training model..."
        poetry install
        poetry run python trainer/train.py
        echo " -- Training complete. file in: $model_path."
    fi


    #  -- Build Images
    echo " -- Building Image $projectName:$versionLatest"
    docker build -t $projectName:$versionLatest .


    #  --  Apply overlays/dev kustomization
    echo " -- Apply overlays/dev kustomization"
    kustomize build .k8s/overlays/dev | kubectl apply -f -


    #  Kubectl Tunnel
    minikube tunnel -c > /dev/null 2>&1 & TUNNEL_PID=$!
    echo " -- Activate Tunnel in PID: $TUNNEL_PID"


    # -- Test if service is Up
    echo " -- Test if service is up on: $health_url"
    while [ $total_seconds -lt $timeout_seconds ]; do
        # response=$(curl -s -w '%{http_code}' $health_url -o /dev/null)
        response=$(curl -o /dev/null -s -w "%{http_code}" -X GET $health_url)
        if [ $response -eq 200 ]; then
            echo " -- Total seconds taken: $total_seconds seconds"
            break
        else
            sleep $wait_seconds
            total_seconds=$((total_seconds + wait_seconds))
            request_count=$((request_count + 1))
            if [ $((request_count % 2)) -eq 0 ]; then
                echo " ---- Still trying... | Total seconds: $total_seconds | Total Requests: $request_count | Last response status: $response"
                if [[ "$VERBOSE" = true ]]; then
                    kubectl -n rmarin get pods
                fi
            fi
        fi
    done


    #  -- Testing service
    echo " -- Testing service $projectName:$versionLatest"
    echo " -- testing '/hello' endpoint with ?name=Winegar"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar")
    echo " -- testing '/' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/")
    echo " -- testing '/docs' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs")
    echo " -- testing '/predict' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$json_data" "http://localhost:8000/predict")
    echo " -- testing '/bulk_predict' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$bulk_json_data" "http://localhost:8000/bulk_predict")


    # -- Stop minikube and kill TUNNEL_PID
    echo " -- Cleanup: Kill tunnel PID: $TUNNEL_PID, delete resources and w255, stop Minikube"
    kill -9 $TUNNEL_PID
    kustomize build .k8s/overlays/dev | kubectl delete -f -
    minikube stop


else
    # -- Startup Minikube
    echo " -- Starting up Minikube"
    minikube start --kubernetes-version=v1.27.3 &> /dev/null


    # -- Setup dockerdaemon in minikube and default kubectl namespace as w255
    echo " -- Setup dockerdaemon to minikube"
    eval $(minikube -p minikube docker-env) &> /dev/null


    # -- Train Model 
    if [ -f "$model_path" ]; then
        echo " -- Model found in $model_path. Skipping training."
    else
        echo " -- Model not found in local folder. Training model..."
        poetry install &> /dev/null
        poetry run python trainer/train.py &> /dev/null
        echo " -- Training complete. file in: $model_path."
    fi


    #  -- Build Images
    echo " -- Building Image $projectName:$versionLatest"
    docker build -t $projectName:$versionLatest . &> /dev/null


    #  --  Apply overlays/dev kustomization
    echo " -- Apply overlays/dev kustomization"
    kustomize build .k8s/overlays/dev | kubectl apply -f - &> /dev/null


    #  Kubectl Tunnel
    minikube tunnel -c > /dev/null 2>&1 & TUNNEL_PID=$!
    echo " -- Activate Tunnel in PID: $TUNNEL_PID"


    # -- Test if service is Up
    echo " -- Test if service is up on: $health_url"
    while [ $total_seconds -lt $timeout_seconds ]; do
        # response=$(curl -s -w '%{http_code}' $health_url -o /dev/null)
        response=$(curl -o /dev/null -s -w "%{http_code}" -X GET $health_url)
        if [ $response -eq 200 ]; then
            echo " -- Total seconds taken: $total_seconds seconds"
            break
        else
            sleep $wait_seconds
            total_seconds=$((total_seconds + wait_seconds))
            request_count=$((request_count + 1))
            if [ $((request_count % 2)) -eq 0 ]; then
                echo " ---- Still trying... | Total seconds: $total_seconds | Total Requests: $request_count | Last response status: $response"
                if [[ "$VERBOSE" = true ]]; then
                    kubectl -n rmarin get pods
                fi
            fi
        fi
    done


    #  -- Testing service
    echo " -- Testing service $projectName:$versionLatest"
    echo " -- testing '/hello' endpoint with ?name=Winegar"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar")
    echo " -- testing '/' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/")
    echo " -- testing '/docs' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs")
    echo " -- testing '/predict' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$json_data" "http://localhost:8000/predict")
    echo " -- testing '/bulk_predict' endpoint"
    echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$bulk_json_data" "http://localhost:8000/bulk_predict")


    # -- Stop minikube and kill TUNNEL_PID
    echo " -- Cleanup: Kill tunnel PID: $TUNNEL_PID, delete resources and w255, stop Minikube"
    kill -9 $TUNNEL_PID &> /dev/null
    kustomize build .k8s/overlays/dev | kubectl delete -f - &> /dev/null
    minikube stop &> /dev/null


fi


#  -- Done
echo " -- Done"