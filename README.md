PythonServer-lifty
==================

A school project to reduce CO2-emissions by providing a platform to parents so they can take other children with them when 
driving their children to school.

Planned is a website, an Android app and a IOS app, also a python server,
which processes data and runs an algorithm on location 
data and the number of vehicles in order to find the optimal routes to the school.

This Project is being developed by the Q2 computer science course of the Königin-Luise-Stiftung Berlin school.

The provided code only represents the Python Server of the project.

In order to use the code:

  - create a database using the commands provided in SQL.sql
  - insert your database login data into json_config.json
  - insert your Google Distance Matrix API-Key into json_config.json
  - insert the host, which will handle the logging, in __innit__.py
  - populate your database with userdata
  - in Json.py replace the "/PyhtonServer/..." filepaths with the actual filepaths of the according files.



# Structure of the program

The project consists of two main parts:

   - the frontend
   - the backend

The frontend is the interface between user and program, i. e. it is optimized for the aspects of usability and design. 

The backend is the heart of the program, i. e. it brings everything to life and must therefore be heavily tested on 
functionality and possible security risks.

# Structure of the backend 

The backend is divided into three different parts:
- PHP Server
- MySQL database(DB)
- Python Server
		
The PHP Server acts as a middle man between the user interface and the rest of the backend. 
That means, data is handed to the server, which communicates it to the DB.
Also, the Python Server hands data to the middle man, who distributes it then to the user interfaces. 
This practice is supposed to increase security while maintaining a minimal latency.

The MySQL database is the main structured data storing component of the program.
It stores data like user addresses, user logins etc. but also stores school data.
This DB is needed because a lot of data storing is required while it is also important,
that the data can be efficiently searched through.

The Python Server houses the algorithm, which produces the best routes for every driver,
every day, for every arrival time, for every school.
That is why it is so important to keep the server separate the rest of the backend,
it needs to be robust, secure and stable.
The Algorithm is called from a thread, which under certain conditions is started in the indefinitely running main process.
