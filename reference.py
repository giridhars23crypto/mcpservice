import os
import requests

def get_top_10_attractions(city_name: str) -> str:
    try:
        api_key = os.environ.get("GOOGLE_PLACES_API")
        if not api_key:
            raise ValueError("Google API key not found in environment variables.")

        endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query = f"tourist attractions in {city_name}"

        params = {
            "query": query,
            "key": api_key
        }

        response = requests.get(endpoint, params=params, timeout=10)
        data = response.json()

        if "results" not in data or not data["results"]:
            return "No results found."

        top_10 = data["results"][:10]
        output = "\n".join([f"{i+1}. {place['name']}" for i, place in enumerate(top_10)])
        return output

    except Exception:
        return "No results found."
