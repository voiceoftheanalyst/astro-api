from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from .calculator import AstrologyCalculator
import traceback

bp = Blueprint("api", __name__)

@bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Astrology API is running",
        "version": "1.0",
        "endpoints": {
            "/natal": "Calculate natal chart positions",
            "/transits": "Calculate current transits and aspects"
        }
    })

@bp.route("/natal", methods=["POST"])
def get_natal_chart():
    try:
        data = request.get_json()
        calculator = AstrologyCalculator()
        
        # Parse birth data
        birth_date = datetime.fromisoformat(data["birth_date"].replace("Z", "+00:00"))
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        
        # Calculate positions
        julian_day = calculator.get_julian_day(
            birth_date.year, birth_date.month, birth_date.day,
            birth_date.hour, birth_date.minute
        )
        positions, houses = calculator.get_planet_positions(julian_day, latitude, longitude)
        
        return jsonify({
            "success": True,
            "positions": positions,
            "houses": [float(h) for h in houses]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/transits", methods=["POST"])
def get_transits():
    try:
        data = request.get_json()
        calculator = AstrologyCalculator()
        
        # Get birth data for natal positions
        birth_date = datetime.fromisoformat(data["birth_date"].replace("Z", "+00:00"))
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        
        # Calculate natal positions
        natal_jd = calculator.get_julian_day(
            birth_date.year, birth_date.month, birth_date.day,
            birth_date.hour, birth_date.minute
        )
        natal_positions, _ = calculator.get_planet_positions(natal_jd, latitude, longitude)
        
        # Calculate current transits
        now = datetime.now(timezone.utc)
        current_jd = calculator.get_julian_day(
            now.year, now.month, now.day,
            now.hour, now.minute
        )
        transit_positions, _ = calculator.get_planet_positions(current_jd, latitude, longitude)
        
        # Calculate aspects
        aspects = calculator.calculate_aspects(transit_positions, natal_positions, transit_natal=True)
        
        return jsonify({
            "success": True,
            "natal_positions": natal_positions,
            "transit_positions": transit_positions,
            "aspects": aspects,
            "calculation_time": now.isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 400
