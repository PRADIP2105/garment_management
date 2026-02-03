# Garment Work & Material Management System

A production-ready SaaS application for middle-level garment contractors to manage workers, suppliers, materials, and production workflow.

## Features

- **Multi-tenant SaaS architecture** - Each company is isolated
- **User Management** - Owner and Staff roles
- **Worker Management** - Track workers with skills and contact details
- **Supplier Management** - Manage supplier information
- **Material Management** - Raw material master and inward tracking
- **Work Distribution** - Distribute work and materials to workers
- **Work Return** - Track completed work and returned materials
- **Stock Management** - Automated stock ledger with real-time tracking
- **Dashboard** - Overview of operations and key metrics
- **Multi-language Support** - English and Gujarati
- **Web & Mobile Apps** - Web interface and Flet-based mobile app

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT-based
- **Web Frontend**: Django Templates + Bootstrap
- **Mobile App**: Flet (Python-based)
- **API**: RESTful API with proper tenant isolation

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd garment-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb garment_management
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Mobile App

To run the mobile app:

```bash
python mobile_app.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new company and owner
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/token/refresh/` - Refresh access token

### Workers
- `GET /api/workers/` - List workers
- `POST /api/workers/` - Create worker
- `GET /api/workers/{id}/` - Get worker details
- `PUT /api/workers/{id}/` - Update worker
- `DELETE /api/workers/{id}/` - Delete worker

### Suppliers
- `GET /api/suppliers/` - List suppliers
- `POST /api/suppliers/` - Create supplier
- `GET /api/suppliers/{id}/` - Get supplier details
- `PUT /api/suppliers/{id}/` - Update supplier
- `DELETE /api/suppliers/{id}/` - Delete supplier

### Materials
- `GET /api/materials/raw-materials/` - List raw materials
- `POST /api/materials/raw-materials/` - Create raw material
- `GET /api/materials/inward/` - List material inward records
- `POST /api/materials/inward/` - Create material inward

### Work Management
- `GET /api/work/types/` - List work types
- `POST /api/work/types/` - Create work type
- `GET /api/work/distributions/` - List work distributions
- `POST /api/work/distributions/` - Create work distribution
- `GET /api/work/returns/` - List work returns
- `POST /api/work/returns/` - Create work return

### Stock
- `GET /api/stock/current/` - Current stock levels
- `GET /api/stock/ledger/` - Stock ledger entries
- `GET /api/stock/current/low_stock/` - Low stock materials

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics

## Architecture

```
Mobile App (Flet)
    |
Web App (Django Templates)
    |
REST API (DRF)
    |
Django Business Logic
    |
PostgreSQL Database
```

## Multi-Tenancy

- Each company is a separate tenant
- All business data is isolated by company_id
- Users can only access their own company's data
- Middleware enforces tenant isolation

## User Roles

1. **Owner** - Full access to all features including company management
2. **Staff** - Limited access, cannot delete company

## Stock Management

- Automatic stock calculation: `opening + inward - issued + returned = closing`
- Real-time stock updates on material inward, work distribution, and returns
- Stock ledger maintains complete transaction history
- No manual stock editing allowed

## Development

### Project Structure

```
garment_management/
├── apps/
│   ├── authentication/     # User authentication
│   ├── companies/         # Company and user profiles
│   ├── workers/           # Worker management
│   ├── suppliers/         # Supplier management
│   ├── materials/         # Material management
│   ├── work_management/   # Work distribution and returns
│   ├── stock/            # Stock management
│   ├── dashboard/        # Dashboard statistics
│   └── web/              # Web frontend
├── templates/            # HTML templates
├── static/              # Static files
├── mobile_app.py        # Flet mobile application
└── manage.py           # Django management script
```

### Key Design Principles

1. **API-First**: All functionality exposed via REST API
2. **Tenant Isolation**: Strict data separation between companies
3. **Service Layer**: Business logic separated from views
4. **Automated Stock**: No manual stock manipulation
5. **Audit Trail**: Complete transaction history in stock ledger

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper database credentials
3. Set up static file serving
4. Configure CORS for frontend domains
5. Use proper secret key
6. Set up SSL/HTTPS
7. Configure logging

## License

This project is proprietary software. All rights reserved.