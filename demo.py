
from emotion_analyzer import EmotionAnalyzer
from response_engine import ResponseEngine

def run_demo():
    print("DEBUG: Starting demo script...", flush=True)
    print("Loading models for demonstration...", flush=True)
    analyzer = EmotionAnalyzer()
    
    # Probe sentences to find mapping
    probes = [
        ("I am terrified and having a panic attack.", "anxiety"),
        ("I am exhausted, sleepy and so tired.", "fatigue"),
        ("I am angry, annoyed and frustrated.", "frustration"),
        ("It is a book.", "neutral"),
        ("I am so happy and excited! This is great!", "positive")
    ]
    
    print("\nPROBING MODEL MAPPING:\n")
    for text, expected in probes:
        # We access the internal model to get raw ID since analyzer returns LABEL_X
        inputs = analyzer.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        import torch
        with torch.no_grad():
            outputs = analyzer.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred_id = torch.argmax(probs, dim=1).item()
        
        print(f"Text: '{text}'")
        print(f"Expected: {expected} -> Predicted ID: {pred_id} (LABEL_{pred_id})")
        print("-" * 30)

