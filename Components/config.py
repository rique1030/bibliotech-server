from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()

# Config file
# This file is used to store the configuration of the application

# DEVELOPMENT OR PRODUCTION
class DeploymentMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

# Borrowing
REQUEST_TIMEOUT = 10 # Seconds before a request is timed out
REVIEW_TIMEOUT = 30 # Additional seconds added to the request timeout

DEPLOYMENT_MODE = DeploymentMode.DEVELOPMENT


DEVELOPMENT_CONFIG = {
    "DB_NAME": "bibliotech_db",
    "DB_USER": "root",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": 3306,
}

# For production, ensure these environment variables are set in Replit Secrets
PRODUCTION_CONFIG = {
    "DB_NAME": os.getenv("DB_NAME"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": int(os.getenv("DB_PORT", "3306")),  # Convert to int with default
}
