# thsltrans-api
Rule-based system implemented as API service for ThSL translator web application (SKE senior project 2021, Kasetsart University)

Deployed at https://thsltrans-api.herokuapp.com/

## Requirements
* Python version 3.8 or later

### Dependencies
* [Flask](https://flask.palletsprojects.com/en/2.0.x/)
* [MongoEngine](http://mongoengine.org/)
* [Spacy](https://spacy.io/)

## How to run the server locally
1. Create `.env` file at the root directory, `thsltrans-api`. 
See the [Setting up environment variables](#setting-up-environment-variables) section for more details.

1. Install all dependencies  from `requirements.txt`.
    ```shell script
    pip install -r requirements.txt
    ```
2. Go to the root directory, then run the following command
    ```shell script
    py app.py
    ```
   * This command will run Flask application at http://127.0.0.1:5000/

## Setting up environment variables

Please create `.env` file at the root directory for storing the environment variables. The required environment variables are as follow.

| Name          | Description                                       |
|---------------|---------------------------------------------------|
| `MONGO_URI`   | A connection string of MongoDB database\* | 
| `DB_NAME`     | A name of the database                            |

* If you are using a connection string of MongoDB Atlas, 
please use a connection string for Python version `3.4 or later` to prevent the error.
