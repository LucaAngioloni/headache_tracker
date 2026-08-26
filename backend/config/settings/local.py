from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"  # noqa: F405

if os.environ.get("DJANGO_TEST_SQLITE"):  # noqa: F405
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "test.sqlite3"),  # noqa: F405
        }
    }
