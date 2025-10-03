import duckdb
import pandas as pd
from typing import Optional

from .cache import Cache


class Data:
    def __init__(
        self,
        src: str,
        cache: Optional[Cache] = Cache(),
    ):
        self.src = src
        self.cache = cache

    def exists(self) -> bool:
        return self.cache.exists("data.csv")

    def load(self) -> pd.DataFrame:
        if not self.exists():
            self.create()

        query = f"""
            SELECT *
            FROM read_csv_auto('{self.cache.path("data.csv")}')
        """

        return duckdb.query(query).to_df()

    def create(self) -> None:
        date_start = "2024-01-01"
        date_end = "2025-01-01"

        query = f"""
            WITH filtered AS (
                SELECT
                    *,
                    DATEDIFF(
                        'second',
                        CAST("Created Date" AS TIMESTAMP),
                        CAST("Closed Date" AS TIMESTAMP)
                    ) AS "Response Time"
                FROM read_csv_auto('{self.src}', types={{'Incident Zip': 'VARCHAR'}})
                WHERE
                    CAST("Created Date" AS DATE) BETWEEN '{date_start}'::DATE AND '{date_end}'::DATE
                    AND "Incident Zip" IS NOT NULL
                    AND "Created Date" IS NOT NULL
                    AND "Closed Date" IS NOT NULL
                    AND DATEDIFF(
                        'second',
                        CAST("Created Date" AS TIMESTAMP),
                        CAST("Closed Date" AS TIMESTAMP)
                    ) >= 0
            )
            SELECT
                "Incident Zip" as zip,
                DATE_TRUNC('month', CAST("Created Date" AS DATE)) AS month,
                AVG("Response Time") / 3600.0 AS avg_response_time_hours
            FROM filtered
            GROUP BY "Incident Zip", DATE_TRUNC('month', CAST("Created Date" AS DATE))
            ORDER BY zip, month
        """

        df = duckdb.query(query).to_df()

        # remove non-zip rows
        df = df[df["zip"].str.match(r"^\d{5}$")]

        # save to cache
        df.to_csv(self.cache.path("data.csv"), index=False)
