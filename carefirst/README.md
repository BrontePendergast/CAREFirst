# Lab 4

Course: DATASCI-255
Section: 1
Author: Ricardo Marin
email: rmarin@berkeley.edu

## Descrption

This web application can predict the price of a house depending on a defined set of variables, and can be deployed in Azure Kubernetes Service. As a bonus it also returns a hello message personalized with a name provided by the user. 

 It is comprised of 4 **endpoints**:

1. /hello: Funcitonality that return a hello message personalized with a name. It takes one paramater as input: **name**. The result will be like shown below
```
{"message": "hello [name]"}
```
2. /docs: Full documentation
3. /opeapi.json: Opeapi standard documentation json
4. /predict: Functionality that returns the predicted house value based on a simple machine learning model that uses the California Housing Dataset to train a Support vector regression model. It takes 8 inputs as a JSON object representing one datapoint to be predicted. The result of the predict endpoint will return a single value like this:
```
{"house_value": 4.3}
```
4. /bulk_predict: as well as the /predict, this endpoint returns the predicted house values of a bulk of houses provided by the user. It takes a list of houses as a JSON object representing several data points. The result of the bulk predict endopint will return alist of float values such as:
```
{"house_values": [4.3, 3.1, 2.3]}
```

## Project Tree
```bash
.
└── lab4/
│   ├── .k8s
│   │   ├── base
│   │   │   ├── config-map.yaml
│   │   │   ├── deployment-lab4.yaml
│   │   │   ├── deployment-redis.yaml
│   │   │   ├── kustomization.yaml
│   │   │   ├── service-lab4.yaml
│   │   │   └── service-redis.yaml
│   │   └── overlays
│   │       ├── dev
│   │       │   ├── kustomization.yaml
│   │       │   └── namespace.yaml
│   │       └── prod
│   │           ├── kustomization.yaml
│   │           ├── patch-deployment-lab4.yaml
│   │           ├── patch-deployment-lab4_copy.yaml
│   │           └── virtual-service.yaml
│   ├── Dockerfile
│   ├── README.md
│   ├── build-push.sh
│   ├── infra
│   │   ├── deployment-pythonapi.yaml
│   │   ├── deployment-redis.yaml
│   │   ├── namespace.yaml
│   │   ├── service-prediction.yaml
│   │   └── service-redis.yaml
│   ├── model_pipeline.pkl
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── run.sh
│   ├── src
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests
│   │   ├── __init__.py
│   │   └── test_src.py
│   └── trainer
│       ├── poetry.lock
│       ├── predict.py
│       └── train.py
```

## Prerequisites
Before getting started, ensure you have the following installed:

- Python 3.7+
- venv for virtual environments
- Poetry (for dependency management)
- Docker (for containerization)
- pytest (for testing)
- kubectl
- minikube
- Azure CLI
- ACR
- Kustomize

## Install dependencies
Install all dependencies using poetry as package manager
```bash
python -m venv venv
source venv/bin/activate 
poetry install
```

## Testing
Run the folllowing script to run the default functionality tests
```bash
poetry run pytest
```
The default tests include but is not limited to:
1. /hello endpoint functionality with "Ricardo" as name parameter
2. /hello endpoint returns correct error status when not given a parameter
3. / endpoint returns 404 since it's not being used
4. /docs endpoints returns status code 200
5. /opeapi.json returns correct json filetype and asserts opeanpi version to be greater or equal than version 3.0
6. /predict Test prediction with default set of values

```
{

    "MedInc": 8.3252,
    "HouseAge": 41,
    "AveRooms": 6.98412698,
    "AveBedrms": 1.02380952,
    "Population": 322,
    "AveOccup": 2.55555556,
    "Latitude": 37.88,
    "Longitude": -122.23,
}
```

7. /predict endpoint No negative values for MedInc
8. /predict endpoints values with wrong format and values.
9. /bulk_predict Test prediction with default set of values

```
{
    "houses": [
        {
            "MedInc": 8.3252,
            "HouseAge": 41,
            "AveRooms": 6.98412698,
            "AveBedrms": 1.02380952,
            "Population": 322,
            "AveOccup": 2.55555556,
            "Latitude": 37.88,
            "Longitude": -122.23,
        },
        {
            "MedInc": 8.3252,
            "HouseAge": 41,
            "AveRooms": 6.98412698,
            "AveBedrms": 1.02380952,
            "Population": 322,
            "AveOccup": 2.55555556,
            "Latitude": 37.88,
            "Longitude": -122.23,
        },
    ]
}
```

10. /bulk_predict endpoints with non negative values in fields
11. /bulk_predict prediction with input values with wrong format and wrong set of values

## Build the Docker image locally
To tag the latest version of the lab4 solution run the following command:
```bash
docker build -t lab4:latest .
```

To build the image inside the minikube environment run 
```bash
eval $(minikube -p minikube docker-env)
docker build -t lab4:latest .
```

## Build the Docker image in Azure Container Registry
To build the image in the Azure container registry, we will need to specify the image qualified domain name (FQDN) and a TAG, in which we usually use the commit ID. We will assume for this example my own respository in ACR and the lab4 image name.

```bash
export IMAGE_FQDN=w255mids.azurecr.io/rmarin/lab4
export TAG=$(git rev-parse --short HEAD)

az acr login --name w255mids
docker build --platform linux/amd64 -t lab4:${TAG} .
docker tag lab4:${TAG} ${IMAGE_FQDN}:${TAG}
docker push ${IMAGE_FQDN}:${TAG}
```

## Run Docker container
To run the application from the latest tag run the following command: 
```bash
docker run -d -p 8000:8000 --name lab4-latest lab4:latest 
```

## Run stand alone application
To run the application without the docker container run the following command"
```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## run\.sh
Before running the script, make sure it has the correct set of permissions. Run the following commands to execute the script

```bash
chmod 755 run.sh
./run.sh
```

We've included a bash script, **run\.sh**, to simplify building, running and testing of the containerized application. It will also handle image versioning by creating an ID based on the current date and the last 7 characters of the commit id following this structure **YYYMMDD-COMMIT_ID**. It  also includes logic to handle the branch name of the git reporsitory. This is aims to include different environments based on the branch name. The resulting version tag will include the branch name following this format **BRANCH_NAME-YYYMMDD-COMMIT_ID**, and **BRANCH_NAME-latest** version tag for a specific latest version for a given environment. This process excludes the **main** branch. 

This versioning process was added to keep track of the images based on the development day, commit id and environments with the main goal to make the bug tracking and rollback porcesses easier.

The script will complete the following tasks:

1. **Starting up Minikubel** Startup a minikube environment to build our image and test our deployment.
2. **Setup dockerdaemon to minikube** Sets up the docker daemon to minikube's deamon. 
3. **Train Model** Lookup for the model in path *./model_pipeline.pkl*, if it's not found, train the model with the *trainer/train.py* script and generate the model file. If it's found, skip to next step.
4. **Building Image** Builds **lab4:latest** image using minikube's docker daemon.
5. **Apply Dev overlay with Kustomize**
```
├── base
│   ├── config-map.yaml
│   ├── deployment-lab4.yaml
│   ├── deployment-redis.yaml
│   ├── kustomization.yaml
│   ├── service-lab4.yaml
│   └── service-redis.yaml
└── overlays
    ├── dev
    │   ├── kustomization.yaml
    │   └── namespace.yaml
```
6. **Activate Tunnel** activate minikube tunnel to Load Balancer service in minikube
7. **Test if service is up** `CURL` each 5 seconds to health endpoint in localhost to check if application is running and ready.
8. Run requirements **tests** that include the following:

```bash
echo " -- testing '/hello' endpoint with ?name=Winegar"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=Winegar")
echo " -- testing '/' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/")
echo " -- testing '/docs' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs")
echo " -- testing '/predict' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$house" "http://localhost:8000/predict")
echo " -- testing '/bulk_predict' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$houses" "http://localhost:8000/bulk_predict")
```

9. **Kill tunnel and stops minikube** Kills `minikube tunnel` process and stops minikube

## build-push\.sh

Before running the script, make sure it has the correct set of permissions. Run the following commands to execute the script

```bash
chmod 755 build-push.sh
./run.sh
```

This Bash script orchestrates the deployment and testing of the Docker container of our project, integrating with MIDS Azure services and Kubernetes. Initially, it checks for the -v or --verbose flag, which if present, enables verbose mode for detailed console output. It then sets up necessary variables like the Azure Container Registry (ACR) domain, Docker image name, Git commit ID which is used as the docker image `TAG`, and constructs a fully-qualified domain name (FQDN) for the image. Additionally, it prepares variables related to Kubernetes services and testing parameters.

The script prepares the Kubernetes deployment configuration the image `TAG` into the deployment YAML patch used by Kustomize. This setup is crucial for deploying the correct version of the application. Then, the script performs a series of  operations, such as logging into ACR, building and pushing the Docker image to the ACR registry, and deploying it on Azure Kubernetes Service (AKS). After, it checks the service's health endpoint until a successful response is received or a timeout occurs. This loop provides feedback on the progress until the service is up and running

Finally, the script tests various service endpoints, `/`, `/hello`, `/docs`, `/predict`, and `/bulk_predict`. It sends requests to these endpoints and prints the HTTP status codes of the responses, ensuring the service's functionalities are operating correctly. We use the same approach as we did in `run.sh`

1. **Sets up all variables and creates Image Tag** set up of all variables including image tag (commit id), image FQDN and ACR registry name.
2. **Replaces image tag in deployment patch** replaces the current image tag in the deplyment patch for kustomize to deploy later.
3. **Login to ACR and builds and push the image tag to ACR Registry**
4. **Apply prod overlay with Kustomize**
```
├── base
│   ├── config-map.yaml
│   ├── deployment-lab4.yaml
│   ├── deployment-redis.yaml
│   ├── kustomization.yaml
│   ├── service-lab4.yaml
│   └── service-redis.yaml
└── overlays
    └── prod
        ├── kustomization.yaml
        ├── patch-deployment-lab4.yaml
        ├── patch-deployment-lab4_copy.yaml
        └── virtual-service.yaml
```

5. **Test if service is up** `CURL` each 5 seconds to health endpoint in localhost to check if application is running and ready.
6. Run requirements tests that include the following:

```bash
echo " -- testing '/hello' endpoint with ?name=Winegar"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/hello?name=Winegar")
echo " -- testing '/' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/")
echo " -- testing '/docs' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "$VSVC_URL/docs")
echo " -- testing '/predict' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$json_data" "$VSVC_URL/predict")
echo " -- testing '/bulk_predict' endpoint"
echo " -- "$(curl -o /dev/null -s -w "%{http_code}\n" -X POST -H "Content-Type: application/json" -d "$bulk_json_data" "$VSVC_URL/bulk_predict")
```

## Lab Questions

### What are the downsides of using latest as your docker image tag?

Using the latest tag for Docker images can introduce significant issues, such as lack of version control, inconsistencies across environments, and difficulties in tracking changes and rolling back to specific states. This approach risks introducing untested or unstable versions into production, especially in automated deployment scenarios, potentially leading to software bugs, incompatibilities, or security vulnerabilities. To ensure reliability and consistency, it's recommended to use specific, versioned tags for Docker images, facilitating clearer tracking and safer deployment practices.

### What does `kustomize` do for us?

Kustomize is a Kubernetes configuration management tool that streamlines the customization of our YAML manifests. It supports environment-specific overlays, reducing duplication across configurations for different deployment stages (like development and production). Specifically we use Kustomize to set up specific deployment configuration depending on our developemnt environments, dev and prod. We start with a **base** set of yaml configurations for our **deployments**, **services**, and we add a set of **configmaps** for our redis deployment We then add yaml configuration patches (overlays) for **dev** and **prod**, which modifies resource and requests limits, image **tag** to use, **virtualservices** configuration for **istio**, and other configurations. Kustomize enables great flexibility to coordinate deployments between a large set of contributors, since it's easier to standarize the environment configurations for deployment.