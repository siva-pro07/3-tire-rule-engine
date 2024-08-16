# Rule Engine Application

## Overview

This project is a simple Rule Engine application that allows users to create rules, combine them, and evaluate them dynamically. It includes both frontend and backend components. The backend is built using Flask and PostgreSQL, while the frontend uses HTML, Bootstrap, and jQuery.

## Directory Structure

```plaintext
.
├── backend
│   ├── api
│   │   ├── ast_utils.py
│   │   └── routes.py
│   ├── tests
│   │   └── test_rule_engine.py
├── frontend
│   └── index.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
## Design Choices

* **Backend Framework:** Flask was chosen for its simplicity and ability to quickly create APIs for rule creation, combination, and evaluation.

* **Database:** PostgreSQL was selected due to its robustness and familiarity with JSON types, which are useful for storing AST structures.

* **Frontend:** The frontend uses HTML, Bootstrap, and jQuery for dynamic rule management and data display.

* **AST Management:** The AST (Abstract Syntax Tree) helps in parsing and representing rules in a hierarchical manner, making it easy to evaluate complex conditions.

## Prerequisites

**Docker:** The application is containerized using Docker for consistent development and production environments.

**Docker Compose:** To manage multi-container Docker applications.

Ensure that you have both Docker and Docker Compose installed:

* Install Docker
* Install Docker Compose

## Setup and Installation

**1.Clone the repository:**

```bash
git clone [https://github.com/yourusername/rule-engine.git](https://github.com/yourusername/rule-engine.git)
cd rule-engine
```
**2.Set up the environment using Docker Compose:**

We have a docker-compose.yml that will spin up both the Flask backend and the PostgreSQL database.

```Bash
docker-compose up --build
```

This will build the Docker images and run the containers.

**3.Accessing the Application**
* Frontend: Visit http://localhost:5000 in your browser to access the rule engine interface.
* API: The API will be running on http://localhost:5000.

**4.Database:**

* The PostgreSQL container will be running, and you can access it using localhost:5432.
* Default credentials are set in docker-compose.yml, but you can customize them if necessary.

## Endpoints

* POST /create_rule: Creates a new rule and stores it in the database.
* POST /combine_rules: Combines two or more rules and stores the combined result in the database.
* POST /evaluate_rule: Evaluates a rule against provided data and returns the result.
* GET /: Renders the frontend with the rules and combined rules displayed.

## Running Tests
To run unit tests for the rule engine, you can use:

Bash
docker exec -it <container_id> pytest
Use code with caution.

## Dependencies

All Python dependencies are listed in requirements.txt. These are installed in the Docker container when building the images. The primary libraries used include:

* Flask
* SQLAlchemy
* psycopg2
* pytest

## Using the Application

* Create Rules: Input the rule logic in the frontend interface and click "Create Rule".
* Combine Rules: Enter rule IDs to combine and click "Combine Rules".
* Evaluate Rules: Provide the AST and data to evaluate a rule and get the results.

## Docker Compose Details
Here is a sample of docker-compose.yml:

```YAML
version: '3.8'
services:
  app:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db/rule_engine_db

  db:
    image: postgres:latest
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: rule_engine_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/datavolumes:
  pgdata:
```
## License

This project is licensed under the MIT License.

## Author

Developed by K Siva Kesava