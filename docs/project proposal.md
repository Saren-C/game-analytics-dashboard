# Video Game Trends & Analytics Dashboard Project Proposal

Developer: Saren Chatham
Target Audience: Video game enthusiasts 
Technology Stack: Python, Power BI, RAWG Video Games Database API

## Background:

The video game industry is one of the largest entertainment industries in the world, generating large amounts of publicly available data related to game releases, ratings, genres, publishers, and gaming platforms. However, this data is often spread across multiple sources and can be difficult to analyze efficiently.

This project will use the RAWG Video Games Database API to collect and analyze video game metadata in order to identify trends in the gaming industry. The project will focus on building a complete end-to-end data engineering pipeline that extracts data from a REST API, transforms the data into structured formats, stores the processed data, and visualizes insights through an interactive dashboard.

This topic is interesting because video game data contains rich categorical and time-series information that is well suited for data analysis and visualization. Gamers, analysts, and entertainment companies could use similar dashboards to monitor trends in genres, ratings, release patterns, and platform popularity.

## Problem Statement:

Video game data is available through public APIs, but the data is often stored in complex nested JSON structures that are difficult to analyze directly. There is a need for a streamlined process that extracts, transforms, and visualizes video game metadata in a user-friendly format.

This project aims to solve this problem by building an automated pipeline that converts raw API data into structured datasets and presents insights through an interactive analytics dashboard.

## Project Assumptions:

* Gamers use ratings, genres, and platform availability when evaluating games.
* Interactive dashboards provide a more effective way to explore game trends than raw API data.
* Game metadata such as genre, platform, and release date can be used to identify meaningful industry patterns.
* Higher-rated games generally reflect stronger player reception and engagement.
* Users are interested in comparing games across platforms, genres, and release periods.
* Historical game data can be used to analyze changes in gaming trends over time.


## Objectives:

The objectives of this project are to:
* Extract video game metadata from the RAWG REST API using Python
* Transform nested JSON responses into structured tabular datasets
* Clean and standardize game information such as genres, ratings, release dates, and platforms
* Store processed data in PostgreSQL database tables
* Build an interactive Power BI dashboard to visualize gaming trends and metrics
* Create visualizations that allow users to explore:
    * Game genre popularity
    * Platform distribution
    * Game ratings
    * Release trends over time
    * Publisher activity
* Demonstrate a complete ETL workflow from API extraction to business intelligence reporting

## Methodology / Technical Approach

### Data Source

The project will use the following API:
RAWG Video Games Database API

### The API provides structured video game metadata including:
* Game titles
* Genres
* Ratings
* Release dates
* Platforms
* Publishers
* Metacritic scores

### Tools and Technologies

Programming & ETL
* Python
* requests
* pandas
* SQLAlchemy
Data Storage
* PostgreSQL
Visualization
* Microsoft Power BI

### ETL Workflow Design

Extract
* Connect to the RAWG API using Python requests
* Retrieve game metadata through REST API endpoints
* Store raw JSON responses temporarily
Transform
* Parse nested JSON structures into structured tables
* Clean missing or inconsistent values
* Standardize date and categorical fields
* Separate relational data such as genres and platforms into normalized tables
Load
* Use SQLAlchemy to define relational database schemas
* Load transformed datasets into PostgreSQL tables
* Query structures data for dashboard integration in Power BI
Visualization
* Connect Power BI to the processed datasets
* Build interactive dashboards and KPIs
* Create filters and slicers for user exploration

## Planned Dashboard Visualizations

The Power BI dashboard will include:
* KPI cards for total games, average ratings, and average metascore
* Bar charts showing genre popularity
* Line charts showing game release trends over time
* Platform comparison charts
* Tables displaying top-rated games
* Interactive slicers for genres, platforms, and release years

## ETL Architecture Diagram

RAWG REST API
       ↓
Python API Requests
       ↓
JSON Data Extraction
       ↓
Data Cleaning & Transformation (Pandas)
       ↓
SQLAlchemy ORM
       ↓
PostgreSQL Database
       ↓
Power BI Dashboard
       ↓
Interactive Insights & Visualizations

## Data Quality and Validation

Data quality checks identified a single missing value in the metacritic field. Because the missing value represents an insignificant portion of the dataset and does not impact dashboard measures or visualizations, it will be retained as NULL rather than being imputed or removed.

## Timeline

Week 1 - Finalize project proposal, research API structure, obtain API key
Week 2 - Build API extraction scripts and retrieve sample datasets
Week 3 - Clean and transform JSON data, design database schema, load data into PostgreSQL
Week 4 - Build Power BI dashboard and create visualizations 
Week 5 - Final testing, dashboard refinement, presentation preparation, project submission

## Expected Outcomes

By the end of the project, the completed deliverables will include:
* A functional ETL pipeline using Python
* Automated extraction of video game data from a REST API
* A PostgreSQL relational database populated through SQLAlchemy ETL process
* An interactive Power BI dashboard with gaming trend visualizations
* A final presentation demonstrating the pipeline and analytical insights
* Documentation explaining the workflow and technical implementation

The final project will demonstrate the ability to design and implement a complete data engineering workflow from data acquisition to insight generation.