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

    data_provider_count_threshold: Optional[int] = Field(None,
                                                         description="""Minimum number of data provider which must \
                                                         have contributed data to a result period in order for that \
                                                         period to be transmitted to clients.""")

def load_configuration(config_file: str = ".env") -> Configuration:
    """
    Loads the configuration from a file or environment variables.
    Environment variables take precedence over values in the configuration file.
    """

    load_dotenv(config_file)

    args = {}
    def maybe_from_env(key, variable_name, transform=None):
        value = os.getenv(variable_name)
        if value is None:
            filename = os.getenv(f"{variable_name}_FILE")
            if filename is not None:
                with open(filename) as file:
                    value = file.read().strip()

        if value is not None:
            if transform:
                value = transform(value)
            container = args
            if isinstance(key, tuple):
                for step in key[:-1]:
                    if step not in container:
                        container[step] = {}
                    container = container[step]
                key = key[-1]
            container[key] = value

    maybe_from_env(("database", "host"), "DATABASE_HOST")
    maybe_from_env(("database", "port"), "DATABASE_PORT", int)
    maybe_from_env(("database", "database"), "DATABASE_NAME")
    maybe_from_env(("database", "user"), "DATABASE_USER")
    maybe_from_env(("database", "password"), "DATABASE_PASSWORD")
    maybe_from_env(("database", "dbschema"), "DATABASE_SCHEMA")

    maybe_from_env("data_provider_count_threshold", "DATA_PROVIDER_COUNT_THRESHOLD")

    return Configuration(**args)
