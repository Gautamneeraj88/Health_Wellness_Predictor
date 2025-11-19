"""
Health Recommendation Engine
Generates personalized recommendations based on wellness metrics
"""

from typing import Dict, List, Tuple
import pandas as pd


class RecommendationEngine:
    """Generate personalized health recommendations"""
    
    def __init__(self):
        self.recommendations = []
        self.warnings = []
        self.achievements = []
    
    def generate_recommendations(self, metrics: Dict) -> Dict[str, List[str]]:
        """
        Generate comprehensive recommendations based on health metrics
        
        Args:
            metrics: Dictionary containing health data
        
        Returns:
            Dictionary with recommendations, warnings, and achievements
        """
        self.recommendations = []
        self.warnings = []
        self.achievements = []
        
        # Analyze each health metric
        self._analyze_sleep(metrics.get('sleepHours', 0))
        self._analyze_activity(metrics.get('steps', 0))
        self._analyze_hydration(metrics.get('waterIntake', 0))
        self._analyze_nutrition(metrics.get('calories', 0))
        self._analyze_screen_time(metrics.get('screenTime', 0))
        self._analyze_stress(metrics.get('stressLevel', 0))
        
        return {
            'recommendations': self.recommendations,
            'warnings': self.warnings,
            'achievements': self.achievements
        }
    
    def _analyze_sleep(self, hours: float):
        """Analyze sleep patterns"""
        if hours < 6:
            self.warnings.append("⚠️ Insufficient sleep detected")
            self.recommendations.append("🛏️ Aim for 7-9 hours of sleep per night")
            self.recommendations.append("💡 Establish a consistent bedtime routine")
            self.recommendations.append("📱 Avoid screens 1 hour before bed")
        elif 6 <= hours < 7:
            self.recommendations.append("🛏️ Try to get an extra hour of sleep")
            self.recommendations.append("💤 Quality sleep improves overall wellness")
        elif 7 <= hours <= 9:
            self.achievements.append("✅ Excellent sleep duration!")
        elif 9 < hours <= 10:
            self.recommendations.append("💭 Ensure your sleep quality is good")
        else:
            self.warnings.append("⚠️ Excessive sleep may indicate health issues")
            self.recommendations.append("🏥 Consider consulting a healthcare professional")
    
    def _analyze_activity(self, steps: int):
        """Analyze physical activity levels"""
        if steps < 4000:
            self.warnings.append("⚠️ Very low physical activity")
            self.recommendations.append("🚶 Start with a 10-minute walk daily")
            self.recommendations.append("💪 Gradually increase to 8000-10000 steps")
            self.recommendations.append("🎯 Set small, achievable daily goals")
        elif 4000 <= steps < 6000:
            self.recommendations.append("👟 You're on the right track! Aim for 8000+ steps")
            self.recommendations.append("🏃 Try taking stairs instead of elevators")
        elif 6000 <= steps < 8000:
            self.recommendations.append("💪 Great progress! Push for 8000 steps")
        elif 8000 <= steps <= 12000:
            self.achievements.append("✅ Excellent activity level!")
        elif steps > 15000:
            self.achievements.append("🏆 Outstanding activity! You're very active!")
            self.recommendations.append("🧘 Don't forget to rest and recover")
    
    def _analyze_hydration(self, liters: float):
        """Analyze water intake"""
        if liters < 1.5:
            self.warnings.append("⚠️ Low hydration level")
            self.recommendations.append("💧 Drink at least 2-3 liters of water daily")
            self.recommendations.append("⏰ Set hourly reminders to drink water")
            self.recommendations.append("🥤 Keep a water bottle with you")
        elif 1.5 <= liters < 2:
            self.recommendations.append("💧 Increase water intake to 2-3 liters")
        elif 2 <= liters <= 3:
            self.achievements.append("✅ Perfect hydration!")
        elif liters > 3.5:
            self.recommendations.append("💭 Ensure you're not overhydrating")
    
    def _analyze_nutrition(self, calories: int):
        """Analyze calorie intake"""
        if calories < 1200:
            self.warnings.append("⚠️ Very low calorie intake")
            self.recommendations.append("🍎 Ensure adequate nutrition (1500-2500 cal)")
            self.recommendations.append("🥗 Focus on nutrient-dense foods")
        elif 1200 <= calories < 1500:
            self.recommendations.append("🍽️ Consider increasing calorie intake slightly")
        elif 1800 <= calories <= 2500:
            self.achievements.append("✅ Balanced calorie intake!")
        elif 2500 < calories <= 3000:
            self.recommendations.append("⚖️ Monitor your calorie intake")
            self.recommendations.append("🏃 Ensure adequate physical activity")
        elif calories > 3000:
            self.warnings.append("⚠️ High calorie intake detected")
            self.recommendations.append("🥗 Focus on portion control")
            self.recommendations.append("💪 Increase physical activity")
    
    def _analyze_screen_time(self, hours: float):
        """Analyze screen time"""
        if hours > 6:
            self.warnings.append("⚠️ Excessive screen time")
            self.recommendations.append("📱 Reduce screen time to under 4 hours")
            self.recommendations.append("👀 Take 20-20-20 breaks (every 20 min, look 20 ft away for 20 sec)")
            self.recommendations.append("🌳 Spend more time outdoors")
        elif 4 < hours <= 6:
            self.recommendations.append("📱 Try to reduce screen time further")
            self.recommendations.append("📚 Replace screen time with reading or hobbies")
        elif 2 < hours <= 4:
            self.recommendations.append("👍 Good screen time management")
        elif hours <= 2:
            self.achievements.append("✅ Excellent screen time control!")
    
    def _analyze_stress(self, level: int):
        """Analyze stress levels"""
        if level >= 8:
            self.warnings.append("⚠️ Very high stress levels")
            self.recommendations.append("🧘 Practice daily meditation or deep breathing")
            self.recommendations.append("💆 Consider stress management techniques")
            self.recommendations.append("👥 Talk to friends, family, or a professional")
            self.recommendations.append("🎯 Identify and address stress sources")
        elif 6 <= level < 8:
            self.warnings.append("⚠️ Elevated stress levels")
            self.recommendations.append("🧘 Try relaxation techniques")
            self.recommendations.append("🚶 Take short breaks throughout the day")
        elif 4 <= level < 6:
            self.recommendations.append("😌 Practice stress reduction techniques")
            self.recommendations.append("🎨 Engage in hobbies you enjoy")
        elif level <= 3:
            self.achievements.append("✅ Great stress management!")
    
    def get_priority_recommendations(self, metrics: Dict, limit: int = 5) -> List[str]:
        """Get top priority recommendations"""
        result = self.generate_recommendations(metrics)
        
        # Prioritize warnings and recommendations
        priority_items = []
        priority_items.extend(result['warnings'])
        priority_items.extend(result['recommendations'][:limit - len(result['warnings'])])
        
        return priority_items[:limit]
    
    def get_wellness_category_scores(self, metrics: Dict) -> Dict[str, Dict]:
        """
        Calculate category-wise wellness scores
        
        Returns:
            Dictionary with category scores and status
        """
        categories = {}
        
        # Sleep score
        sleep = metrics.get('sleepHours', 0)
        if 7 <= sleep <= 9:
            categories['Sleep'] = {'score': 100, 'status': 'Excellent', 'emoji': '😴'}
        elif 6 <= sleep < 7 or 9 < sleep <= 10:
            categories['Sleep'] = {'score': 75, 'status': 'Good', 'emoji': '😊'}
        elif 5 <= sleep < 6 or 10 < sleep <= 11:
            categories['Sleep'] = {'score': 50, 'status': 'Fair', 'emoji': '😐'}
        else:
            categories['Sleep'] = {'score': 25, 'status': 'Poor', 'emoji': '😟'}
        
        # Activity score
        steps = metrics.get('steps', 0)
        if 8000 <= steps <= 12000:
            categories['Activity'] = {'score': 100, 'status': 'Excellent', 'emoji': '🏃'}
        elif 6000 <= steps < 8000 or 12000 < steps <= 15000:
            categories['Activity'] = {'score': 75, 'status': 'Good', 'emoji': '🚶'}
        elif 4000 <= steps < 6000:
            categories['Activity'] = {'score': 50, 'status': 'Fair', 'emoji': '😐'}
        else:
            categories['Activity'] = {'score': 25, 'status': 'Poor', 'emoji': '😟'}
        
        # Hydration score
        water = metrics.get('waterIntake', 0)
        if 2 <= water <= 3:
            categories['Hydration'] = {'score': 100, 'status': 'Excellent', 'emoji': '💧'}
        elif 1.5 <= water < 2 or 3 < water <= 3.5:
            categories['Hydration'] = {'score': 75, 'status': 'Good', 'emoji': '💦'}
        elif 1 <= water < 1.5:
            categories['Hydration'] = {'score': 50, 'status': 'Fair', 'emoji': '😐'}
        else:
            categories['Hydration'] = {'score': 25, 'status': 'Poor', 'emoji': '😟'}
        
        # Nutrition score
        calories = metrics.get('calories', 0)
        if 1800 <= calories <= 2500:
            categories['Nutrition'] = {'score': 100, 'status': 'Excellent', 'emoji': '🥗'}
        elif 1500 <= calories < 1800 or 2500 < calories <= 3000:
            categories['Nutrition'] = {'score': 75, 'status': 'Good', 'emoji': '🍎'}
        elif 1200 <= calories < 1500:
            categories['Nutrition'] = {'score': 50, 'status': 'Fair', 'emoji': '😐'}
        else:
            categories['Nutrition'] = {'score': 25, 'status': 'Poor', 'emoji': '😟'}
        
        # Stress score
        stress = metrics.get('stressLevel', 0)
        if 1 <= stress <= 3:
            categories['Stress'] = {'score': 100, 'status': 'Excellent', 'emoji': '😌'}
        elif 4 <= stress <= 5:
            categories['Stress'] = {'score': 75, 'status': 'Good', 'emoji': '😊'}
        elif 6 <= stress <= 7:
            categories['Stress'] = {'score': 50, 'status': 'Fair', 'emoji': '😐'}
        else:
            categories['Stress'] = {'score': 25, 'status': 'Poor', 'emoji': '😰'}
        
        return categories


def get_recommendations(metrics: Dict) -> Dict[str, List[str]]:
    """
    Convenient function to get recommendations
    
    Args:
        metrics: Health metrics dictionary
    
    Returns:
        Dictionary with recommendations, warnings, and achievements
    """
    engine = RecommendationEngine()
    return engine.generate_recommendations(metrics)


def get_category_scores(metrics: Dict) -> Dict[str, Dict]:
    """Get wellness category scores"""
    engine = RecommendationEngine()
    return engine.get_wellness_category_scores(metrics)


if __name__ == "__main__":
    # Test the recommendation engine
    print("Testing Recommendation Engine...\n")
    
    sample_metrics = {
        'sleepHours': 6.5,
        'calories': 2200,
        'steps': 5500,
        'waterIntake': 1.8,
        'screenTime': 5,
        'stressLevel': 6
    }
    
    result = get_recommendations(sample_metrics)
    
    print("🎯 RECOMMENDATIONS:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    print("\n⚠️  WARNINGS:")
    for warn in result['warnings']:
        print(f"  {warn}")
    
    print("\n✅ ACHIEVEMENTS:")
    for ach in result['achievements']:
        print(f"  {ach}")
    
    print("\n📊 CATEGORY SCORES:")
    categories = get_category_scores(sample_metrics)
    for category, data in categories.items():
        print(f"  {category:12s}: {data['score']:3d}/100 - {data['status']} {data['emoji']}")
