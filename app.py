from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import socket
import os
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)  # Explicitly load .env file

# Debug print to verify environment variable loading
print("DEBUG - SQLALCHEMY_DATABASE_URI:", os.getenv("SQLALCHEMY_DATABASE_URI"))

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration (FIXED: Using SQLALCHEMY_DATABASE_URI)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('"') and app.config['SQLALCHEMY_DATABASE_URI'].endswith('"'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'][1:-1]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)
# DB Table Model
class Game1(db.Model):
    __tablename__ = 'Game1'  # Match PostgreSQL table name (case-sensitive)
    userid = db.Column(db.Text, primary_key=True)
    highscore_p = db.Column(db.Integer, nullable=False)
    highscore_a = db.Column(db.Integer, nullable=False)
    highscore_gdp = db.Column(db.Integer, nullable=False)

    def __init__(self, userid, highscore_p, highscore_a, highscore_gdp):
        self.userid = userid
        self.highscore_p = highscore_p
        self.highscore_a = highscore_a
        self.highscore_gdp = highscore_gdp

    def to_dict(self):
        return {
            'userid': self.userid,
            'highscore_p': self.highscore_p,
            'highscore_a': self.highscore_a,
            'highscore_gdp': self.highscore_gdp
        }

# Get unique hostname as user ID
def get_hostname():
    return socket.gethostname()

# Home route
@app.route('/')
def home():
    return "Hello, Flask connected to PostgreSQL!"

# Get all data (for debugging or display)
@app.route('/data')
def get_data():
    try:
        all_data = Game1.query.all()
        return jsonify([user.to_dict() for user in all_data])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add test data (FOR DEVELOPMENT ONLY)
@app.route('/add')
def add_data():
    try:
        existing_user = Game1.query.filter_by(userid="user123").first()

        if existing_user:
            return jsonify({'error': 'User already exists!'}), 400  # Prevent duplicate insertion

        new_row = Game1(userid="user123", highscore_p=100, highscore_a=80, highscore_gdp=60)
        db.session.add(new_row)
        db.session.commit()
        
        return "New row added successfully!"
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Save or update score (POST request with JSON body)
@app.route('/save_score', methods=['GET', 'POST'])
def save_or_update_score():
    if request.method == 'GET':
        return "This route only accepts POST requests. Use a tool like Postman or Python to send data."
    try:
        data = request.get_json()
        highscore_p = data.get('highscore_p', 0)
        highscore_a = data.get('highscore_a', 0)
        highscore_gdp = data.get('highscore_gdp', 0)

        userid = get_hostname()
        user = Game1.query.filter_by(userid=userid).first()

        if user:
            user.highscore_p = max(user.highscore_p, highscore_p)
            user.highscore_a = max(user.highscore_a, highscore_a)
            user.highscore_gdp = max(user.highscore_gdp, highscore_gdp)
            message = "High scores updated!"
        else:
            new_user = Game1(
                userid=userid,
                highscore_p=highscore_p,
                highscore_a=highscore_a,
                highscore_gdp=highscore_gdp
            )
            db.session.add(new_user)
            message = "New user and scores added!"

        db.session.commit()
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist (for development/testing)
    app.run(debug=True)