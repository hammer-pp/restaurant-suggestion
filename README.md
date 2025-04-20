1. Make sure there is a user.parquet and restaurant.parquet in folder (also model.pkl)
2. Run docker-compose file using ** docker-compose up -d --build ** in terminal 
3. In the docker container stop running 'lmwn' container (some problem with the database connection on a docker container)
4. Go to localhost:8080 in lmwn database and import 'request.sql' file 

	Run the server from VS code instead

5. Open 'conn_db.py' file
6. If an error occurs, Can't find the library -> Go to requirements.txt install the library follow the list
6. Run 'conn_db.py' file
7. Go to http://127.0.0.1:5000/recommend/uxxxxx (replace with user_id that in request ex.u00032 u00073) and server will return expect restaurant
