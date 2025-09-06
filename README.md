# GrabHack Customer Service Platform

A comprehensive customer service platform for Grab services (Grab Food, Grab Cabs, Grab Mart) with role-based authentication and AI-powered complaint resolution.

## Features

### User Types & Access
- **Customer**: Can complain about all 3 services (Food, Cabs, Mart)
- **Delivery Agent**: Can handle Food and Mart delivery issues  
- **Restaurant**: Can handle Food service issues only
- **Driver**: Can handle Cabs service issues only
- **Dark Store**: Can handle Mart inventory and operational issues only

### Service-Specific Query Categorization
Each service has detailed issue categories with sub-issues:
- **Grab Food**: 5 main categories with 20+ sub-issues
- **Grab Cabs**: 3 main categories with focused ride and driver issues  
- **Grab Mart**: 3 main categories with grocery-specific problems

## Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to the project:**
```bash
cd last_mile_coordinator
```

2. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api

### Manual Setup

#### Backend Setup
```bash
cd GrabHack
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Demo Login Credentials

| User Type | Username | Password | Services Available |
|-----------|----------|----------|-------------------|
| Customer | customer1 | pass123 | Food, Cabs, Mart |
| Delivery Agent | agent1 | pass123 | Food, Mart |
| Restaurant | resto1 | pass123 | Food |
| Driver | driver1 | pass123 | Cabs |
| Dark Store | store1 | pass123 | Mart |

## How to Use

1. **Login** with any of the demo credentials above
2. **View Dashboard** to see your orders/activities
3. **Select a Service** to submit a complaint
4. **Choose Issue Category** relevant to your role and service
5. **Select Specific Sub-Issue** from the detailed options
6. **Describe Your Problem** in detail
7. **Get AI-Generated Solution** instantly

## Architecture

### Backend (Flask)
- RESTful API with role-based endpoints
- SQLite database with users, orders, and complaints tables
- Pre-seeded with demo data for all user types
- AI solution generation based on service, role, and issue type

### Frontend (React)
- Role-based navigation and service access
- Dynamic issue categorization based on user type
- Responsive design with modern UI
- Real-time complaint submission and AI response

### Database Schema
- **Users**: Authentication and role management
- **Orders**: Service-specific order/activity data  
- **Complaints**: Complaint tracking with AI solutions

## Issue Categories by Service & Role

### Grab Food
- **Customer**: Order quality, delivery experience, driver interaction, payments, technical issues
- **Restaurant**: Portion standards, food safety, preparation efficiency, operational issues
- **Delivery Agent**: Navigation, logistics, operational challenges, customer interaction

### Grab Cabs  
- **Customer**: Ride safety, driver behavior, payment disputes
- **Driver**: Performance coaching, route optimization, earnings support

### Grab Mart
- **Customer**: Product quality, missing items, substitution issues  
- **Dark Store**: Inventory management, quality control, warehouse efficiency
- **Delivery Agent**: Grocery handling, cold chain delivery, bulk order management

## Technology Stack

- **Frontend**: React 18, React Router, Axios, Styled Components
- **Backend**: Flask, Flask-CORS, SQLite
- **Infrastructure**: Docker, Docker Compose
- **AI Integration**: Built-in solution generation (expandable to full AI orchestration)

## Future Enhancements

1. Integration with existing AI orchestration system
2. Real-time chat support
3. Advanced analytics and reporting
4. Mobile app support
5. Multi-language support
6. Advanced user management and permissions