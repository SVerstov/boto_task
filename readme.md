# Overview

Testing task for **Boto** company. URL shortener with the ability to edit and delete links.

The code contains my developments from other my projects, such as **logging system**, **configuration system** and data access object.
Some of them may seem excessive for this small project, but they will be very usefully if the project grows.

By default, the project uses `sqlite`, but you can change it to `postgres` in the config.

# Installation

## File Copying

Copy 2 configuration files. Configure as desired:
config.toml.dist -> config.toml
logger.toml.dist -> logger.toml

## Virtual Environment

It is desirable that `poetry` is already installed in the system.
Install dependencies from **pyproject.toml**.
You can do this with the command `make init` and `make install`.

## Migrations

Apply migrations to create tables:

```
make migrate
```

# Running

```
make run
```

After launching, you can view the description of endpoints here:
http://127.0.0.1:5000/docs

# Testing

Uses pytest:

```
make test
```

# Logging

Logging is configured in the `config/logger.toml` file.
Logs can be found in the `logs` folder.