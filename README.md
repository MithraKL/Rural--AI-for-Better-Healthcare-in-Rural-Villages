# Rural Healthcare Management System

An intelligent nervous system for rural healthcare, connecting data to decisions and transforming reactive crisis management into proactive preventive care across every village.

## Product Vision

To become the intelligent nervous system of rural healthcare, connecting data to decisions and transforming reactive crisis management into proactive preventive care across every village.

## Target Audience

- **District Health Officers**: Managing multiple villages and coordinating healthcare resources
- **Frontline Health Workers**: Including Anganwadi staff, ASHA workers, and ANM personnel
- **Policy Makers**: Responsible for rural healthcare resource allocation and program design

## Core Features

- **Health Records Management**: Complete CRUD operations for patient health records
- **Village Management**: Track and manage rural villages with population and location data
- **Health Worker Management**: Manage frontline healthcare workers and their assignments
- **Data-Driven Insights**: Connect health data to enable informed decision-making

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **Architecture**: Modular Monolith

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Clone the repository or navigate to the project directory:
```bash
cd /app/user_workspace/team_027/f02f5792-e4b4-4512-bd64-bf086c9d84a2
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` file and update the configuration values as needed.

## Running the Application

### Development Mode

Run the application with auto-reload enabled:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### Villages
- `POST /api/v1/villages` - Create a new village
- `GET /api/v1/villages` - Get all villages (with optional filters)
- `GET /api/v1/villages/{village_id}` - Get a specific village
- `PUT /api/v1/villages/{village_id}` - Update a village
- `DELETE /api/v1/villages/{village_id}` - Delete a village

### Health Workers
- `POST /api/v1/workers` - Create a new health worker
- `GET /api/v1/workers` - Get all health workers (with optional filters)
- `GET /api/v1/workers/{worker_id}` - Get a specific health worker
- `PUT /api/v1/workers/{worker_id}` - Update a health worker
- `DELETE /api/v1/workers/{worker_id}` - Delete a health worker

### Health Records
- `POST /api/v1/health-records` - Create a new health record
- `GET /api/v1/health-records` - Get all health records (with optional filters)
- `GET /api/v1/health-records/{record_id}` - Get a specific health record
- `PUT /api/v1/health-records/{record_id}` - Update a health record
- `DELETE /api/v1/health-records/{record_id}` - Delete a health record

## Database

The application uses SQLite by default for easy setup. The database file `rural_healthcare.db` will be created automatically in the project root when you first run the application.

### Database Models

1. **Village**: Stores village information including name, district, state, population, and coordinates
2. **HealthWorker**: Manages frontline health workers with their roles and assignments
3. **HealthRecord**: Tracks patient health records with symptoms, diagnosis, and treatment information

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for security (change in production)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## Architecture Overview

The application follows a **Modular Monolith** architecture with clear separation of concerns:

```
backend/
├── main.py           # Application entry point
├── config.py         # Configuration management
├── database.py       # Database setup and session management
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic schemas for validation
└── routers/          # API route handlers
    ├── health_records.py
    ├── villages.py
    └── workers.py
```

## Development Guidelines

- All API endpoints include proper error handling
- Input validation is performed using Pydantic schemas
- Database operations use SQLAlchemy ORM for security
- Logging is configured for monitoring and debugging
- CORS is configured for frontend integration

## Security Features

- Input validation on all endpoints
- SQL injection prevention through ORM
- Environment-based configuration
- Secure password handling ready (for future authentication)
- CORS configuration for controlled access

## Future Enhancements

- User authentication and authorization
- Advanced analytics and reporting
- Mobile application for field workers
- Real-time notifications and alerts
- Integration with government health systems
- Predictive analytics for preventive care

## Support

For issues, questions, or contributions, please contact the development team.

## License

[Specify your license here]
