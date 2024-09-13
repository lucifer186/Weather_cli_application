import mysql.connector
from mysql.connector import Error
import bcrypt
import requests

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='weather',
            user='sss_assignment_sep24',
            password='doitnow'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                print("User already registered with this username.")
            else:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
                connection.commit()
                print("User registered successfully.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
                print("Login successful.")
                return result[0]
            else:
                print("Invalid username or password.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()
    return None


def fetch_weather(location):
    api_key = ''
    base_url=   f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}'
    
    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200:
            weather_data = {
                "location": data['name'],
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "weather_condition": data['weather'][0]['description'],
                "wind_speed": data['wind']['speed']
            }
            return weather_data
        else:
            print("Unable to show weather data. Please provide right location ")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


def store_search_history(user_id, weather_data):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO search_history (user_id, location, temperature, humidity, weather_condition, wind_speed) "
                "VALUES (%s, %s, %s, %s, %s, %s)", 
                (user_id, weather_data['location'], weather_data['temperature'], weather_data['humidity'], 
                 weather_data['weather_condition'], weather_data['wind_speed'])
            )
            connection.commit()
            print("Search history stored.")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

def view_search_history(user_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT location, temperature, humidity, weather_condition, wind_speed, search_timestamp FROM search_history WHERE user_id = %s", (user_id,))
            rows = cursor.fetchall()
            for row in rows:
                print(f"Date:{row[5]}, Location: {row[0]}, temperature: {row[1]}°C, Humidity: {row[2]}%, Condition: {row[3]}, Wind Speed: {row[4]} m/s")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()

def delete_search_history(user_id, location):
    connection = create_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM search_history WHERE location = %s AND user_id = %s", (location, user_id))
        connection.commit()
        
     
        if cursor.rowcount > 0:
            print(f"{location} city data successfully deleted")
        else:
            print("No matching search history found for the given location.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        cursor.close()
        connection.close()        
        
def update_user_profile(user_id, new_username=None, new_password=None):
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        if new_username:
            query = "UPDATE users SET username = %s WHERE id = %s"
            cursor.execute(query, (new_username, user_id))
        
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            query = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(query, (hashed_password, user_id))
        
        conn.commit()
        print("User profile updated successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
        
        
def fetch_5_day_forecast(city_name):
    api_key = ''
    base_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}'
    
    try:
        response = requests.get(base_url)
        data = response.json()
        
        if response.status_code == 200:
            forecast_data = []
            for entry in data['list']:
                forecast = {
                    "date": entry['dt_txt'],
                    "temperature": entry['main']['temp'],
                    "humidity": entry['main']['humidity'],
                    "weather_condition": entry['weather'][0]['description'],
                    "wind_speed": entry['wind']['speed']
                }
                forecast_data.append(forecast)
            return forecast_data
        else:
            print(f"Error fetching forecast data for city '{city_name}'. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


def cli_menu():
    print("Welcome to the Weather CLI App")
    while True:
        print("1. Register")
        print("2. Log in")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            user_id = login_user()
            if user_id:
                while True:
                    print("\n1. Search Weather")
                    print("2. View Search History")
                    print("3. Delete Search History")
                    print("4. Update Profile")
                    print("5. 5-Day Forecast")
                    print("6. Logout")
                    user_choice = input("Enter your choice: ")

                    if user_choice == '1':
                        location = input("Enter location: ")
                        weather_data = fetch_weather(location)
                        if weather_data:
                            print(f"Weather in {weather_data['location']}:")
                            print(f"Temperature: {weather_data['temperature']}°C")
                            print(f"Humidity: {weather_data['humidity']}%")
                            print(f"Condition: {weather_data['weather_condition']}")
                            print(f"Wind Speed: {weather_data['wind_speed']} m/s")
                            store_search_history(user_id, weather_data)
                    elif user_choice == '2':
                        view_search_history(user_id)
                    elif user_choice == '3':
                        location = input("Enter the location to delete from search history: ")
                        delete_search_history(user_id, location)
                    elif user_choice == '4':
                        new_username = input("Enter new username (or press Enter to keep current): ")
                        new_password = input("Enter new password (or press Enter to keep current): ")
                        update_user_profile(user_id, new_username if new_username else None, new_password if new_password else None)
        
                    elif user_choice == '5':
                        city = input("Enter the city for 5-day forecast: ")
                        forecast_data = fetch_5_day_forecast(city)
                        if forecast_data:
                            for forecast in forecast_data:
                                print(f"Date: {forecast['date']}, Temperature: {forecast['temperature']}°C, weather_condition: {forecast['weather_condition']}, Wind Speed: {forecast['wind_speed']} m/s")
        
                        
                    elif user_choice == '6':
                        print("Logged out.")
                        break
        
        elif choice == '3':
            print("Goodbye!")
            break

if __name__ == "__main__":
    cli_menu()
