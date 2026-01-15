
import random

class ResponseEngine:
    def __init__(self):
        # Define the empathy mapping
        self.response_map = {
            'fatigue': [
                "It sounds like you're exhausted. Remember, rest is just as important as the workout itself. Maybe take a lighter day?",
                "You've been working hard! Listen to your body and take a break if you need it.",
                "It's okay to feel tired. Recovery is where the progress happens."
            ],
            'frustration': [
                "I hear your frustration. Progress isn't always linear, but you are moving forward.",
                "Don't be too hard on yourself. Every effort counts, even when it doesn't feel like it.",
                "It's normal to feel stuck sometimes. Stick with it, you're doing great."
            ],
            'anxiety': [
                "I understand this can be overwhelming. Let's take it one step at a time.",
                "You're safe here. There's no pressure, just do what feels right for you today.",
                "Take a deep breath. Focus on how you feel, not the numbers."
            ],
            'positive': [
                "That's the spirit! Keep up that amazing energy!",
                "Love to hear it! You're crushing it!",
                "Fantastic! Your motivation is inspiring."
            ],
            'neutral': [
                "Got it. Ready for the next set?",
                "Okay, let's keep moving.",
                "Understood. What's next on your plan?"
            ]
        }
        
        self.disclaimer = (
            "\n[DISCLAIMER: I am an AI, not a healthcare professional. "
            "I cannot diagnose medical conditions or provide clinical advice. "
            "If you feel unwell, please stop and consult a professional.]"
        )

    def get_disclaimer(self):
        return self.disclaimer

    def generate_response(self, emotion):
        """
        Generate an empathetic response and an optional recommendation.
        Returns tuple: (text, recommendation_dict)
        """
        emotion = emotion.lower()
        text = "I'm listening. Tell me more about how you're feeling."
        recommendation = None

        if emotion in self.response_map:
            text = random.choice(self.response_map[emotion])

        # Dynamic Recommendations
        if emotion == 'fatigue':
            recommendation = {
                "type": "video",
                "title": "5 Minute Gentle Yoga for Fatigue",
                "url": "https://www.youtube.com/embed/sTANio_2E0Q" # Placeholder
            }
        elif emotion == 'anxiety':
            recommendation = {
                "type": "action",
                "title": "Box Breathing Exercise",
                "action": "Breathe In (4s) -> Hold (4s) -> Out (4s) -> Hold (4s)"
            }
        elif emotion == 'positive':
            recommendation = {
                "type": "video",
                "title": "High Energy HIIT Workout",
                "url": "https://www.youtube.com/embed/ml6cT4AZdqI" # Placeholder
            }
        elif emotion == 'frustration':
            recommendation = {
                "type": "video",
                "title": "Release Tension Meditation",
                "url": "https://www.youtube.com/embed/z6X5oEIg6Ak" # Placeholder
            }
            
        return text, recommendation

if __name__ == "__main__":
    engine = ResponseEngine()
    print(engine.get_disclaimer())
    print(f"Fatigue response: {engine.generate_response('fatigue')}")
