"""
RAWG Video Games ETL Pipeline
-----------------------------------------
This ETL pipeline extracts video game data from the RAWG API,
performs cleaning, transformation, validation, and incremental
upsert loading into an existing PostgreSQL database.

This version demonstrates:
- API extraction
- Cleaning and normalization
- Transformation and derived metrics
- Data validation and quality checks
- Incremental loading with UPSERT logic
- PostgreSQL loading
- Logging and error handling

Required packages:
    pip install pandas sqlalchemy psycopg2-binary python-dotenv requests

Expected .env variables:
    SUPABASE_DB_URL=postgresql://...
    RAWG_API_KEY=your_api_key
"""

from __future__ import annotations

import logging
import os
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# -------------------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Environment Variables
# -------------------------------------------------------------------
load_dotenv()

RAWG_API_KEY = os.getenv("RAWG_API_KEY")
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

RAWG_API_URL = "https://api.rawg.io/api/games"


# -------------------------------------------------------------------
# Database Connection
# -------------------------------------------------------------------
def get_engine():
    """Create SQLAlchemy engine."""

    if not DATABASE_URL:
        raise RuntimeError(
            "SUPABASE_DB_URL not found in .env"
        )

    logger.info("Connecting to PostgreSQL database")

    return create_engine(DATABASE_URL)


# -------------------------------------------------------------------
# API Extraction
# -------------------------------------------------------------------
def extract_games(page_size: int = 100) -> list[dict]:
    """Extract game data from RAWG API."""

    logger.info("Extracting RAWG API data")

    if not RAWG_API_KEY:
        raise RuntimeError(
            "RAWG_API_KEY not found in .env"
        )

    params = {
        "key": RAWG_API_KEY,
        "page_size": page_size,
    }

    try:

        response = requests.get(
            RAWG_API_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    except requests.RequestException as error:

        logger.exception("RAWG API request failed")

        raise RuntimeError(
            "Unable to retrieve RAWG API data"
        ) from error


# -------------------------------------------------------------------
# Raw API Validation
# -------------------------------------------------------------------
def validate_raw_data(games_data: list[dict]) -> None:
    """Validate API response structure."""

    logger.info("Validating raw API response")

    if not isinstance(games_data, list):
        raise ValueError(
            "RAWG API response is not a list"
        )

    if len(games_data) == 0:
        raise ValueError(
            "RAWG API returned zero records"
        )

    required_fields = {
        "id",
        "name",
        "released",
        "rating",
    }

    sample_record = games_data[0]

    missing_fields = required_fields.difference(
        sample_record.keys()
    )

    if missing_fields:
        raise ValueError(
            f"Missing required fields: {sorted(missing_fields)}"
        )

    logger.info("Raw API validation passed")


# -------------------------------------------------------------------
# Data Transformation and Cleaning
# -------------------------------------------------------------------
def transform_games_data(
    games_data: list[dict],
):
    """Clean and normalize RAWG API data."""

    logger.info("Transforming RAWG data")

    game_rows = []
    genre_rows = []
    game_genre_rows = []
    platform_rows = []
    game_platform_rows = []

    for game in games_data:

        game_id = game.get("id")

        game_rows.append(
            {
                "game_id": game_id,
                "game_name": str(
                    game.get("name", "")
                ).strip(),
                "released": game.get("released"),
                "rating": game.get("rating"),
                "ratings_count": game.get("ratings_count"),
                "metacritic": game.get("metacritic"),
                "playtime": game.get("playtime"),
                "updated": game.get("updated"),
            }
        )

        # -----------------------------------------------------------
        # Genre transformation
        # -----------------------------------------------------------
        for genre in game.get("genres", []):

            genre_rows.append(
                {
                    "genre_id": genre.get("id"),
                    "genre_name": genre.get("name"),
                }
            )

            game_genre_rows.append(
                {
                    "game_id": game_id,
                    "genre_id": genre.get("id"),
                }
            )

        # -----------------------------------------------------------
        # Platform transformation
        # -----------------------------------------------------------
        for platform_entry in game.get(
            "platforms",
            [],
        ):

            platform = platform_entry.get(
                "platform",
                {},
            )

            platform_rows.append(
                {
                    "platform_id": platform.get("id"),
                    "platform_name": platform.get("name"),
                }
            )

            game_platform_rows.append(
                {
                    "game_id": game_id,
                    "platform_id": platform.get("id"),
                }
            )

    # ---------------------------------------------------------------
    # Create DataFrames
    # ---------------------------------------------------------------
    games_df = pd.DataFrame(game_rows)

    genres_df = (
        pd.DataFrame(genre_rows)
        .drop_duplicates()
    )

    game_genres_df = (
        pd.DataFrame(game_genre_rows)
        .drop_duplicates()
    )

    platforms_df = (
        pd.DataFrame(platform_rows)
        .drop_duplicates()
    )

    game_platforms_df = (
        pd.DataFrame(game_platform_rows)
        .drop_duplicates()
    )

    # ---------------------------------------------------------------
    # Datatype conversion
    # ---------------------------------------------------------------
    games_df["released"] = pd.to_datetime(
        games_df["released"],
        errors="coerce",
    ).dt.date

    games_df["updated"] = pd.to_datetime(
        games_df["updated"],
        errors="coerce",
    )

    numeric_columns = [
        "rating",
        "ratings_count",
        "metacritic",
        "playtime",
    ]

    for column in numeric_columns:

        games_df[column] = pd.to_numeric(
            games_df[column],
            errors="coerce",
        )
    for column in numeric_columns:
            games_df[column] = games_df[column].replace([np.inf, -np.inf], np.nan)
            games_df[column] = games_df[column].where(pd.notnull(games_df[column]), None)
            games_df[column] = games_df[column].astype("object")
    # ---------------------------------------------------------------
    # Derived metrics
    # ---------------------------------------------------------------
    games_df["rating_category"] = pd.cut(
        games_df["rating"],
        bins=[0, 2, 3, 4, 5],
        labels=[
            "Poor",
            "Average",
            "Good",
            "Excellent",
        ],
    )

    logger.info(
        "Transformation complete: %s rows",
        len(games_df),
    )

    return (
        games_df,
        genres_df,
        game_genres_df,
        platforms_df,
        game_platforms_df,
    )


# -------------------------------------------------------------------
# Data Validation
# -------------------------------------------------------------------
def validate_transformed_data(
    games_df: pd.DataFrame,
) -> None:
    """Run data quality checks."""

    logger.info(
        "Running transformed data validation"
    )

    required_columns = [
        "game_id",
        "game_name",
        "rating",
    ]

    null_counts = (
        games_df[required_columns]
        .isna()
        .sum()
    )

    if null_counts.any():

        raise ValueError(
            f"Null values found: {null_counts.to_dict()}"
        )

    duplicate_games = (
        games_df["game_id"]
        .duplicated()
        .sum()
    )

    if duplicate_games > 0:

        raise ValueError(
            f"Duplicate game IDs found: {duplicate_games}"
        )

    invalid_ratings = games_df[
        ~games_df["rating"].between(0, 5)
    ]

    if not invalid_ratings.empty:

        raise ValueError(
            "Ratings outside valid range 0-5"
        )

    logger.info("Data validation passed")


# -------------------------------------------------------------------
# Incremental UPSERT Loading
# -------------------------------------------------------------------
def upsert_games(
    engine,
    games_df: pd.DataFrame,
) -> None:
    """
    Insert new games and update existing games.
    """

    logger.info(
        "Performing incremental UPSERT on games table"
    )

    upsert_sql = text(
        """
        INSERT INTO public.games (
            game_id,
            game_name,
            released,
            rating,
            ratings_count,
            metacritic,
            playtime,
            updated
        )
        VALUES (
            :game_id,
            :game_name,
            :released,
            :rating,
            :ratings_count,
            :metacritic,
            :playtime,
            :updated
        )

        ON CONFLICT (game_id)

        DO UPDATE SET
            game_name = EXCLUDED.game_name,
            released = EXCLUDED.released,
            rating = EXCLUDED.rating,
            ratings_count = EXCLUDED.ratings_count,
            metacritic = EXCLUDED.metacritic,
            playtime = EXCLUDED.playtime,
            updated = EXCLUDED.updated
        """
    )

    with engine.begin() as connection:

        for row in games_df.to_dict(
            orient="records"
        ):
            cleaned_row = {
                k: (None if pd.isna(v) else v)
                for k, v in row.items()
            }

            connection.execute(
                upsert_sql,
                cleaned_row,
            )

    logger.info(
        "Games UPSERT complete"
    )


# -------------------------------------------------------------------
# Dimension Table Loading
# -------------------------------------------------------------------
def load_dimension_tables(engine, genres_df, platforms_df) -> None:
    """
    Load genres and platforms using UPSERT logic
    to prevent duplicate primary key violations.
    """

    logger.info("Loading dimension tables with UPSERT logic")

    genre_sql = text("""
        INSERT INTO public.genres (
            genre_id,
            genre_name
        )
        VALUES (
            :genre_id,
            :genre_name
        )
        ON CONFLICT (genre_id)
        DO UPDATE SET
            genre_name = EXCLUDED.genre_name
    """)

    platform_sql = text("""
        INSERT INTO public.platforms (
            platform_id,
            platform_name
        )
        VALUES (
            :platform_id,
            :platform_name
        )
        ON CONFLICT (platform_id)
        DO UPDATE SET
            platform_name = EXCLUDED.platform_name
    """)

    with engine.begin() as connection:

        for row in genres_df.to_dict(orient="records"):
            connection.execute(genre_sql, row)

        for row in platforms_df.to_dict(orient="records"):
            connection.execute(platform_sql, row)

    logger.info("Dimension table UPSERT complete")


# -------------------------------------------------------------------
# Bridge Table Loading
# -------------------------------------------------------------------
def load_bridge_tables(
    engine,
    game_genres_df,
    game_platforms_df,
) -> None:
    """
    Insert bridge table rows while avoiding duplicates.
    """

    logger.info(
        "Loading bridge tables"
    )

    game_genre_sql = text(
        """
        INSERT INTO public.game_genres (
            game_id,
            genre_id
        )
        VALUES (
            :game_id,
            :genre_id
        )

        ON CONFLICT (game_id, genre_id)
        DO NOTHING
        """
    )

    game_platform_sql = text(
        """
        INSERT INTO public.game_platforms (
            game_id,
            platform_id
        )
        VALUES (
            :game_id,
            :platform_id
        )

        ON CONFLICT (game_id, platform_id)
        DO NOTHING
        """
    )

    with engine.begin() as connection:

        for row in game_genres_df.to_dict(
            orient="records"
        ):

            connection.execute(
                game_genre_sql,
                row,
            )

        for row in game_platforms_df.to_dict(
            orient="records"
        ):

            connection.execute(
                game_platform_sql,
                row,
            )

    logger.info(
        "Bridge table loading complete"
    )


# -------------------------------------------------------------------
# Main ETL Workflow
# -------------------------------------------------------------------
def main():
    """Run ETL pipeline."""

    try:

        engine = get_engine()

        # -----------------------------------------------------------
        # Extract
        # -----------------------------------------------------------
        games_data = extract_games()

        validate_raw_data(
            games_data
        )

        # -----------------------------------------------------------
        # Transform
        # -----------------------------------------------------------
        (
            games_df,
            genres_df,
            game_genres_df,
            platforms_df,
            game_platforms_df,
        ) = transform_games_data(
            games_data
        )

        validate_transformed_data(
            games_df
        )

        # -----------------------------------------------------------
        # Load dimensions
        # -----------------------------------------------------------
        load_dimension_tables(
            engine,
            genres_df,
            platforms_df,
        )

        # -----------------------------------------------------------
        # Incremental UPSERT
        # -----------------------------------------------------------
        upsert_games(
            engine,
            games_df,
        )

        # -----------------------------------------------------------
        # Load bridge tables
        # -----------------------------------------------------------
        load_bridge_tables(
            engine,
            game_genres_df,
            game_platforms_df,
        )

        logger.info(
            "ETL pipeline completed successfully"
        )

    except Exception:

        logger.exception(
            "ETL pipeline failed"
        )

        raise


if __name__ == "__main__":
    main()