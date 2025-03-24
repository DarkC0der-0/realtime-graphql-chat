# Realtime GraphQL Chat Application

## Overview

This is a full-stack realtime graphql chat application built using React for the frontend, FastAPI for the backend, PostgreSQL for the database, and Redis for Pub/Sub. The application supports real-time messaging, user authentication, and message storage. It uses Docker for containerization and includes CI/CD pipelines with GitHub Actions.

## Table of Contents

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Docker](#docker)
- [API Documentation](#api-documentation)
  - [Queries](#queries)
  - [Mutations](#mutations)
  - [Subscriptions](#subscriptions)
- [Running Tests](#running-tests)
- [Deploying the Application](#deploying-the-application)
- [Example Use Cases](#example-use-cases)
- [Architecture Diagram](#architecture-diagram)

## Installation and Setup

### Backend

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DarkC0der-0/realtime-graphql-chat.git
   cd realtime-graphql-chat/backend
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the `backend` directory and add the following:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/app
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the frontend server**:
   ```bash
   npm run dev
   ```

### Docker

1. **Ensure Docker is installed and running**:
   Install Docker from [here](https://docs.docker.com/get-docker/).

2. **Build and run the containers**:
   ```bash
   docker-compose up --build
   ```

## API Documentation

### Queries

- **Fetch messages by room**:
  ```graphql
  query FetchMessages($roomId: Int!, $first: Int, $after: String) {
    messagesByRoom(roomId: $roomId, first: $first, after: $after) {
      edges {
        cursor
        node {
          id
          content
          timestamp
          sender {
            id
            name
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
  ```

- **Fetch all users**:
  ```graphql
  query {
    allUsers {
      id
      name
      email
    }
  }
  ```

### Mutations

- **Create a new message**:
  ```graphql
  mutation CreateMessage($content: String!, $userId: Int!, $roomId: Int!) {
    createMessage(content: $content, userId: $userId, roomId: $roomId) {
      message {
        id
        content
        sender {
          id
          name
        }
      }
    }
  }
  ```

- **Create a new user**:
  ```graphql
  mutation CreateUser($username: String!) {
    createUser(username: $username) {
      user {
        id
        name
      }
    }
  }
  ```

### Subscriptions

- **Subscribe to new messages in a room**:
  ```graphql
  subscription OnMessageCreated($roomId: Int!) {
    messageCreated(roomId: $roomId) {
      id
      content
      timestamp
      sender {
        id
        name
      }
    }
  }
  ```

## Running Tests

### Backend Tests

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

### Frontend Tests

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Run tests**:
   ```bash
   npm test
   ```

## Deploying the Application

### Using GitHub Actions

1. **Set up secrets in your GitHub repository**:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. **Create a GitHub Actions workflow**:
   Place the following YAML file in `.github/workflows/ci-cd.yml`:
   ```yaml
   name: CI/CD Pipeline

   on:
     push:
       branches:
         - main

   jobs:
     test:
       name: Run Tests
       runs-on: ubuntu-latest

       services:
         postgres:
           image: postgres:13
           env:
             POSTGRES_USER: postgres
             POSTGRES_PASSWORD: password
             POSTGRES_DB: app
           ports:
             - 5432/tcp
           options: >-
             --health-cmd="pg_isready -U postgres"
             --health-interval=10s
             --health-timeout=5s
             --health-retries=5

         redis:
           image: redis:latest
           ports:
             - 6379/tcp
           options: >-
             --health-cmd="redis-cli ping"
             --health-interval=10s
             --health-timeout=5s
             --health-retries=5

       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.9'

         - name: Install dependencies for backend
           run: |
             cd backend
             python -m pip install --upgrade pip
             pip install -r requirements.txt

         - name: Run backend tests
           run: |
             cd backend
             pytest

         - name: Set up Node.js
           uses: actions/setup-node@v2
           with:
             node-version: '14'

         - name: Install dependencies for frontend
           run: |
             cd frontend
             npm install

         - name: Run frontend tests
           run: |
             cd frontend
             npm test

     build:
       name: Build Docker Images
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v1

         - name: Log in to Docker Hub
           uses: docker/login-action@v2
           with:
             username: ${{ secrets.DOCKER_USERNAME }}
             password: ${{ secrets.DOCKER_PASSWORD }}

         - name: Build and push backend image
           run: |
             docker buildx build --push --tag ${{ secrets.DOCKER_USERNAME }}/backend:latest ./backend

         - name: Build and push frontend image
           run: |
             docker buildx build --push --tag ${{ secrets.DOCKER_USERNAME }}/frontend:latest ./frontend

     deploy:
       name: Deploy to AWS ECS
       needs: build
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Configure AWS credentials
           uses: aws-actions/configure-aws-credentials@v1
           with:
             aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
             aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
             aws-region: ${{ secrets.AWS_REGION }}

         - name: Deploy to ECS
           run: |
             ecs-cli configure --cluster my-cluster --default-launch-type EC2 --region ${{ secrets.AWS_REGION }} --config-name my-config
             ecs-cli configure profile --access-key ${{ secrets.AWS_ACCESS_KEY_ID }} --secret-key ${{ secrets.AWS_SECRET_ACCESS_KEY }} --profile-name my-profile
             ecs-cli compose --file docker-compose.yml service up
             ecs-cli compose --file docker-compose.yml service start
   ```

## Example Use Cases

- **User Authentication**: Users can sign up and log in to the application to start chatting.
- **Real-Time Messaging**: Users can send and receive messages in real-time within chat rooms.
- **Message Storage**: Messages are stored in a PostgreSQL database and can be retrieved later.

## Architecture Diagram

![Architecture Diagram](path/to/architecture-diagram.png)
