import os
from typing import Optional, Sequence

from load_dotenv import load_dotenv
from pydantic import BaseModel, Field

class DatabaseConfiguration(BaseModel):
    host: str = Field(..., description="Hostname or IP address of the database server")
    port: int = Field(5432, description="Port number for the database connection")
    database: str = Field("indicate", description="Name of the database")
    user: str = Field("postgres", description="Username for database authentication")
    password: Optional[str] = Field(None, description="Password for database authentication")
    dbschema: str = Field("indicate", description="The schema in which the results are stored")

class Configuration(BaseModel):
    database: DatabaseConfiguration

def load_configuration(config_file: str = ".env") -> Configuration:
    """
    Loads the configuration from a file or environment variables.
    Environment variables take precedence over values in the configuration file.
    """

    load_dotenv(config_file)

    # Create a dictionary from environment variables
    config_dict = {
        "database": {
            "host": os.getenv("DATABASE_HOST"),
            "password": os.getenv("DATABASE_PASSWORD"),
        },
    }

    def maybe_from_env(key, variable_name, transform=None):
        value = os.getenv(variable_name)
        if value:
            if transform:
                value = transform(value)
            container = config_dict
            if isinstance(key, Sequence):
                for step in key[:-1]:
                    container = container[step]
                key = key[-1]
            container[key] = value
    maybe_from_env(("database", "port"), "DATABASE_PORT", int)
    maybe_from_env(("database", "user"), "DATABASE_USER")
    maybe_from_env(("database", "database"), "DATABASE_NAME")
    maybe_from_env(("database", "dbschema"), "DATABASE_SCHEMA")

    return Configuration(**config_dict)
