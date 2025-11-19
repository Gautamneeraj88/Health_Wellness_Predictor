from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import DatabaseManager
from api.auth import AuthManager
from app.utils.predict import predict_wellness_score
from app.utils.recommend import get_recommendations, get_category_scores

# Initialize FastAPI app
app = FastAPI(
    title="Health & Wellness Predictor API",
    description="Backend API for health tracking and wellness predictions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db = DatabaseManager()
auth_manager = AuthManager()
security = HTTPBearer()

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class HealthEntry(BaseModel):
    date: str
    sleepHours: float
    calories: float
    steps: int
    waterIntake: float
    screenTime: float = 0
    stressLevel: int = 5

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user"""
    token = credentials.credentials
    user_data = auth_manager.verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.get_user_by_id(user_data['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Dependency for admin authentication
async def get_admin_user(current_user = Depends(get_current_user)):
    """Verify user is admin"""
    if not current_user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Root endpoint
@app.get("/")
async def root():
    """API status"""
    return {
        "status": "online",
        "message": "Health & Wellness Predictor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register")
async def register(user: UserRegister):
    """Register new user"""
    try:
        # Check if user exists
        existing = db.get_user_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = auth_manager.hash_password(user.password)
        
        # Create user
        user_id = db.create_user(
            email=user.email,
            password_hash=password_hash,
            full_name=user.full_name
        )
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate token
        token = auth_manager.create_token(user_id)
        
        # Get user data
        user_data = db.get_user_by_id(user_id)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": user_data['id'],
                "email": user_data['email'],
                "full_name": user_data['full_name'],
                "is_admin": user_data['is_admin']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    try:
        # Get user
        user = db.get_user_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_manager.verify_password(credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Generate token
        token = auth_manager.create_token(user['id'])
        
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "is_admin": user['is_admin']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user['id'],
        "email": current_user['email'],
        "full_name": current_user['full_name'],
        "is_admin": current_user['is_admin'],
        "created_at": current_user.get('created_at'),
        "last_login": current_user.get('last_login')
    }

# ============================================================================
# HEALTH DATA ENDPOINTS
# ============================================================================

@app.post("/api/health/entry")
async def add_health_entry(entry: HealthEntry, current_user = Depends(get_current_user)):
    """Add health entry and get wellness prediction"""
    try:
        # Prepare input for prediction
        input_data = {
            'sleepHours': entry.sleepHours,
            'calories': entry.calories,
            'steps': entry.steps,
            'waterIntake': entry.waterIntake,
            'screenTime': entry.screenTime,
            'stressLevel': entry.stressLevel
        }
        
        # Predict wellness score
        wellness_score = predict_wellness_score(input_data)
        
        # Get recommendations
        recommendations = get_recommendations(input_data)
        categories = get_category_scores(input_data)
        
        # Save to database
        db.add_health_entry(
            user_id=current_user['id'],
            date=entry.date,
            sleep_hours=entry.sleepHours,
            calories=entry.calories,
            steps=entry.steps,
            water_intake=entry.waterIntake,
            screen_time=entry.screenTime,
            stress_level=entry.stressLevel,
            wellness_score=wellness_score
        )
        
        return {
            "success": True,
            "wellnessScore": round(wellness_score, 2),
            "date": entry.date,
            "recommendations": recommendations,
            "categories": categories,
            "message": "Health entry saved successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save entry: {str(e)}"
        )

@app.get("/api/health/history")
async def get_health_history(
    days: int = 30,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    current_user = Depends(get_current_user)
):
    """Get health history"""
    try:
        history = db.get_user_health_history(current_user['id'], days=days)
        
        # Apply pagination if limit is provided
        if limit is not None:
            history = history[offset:offset+limit]
        
        return {
            "success": True,
            "entries": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@app.get("/api/health/latest")
async def get_latest_entry(current_user = Depends(get_current_user)):
    """Get latest health entry"""
    try:
        entry = db.get_latest_entry(current_user['id'])
        if not entry:
            return {"success": True, "entry": None, "message": "No entries found"}
        
        return {"success": True, "entry": entry}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entry: {str(e)}"
        )

@app.get("/api/health/statistics")
async def get_statistics(
    days: int = 30,
    current_user = Depends(get_current_user)
):
    """Get health statistics"""
    try:
        stats = db.get_user_statistics(current_user['id'], days=days)
        return {
            "success": True,
            "statistics": stats,
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@app.delete("/api/health/entry/{entry_id}")
async def delete_entry(entry_id: int, current_user = Depends(get_current_user)):
    """Delete health entry"""
    try:
        success = db.delete_health_entry(entry_id, current_user['id'])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found or unauthorized"
            )
        
        return {
            "success": True,
            "message": "Entry deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete entry: {str(e)}"
        )

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.get("/api/health/predict")
async def predict_wellness_authenticated(
    sleepHours: float,
    calories: float,
    steps: int,
    waterIntake: float,
    screenTime: float = 0,
    stressLevel: int = 5,
    current_user = Depends(get_current_user)
):
    """Get wellness prediction without saving (authenticated)"""
    try:
        input_data = {
            'sleepHours': sleepHours,
            'calories': calories,
            'steps': steps,
            'waterIntake': waterIntake,
            'screenTime': screenTime,
            'stressLevel': stressLevel
        }
        
        wellness_score = predict_wellness_score(input_data)
        recommendations = get_recommendations(input_data)
        categories = get_category_scores(input_data)
        
        return {
            "success": True,
            "wellnessScore": round(wellness_score, 2),
            "recommendations": recommendations,
            "categories": categories
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/api/predict")
async def predict_wellness_public(
    sleepHours: float,
    calories: float,
    steps: int,
    waterIntake: float,
    screenTime: float = 0,
    stressLevel: int = 5
):
    """Get wellness prediction without authentication (public endpoint)"""
    try:
        input_data = {
            'sleepHours': sleepHours,
            'calories': calories,
            'steps': steps,
            'waterIntake': waterIntake,
            'screenTime': screenTime,
            'stressLevel': stressLevel
        }
        
        wellness_score = predict_wellness_score(input_data)
        recommendations = get_recommendations(input_data)
        categories = get_category_scores(input_data)
        
        return {
            "success": True,
            "wellnessScore": round(wellness_score, 2),
            "recommendations": recommendations,
            "categories": categories
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_all_users(admin_user = Depends(get_admin_user)):
    """Get all users (admin only)"""
    try:
        users = db.get_all_users()
        return {
            "success": True,
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, admin_user = Depends(get_admin_user)):
    """Delete user (admin only)"""
    try:
        # Prevent admin from deleting themselves
        if user_id == admin_user['id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = db.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@app.get("/api/admin/statistics")
async def get_admin_statistics(admin_user = Depends(get_admin_user)):
    """Get system statistics (admin only)"""
    try:
        stats = db.get_system_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("✓ Multi-user database initialized:", db.db_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
