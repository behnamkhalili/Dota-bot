# Dota2 Data Tracker & Dashboard (In Progress)

## Project Overview
This project collects Dota2 match data from multiple APIs (Stratz, OpenDota, Steam), stores it in a SQLite database using SQLAlchemy and Pydantic for data validation, and visualizes it through interactive dashboards. Core orchestration, player tracking, and some dashboard features are still under development.

## Features
- Fetching match data from multiple APIs and storing it in SQLite
- ETL pipeline for data cleaning and preparation (in progress)
- Interactive dashboards for match and player analysis (Dash, Plotly, Dash Bootstrap Components) [in progress]
- Planned: player/match tracking system and automated notifications via Telegram bot

## Technologies & Tools
- **Programming:** Python
- **Database:** SQLite, SQLAlchemy
- **Data Validation:** Pydantic
- **APIs:** Stratz API, OpenDota API, Steam API
- **Visualization:** Dash, Plotly, Dash Bootstrap Components (DBC)
- **Workflow / Orchestration:** In progress (ETL pipeline)
- **Dependency Management:** Poetry

## Contributing
- This is an ongoing project. Contributions and improvements are welcome!
- Fork the repository and submit pull requests for new features or fixes.

## Status
- **Core data fetching and storage:** Implemented
- **ETL orchestration:** In progress
- **Dashboard features:** In progress
- **Player/match tracking & Telegram bot:** Planned
