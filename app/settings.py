from starlette.config import Config
from starlette.datastructures import Secret
from uuid import UUID

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

SERVER_URL = config("DATA_CONNECTER_SERVER_URL", default="http://localhost:9020")
