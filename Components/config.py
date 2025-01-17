from enum import Enum

# Config file
# This file is used to store the configuration of the application

# DEVELOPMENT OR PRODUCTION
class DeploymentMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

DEPLOYMENT_MODE = DeploymentMode.DEVELOPMENT


DEVELOPMENT_CONFIG = {
    "DB_NAME": "bibliotech_db",
    "DB_USER": "root",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": 3306,
}

PRODUCTION_CONFIG = {
    "DB_NAME": "bibliotech_planestill",
    "DB_USER": "bibliotech_planestill",
    "DB_PASSWORD": "2df559976a9a869cba3a04b57c6594747c004e6a",
    "DB_HOST": "dq54g.h.filess.io",
    "DB_PORT": 3305,
}




#     "PRODUCTION": {
#         "DB_NAME": "bibliotech_planestill",
#         "DB_USER": "bibliotech_planestill",
#         "DB_PASSWORD": "2df559976a9a869cba3a04b57c6594747c004e6a",
#         "DB_HOST": "dq54g.h.filess.io",
#         "DB_PORT": 3305,
#     },
# }

HOURS_PER_BACKUP = 24