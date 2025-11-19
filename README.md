# 🎓 Health & Wellness Predictor - Student Version

A complete **Machine Learning-powered health tracking system** with user authentication, wellness predictions, and admin management.

## 🎯 Project Overview

This backend system provides:
- ✅ User registration & authentication (JWT)
- ✅ Health data tracking (sleep, activity, nutrition, etc.)
- ✅ ML-powered wellness score predictions
- ✅ Personalized health recommendations
- ✅ Historical data & statistics
- ✅ Admin panel for user management
- ✅ RESTful API for frontend integration

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Backend

```bash
# Make startup script executable
chmod +x start_backend.sh

# Start the server
./start_backend.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Default Admin Account

```
Email: admin@wellness.com
Password: admin
```

**⚠️ Change this password immediately in production!**

## 📁 Project Structure

```
health_wellness_student_version/
├── api/
│   ├── server.py          # FastAPI application with all endpoints
│   ├── auth.py            # JWT authentication & password hashing
│   └── database.py        # SQLite database operations
├── app/
│   ├── utils/
│   │   ├── predict.py     # ML wellness prediction
│   │   └── recommend.py   # Health recommendation engine
│   └── model/
│       ├── wellness_model.joblib      # Pre-trained ML model
│       ├── preprocessor.joblib        # Data preprocessing
│       └── metrics.json               # Model performance metrics
├── app/db/
│   └── wellness_multiuser.db          # SQLite database (auto-created)
├── start_backend.sh       # Startup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔌 API Endpoints

### 🔐 Authentication

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new user | No |
| `/auth/login` | POST | Login user | No |
| `/auth/me` | GET | Get current user info | Yes |

### 💚 Health Data

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/health/entry` | POST | Add health entry | Yes |
| `/api/health/history` | GET | Get health history | Yes |
| `/api/health/latest` | GET | Get latest entry | Yes |
| `/api/health/statistics` | GET | Get user statistics | Yes |
| `/api/health/entry/{id}` | DELETE | Delete entry | Yes |

### 🔮 Predictions

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/predict` | GET | Get prediction (public) | No |
| `/api/health/predict` | GET | Get prediction (auth) | Yes |

### 👑 Admin

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/admin/users` | GET | List all users | Admin |
| `/api/admin/users/{id}` | DELETE | Delete user | Admin |
| `/api/admin/statistics` | GET | System statistics | Admin |

## 📖 Usage Examples

### Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123",
    "full_name": "Test Student"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "full_name": "Test Student",
    "is_admin": false
  }
}
```

### Add Health Entry

```bash
curl -X POST http://localhost:8000/api/health/entry \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-19",
    "sleepHours": 7.5,
    "calories": 2000,
    "steps": 8500,
    "waterIntake": 2.5,
    "screenTime": 3.0,
    "stressLevel": 4
  }'
```

Response:
```json
{
  "success": true,
  "wellnessScore": 78.5,
  "date": "2025-11-19",
  "recommendations": {
    "achievements": ["Great sleep!", "Good hydration!"],
    "recommendations": ["Try to reach 10,000 steps"],
    "warnings": []
  },
  "categories": {
    "Sleep": {"score": 90, "status": "Excellent"},
    "Activity": {"score": 75, "status": "Good"}
  }
}
```

### Get History

```bash
curl -X GET "http://localhost:8000/api/health/history?days=30&limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Prediction (Public)

```bash
curl "http://localhost:8000/api/predict?sleepHours=7.5&calories=2000&steps=8500&waterIntake=2.5&screenTime=3.0&stressLevel=4"
```

## 🎓 For Your College Project

### Frontend Integration

Your frontend should:

1. **Store JWT token** after login (localStorage or cookies)
2. **Include token** in all authenticated requests:
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`,
     'Content-Type': 'application/json'
   }
   ```
3. **Handle token expiry** (7 days) - redirect to login if 401 error
4. **Implement all pages**:
   - Login/Register pages
   - Dashboard (show statistics)
   - Add Health Data form
   - History view (table/cards)
   - Predictions page
   - Admin panel (if admin user)

### Example: React/Next.js Integration

```typescript
// api-client.ts
const API_BASE_URL = 'http://localhost:8000';

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  
  return data;
}

export async function addHealthEntry(entry: HealthEntry) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_BASE_URL}/api/health/entry`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(entry)
  });
  
  return response.json();
}

export async function getHistory(days = 30, limit = 100, offset = 0) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `${API_BASE_URL}/api/health/history?days=${days}&limit=${limit}&offset=${offset}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
}
```

## 🔒 Security Features

- ✅ **Password Hashing**: Bcrypt with 12 rounds
- ✅ **JWT Tokens**: 7-day expiry
- ✅ **User Isolation**: Each user sees only their data
- ✅ **Admin Protection**: Admin endpoints require admin role
- ✅ **SQL Injection Prevention**: Parameterized queries
- ✅ **CORS Enabled**: For frontend integration

## 🧪 Testing

### Using Interactive Docs

Visit http://localhost:8000/docs to:
1. See all endpoints
2. Test API calls
3. View request/response schemas
4. Try authentication flow

### Using Postman

1. Import OpenAPI spec from `/openapi.json`
2. Create environment with `base_url` = `http://localhost:8000`
3. Add `token` variable after login
4. Test all endpoints

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at TEXT,
    last_login TEXT
);
```

### Health Entries Table
```sql
CREATE TABLE health_entries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sleepHours REAL,
    calories REAL,
    steps INTEGER,
    waterIntake REAL,
    screenTime REAL,
    stressLevel INTEGER,
    wellnessScore REAL,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)
);
```

## 🤖 ML Model Details

- **Algorithm**: Gradient Boosting (XGBoost/LightGBM)
- **Features**: 6 health metrics
- **Output**: Wellness score (0-100)
- **Training**: Pre-trained on 10,000+ health records
- **Accuracy**: RMSE < 5 points

### Input Features:
1. Sleep Hours (0-12)
2. Calories (1000-4000)
3. Steps (0-30000)
4. Water Intake (0-5 liters)
5. Screen Time (0-24 hours)
6. Stress Level (1-10)

## 📝 Project Report Tips

### Key Points to Include:

1. **Architecture**: Explain REST API, JWT auth, SQLite database
2. **Security**: Describe password hashing, token management
3. **ML Integration**: How pre-trained model is used
4. **Database Design**: Foreign keys, unique constraints
5. **API Design**: RESTful principles, error handling

### Common Questions:

**Q: Why FastAPI?**
A: Automatic docs, async support, Pydantic validation, modern Python

**Q: Why SQLite?**
A: Lightweight, portable, no server needed for development

**Q: How does authentication work?**
A: JWT tokens with 7-day expiry, stored client-side

**Q: Can you retrain the model?**
A: No, model is pre-trained (training code not included)

## 🚀 Deployment

### Local Development
```bash
./start_backend.sh
```

### Production (Example with Gunicorn)
```bash
pip install gunicorn
gunicorn api.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🆘 Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Module not found
```bash
pip install -r requirements.txt
```

### Database locked
```bash
rm app/db/wellness_multiuser.db
# Restart server (auto-creates new DB)
```

## 📧 Support

For questions about the code:
1. Check `/docs` endpoint
2. Read code comments
3. Review this README
4. Check API responses for error messages

## 📄 License

Educational use only. Not for commercial purposes.

---

**Good luck with your project! 🎓**
