from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import socket

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://avnadmin:AVNS_Pqg0EaCm9QeHSPH5o1j@pg-3983cda9-gamedata.k.aivencloud.com:28641/defaultdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Initialize SQLAlchemy with Flask

# DB Table
class Game1(db.Model):
    __tablename__ = 'Game1'  # Make sure this matches your PostgreSQL table name exactly (case-sensitive)
    userid = db.Column(db.Text, primary_key=True)
    highscore_p = db.Column(db.Integer, nullable=False)
    highscore_a = db.Column(db.Integer, nullable=False)
    highscore_gdp = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Game1 userid={self.userid}, highscore_p={self.highscore_p}, highscore_a={self.highscore_a}, highscore_gdp={self.highscore_gdp}>"

# Function to get the current hostname
def get_hostname():
    return socket.gethostname()  # Gets the unique hostname of the user's PC

# Home route
@app.route('/')
def home():
    return "Hello, Flask connected to PostgreSQL!"

# Display data route
@app.route('/data')
def get_data():
    all_data = Game1.query.all()  # Fetch all rows from the Game1 table
    return render_template('data.html', data=all_data)  # Pass data to the HTML template

# Insert sample data route (optional for testing purposes)
@app.route('/add')
def add_data():
    new_row = Game1(userid="user123", highscore_p=100, highscore_a=80, highscore_gdp=60)  # Replace values as needed
    db.session.add(new_row)
    db.session.commit()
    return "New row added successfully!"

# Save or update score route
@app.route('/save_score/<int:highscore_p>/<int:highscore_a>/<int:highscore_gdp>', methods=['POST'])
def save_or_update_score(highscore_p, highscore_a, highscore_gdp):
    print(f"Request received: highscore_p={highscore_p}, highscore_a={highscore_a}, highscore_gdp={highscore_gdp}")
    userid = get_hostname()  # Use the hostname as the unique user ID
    user = Game1.query.filter_by(userid=userid).first()  # Check if user already exists in the table

    if user:
        # Update scores if the new ones are higher
        user.highscore_p = max(user.highscore_p, highscore_p)
        user.highscore_a = max(user.highscore_a, highscore_a)
        user.highscore_gdp = max(user.highscore_gdp, highscore_gdp)
        message = "High scores updated!"
    else:
        # Add a new entry if the user does not exist
        new_user = Game1(userid=userid, highscore_p=highscore_p, highscore_a=highscore_a, highscore_gdp=highscore_gdp)
        db.session.add(new_user)
        message = "New user and scores added!"

    db.session.commit()  # Save changes to the database
    return message

# Main block to start the Flask app
if __name__ == '__main__':
    app.run(debug=True)