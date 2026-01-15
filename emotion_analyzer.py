
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import os

class EmotionAnalyzer:
    def __init__(self, model_path="./roberta_model"):
        """
        Initialize the model and tokenizer.
        """
        print(f"DEBUG: EmotionAnalyzer Init with path {model_path}", flush=True)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model directory not found at {model_path}. Please ensure 'roberta_model.zip' is unzipped.")
        
        print(f"Loading model from {model_path}...")
        try:
            self.tokenizer = RobertaTokenizer.from_pretrained(model_path)
            self.model = RobertaForSequenceClassification.from_pretrained(model_path)
            self.model.eval()  # Set to evaluation mode
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def predict_emotion(self, text):
        """
        Predict the emotion from the input text.
        Returns a tuple: (predicted_label, confidence_score)
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get the predicted class index
        predicted_class_id = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class_id].item()
        
        # Explicit mapping based on probe results
        id_to_emotion = {
            0: 'anxiety',
            1: 'fatigue',
            2: 'frustration',
            3: 'neutral',
            4: 'positive'
        }
        
        predicted_label = id_to_emotion.get(predicted_class_id, "unknown")
        
        return predicted_label, confidence

if __name__ == "__main__":
    # Simple test
    try:
        analyzer = EmotionAnalyzer()
        test_text = "I am so tired of this workout."
        emotion, conf = analyzer.predict_emotion(test_text)
        print(f"Text: '{test_text}'")
        print(f"Predicted Emotion: {emotion} ({conf:.2f})")
    except Exception as e:
        print(f"Test failed: {e}")
