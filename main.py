import requests

def get_location():
    try:
        # Getting IP address and location information
        response = requests.get('https://ipinfo.io')
        data = response.json()

        # Retrieving the data you need
        ip = data.get('ip')
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        loc = data.get('loc')  # Latitude and longitude

        # Displaying information
        print(f"IP: {ip}")
        print(f"Город: {city}")
        print(f"Регион: {region}")
        print(f"Страна: {country}")
        print(f"Координаты: {loc}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    get_location()