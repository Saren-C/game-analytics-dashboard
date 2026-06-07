# video_game_etl_project

Video Game ETL Pipeline using the RAWG API and PostgreSQL (Supabase)

This project extracts video game data from the RAWG API, transforms and validates the data, and incrementally loads it into a PostgreSQL database using UPSERT logic.

---

# Project Structure

```text
game-analytics-dashboard/

├── diagrams/
│   ├── Dataflow Diagram.png
│   └── ER Diagram.png
│
├── docs/
│   ├── project proposal.md
│   └── schema doc.md
│
├── .env
├── dashboard.png
├── ETL_script.py
├── load_script.py
├── README.md
├── requirements.txt
└── SQL.txt
```

---

# Scripts

## ETL_script.py

### Purpose

Production ETL pipeline that retrieves video game data from the RAWG API and loads it into a PostgreSQL database hosted in Supabase.

### Workflow

#### Extract

* Connects to the RAWG API
* Retrieves the latest video game data
* Validates API response structure
* Confirms required fields are present

#### Transform

* Converts API JSON responses into structured DataFrames
* Extracts:

  * Games
  * Genres
  * Platforms
  * Game-Genre relationships
  * Game-Platform relationships
* Converts data types
* Parses dates and timestamps
* Removes duplicate dimension records
* Creates derived rating categories

#### Validate

Performs data quality checks:

* Required fields cannot be null
* Game IDs must be unique
* Ratings must be between 0 and 5
* Detects duplicate game records

#### Load

Loads data into PostgreSQL using incremental UPSERT logic.

### Incremental Loading Strategy

#### Games Table

Uses PostgreSQL ON CONFLICT logic:

* Inserts new games
* Updates existing games when data changes
* Prevents duplicate game IDs

Example:

If a game's rating changes from 4.2 to 4.4:

* Existing record is updated
* No duplicate row is created

#### Dimension Tables

Genres and Platforms use UPSERT logic:

* Inserts new genres/platforms
* Updates names if they change
* Prevents primary key violations

#### Bridge Tables

Game-Genre and Game-Platform tables use:

```sql
ON CONFLICT DO NOTHING
```

This:

* Inserts new relationships
* Ignores existing relationships
* Prevents duplicate bridge records

---

# Database Tables

## games

Stores core game information.

Columns:

* game_id
* game_name
* released
* rating
* ratings_count
* metacritic
* playtime
* updated

---

## genres

Stores unique game genres.

Columns:

* genre_id
* genre_name

Examples:

* Action
* RPG
* Adventure
* Shooter

---

## platforms

Stores gaming platforms.

Columns:

* platform_id
* platform_name

Examples:

* PC
* PlayStation 5
* Xbox Series X
* Nintendo Switch

---

## game_genres

Bridge table connecting games and genres.

Columns:

* game_id
* genre_id

---

## game_platforms

Bridge table connecting games and platforms.

Columns:

* game_id
* platform_id

---

# Usage

## Run the ETL Pipeline

```bash
python ETL_script.py
```

Expected output:

```text
Connecting to PostgreSQL database
Extracting RAWG API data
Validating raw API response
Transforming RAWG data
Running transformed data validation
Loading dimension tables
Performing incremental UPSERT on games table
Loading bridge tables
ETL pipeline completed successfully
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
SUPABASE_DB_URL=postgresql://username:password@host:5432/database
RAWG_API_KEY=your_rawg_api_key
```

### Variables

#### SUPABASE_DB_URL

Connection string for the PostgreSQL database.

#### RAWG_API_KEY

API key obtained from RAWG.

RAWG Developer Portal:

https://rawg.io/apidocs

---

# Learning Outcomes

This project demonstrates:

* REST API integration
* JSON data extraction
* ETL pipeline design
* Data validation and quality checks
* Incremental loading strategies
* PostgreSQL UPSERT operations
* Dimensional data modeling
* Many-to-many relationship handling
* SQLAlchemy database connectivity
* Logging and exception handling

---

# Data Source

## RAWG Video Games Database API

Website:

https://rawg.io/apidocs

Provides:

* Video game metadata
* Ratings
* Review counts
* Release dates
* Genres
* Platforms
* Metacritic scores

---

# Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Required libraries:

* pandas
* numpy
* requests
* sqlalchemy
* psycopg2-binary
* python-dotenv

---

# ER Diagram

The repository includes:

```text
ER Diagram.png
```

The diagram illustrates:

* games table
* genres table
* platforms table
* game_genres bridge table
* game_platforms bridge table

and the relationships between them.

---

# API Reference

RAWG API Documentation:

https://rawg.io/apidocs

Features:

* Free developer tier available
* Large video game database
* Ratings and review metrics
* Platform and genre metadata
* Regularly updated game information

---

# Power BI Dashboard

## Dashboard Overview

The Power BI dashboard provides an interactive view of video game trends, ratings, genres, platforms, and release activity using data collected from the RAWG API and stored in PostgreSQL (Supabase).

The dashboard is designed to help users explore video game performance metrics, identify genre and platform trends, and discover highly rated games through interactive visualizations and filters.

### Dashboard Features

#### KPI Cards

Provides high-level summary metrics including:

* Total Games
* Average Rating
* Average Metacritic Score

#### Genre Analysis

Bar charts display:

* Number of games by genre
* Average rating by genre

This allows users to compare genre popularity with overall game quality.

#### Release Trends

Line charts visualize:

* Number of games released over time

Users can identify growth patterns and release trends across different years.

#### Platform Analysis

Comparison charts display:

* Number of games by platform
* Average ratings by platform

These visuals help identify the most popular and highest-performing gaming platforms.

#### Top Rated Games

Interactive tables display:

* Highest-rated games
* Ratings
* Metacritic scores
* Release information

#### Interactive Filtering

Users can dynamically filter the dashboard using slicers for:

* Genre
* Platform
* Release Year

All visualizations update automatically based on selected filters.

---

## How to Run the Dashboard

### Prerequisites

* Power BI Desktop
* Access to the PostgreSQL database hosted in Supabase

### Steps

1. Open the Power BI project file (.pbix).
2. Refresh the dataset connection.
3. Power BI will retrieve the latest data from the PostgreSQL database.
4. Use the dashboard pages, visuals, and slicers to explore the data.

If the database has been updated using the ETL pipeline, select **Refresh** within Power BI to load the newest records.

---

## Business Insights

Several insights can be identified from the current dataset:

### Genre Insights

* Action is the most common genre and contains the largest number of games.
* Puzzle games have the highest average rating despite having fewer titles.

This suggests that while Action games dominate the market in volume, Puzzle games may deliver stronger player satisfaction on average.

### Platform Insights

* PC contains the largest number of games in the dataset.
* PlayStation 2 has the highest average rating among platforms represented.

This indicates that platform popularity does not necessarily correlate with higher game ratings.

### Release Trends

The release trend visualizations can be used to identify periods of increased game production and changing industry activity over time.

---

## Dashboard Considerations

### Limited Dataset

The dashboard is built using a limited sample of data retrieved from the RAWG API. Results should be viewed as representative of the available dataset rather than the entire video game industry.

### Many-to-Many Relationships

Video games can belong to multiple genres and can be released on multiple platforms.

Because of these many-to-many relationships:

* Genre totals may exceed the number of unique games.
* Platform totals may exceed the number of unique games.
* Filtering by genre or platform may affect aggregated metrics differently than a one-to-one data model.

These relationships are intentionally preserved to accurately represent how games are categorized and distributed across platforms.