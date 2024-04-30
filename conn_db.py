import mysql.connector
import pandas as pd
import time
from loaddata import model
from loaddata import user_df
from loaddata import restaurant_df
from flask import Flask, jsonify
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def calculate_model(user_id, model, user_df, restaurant_df, user_coords, size, max_dis):
    USER_ID = str(user_id)

    def haversine_vectorized(lat1, lon1, lat2, lon2):
        R = 6371000    # Radius of the Earth in meters
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c
        return distance

    def calculate_displacement(row):
        try:
            if 'latitude' in row and 'longitude' in row:
                recommend_df_latitude = row['latitude'].astype(float)
                recommend_df_longitude = row['longitude'].astype(float)
                distances = haversine_vectorized(user_coords[0], user_coords[1], recommend_df_latitude, recommend_df_longitude)
                return distances
        except Exception as e:
            print(f"Error calculating displacement: {str(e)}")
            print("Latitude or longitude column not found in row:", row)

    # Find 2000 nearest neighbors to recommend restaurants
    difference, ind = model.kneighbors(
        user_df[user_df["user_id"] == USER_ID].drop(columns="user_id"), n_neighbors=2000)

    # Get restaurant id from restaurant indices returned from the model
    recommend_df = restaurant_df.loc[ind[0]]

    # Set distance as restaurant score
    recommend_df["difference"] = difference[0]

    # Vectorized displacement calculation
    recommend_df["displacement"] = calculate_displacement(recommend_df)

    recommend_df = recommend_df[recommend_df['displacement'] < max_dis]

    recommend_df = recommend_df.head(size)

    # Return the result in JSON format
    return recommend_df[["restaurant_id", "difference", "displacement"]].to_json(orient="records", indent=4)

'''
Replace with your Database host, user, password, databasename 
In case use XAMPP and database name is lmwn
'''
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'lmwn',
}
db_config['pool_size'] = 10

app = Flask(__name__)

@app.route('/recommend/<string:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        # Establish a connection to the database
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            # Create a cursor to execute SQL queries
            cursor = connection.cursor()

            # Specify the SQL query to select size from the user table
            query =  f"SELECT latitude, longitude, size, sort_dis, max_dis FROM request WHERE user_id ='{user_id}'"

            # Execute the user query
            cursor.execute(query)
            user_data = cursor.fetchmany(1)

            for user_row in user_data:
                user_id = str(user_id) 
                user_coords = (float(user_row[0]), float(user_row[1]))
                size = int(user_row[2])
                sort_dis = int(user_row[3])
                max_dis = int(user_row[4])
        
            start_time = time.time()
            results = calculate_model(user_id,model,user_df,restaurant_df,user_coords,size,max_dis)
            print("For user ",user_id)

            response_data = eval(results)
            desired_format = {"restaurants": []}
            for item in response_data:
                new_item = {
                    "id": item["restaurant_id"],
                    "difference": item["difference"],
                    "displacement": item["displacement"]
                }
                desired_format["restaurants"].append(new_item)
            response = jsonify(desired_format)
            end_time = time.time()
            elapsed_time = end_time - start_time

            print("Time: ",elapsed_time)

            return response
        
    except mysql.connector.Error as err:
        return jsonify({"message": {err}}), 404

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            # Make sure to fetch all remaining results before closing the cursor
            cursor.fetchall()
            cursor.close()

        if connection.is_connected():
            connection.close()
if __name__ == '__main__':
    app.run(debug=True)


