
# YouTube Data Harvesting and Warehousing

Welcome to the YouTube Data Analysing app! This Streamlit application allows users to explore and analyze data from various YouTube channels. You can retrieve data like the channel name, subscriber count, total video count, and much more, and store it in a SQL database for further analysis.


## Features

- Input YouTube Channel ID: Users can enter a YouTube channel ID to fetch all relevant data using the YouTube API.
- Collect Data for Multiple Channels: The app allows collecting data of YouTube channels and stores this data in a data lake with just a button click.
- Data Storage Options: Data can be stored in a MySQL  database.
- Data Retrieval and Search: Users can search and retrieve data from the SQL database with various queries written inside the app.



## How to Set Up and Run the Project

To get this application up and running on your local machine, follow these steps:

- Prerequisites
Python installed on your computer.
Access to the Internet to install dependencies.
A Youtube API key to access YouTube data (you can get one from the Google Developers Console).

- Installation
Install required Python libraries:
pip install streamlit pandas mysql-connector sqlalchemy google-api-python-client

- Set up your database:
Have the MySQL server or cloud server  installed and running.
Create a database for storing the YouTube data 

- Configure your API key:
Store your Youtube API key in a secure place and reference it in your application code to authenticate API requests.

- Running the Application
To run the app, navigate to the project directory in your terminal and type:
streamlit run streamlit01.py
This will start the Streamlit application, and it should be accessible via a web browser at localhost:8501.


## Usage

- Enter a YouTube Channel ID: Start by entering a YouTube channel ID into the input field.
- Fetch and View Data: Click the 'Fetch Channel Data' button to retrieve and display the channel's data.
- Store and Analyse Data: Use the interface to store data in the database and analyse it using the 10 questions on the next page.

## Technologies Used

- YouTube Data: For fetching Data from YouTube.
- Python: For Data Extraction from API.
- Pandas: For Converting Data to Data Frame.
- SQL: For Data Storage and Querying.
- Streamlit: For Creating the Web Application.
