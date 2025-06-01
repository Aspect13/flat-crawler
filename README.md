## Project Architecture

The application follows a modular architecture with the following components:

- FastAPI for REST API endpoints
- SQLModel/SQLAlchemy for database operations
- Abstract Data Provider interface for different data sources
- Alembic for database migrations

## Data Providers

The application supports multiple data providers through the `DataProviderFactory`. Each provider must implement the
`DataProvider` interface.


### Available Providers

- Telegram channels
- (Additional providers can be added by implementing the DataProvider interface)


## Project Structure

### Directories

- `/api` - FastAPI application endpoints and routing
- `models.py` - Database models and schemas
- `/providers` - Data provider implementations
- `/migrations` - Alembic database migrations
- `config.py` - Configuration file with settings

### Key Files

- `main.py` - Core application logic and services
- `api/main.py` - FastAPI application instance and routes

### Run

1. Activate your virtual environment: `python -m venv venv` `source ./venv/bin/activate`
2. Install test dependencies: `pip install -r requirements.txt`
3. Run migrations: `alembic upgrade head`
4. Run app: `uvicorn api.main:app --host 0.0.0.0 --port 80 --reload`

Note: Make sure your database is properly configured in `config.py` before running migrations.

### Example .env file
```aiignore
db_connection_string=sqlite:///flats.db

flip_flat_api_hash=
flip_flat_app_id=
flip_flat_channel_id=1676033482
```