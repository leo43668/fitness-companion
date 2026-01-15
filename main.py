
import sys
import time
from emotion_analyzer import EmotionAnalyzer
from response_engine import ResponseEngine

def main():
    print("Initializing Empathetic Fitness Agent...")
    
    try:
        # Initialize components
        analyzer = EmotionAnalyzer()
        engine = ResponseEngine()
    except Exception as e:
        print(f"Failed to initialize components: {e}")
        sys.exit(1)
        
    print("\n" + "="*50)
    print("      FITNESS COMPANION BOT (EMOTION AWARE)")
    print("="*50)
    print(engine.get_disclaimer())
    print("\nI'm here to support your fitness journey. How are you feeling today?")
    print("(Type 'quit' or 'exit' to end the chat)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit']:
                print("\nBot: Keep moving forward! Goodbye!")
                break
            
            # 1. Detect Emotion
            emotion, confidence = analyzer.predict_emotion(user_input)
            
            # Debug info (optional, helpful for dissertation)
            # print(f"   [Debug: Detected '{emotion}' with confidence {confidence:.2f}]")
            
            # 2. Generate Response
            response = engine.generate_response(emotion)
            
            # 3. Output
            print(f"Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"\n[Error processing message: {e}]")

if __name__ == "__main__":
    main()
