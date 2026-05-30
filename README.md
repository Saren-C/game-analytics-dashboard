# video_game_etl_project

Video Game ETL Pipeline using the RAWG API and PostgreSQL (Supabase)

This project extracts video game data from the RAWG API, transforms and validates the data, and incrementally loads it into a PostgreSQL database using UPSERT logic.

---

# Project Structure

```text
video_game_etl_project/

├── ETL_script.py
├── README.md
├── requirements.txt
├── .env
└── ER Diagram.png
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

# Derived Metrics

## Rating Category

Games are grouped into categories using rating values.

| Rating Range | Category  |
| ------------ | --------- |
| 0 - 2        | Poor      |
| 2 - 3        | Average   |
| 3 - 4        | Good      |
| 4 - 5        | Excellent |

This field is generated during transformation and can be used for reporting and dashboard filtering.

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