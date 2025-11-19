# 📚 API Documentation

Complete reference for all API endpoints.

## 🔗 Base URL

```
http://localhost:8000
```

## 🔐 Authentication

All authenticated endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

Get token from `/auth/login` or `/auth/register` response.

---

## 📋 Endpoints

### 🔐 Authentication Endpoints

#### 1. Register User

**Endpoint:** `POST /auth/register`

**Description:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

**Errors:**
- `400`: Email already registered
- `500`: Server error

---

#### 2. Login User

**Endpoint:** `POST /auth/login`

**Description:** Login existing user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

**Errors:**
- `401`: Invalid email or password
- `500`: Server error

---

#### 3. Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Get current user information

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_admin": false,
  "created_at": "2025-11-19T10:00:00",
  "last_login": "2025-11-19T15:30:00"
}
```

---

### 💚 Health Data Endpoints

#### 4. Add Health Entry

**Endpoint:** `POST /api/health/entry`

**Description:** Add new health entry and get wellness prediction

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "date": "2025-11-19",
  "sleepHours": 7.5,
  "calories": 2000,
  "steps": 8500,
  "waterIntake": 2.5,
  "screenTime": 3.0,
  "stressLevel": 4
}
```

**Field Descriptions:**
- `date`: Date in YYYY-MM-DD format (one entry per day)
- `sleepHours`: Hours of sleep (0-12)
- `calories`: Calorie intake (1000-4000)
- `steps`: Number of steps (0-30000)
- `waterIntake`: Water in liters (0-5)
- `screenTime`: Screen hours (0-24) [optional, default: 0]
- `stressLevel`: Stress level (1-10) [optional, default: 5]

**Response (200 OK):**
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
    "Activity": {"score": 75, "status": "Good"},
    "Hydration": {"score": 85, "status": "Great"},
    "Nutrition": {"score": 80, "status": "Good"}
  },
  "message": "Health entry saved successfully"
}
```

---

#### 5. Get Health History

**Endpoint:** `GET /api/health/history`

**Description:** Get user's health history

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `days` (optional, default: 30): Number of days to retrieve
- `limit` (optional): Maximum number of entries to return
- `offset` (optional, default: 0): Number of entries to skip (for pagination)

**Example:**
```
GET /api/health/history?days=30&limit=10&offset=0
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 2,
  "entries": [
    {
      "id": 1,
      "user_id": 1,
      "date": "2025-11-19",
      "sleepHours": 7.5,
      "calories": 2000,
      "steps": 8500,
      "waterIntake": 2.5,
      "screenTime": 3.0,
      "stressLevel": 4,
      "wellnessScore": 78.5,
      "created_at": "2025-11-19T10:00:00",
      "updated_at": "2025-11-19T10:00:00"
    },
    {
      "id": 2,
      "user_id": 1,
      "date": "2025-11-18",
      "sleepHours": 8.0,
      "calories": 2200,
      "steps": 10000,
      "waterIntake": 3.0,
      "screenTime": 2.0,
      "stressLevel": 3,
      "wellnessScore": 85.2,
      "created_at": "2025-11-18T09:00:00",
      "updated_at": "2025-11-18T09:00:00"
    }
  ]
}
```

---

#### 6. Get Latest Entry

**Endpoint:** `GET /api/health/latest`

**Description:** Get user's most recent health entry

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "entry": {
    "id": 1,
    "user_id": 1,
    "date": "2025-11-19",
    "sleepHours": 7.5,
    "calories": 2000,
    "steps": 8500,
    "waterIntake": 2.5,
    "wellnessScore": 78.5
  }
}
```

---

#### 7. Get User Statistics

**Endpoint:** `GET /api/health/statistics`

**Description:** Get aggregated health statistics

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `days` (optional, default: 30): Period for statistics

**Example:**
```
GET /api/health/statistics?days=30
```

**Response (200 OK):**
```json
{
  "success": true,
  "period_days": 30,
  "statistics": {
    "total_entries": 30,
    "average_wellness_score": 79.5,
    "averages": {
      "sleepHours": 7.2,
      "calories": 2100,
      "steps": 8500,
      "waterIntake": 2.3,
      "screenTime": 3.5,
      "stressLevel": 4.2
    },
    "trends": {
      "wellness_improving": true,
      "sleep_trend": "stable",
      "activity_trend": "increasing"
    }
  }
}
```

---

#### 8. Delete Health Entry

**Endpoint:** `DELETE /api/health/entry/{entry_id}`

**Description:** Delete specific health entry

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `entry_id`: ID of entry to delete

**Example:**
```
DELETE /api/health/entry/5
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Entry deleted successfully"
}
```

**Errors:**
- `404`: Entry not found or unauthorized
- `500`: Server error

---

### 🔮 Prediction Endpoints

#### 9. Get Prediction (Public)

**Endpoint:** `GET /api/predict`

**Description:** Get wellness prediction without saving (no auth required)

**Query Parameters:**
- `sleepHours` (required): Hours of sleep
- `calories` (required): Calorie intake
- `steps` (required): Number of steps
- `waterIntake` (required): Water in liters
- `screenTime` (optional, default: 0): Screen hours
- `stressLevel` (optional, default: 5): Stress level

**Example:**
```
GET /api/predict?sleepHours=7.5&calories=2000&steps=8500&waterIntake=2.5&screenTime=3.0&stressLevel=4
```

**Response (200 OK):**
```json
{
  "success": true,
  "wellnessScore": 78.5,
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

---

#### 10. Get Prediction (Authenticated)

**Endpoint:** `GET /api/health/predict`

**Description:** Same as public endpoint but requires authentication

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:** Same as public endpoint

**Response:** Same as public endpoint

---

### 👑 Admin Endpoints

#### 11. Get All Users

**Endpoint:** `GET /api/admin/users`

**Description:** List all users (admin only)

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 5,
  "users": [
    {
      "id": 1,
      "email": "admin@wellness.com",
      "full_name": "Admin User",
      "is_admin": true,
      "created_at": "2025-11-01T00:00:00",
      "last_login": "2025-11-19T15:00:00",
      "entry_count": 30
    },
    {
      "id": 2,
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_admin": false,
      "created_at": "2025-11-10T10:00:00",
      "last_login": "2025-11-19T14:00:00",
      "entry_count": 15
    }
  ]
}
```

**Errors:**
- `403`: Not admin user
- `500`: Server error

---

#### 12. Delete User

**Endpoint:** `DELETE /api/admin/users/{user_id}`

**Description:** Delete user account (admin only)

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Path Parameters:**
- `user_id`: ID of user to delete

**Example:**
```
DELETE /api/admin/users/5
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Errors:**
- `400`: Cannot delete own account
- `403`: Not admin user
- `404`: User not found
- `500`: Server error

---

#### 13. Get System Statistics

**Endpoint:** `GET /api/admin/statistics`

**Description:** Get system-wide statistics (admin only)

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "statistics": {
    "total_users": 50,
    "active_users_today": 25,
    "total_health_entries": 1500,
    "entries_today": 35,
    "average_wellness_score": 78.5,
    "admin_count": 2,
    "new_users_this_week": 8
  }
}
```

---

## 🔒 Error Responses

All endpoints may return these errors:

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Entry not found or unauthorized"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to save entry: <error message>"
}
```

---

## 📝 Data Validation

### Email Format
- Must be valid email format
- Example: `user@example.com`

### Password Requirements
- Minimum 6 characters (recommended: 8+)
- Use strong passwords in production

### Date Format
- Must be `YYYY-MM-DD`
- Example: `2025-11-19`

### Numeric Ranges
- `sleepHours`: 0-12
- `calories`: 1000-4000
- `steps`: 0-30000
- `waterIntake`: 0-5
- `screenTime`: 0-24
- `stressLevel`: 1-10

---

## 🔄 Rate Limiting

Currently no rate limiting. In production, implement:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## 📱 Frontend Integration Example

```typescript
// TypeScript/JavaScript example

const API_BASE = 'http://localhost:8000';

// Login and store token
async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/auth/login`, {
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

// Add health entry
async function addHealthEntry(entry: HealthEntry) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_BASE}/api/health/entry`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(entry)
  });
  
  return response.json();
}

// Get history with pagination
async function getHistory(days = 30, limit = 10, offset = 0) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `${API_BASE}/api/health/history?days=${days}&limit=${limit}&offset=${offset}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
}

// Get statistics
async function getStatistics(days = 30) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `${API_BASE}/api/health/statistics?days=${days}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
}

// Delete entry
async function deleteEntry(entryId: number) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `${API_BASE}/api/health/entry/${entryId}`,
    {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
}

// Admin: Get all users
async function getAllUsers() {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${API_BASE}/api/admin/users`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.json();
}

// Admin: Delete user
async function deleteUser(userId: number) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `${API_BASE}/api/admin/users/${userId}`,
    {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
}
```

---

## 🧪 Testing with cURL

See `README.md` for cURL examples.

---

## 📞 Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation where you can:
- Test all endpoints
- See request/response schemas
- Try authentication flow
- Download OpenAPI spec

---

**Happy coding! 🚀**
