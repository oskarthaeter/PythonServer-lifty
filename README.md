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
  - populate your database with userdata
  - in Json.py replace the "/PyhtonServer/..." filepaths with the actual filepaths of the according files.



# Structure of the program

The project consists of two main parts:

   - the frontend
   - the backend

The frontend is the interface between user and program, i. e. it is optimized for the aspects of usability and design. 

The backend is the heart of the program, i. e. it brings everything to life and must therefore be heavily tested on functionality and possible security risks.

![Diagram](/Users/oskarhaeter/Downloads/Untitled Diagram.png)



# Structure of the frontend

The frontend is divided into three parts:
- browser interface(Website)
- Android interface(Java App)
- iOS interface(Swift App)

These three interfaces should follow relatively uniformly the given schema:

Registration:

The user has to register himself once in order to use the program.
In this process the user must enter personal data(forename, name, address),
contact data(tel, e-mail) and if they either are a parent(driver) or a child(passenger). The user also has to select a password.
Also a table of the child’s timetable should be entered, so the program knows who needs to be at the school at a certain time.

Login:

The user has to login every time they want to use the service, provided they are already registered.
In order to increase user-friendliness, an option for remembering login data should be made available.
	
Account management:

This pane is supposed to give the user the ability to change certain attributes of their account data.
Also an action for deleting the account should be provided.
		
Main page:

On this page an interface should be displayed, which gives the option for deciding if the user(driver) will be able to drive the following day(yes/no) or if the user(passenger) wants to be picked up the next day(yes/no).
Additionally: Statistical data showing driven kilometers, number of rides, CO2 in t saved, polar bears saved etc.
Driver: A button needs to be displayed, which opens Google Maps with the route which needs to be driven. 
Passenger: A timecode needs to be displayed, which represents the time the passenger needs to be outside waiting to be picked up. Also the contact data of the driver needs to be displayed(tel.).

# Structure of the backend 

The backend is divided into three different parts:
- PHP Server
- MySQL Database(DB)
- Python Server
		
The PHP Server acts as a middle man between the user interface and the rest of the backend. That means, data is handed to the server, which communicates it to the DB.
Also, the Python Server hands data to the middle man, who distributes it then to the user interfaces. This practice is supposed to increase security while maintaining minimum latency.

The MySQL Database is the main file storing component of the program.
It stores data like user addresses, user logins etc. but also stores school data.
This DB is needed because a lot of data storing is needed but it is also important, that the data can be quickly searched through.

The Python Server houses the algorithm, which looks for the best routes for every driver, every day, for every arrival time, for every school. That is why it is so important to keep the server closed off of the rest of the backend, it needs to be robust, secure and stable.


