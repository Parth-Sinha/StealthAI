# GRAPHFLOW DATABASE

## Overview
This project is a web application built with a FastAPI backend and a ReactJS frontend. The backend handles interactions with a Neo4j graph database and MongoDB, while the frontend provides a user-friendly interface for visualizing and interacting with the data.

## Tech Stack
- **Backend**: 
  - FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.6+.
  - Neo4j: A graph database management system.
  - MongoDB: A NoSQL document database for storing application data.
  - Pydantic: For data validation and settings management.
  - Uvicorn: An ASGI server for serving FastAPI applications.

- **Frontend**:
  - React: A JavaScript library for building user interfaces.
  - Axios: For making HTTP requests from the frontend to the backend.

- **Containerization**:
  - Docker: For containerizing the application.
  - Docker Compose: For defining and running multi-container Docker applications.

## Folder Structure
```
/project
  ├── app/                  # Backend application files
  │   ├── main.py          # Entry point for FastAPI application
  │   ├── crud.py          # CRUD operations for the database
  │   ├── database.py       # Database connection and utilities
  │   ├── neo4j_crud.py    # Neo4j specific CRUD operations
  │   ├── mongo_crud.py     # MongoDB specific CRUD operations
  │   ├── requirements.txt  # Python dependencies
  │   └── schemas.py       # Pydantic schemas for data validation
  ├── frontend/             # Frontend application files
  │   ├── graphdb/         # ReactJS application
  │   │   └── src/         # Source files for React components
  ├── Docker-compose.yml     # Docker Compose configuration
  ├── Dockerfile             # Dockerfile for backend
  └── frontend.Dockerfile    # Dockerfile for frontend
  |__ test/                   # Sample create / run graph
    ├── create_graph_1.json          # Sample file for creating graph1
    ├── create_graph_2.json          # Sample file for creating graph1
    ├── run_graph_1_1.json       # sample run file for graph1
    ├── run_graph_1_2.json    # sample run file for graph1
    ├── run_graph_2_1.json     # sample run file for graph2
    ├── run_graph_2_2.json      #sample run file for graph2
```

## Prerequisites
- Make sure you have the following installed on your local machine:
  - [Docker](https://docs.docker.com/get-docker/) (version 27.2.0)
  - [Docker Compose](https://docs.docker.com/compose/install/) (Docker Compose version v2.29.2-desktop.2)
  - [Python](https://www.python.org/downloads/) (version 3.10.7) for running the backend outside of Docker (optional)

## Setup Instructions

### 1. Clone the Repository
First, clone the project repository from GitHub to your local machine:

```bash
git clone <repository-url>
cd project
```

### 2. Set Up the Backend

#### 2.1 Install Backend Dependencies
Navigate to the `app` directory and install the required Python packages:

```bash
cd app
pip install -r requirements.txt
```

#### 2.2 Configure Neo4j and MongoDB Connection
Update your Neo4j and MongoDB database connection details in `app/database.py`. Modify the `neo4j_uri`, `neo4j_user`, `neo4j_password`, and MongoDB connection settings as needed.

#### 2.3 Setup Environment Variables
Setup .env file under app directory
```bash
# Neo4j configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password

# MongoDB configuration
MONGODB_URI=mongodb://username:password@localhost:27017
DB_NAME=your_db_name

```

### 3. Set Up the Frontend

#### 3.1 Navigate to the Frontend Directory
Go to the `frontend/graphdb` directory:

```bash
cd ../frontend/graphdb
```

#### 3.2 Install Frontend Dependencies
Install the required packages for the React application:

```bash
npm install
```

### 4. Running the Application

#### 4.1 Using Docker Compose
The easiest way to run the application is using Docker Compose. From the root of the project directory, run:

```bash
docker-compose up --build
```

This command will:
- Build and start both the backend and frontend services.
- Create a network for the services to communicate.
- Expose the FastAPI application at `http://localhost:8000` and the React application at `http://localhost:3000`.

#### 4.2 Running Backend and Frontend Separately (Optional)

If you prefer to run the backend and frontend separately without Docker, you can do the following:

**Run the Backend**:
- In a terminal, navigate to the `app` directory and run the FastAPI application:

```bash
cd app
uvicorn main:app --reload
```

This will start the FastAPI server at `http://localhost:8000`.


**Run the Frontend**:
- In another terminal, navigate to the `frontend/graphdb` directory and start the React application:

```bash
cd frontend/graphdb
npm start
```

This will start the React application at `http://localhost:3000`.


### 5. Accessing the Application
- Open your web browser and navigate to `http://localhost:3000` to view the React application.
- The backend API can be accessed at `http://localhost:8000`.

### 6. API Endpoints
The FastAPI backend exposes several endpoints for interacting with the Neo4j and MongoDB databases. You can view the documentation at `http://localhost:8000/docs` to see the available endpoints and test them.

### 7. Features

- **localhost:3000/**: Displays a list of all graphs in the database and an option to create more graphs by uploading an appropriate JSON file. For each `graph_id`, all associated `run_ids` are shown.

    - Clicking on a `graph_id` redirects to `localhost:3000/graph/{graph_id}`.

- **localhost:3000/graph/{graph_id}**: Visualizes the graph in 3D, allowing users to:
    - View attributes and values of nodes by selecting them.
    - Upload a file (GraphRunSchema JSON) to run the graph and view the output.

- **localhost:3000/output/{run_id}**: Displays the output of a specific graph run associated with `run_id`, showing:
    - Any islands formed.
    - The final computed values for each node as a result of the run.
    - Level Order Traversal and Topological Sort Order for the graph.


### 8. Stopping the Application
If you started the application with Docker Compose, you can stop it by pressing `CTRL+C` in the terminal where it's running, or by running:

```bash
docker-compose down
```



# DEMO

## Main Page
Shows a list of all the Graph_ids present in the Neo4j
![stealthAi_mainPage](https://github.com/user-attachments/assets/3baaeae9-7b33-404f-b37b-7dd3258367d1)


## For SAMPLE GRAPH 1 (create_graph_1.json)

### Running on Sample 1 (run_graph_1_1.json)
 

https://github.com/user-attachments/assets/2971d986-868c-45fa-bead-7cf6d7d59d0f


### Running on Sample 2 (run_graph_1_2.json)


https://github.com/user-attachments/assets/b95701f5-cf28-470f-b764-122221a30289


## For SAMPLE GRAPH 2 (create_graph_2.json)

### Running on Sample 1 (run_graph_2_1.json)



https://github.com/user-attachments/assets/40ecff5f-dac2-4328-b1bf-4eb231a0cefd



### Running on Sample 2 (run_graph_2_2.json)


https://github.com/user-attachments/assets/c46d04e0-2b40-4019-9357-2870ce9243ed


## BACKEND APIs

![backendApis](https://github.com/user-attachments/assets/7e67ed29-12c2-46ca-9dfb-8fee5c9c5ac4)

