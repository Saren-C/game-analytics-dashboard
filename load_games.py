"""
RAWG Video Games ETL Loader
---------------------------
Creates the PostgreSQL schema and loads video game data from the RAWG API.

Required packages:
    pip install pandas sqlalchemy psycopg2-binary python-dotenv requests

.env values expected:
    DB_PASSWORD=database_password
    DB_REF=supabaseproject_ref
    RAWG_API_KEY=rawg_api_key

Optional:
    SUPABASE_DB_URL=postgresql+psycopg2://...
    RESET_TABLES=true
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import Date, Float, Integer, String


BASE_DIR = Path(__file__).resolve().parent

RAWG_API_URL = "https://api.rawg.io/api/games"


# Connection configuration
def get_database_url() -> str:
    load_dotenv()

    database_url = os.getenv("SUPABASE_DB_URL")
    if database_url:
        return database_url

    password = os.getenv("DB_PASSWORD")
    db_ref = os.getenv("DB_REF")

    if not password or not db_ref:
        raise RuntimeError(
            "Set SUPABASE_DB_URL or set both DB_PASSWORD and DB_REF in your .env file."
        )

    return (
        "postgresql+psycopg2://"
        f"postgres:{password}"
        f"@db.{db_ref}.supabase.co:5432/postgres"
    )


def table_reset_enabled() -> bool:
    return os.getenv("RESET_TABLES", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }


# API extraction
def fetch_games_data(page_size: int = 100) -> list[dict]:
    load_dotenv()

    api_key = os.getenv("RAWG_API_KEY")

    if not api_key:
        raise RuntimeError("RAWG_API_KEY not found in .env file.")

    params = {
        "key": api_key,
        "page_size": page_size,
    }

    response = requests.get(RAWG_API_URL, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"RAWG API request failed: {response.status_code}"
        )

    data = response.json()

    return data["results"]


# Schema creation
def create_schema(engine) -> None:
    drop_sql = """
    DROP TABLE IF EXISTS public.game_platforms CASCADE;
    DROP TABLE IF EXISTS public.game_genres CASCADE;
    DROP TABLE IF EXISTS public.platforms CASCADE;
    DROP TABLE IF EXISTS public.genres CASCADE;
    DROP TABLE IF EXISTS public.games CASCADE;
    """

    create_sql = """
    CREATE TABLE IF NOT EXISTS public.games (
        game_id INTEGER PRIMARY KEY,
        game_name TEXT NOT NULL,
        released DATE,
        rating DOUBLE PRECISION,
        ratings_count INTEGER,
        metacritic INTEGER,
        playtime INTEGER,
        updated TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS public.genres (
        genre_id INTEGER PRIMARY KEY,
        genre_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS public.game_genres (
        game_id INTEGER NOT NULL REFERENCES public.games(game_id),
        genre_id INTEGER NOT NULL REFERENCES public.genres(genre_id),
        PRIMARY KEY (game_id, genre_id)
    );

    CREATE TABLE IF NOT EXISTS public.platforms (
        platform_id INTEGER PRIMARY KEY,
        platform_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS public.game_platforms (
        game_id INTEGER NOT NULL REFERENCES public.games(game_id),
        platform_id INTEGER NOT NULL REFERENCES public.platforms(platform_id),
        PRIMARY KEY (game_id, platform_id)
    );
    """

    with engine.begin() as conn:
        if table_reset_enabled():
            conn.execute(text(drop_sql))

        conn.execute(text(create_sql))


# Data transformation
def build_tables(
    games_data: list[dict],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    game_rows = []
    genre_rows = []
    game_genre_rows = []
    platform_rows = []
    game_platform_rows = []

    for game in games_data:

        game_rows.append(
            {
                "game_id": game.get("id"),
                "game_name": game.get("name"),
                "released": game.get("released"),
                "rating": game.get("rating"),
                "ratings_count": game.get("ratings_count"),
                "metacritic": game.get("metacritic"),
                "playtime": game.get("playtime"),
                "updated": game.get("updated"),
            }
        )

        # Genres
        for genre in game.get("genres", []):

            genre_rows.append(
                {
                    "genre_id": genre.get("id"),
                    "genre_name": genre.get("name"),
                }
            )

            game_genre_rows.append(
                {
                    "game_id": game.get("id"),
                    "genre_id": genre.get("id"),
                }
            )

        # Platforms
        for platform_entry in game.get("platforms", []):

            platform = platform_entry.get("platform", {})

            platform_rows.append(
                {
                    "platform_id": platform.get("id"),
                    "platform_name": platform.get("name"),
                }
            )

            game_platform_rows.append(
                {
                    "game_id": game.get("id"),
                    "platform_id": platform.get("id"),
                }
            )

    games_df = pd.DataFrame(game_rows)
    genres_df = pd.DataFrame(genre_rows).drop_duplicates()
    game_genres_df = pd.DataFrame(game_genre_rows).drop_duplicates()
    platforms_df = pd.DataFrame(platform_rows).drop_duplicates()
    game_platforms_df = pd.DataFrame(game_platform_rows).drop_duplicates()

    games_df["released"] = pd.to_datetime(
        games_df["released"],
        errors="coerce"
    ).dt.date

    games_df["updated"] = pd.to_datetime(
        games_df["updated"],
        errors="coerce"
    )

    return (
        games_df,
        genres_df,
        game_genres_df,
        platforms_df,
        game_platforms_df,
    )


# Data loading helper
def write_table(
    df: pd.DataFrame,
    table_name: str,
    engine,
    dtype: dict,
) -> None:

    print(f"Loading {table_name} table...")

    df.to_sql(
        table_name,
        engine,
        schema="public",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
        dtype=dtype,
    )


# Table loading
def load_tables(
    engine,
    games_df,
    genres_df,
    game_genres_df,
    platforms_df,
    game_platforms_df,
) -> None:

    write_table(
        games_df,
        "games",
        engine,
        {
            "game_id": Integer(),
            "game_name": String(),
            "released": Date(),
            "rating": Float(),
            "ratings_count": Integer(),
            "metacritic": Integer(),
            "playtime": Integer(),
        },
    )

    write_table(
        genres_df,
        "genres",
        engine,
        {
            "genre_id": Integer(),
            "genre_name": String(),
        },
    )

    write_table(
        game_genres_df,
        "game_genres",
        engine,
        {
            "game_id": Integer(),
            "genre_id": Integer(),
        },
    )

    write_table(
        platforms_df,
        "platforms",
        engine,
        {
            "platform_id": Integer(),
            "platform_name": String(),
        },
    )

    write_table(
        game_platforms_df,
        "game_platforms",
        engine,
        {
            "game_id": Integer(),
            "platform_id": Integer(),
        },
    )


# Main ETL workflow
def main() -> None:

    print("Connecting to PostgreSQL database...")
    engine = create_engine(get_database_url())

    print("Fetching RAWG API data...")
    games_data = fetch_games_data(page_size=100)

    print("Transforming API data...")
    (
        games_df,
        genres_df,
        game_genres_df,
        platforms_df,
        game_platforms_df,
    ) = build_tables(games_data)

    print("Creating PostgreSQL schema...")
    create_schema(engine)

    print("Loading tables into PostgreSQL...")
    load_tables(
        engine,
        games_df,
        genres_df,
        game_genres_df,
        platforms_df,
        game_platforms_df,
    )

    print("===================================")
    print("ETL LOAD COMPLETE")
    print("===================================")


if __name__ == "__main__":
    main()