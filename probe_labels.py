
from emotion_analyzer import EmotionAnalyzer
import torch

analyzer = EmotionAnalyzer()
labels = ["anxiety", "fatigue", "frustration", "neutral", "positive"]
sentences = [
    "I am terrified and having a panic attack.", # Anxiety
    "I am exhausted, sleepy and so tired.",      # Fatigue
    "I am angry, annoyed and frustrated.",       # Frustration
    "It is a book.",                             # Neutral
    "I am so happy and excited! This is great!"  # Positive
]

print("\n--- PROBE RESULTS ---")
for text in sentences:
    inputs = analyzer.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = analyzer.model(**inputs)
    pred_id = torch.argmax(outputs.logits, dim=1).item()
    print(f"Text: '{text[:20]}...' -> Header ID: {pred_id}")
print("--- END PROBE ---")
