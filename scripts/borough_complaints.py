import argparse
import duckdb
import pandas as pd


def query(
    input: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    query = f"""
    SELECT "Complaint Type" as "complaint type", Borough as borough, COUNT(*) AS count
    FROM read_csv_auto('{input}')
    WHERE CAST("Created Date" AS DATE) BETWEEN '{start}'::DATE AND '{end}'::DATE
    GROUP BY "Complaint Type", Borough
    ORDER BY "Complaint Type", Borough
    """

    return duckdb.query(query).to_df()


def main() -> None:
    cli = argparse.ArgumentParser(
        description="Filter complaints by a given date range."
    )
    cli.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the input CSV file containing complaint data.",
    )
    cli.add_argument(
        "-s",
        "--start",
        type=str,
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )
    cli.add_argument(
        "-e",
        "--end",
        type=str,
        required=True,
        help="End date in YYYY-MM-DD format.",
    )
    cli.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output file to save results. If not provided, results will be printed to console.",
    )
    args = cli.parse_args()

    result = query(
        input=args.input,
        start=args.start,
        end=args.end,
    )

    if args.output:
        result.to_csv(args.output, index=False)
    else:
        print(result.to_csv(index=False))


if __name__ == "__main__":
    main()
