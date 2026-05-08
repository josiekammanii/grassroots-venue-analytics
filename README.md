# 🎵 Grassroots Music Venue Analytics Database
A relational database and interactive reporting solution designed to support data-driven decision-making at a small independent music venue — addressing financial sustainability challenges facing the UK grassroots sector post-pandemic and during the cost-of-living crisis.

Module: IOT552U — Business Organisation and Decision Making
Institution: Queen Mary University of London
Assessment: 002 Project Report (70%)

## Project Overview
This project builds a complete analytics platform for a grassroots music venue that consolidates event, ticketing, artist booking, promotional campaign, and bar sales data into a single structured database. The solution enables the venue to move away from intuition-based decisions toward evidence-based programming, pricing, and marketing strategies.
The three research questions this solution answers:

Which event types and artists generate the strongest attendance and revenue?
How do ticket sales relate to bar revenue and total event profitability by genre?
Which customer segments are most responsive to promotional pricing strategies?

## How to Run
Option 1 — Google Colab (recommended)

Open the notebook directly: Launch in Colab
Click Runtime → Run all
All 10 tables are created, populated, queried, and visualised automatically

Option 2 — Run locally
Requirements:
pip install numpy pandas plotly sqlite3
# 1. Generate the data
python data/generate_data.py

# 2. Create the database and schema
sqlite3 GrassrootsVenue.db < schema/schema.sql

# 3. Import all data (in FK-safe order)
sqlite3 GrassrootsVenue.db < sql_imports/import_data.sql
Then open notebook/GrassrootsVenue_Database.ipynb in Jupyter to run the queries and charts.

## 📊 Interactive Dashboard
The full interactive dashboard — including three Plotly visualisations and all SQL queries with printed results — is available at:
🔗 View the Colab Notebook https://colab.research.google.com/drive/1lZ58DAbXaINp0fpvLjwoSdFXLsX-Zk_Q?usp=sharing 
Charts produced:

Revenue and Profitability by Genre — horizontal grouped bar with profit/loss diamond markers
Bar Spend Per Attendee by Genre — bubble chart (x = attendees, y = spend/head, size = order volume)
Discount Uptake and Attendance Rate by Age Band — dual-axis gradient bar + spline line
