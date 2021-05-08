## Description
The setting is the provided way to configure the application :

## Environment configuration
In order to easily manage differents types of configurations you can use env variable.

!!! info
    It is possible to configure multiple env using `.env` files.

!!! warning
    If you provide an incorect `.env` filepath it will be silently ignored !

??? example "Linux"
    ```
    DOTENV_PATH=dev.env venv/bin/uvicorn modularapi.asgi:app --reload
    ```
    ```
    DOTENV_PATH=prod.env venv/bin/gunicorn modularapi.asgi:app -k uvicorn.workers.UvicornWorker
    ```

???+ example "Windows TODO"
    ```
    TODO
    ```

### DOTENV_PATH
The DOTHENV_PATH variable environnment is used to provide a path to the `.env` file.

!!! warning
    Set this variable in the `.env` file will have no effect.

### Database settings
#### PG_DNS

This variable is **required**.

The postgres url to connect to the database, see [https://www.postgresql.org/docs/13/libpq-connect.html#LIBPQ-CONNSTRING](https://www.postgresql.org/docs/13/libpq-connect.html#LIBPQ-CONNSTRING){target=_blank} for more information.

### Documentation

#### OPENAPI_URL

default: `/openapi.json`
Could be set to `DISABLED` to disable it

!!! info
    that will also disable docs et redoc UI.

#### DOCS_URL

default: `/docs`
Could be set to `DISABLED` to disable it

#### REDOC_URL

default: `/redoc`
Could be set to `DISABLED` to disable it

### Logging

#### LOG_TO_STDOUT

default: `True`.

Enable a `logging.basicConfig` configuration, under the hood it look like
```py hl_lines="1"
if get_setting().LOG_TO_STDOUT:
    logging.basicConfig(
        level=get_setting().LOGGING_LEVEL,
        format=get_setting().LOGGING_FMT,
    )
```

#### LOGGING_LEVEL

default: `logging.INFO`.

if LOG_TO_STDOUT is set to `False` this variable will have no effect.

under the hood it look like
```py hl_lines="3"
if get_setting().LOG_TO_STDOUT:
    logging.basicConfig(
        level=get_setting().LOGGING_LEVEL,
        format=get_setting().LOGGING_FMT,
    )
```

#### LOGGING_FMT

default: `"%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"`.

if LOG_TO_STDOUT is set to `False` this variable will have no effect.

under the hood it look like
```py hl_lines="4"
if get_setting().LOG_TO_STDOUT:
    logging.basicConfig(
        level=get_setting().LOGGING_LEVEL,
        format=get_setting().LOGGING_FMT,
    )
```

