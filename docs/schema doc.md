# Database Schema Documentation

## Video Game Analytics Data Warehouse

This database stores video game information collected from the RAWG API and loaded into a PostgreSQL database using SQLAlchemy.

The schema is normalized to approximately Third Normal Form (3NF) by:

- Separating entities into related tables
- Avoiding repeated data
- Using bridge tables for many-to-many relationships

---

## Database Overview

The database contains five tables:

- `games`
- `genres`
- `game_genres`
- `platforms`
- `game_platforms`

| Table | Purpose |
|---------|---------|
| games | Stores core video game information and metrics |
| genres | Stores unique game genres |
| game_genres | Bridge table connecting games to genres |
| platforms | Stores gaming platform information |
| game_platforms | Bridge table connecting games to platforms |

---

## games

### Purpose

Stores core video game information from the RAWG API.

### Primary Key

- `game_id`

### Relationships

- One game can relate to many genres through `game_genres`.
- One game can relate to many platforms through `game_platforms`.

### Columns

| Column Name | Data Type | Key | Description |
|------------|-----------|-----|-------------|
| game_id | INTEGER | Primary Key | Unique game identifier |
| game_name | TEXT |  | Video game title |
| released | DATE |  | Game release date |
| rating | FLOAT |  | Average user rating |
| ratings_count | INTEGER |  | Number of user ratings |
| metacritic | INTEGER |  | Metacritic score |
| playtime | INTEGER |  | Estimated playtime |
| updated | TIMESTAMP |  | Timestamp of last API update |

---

## genres

### Purpose

Stores unique video game genres.

### Primary Key

- `genre_id`

### Relationships

- One genre can relate to many games through `game_genres`.

### Columns

| Column Name | Data Type | Key | Description |
|------------|-----------|-----|-------------|
| genre_id | INTEGER | Primary Key | Unique genre identifier |
| genre_name | TEXT | Unique | Genre name |

---

## game_genres

### Purpose

Bridge table implementing the many-to-many relationship between games and genres.

### Primary Key

- (`game_id`, `genre_id`)

### Relationships

- Many-to-many relationship between games and genres.

### Columns

| Column Name | Data Type | Key | Description |
|------------|-----------|-----|-------------|
| game_id | INTEGER | Composite PK / FK | References `games.game_id` |
| genre_id | INTEGER | Composite PK / FK | References `genres.genre_id` |

---

## platforms

### Purpose

Stores unique gaming platform information.

### Primary Key

- `platform_id`

### Relationships

- One platform can relate to many games through `game_platforms`.

### Columns

| Column Name | Data Type | Key | Description |
|------------|-----------|-----|-------------|
| platform_id | INTEGER | Primary Key | Unique platform identifier |
| platform_name | TEXT | Unique | Platform name |

---

## game_platforms

### Purpose

Bridge table implementing the many-to-many relationship between games and platforms.

### Primary Key

- (`game_id`, `platform_id`)

### Relationships

- Many-to-many relationship between games and platforms.

### Columns

| Column Name | Data Type | Key | Description |
|------------|-----------|-----|-------------|
| game_id | INTEGER | Composite PK / FK | References `games.game_id` |
| platform_id | INTEGER | Composite PK / FK | References `platforms.platform_id` |

---

## Cardinality Relationships

| Parent Table | Child Table | Relationship Type |
|-------------|------------|------------------|
| games | game_genres | One-to-Many |
| genres | game_genres | One-to-Many |
| games | game_platforms | One-to-Many |
| platforms | game_platforms | One-to-Many |
| games ↔ genres | Through game_genres | Many-to-Many |
| games ↔ platforms | Through game_platforms | Many-to-Many |

---

# Normalization Notes (3NF)

- Genres are separated into the `genres` table to avoid repeated values.
- Platforms are separated into the `platforms` table to avoid duplicate platform names.
- Many-to-many relationships are resolved using bridge tables.
- Non-key columns depend only on each table's primary key.

---

## Data Source

### RAWG REST API

Video game data is sourced from the RAWG REST API.

The API provides:

- Game titles
- Release dates
- Ratings and review metrics
- Genre information
- Platform information
- Gameplay statistics

---

## Example Relationship Flow

Example:

```text
game_genres.game_id = 3498
        ↓
games.game_id = 3498
        ↓
games.game_name = Grand Theft Auto V
```

This design prevents repeated genre and platform information from being stored directly in the `games` table.