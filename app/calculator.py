import pyswisseph as swe
import datetime
from datetime import datetime, timezone
import pandas as pd
import math

class AstrologyCalculator:
    def __init__(self):
        # Initialize Swiss Ephemeris with built-in ephemeris
        swe.set_ephe_path(None)
        
        self.zodiac_signs = [
            "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer",
            "♌ Leo", "♍ Virgo", "♎ Libra", "♏ Scorpio",
            "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
        ]
        
        self.planets = {
            0: "☉ Sun",
            1: "☽ Moon",
            2: "☿ Mercury",
            3: "♀ Venus",
            4: "♂ Mars",
            5: "♃ Jupiter",
            6: "♄ Saturn",
            7: "⛢ Uranus",
            8: "♆ Neptune",
            9: "♇ Pluto",
            -1: "☋ Black Lilith",
            -2: "☊ North Node",
            -3: "☋ South Node",
            -4: "⚷ Chiron"
        }

    def get_julian_day(self, year, month, day, hour=0, minute=0):
        """Convert date and time to Julian Day"""
        # Convert to UTC if needed
        return swe.julday(year, month, day, hour + minute/60.0)

    def decimal_degrees_to_dms(self, decimal_degrees):
        """Convert decimal degrees to degrees, minutes, seconds format"""
        degrees = int(decimal_degrees)
        decimal_minutes = (decimal_degrees - degrees) * 60
        minutes = int(decimal_minutes)
        seconds = int((decimal_minutes - minutes) * 60)
        return f"{degrees}°{minutes}'{seconds}\""

    def get_zodiac_sign(self, longitude):
        """Convert longitude to zodiac sign"""
        sign_num = int(longitude / 30)
        degree_in_sign = longitude % 30
        return f"{self.zodiac_signs[sign_num]} {int(degree_in_sign)}°"

    def is_retrograde(self, planet_num, jd):
        """Check if planet is retrograde"""
        try:
            speed = swe.calc_ut(jd, planet_num)[0][3]
            return speed < 0
        except:
            return False  # Some points don't have retrograde motion

    def get_planet_positions(self, julian_day, lat=0, lon=0):
        """Calculate positions for all bodies at a given time"""
        positions = {}
        
        # Calculate Ascendant and Descendant using Placidus houses
        houses = swe.houses(julian_day, lat, lon, b"P")  # Use Placidus to get accurate Ascendant
        ascendant = houses[0][0]  # Get Ascendant
        descendant = (ascendant + 180) % 360  # Calculate Descendant
        ascendant_sign = int(ascendant / 30)  # Get sign number (0-11)
        ascendant_degree = ascendant % 30  # Get degree within sign
        
        # Add Ascendant and Descendant to positions
        positions["Ascendant"] = {
            "zodiac_position": self.get_zodiac_sign(ascendant),
            "longitude": ascendant,
            "formatted_longitude": self.decimal_degrees_to_dms(ascendant),
            "latitude": "0°0'0\"",
            "house": 1,
            "retrograde": "",
            "ascendant_sign": self.zodiac_signs[ascendant_sign]
        }
        
        positions["Descendant"] = {
            "zodiac_position": self.get_zodiac_sign(descendant),
            "longitude": descendant,
            "formatted_longitude": self.decimal_degrees_to_dms(descendant),
            "latitude": "0°0'0\"",
            "house": 7,
            "retrograde": "",
            "ascendant_sign": self.zodiac_signs[ascendant_sign]
        }
        
        for body_num, body_name in self.planets.items():
            try:
                # Special calculations for different points
                if body_num == -1:  # Black Lilith
                    position = swe.calc_ut(julian_day, swe.MEAN_APOG)[0]
                elif body_num == -2:  # North Node
                    position = swe.calc_ut(julian_day, swe.MEAN_NODE)[0]
                elif body_num == -3:  # South Node
                    node_pos = swe.calc_ut(julian_day, swe.MEAN_NODE)[0]
                    position = [(node_pos[0] + 180) % 360, node_pos[1], node_pos[2]]
                elif body_num == -4:  # Chiron
                    position = swe.calc_ut(julian_day, swe.CHIRON)[0]
                else:
                    position = swe.calc_ut(julian_day, body_num)[0]
                
                zodiac_pos = self.get_zodiac_sign(position[0])
                retrograde = self.is_retrograde(body_num, julian_day)
                
                # Calculate house placement using Whole Sign system
                planet_sign = int(position[0] / 30)  # Get planet's sign number (0-11)
                planet_degree = position[0] % 30  # Get degree within sign
                
                # Calculate house number based on the difference between planet's sign and ascendant's sign
                # Add 1 to make houses 1-12 instead of 0-11
                house_num = ((planet_sign - ascendant_sign) % 12) + 1
                
                # If the planet is in the same sign as the Ascendant but at a lower degree,
                # it should be in the 12th house
                if planet_sign == ascendant_sign and planet_degree < ascendant_degree:
                    house_num = 12
                
                positions[body_name] = {
                    "zodiac_position": zodiac_pos,
                    "longitude": position[0],
                    "formatted_longitude": self.decimal_degrees_to_dms(position[0]),
                    "latitude": self.decimal_degrees_to_dms(position[1]),
                    "house": house_num,
                    "retrograde": "℞" if retrograde else "",
                    "ascendant_sign": self.zodiac_signs[ascendant_sign]
                }
            except Exception as e:
                print(f"Could not calculate position for {body_name}: {e}")
        
        return positions, [ascendant]  # Return positions and Ascendant for reference

    def calculate_aspects(self, positions1, positions2=None, transit_natal=False):
        """Calculate aspects between two sets of positions (or within one set)"""
        aspects = []
        aspect_types = {
            0: "Conjunction ☌",
            60: "Sextile ⚹",
            90: "Square □",
            120: "Trine △",
            180: "Opposition ☍"
        }
        # Different orbs for transit-natal vs transit-transit aspects
        orb = 1 if transit_natal else 8
        
        if positions2 is None:
            positions2 = positions1
        
        for body1, data1 in positions1.items():
            for body2, data2 in positions2.items():
                if body1 != body2:  # Avoid comparing a body to itself
                    pos1 = data1["longitude"]
                    pos2 = data2["longitude"]
                    
                    angle = abs(pos1 - pos2)
                    if angle > 180:
                        angle = 360 - angle
                    
                    for aspect_angle, aspect_name in aspect_types.items():
                        if abs(angle - aspect_angle) <= orb:
                            if transit_natal:
                                aspects.append(f"Transit {body1} {aspect_name} Natal {body2}")
                            else:
                                aspects.append(f"{body1} {aspect_name} {body2}")
        
        return aspects
