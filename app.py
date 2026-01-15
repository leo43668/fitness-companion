
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from emotion_analyzer import EmotionAnalyzer
from response_engine import ResponseEngine
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_companion_v2.db' # Version 2 DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = None # Disable default message

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    fitness_goal = db.Column(db.String(50)) 
    workout_time = db.Column(db.String(20))
    streak_count = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, nullable=True)
    messages = db.relationship('Message', backref='user', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_bot = db.Column(db.Boolean, default=False)
    emotion = db.Column(db.String(20)) # Detected emotion
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# We use a global variable to load model once
analyzer = None
engine = None

# Initialize DB
with app.app_context():
    db.create_all()

def get_ai_components():
    global analyzer, engine
    if analyzer is None:
        try:
            print("Loading AI Models...")
            analyzer = EmotionAnalyzer()
            engine = ResponseEngine()
            print("AI Models Loaded.")
        except Exception as e:
            print(f"Error loading models: {e}")
            return None, None
    return analyzer, engine

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'signup':
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists. Please choose another.')
                return render_template('auth.html') # Stay on page to show error
            else:
                new_user = User(username=username, password_hash=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                flash('Account created successfully!')
                return redirect(url_for('profile')) # New users go to profile setup
        
        elif action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                # Streak Logic
                today = date.today()
                if user.last_login_date != today:
                    if user.last_login_date == today - timedelta(days=1):
                        user.streak_count += 1
                    else:
                        user.streak_count = 1
                    user.last_login_date = today
                    db.session.commit()
                
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please try again.')
                
    return render_template('auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.fitness_goal = request.form.get('fitness_goal')
        current_user.workout_time = request.form.get('workout_time')
        db.session.commit()
        flash('Profile updated!')
        return redirect(url_for('index'))
    return render_template('profile.html')

@app.route('/dashboard')
@login_required
def dashboard():
    #Get last 20 messages
    recent_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc()).limit(20).all()
    return render_template('dashboard.html', recent_messages=recent_messages)

@app.route('/api/analytics')
@login_required
def analytics():
    # Aggregate emotions
    messages = Message.query.filter_by(user_id=current_user.id, is_bot=False).all()
    emotion_counts = {}
    for msg in messages:
        if msg.emotion:
            emotion_counts[msg.emotion] = emotion_counts.get(msg.emotion, 0) + 1
    return jsonify(emotion_counts)

@app.route('/api/calendar')
@login_required
def calendar_data():
    
    messages = Message.query.filter_by(user_id=current_user.id, is_bot=False).order_by(Message.timestamp.asc()).all()
    calendar = {}
    for msg in messages:
        if msg.emotion and msg.timestamp:
            date_str = msg.timestamp.strftime('%Y-%m-%d')
            calendar[date_str] = msg.emotion
    return jsonify(calendar)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    analyzer, engine = get_ai_components()
    if not analyzer:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Save User Message
    db_msg_user = Message(user_id=current_user.id, content=user_message, is_bot=False)
    
    # AI Processing
    emotion, confidence = analyzer.predict_emotion(user_message)
    response_text, recommendation = engine.generate_response(emotion)
    
    # Contextualize response (Optional Logic)
    if current_user.fitness_goal == 'stress_relief' and emotion in ['fatigue', 'anxiety']:
         response_text += " Remember, your goal is stress relief, so take it easy."
    
    # Save Bot Message
    db_msg_user.emotion = emotion # Save emotion on user message
    db.session.add(db_msg_user)
    
    db_msg_bot = Message(user_id=current_user.id, content=response_text, is_bot=True)
    db.session.add(db_msg_bot)
    db.session.commit()

    disclaimer = engine.get_disclaimer()

    return jsonify({
        "response": response_text,
        "emotion": emotion,
        "confidence": confidence,
        "disclaimer": disclaimer,
        "recommendation": recommendation
    })

if __name__ == '__main__':
    # Pre-load models before starting server
    get_ai_components()
    app.run(debug=True, port=5000)
