import json,requests
from pathlib import Path
API_TIMEOUT = 10
HISTORY_FILE = Path("weather_history.json")
WEATHER_DIR = Path("weather_reports")

CITIES = {
    "1": {
        "name": "Bangalore",
        "latitude": 12.9716,
        "longitude": 77.5946,
    },
    "2": {
        "name": "Mysore",
        "latitude": 12.2958,
        "longitude": 76.6394,
    },
    "3": {
        "name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
    },
    "4": {
        "name": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
    },
}


def fetch_json(url, params=None):
    """Fetch JSON from a URL and handle common API errors."""
    try:
        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except requests.Timeout:
        print("The request timed out. Please try again.")

    except requests.HTTPError as error:
        status = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )
        print(f"The API returned an HTTP error: {status}")

    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")

    except ValueError:
        print("The API did not return valid JSON.")

    return None


def fetch_city_weather(city):
    """Fetch current weather for a supported city."""
    details = CITIES[city]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": details["latitude"],
        "longitude": details["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
    }

    payload = fetch_json(url, params)

    if not isinstance(payload, dict):
        return None

    current = payload.get("current")

    if not isinstance(current, dict):
        print("The weather response was missing expected data.")
        return None

    required = [
        "time",
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
    ]

    if any(key not in current for key in required):
        print("The weather response is incomplete.")
        return None

    units = payload.get("current_units", {})

    return {
        "city": details["name"],
        "time": current["time"],
        "temperature": current["temperature_2m"],
        "temperature_unit": units.get(
            "temperature_2m", "°C"
        ),
        "humidity": current["relative_humidity_2m"],
        "humidity_unit": units.get(
            "relative_humidity_2m", "%"
        ),
        "wind_speed": current["wind_speed_10m"],
        "wind_unit": units.get(
            "wind_speed_10m", "km/h"
        ),
        "source": "Open-Meteo",
    }


def fetch_custom_api():
    """Fetch and display JSON from a user-provided API URL."""
    url = input("Enter a public API URL: ").strip()

    if not url:
        print("URL cannot be empty.")
        return

    if not url.lower().startswith(("https://", "http://")):
        print("Enter a URL beginning with http:// or https://.")
        return

    payload = fetch_json(url)

    if payload is not None:
        print("\n========== CUSTOM API RESPONSE ==========")
        print(json.dumps(payload, indent=2, ensure_ascii=False))


def display_weather(weather):
    """Display a weather record."""
    print(f"\n========== {weather['city'].upper()} WEATHER ==========")

    print(f"Time        : {weather['time']}")
    print(
        f"Temperature : {weather['temperature']} "
        f"{weather['temperature_unit']}"
    )
    print(
        f"Humidity    : {weather['humidity']} "
        f"{weather['humidity_unit']}"
    )
    print(
        f"Wind speed  : {weather['wind_speed']} "
        f"{weather['wind_unit']}"
    )
    print(f"Source      : {weather['source']}\n")


def choose_city():
    """Ask the user to select a supported city."""
    while True:
        print("\nChoose a city:")

        for key, city in CITIES.items():
            print(f"{key}. {city['name']}")

        choice = input(
            "City (number or name, or 'back'): "
        ).strip().lower()

        if choice == "back":
            return None

        for key, city in CITIES.items():
            if (
                choice == key
                or choice == city["name"].lower()
            ):
                return key

        print("Invalid city. Choose one of the listed options.")


def safe_filename():
    """Get a filename without a directory path."""
    while True:
        name = input(
            "Enter a filename (without .txt): "
        ).strip()

        if not name or name in {".", ".."}:
            print("Filename cannot be empty.")
            continue

        if (
            any(char in name for char in '<>:"/\\|?*')
            or name.endswith(".")
        ):
            print("Enter a valid filename.")
            continue

        if name.lower().endswith(".txt"):
            name = name[:-4].strip()

        if not name:
            print("Filename cannot be empty.")
            continue

        return name


def format_weather(weather):
    """Convert a weather record into readable text."""
    return (
        f"City: {weather['city']}\n"
        f"Time: {weather['time']}\n"
        f"Temperature: {weather['temperature']} "
        f"{weather['temperature_unit']}\n"
        f"Humidity: {weather['humidity']} "
        f"{weather['humidity_unit']}\n"
        f"Wind speed: {weather['wind_speed']} "
        f"{weather['wind_unit']}\n"
        f"Source: {weather['source']}\n"
    )


def save_weather_text(weather, append=False):
    """Save a weather record to a text file."""
    WEATHER_DIR.mkdir(exist_ok=True)

    name = safe_filename()
    path = WEATHER_DIR / f"{name}.txt"

    if append and not path.is_file():
        print(f"{path} does not exist. Nothing was appended.")
        return None

    try:
        mode = "a" if append else "w"

        with path.open(mode, encoding="utf-8") as file:
            if append:
                file.write("\n")

            file.write(format_weather(weather))
            file.write("\n")

        print(f"Weather report saved to: {path}")
        return path

    except OSError as error:
        print(f"Could not write the file: {error}")
        return None


def save_history(history):
    """Save weather history as JSON."""
    try:
        with HISTORY_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                history,
                file,
                indent=2,
                ensure_ascii=False,
            )

    except OSError as error:
        print(f"Could not save history: {error}")


def load_history():
    """Load previously saved history."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            history = json.load(file)

        if isinstance(history, list):
            return history

        print("Unexpected history format. Starting with empty history.")

    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load saved history: {error}")

    return []


def view_history(history, selected_file):
    """Display in-memory history and selected file contents."""
    print("\n========== WEATHER HISTORY ==========")

    if history:
        for index, item in enumerate(history, start=1):
            print(f"\n--- Record {index} ---")
            print(format_weather(item))
    else:
        print("No weather history available.")

    if selected_file is None:
        print("\nNo text report is currently selected.")
        return

    try:
        if selected_file.exists():
            print(
                f"\n========== FILE CONTENT: "
                f"{selected_file} =========="
            )
            print(
                selected_file.read_text(encoding="utf-8")
            )
        else:
            print(
                f"\nSelected file no longer exists: "
                f"{selected_file}"
            )

    except OSError as error:
        print(f"Could not read the selected file: {error}")


def delete_history(history, selected_file):
    """Manage history and selected text report separately."""
    if history:
        answer = input(
            "Clear in-memory weather history? (yes/no): "
        ).strip().lower()

        if answer == "yes":
            history.clear()
            save_history(history)
            print("In-memory history cleared.")

    else:
        print("In-memory history is already empty.")

    if HISTORY_FILE.exists():
        answer = input(
            "Delete the saved JSON history file too? (yes/no): "
        ).strip().lower()

        if answer == "yes":
            try:
                HISTORY_FILE.unlink()
                print("Saved JSON history file deleted.")

            except OSError as error:
                print(f"Could not delete history file: {error}")

    if selected_file is None:
        print("No text report is currently selected.")
        return None

    if not selected_file.exists():
        print(f"{selected_file} no longer exists.")
        return None

    answer = input(
        f"Delete the contents of {selected_file}? (yes/no): "
    ).strip().lower()

    if answer == "yes":
        try:
            selected_file.write_text("", encoding="utf-8")
            print("File contents cleared.")

        except OSError as error:
            print(f"Could not clear the file: {error}")
            return selected_file

    answer = input(
        f"Delete the file {selected_file}? (yes/no): "
    ).strip().lower()

    if answer == "yes":
        try:
            selected_file.unlink()
            print("Text report deleted.")
            return None

        except OSError as error:
            print(f"Could not delete the file: {error}")

    return selected_file


def handle_weather_result(
    weather,
    history,
    selected_file,
):
    """Display, record, and optionally save weather."""
    display_weather(weather)

    history.append(weather)
    save_history(history)

    while True:
        choice = input(
            "Save to a new file, append to an existing file, "
            "or skip? (new/add/no): "
        ).strip().lower()

        if choice == "new":
            selected_file = save_weather_text(
                weather,
                append=False,
            )
            break

        elif choice == "add":
            selected_file = save_weather_text(
                weather,
                append=True,
            )
            break

        elif choice == "no":
            print("No text report saved.")
            break

        else:
            print("Enter new, add, or no.")

    return selected_file


def display_menu():
    """Display the main menu and return the user's choice."""
    print(
        "\n========== MINI WEATHER APP ==========\n"
        "1. Fetch data from a custom API URL\n"
        "2. Get weather for a supported city\n"
        "3. View weather history and selected text file\n"
        "4. Manage/delete history and selected text file\n"
        "5. Exit"
    )

    return input("Choose an option: ").strip()


def main():
    history = load_history()
    selected_file = None

    while True:
        choice = display_menu()

        if choice == "1":
            fetch_custom_api()

        elif choice == "2":
            city = choose_city()

            if city is None:
                continue

            weather = fetch_city_weather(city)

            if weather is not None:
                selected_file = handle_weather_result(
                    weather,
                    history,
                    selected_file,
                )

        elif choice == "3":
            view_history(history, selected_file)

        elif choice == "4":
            selected_file = delete_history(
                history,
                selected_file,
            )

        elif choice == "5":
            print("Weather history is saved. Thank you!")
            break

        else:
            print("Enter a valid option from 1 to 5.")

if __name__ == "__main__":
    main()