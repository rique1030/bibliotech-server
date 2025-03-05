from enum import Enum

# Config file
# This file is used to store the configuration of the application

# DEVELOPMENT OR PRODUCTION
class DeploymentMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

# Borrowing
REQUEST_TIMEOUT = 10 # Seconds before a request is timed out
REVIEW_TIMEOUT = 30 # Additional seconds added to the request timeout

DEPLOYMENT_MODE = DeploymentMode.PRODUCTION


DEVELOPMENT_CONFIG = {
    "DB_NAME": "bibliotech_db",
    "DB_USER": "root",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": 3306,
}

PRODUCTION_CONFIG = {
    "DB_NAME": "bibliotech_pickharder",
    "DB_USER": "bibliotech_pickharder",
    "DB_PASSWORD": "2ef75e60cbf825309897ac4d7e723a0e5dd16389",
    "DB_HOST": "0wsez.h.filess.io",
    "DB_PORT": 3305,
}
