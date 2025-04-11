# Astrology API

A RESTful API for calculating astrological charts using Swiss Ephemeris. This API provides endpoints for calculating natal charts, transits, and aspects.

## Features

- Calculate natal charts with planetary positions
- Calculate transits for any date
- Support for major planets, nodes, and Chiron
- Whole Sign house system
- Aspect calculations between planets
- Beautiful Unicode symbols for astrological glyphs

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/astro-api.git
cd astro-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
gunicorn "app:app" --bind 127.0.0.1:5000
```

## API Endpoints

### Natal Chart
```
POST /natal
```
Request body:
```json
{
    "birth_date": "1983-10-25",
    "birth_time": "06:19",
    "birth_place": {
        "latitude": 42.4584,
        "longitude": -71.0662,
        "timezone": "America/New_York"
    }
}
```

### Transits
```
POST /transits
```
Request body:
```json
{
    "birth_data": {
        "birth_date": "1983-10-25",
        "birth_time": "06:19",
        "birth_place": {
            "latitude": 42.4584,
            "longitude": -71.0662,
            "timezone": "America/New_York"
        }
    },
    "transit_date": "2024-04-11"
}
```

## Notes

- The API uses the Swiss Ephemeris package (`pyswisseph`) for calculations
- Ephemeris files are included with the package - no additional setup needed
- All calculations use the Whole Sign house system
- Timezone handling is automatic based on the provided location

## Development

To run tests:
```bash
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details
