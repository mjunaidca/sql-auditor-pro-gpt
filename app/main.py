# main.py
from fastapi import FastAPI, HTTPException, status
from sqlmodel import text, Session, create_engine

from app.core.config import logger_config
from app import settings

logger = logger_config(__name__)

app = FastAPI(
    servers=[
        {
            "url": settings.SERVER_URL,
            "description": "CloudFlare Server"
        },
    ]
)


@app.post("/execute_sql")
def execute_sql_query(query: str, DATABASE_URL: str):
    """
    Execute a raw SQL query and return the results including column names.
    """
    try:
        connection_string = str(DATABASE_URL).replace(
            "postgresql", "postgresql+psycopg"
        )

        engine = create_engine(
            connection_string,
            pool_recycle=300,    # Recycle connections after 5 minutes
            pool_size=100,       # Increase pool size to 100
            max_overflow=100,    # Allow an additional 100 connections beyond the pool size
            pool_timeout=30      # Increase timeout duration to 30 seconds
        )
        with Session(engine) as db:
            logger.info(f"Connected to database")
            logger.info(f"Executing raw SQL query: {query}")

            results = db.exec(text(query))

            column_names = list(results.keys())
            data = [dict(zip(column_names, row)) for row in results.fetchall()]

            logger.info(f"Query results: columns={column_names}, data={data}")

            return {"columns": column_names, "data": data}

    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error executing query: {str(e)}"
        )


@app.get("/database_schema")
def get_database_schema(DATABASE_URL: str):
    """
    Get the database schema including total tables, columns in each table, and column details.
    """
    try:
        connection_string = str(DATABASE_URL).replace(
            "postgresql", "postgresql+psycopg"
        )

        engine = create_engine(
            connection_string,
            pool_recycle=300,    # Recycle connections after 5 minutes
            pool_size=100,       # Increase pool size to 100
            max_overflow=100,    # Allow an additional 100 connections beyond the pool size
            pool_timeout=30      # Increase timeout duration to 30 seconds
        )
        with Session(engine) as db:
            logger.info(f"Connected to database")

            logger.info("Fetching database schema information.")

            # Get total number of tables
            total_tables_query = """
            SELECT COUNT(*)
            FROM pg_catalog.pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
            """
            total_tables_result = db.exec(text(total_tables_query)).fetchone()
            total_tables = total_tables_result[0]

            # Get columns count, column names, and column types for each table
            columns_per_table_query = """
            SELECT t.tablename, a.attname AS column_name, pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
            FROM pg_catalog.pg_tables t
            JOIN pg_catalog.pg_attribute a ON t.tablename = a.attrelid::regclass::text
            WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
            AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY t.tablename, a.attnum;
            """
            columns_per_table_result = db.exec(
                text(columns_per_table_query)).fetchall()

            # Organize the result into a structured format
            schema_info = {
                "total_tables": total_tables,
                "tables": {}
            }

            for row in columns_per_table_result:
                table_name = row.tablename
                if table_name not in schema_info["tables"]:
                    schema_info["tables"][table_name] = {
                        "columns": []
                    }
                schema_info["tables"][table_name]["columns"].append({
                    "column_name": row.column_name,
                    "data_type": row.data_type
                })

            logger.info(f"Database schema information: {schema_info}")
            return schema_info

    except Exception as e:
        logger.error(f"Error fetching database schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching database schema: {str(e)}"
        )


# Policy Router for API Policies
@app.get("/policy", include_in_schema=False)
def get_policy():
    """
    Get the policy information for the API.
    """
    policy_info = {
        "policy": "This Microservice is for educational purposes only.",
        "contact": "mr.junaidshaukat@gmail.com",
        "email": "https://www.linkedin.com/in/mrjunaid/",
        "license": "MIT",
    }
    return policy_info
