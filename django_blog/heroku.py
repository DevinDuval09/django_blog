import os
import dj_database_url

from .settings import *

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")
    )
}

DEBUG = True
TEMPLATE_DEBUG = True
STATIC_ROOT = os.path.join(BASE_DIR, "static")
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = ["*"]

MIDDLEWARE = (
    "whitenoise.middleware.WhiteNoiseMiddleWare",
    *MIDDLEWARE,
)
