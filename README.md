# Intelligent Help Center for PLV students (Group 3)
Julien DE VOS - Lorrain MORLET - Noémie MAZEPA - Auriane MARCELINO - Lisa CHARUEL - Aymeric MARTIN

**Table of Contents**

- [Context](#context)
- [Prerequisites](#prerequisites)
- [Start the project](#start-the-project)
    - [Data pre-processing](#data-preprocessing)
        - [Option 1: watsonx](#option-1-watsonx)
        - [Option 2: Python](#option-2-python)
    - [Setup the MariaDB database](#setup-the-mariadb-database)
    - [Launch the Chainlit app](#launch-the-chainlit-app)

---

## Context
The actual Help center, relies on researches on a database with 400 cases.
To improve the access to information for students, we developed an intelligent conversational agent who understand the request and give the correct answer, based on the questions of the database.

---

## Prerequisites

- Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

- Create the environment variables:

    Create a `.env` file in the root of the project, based on the provided template, and set the required environment variables:

    ```env
    MISTRAL_API_KEY="your_mistral_api_key"
    CHAINLIT_AUTH_SECRET="your_chainlit_auth_secret"
    ```

    To get your CHAINLIT_AUTH_SECRET, execute the following commands:

    ```bash
    cd source/app
    chainlit create-secret
    ```
---

## Start the project

### Data preprocessing

#### Option 1: watsonx
1. Create an project on watsonx (ex: Hackathon_A5)
2. Upload your dataset (csv) on watsonx
3. Clic on your dataset then on "Prepare data"
4. Delete all the columns you don't need (only keep "Title", "Contente" and "Thématiques")
5. Create a concatenate columns grouping those three columns, with " | " as separator
6. Save it and download it

#### Option 2: Python
1. Upload the `Data.xlsx` file containing your data in the `source/app/data` folder

2. Execute the preprocessing.py file:
    ```bash
    cd source/app
    python preprocessing.py
    ```

### Setup the MariaDB database
1. Make sure you have MariaDB installed and running on your machine.

2. Copy the `source/app/preprocessing/create_databases.sql` file content and execute it in your MariaDB instance to create the necessary database and tables.

3. Execute the following commands to insert the preprocessed data into the database:
    ```bash
    cd source/app
    python populate_mariadb.py
    ```

### Launch the Chainlit app

Execute the following commands to start the Chainlit app:
```bash
cd source/app
chainlit run app.py
```

Then, open your browser and go to `http://localhost:8000`.