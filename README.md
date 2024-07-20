<div align="center">
  <picture>
    <source srcset="https://www.munozarturo.com/assets/mockupforge/logo-github.svg">
    <img alt="mockupforge-ms" src="https://www.munozarturo.com/assets/mockupforge/logo-github.svg" width="50%" height="40%">
  </picture>
</div>

<!-- omit from toc -->
# Mockup Forge

This is a microservice that uses a Docker container to run a Python Flask server that generates mockups using the GIMP CLI.

<!-- omit from toc -->
# Table of Contents

- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Deployment](#deployment)
- [REST API](#rest-api)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [`GET /v1/mockup`](#get-v1mockup)
  - [`POST /v1/mockup`](#post-v1mockup)

## Prerequisites

- Docker installed on your local machine

## Local Setup

1. Set the environment variables in a `.env` file. A template `.env` file is provided in `.env.template`.
2. Build the Docker container `sudo docker build -t mockupforge-ms .`.
3. Run the container `sudo docker run -p 5000:8080 mockupforge-ms`.

## Deployment

To deploy the microservice to a cloud platform:

1. Build the Docker image and push it to a container registry.
2. Deploy the container to your chosen cloud platform (e.g., AWS ECS, Google Cloud Run, Kubernetes).
3. Set the necessary environment variables and configurations.
4. Expose the appropriate port and configure any required networking settings.
5. Monitor and scale the service as needed.

## REST API

The Flask server will be accessible at `http://localhost:5000`.

## Authentication

All API endpoints require authentication. Include your API key in the Authorization header of your requests:

```text
Authorization: Bearer YOUR_API_KEY_HERE
```

## API Endpoints

### `GET /v1/mockup`

Headers:

```text
Authorization: Bearer YOUR_API_KEY_HERE
```

Response:

```json
{
  "status": "ok",
  "message": "success",
  "data": {
    "mockups": {
      "mockup_type_1": {
           "dimensions": ["max_width", "max_height"]
      },
      "mockup_type_2": {
           "dimensions": ["max_width", "max_height"]
      }
    }
  }
}
```

It is highly recommended to query this endpoint before generating mockups since it contains the available mockup types where are passed into `POST /v1/mockup` in the request body as `type` and it also includes the maximum dimensions of the image. It is important to note these since the image will always be rescaled by the mockup generator to fit these dimensions. It is recommended to include blank space in the desired design to fit these dimensions to avoid image transformation.

### `POST /v1/mockup`

Headers:

```text
Authorization: Bearer YOUR_API_KEY_HERE
Content-Type: application/json
```

Request Body:

```ts
{
  "type": "mockup_type", // string, must be in mockups
  "image": "image_url", // string
  "color": ["r", "g", "b"] // float[], length=3
}
```

Response:

Will return a response with type of image/png, which is the generated mockup.
