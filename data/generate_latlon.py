import csv
import time
import requests
import os

INPUT_FILE = "data/Study_fields_data.csv"
OUTPUT_FILE = "data/Study_fields_with_latlon.csv"

def geocode(institution, city, country):
    query = f"{institution}, {city}, {country}"

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "flask-university-map-app"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        if data:
            return data[0]["lat"], data[0]["lon"]

    except Exception as e:
        print(f"Error geocoding {query}: {e}")

    return None, None


def main():
    results = []

    with open(INPUT_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            institution = row["Institution"]
            city = row["City"]
            country = row["Country"]

            print(f"Geocoding ({i+1}): {institution}")

            lat, lon = geocode(institution, city, country)

            row["Latitude"] = lat
            row["Longitude"] = lon

            results.append(row)

            # IMPORTANT: avoid hitting API rate limit
            time.sleep(1)

    # write output CSV
    fieldnames = list(results[0].keys())

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\nDone!")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()