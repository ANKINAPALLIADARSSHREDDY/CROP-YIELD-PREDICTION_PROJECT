from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "*"}})

# Database Configuration (Using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_yield.db'  # Change this for MySQL or PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the database model
class CropYieldPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    soil_type = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    historical_yield = db.Column(db.Float, nullable=False)
    predicted_yield = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/predict', methods=['POST'])
def predict_yield():
    try:
        data = request.json

        # Validate required fields
        required_fields = ["location", "year", "cropType", "soilType", "temperature", "rainfall", "humidity", "historicalYield"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract and convert data safely
        location = data["location"]
        year = int(data["year"])
        crop_type = data["cropType"]
        soil_type = data["soilType"]
        temperature = float(data["temperature"])
        rainfall = float(data["rainfall"])
        humidity = float(data["humidity"])
        historical_yield = float(data["historicalYield"])

        # Simple yield prediction formula (replace with ML model)
        predicted_yield = round(historical_yield + (temperature * 0.5) + (rainfall * 0.3) - (humidity * 0.2), 2)

        # Save to Database
        new_prediction = CropYieldPrediction(
            location=location, year=year, crop_type=crop_type, soil_type=soil_type,
            temperature=temperature, rainfall=rainfall, humidity=humidity,
            historical_yield=historical_yield, predicted_yield=f"{predicted_yield} kg/ha"
        )
        db.session.add(new_prediction)
        db.session.commit()

        response = {
            "location": location,
            "year": year,
            "cropType": crop_type,
            "soilType": soil_type,
            "predictedYield": f"{predicted_yield} kg/ha"
        }

        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"error": f"Invalid data format: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
