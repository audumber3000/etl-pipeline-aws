import boto3
import pymysql
import pandas as pd
import os

# RDS connection details (use environment variables for security)
db_host = os.environ.get('DB_HOST', 'etl-database.c1gymuo46joi.ap-south-1.rds.amazonaws.com')
db_user = os.environ.get('DB_USER', 'admin')
db_password = os.environ.get('DB_PASSWORD', 'Audumber')  # Replace with secrets manager for production
db_name = os.environ.get('DB_NAME', 'etl-database-pipeline')
db_port = int(os.environ.get('DB_PORT', 3306))
region = 'ap-south-1'

# Initialize the RDS client with boto3
rds_client = boto3.client('rds', region_name=region)

def create_table(connection, final_query, data_set, just_col, s_string):
    try:
        # Create table query
        cursor = connection.cursor()
        print(final_query)
        cursor.execute(final_query)
        print("Table created!")

        # Insert data into the table
        data_list = []
        numpy_list_of_list = data_set.to_numpy()
        for i in numpy_list_of_list:
            data_list.append(tuple(i))

        # Correct query format for insertion
        insert_query = f"INSERT INTO dummy_table6 ({just_col}) VALUES ({s_string})"
        print(insert_query)  # For debugging
        cursor.executemany(insert_query, data_list)

        connection.commit()  # Commit the changes to the database
        print("Data inserted successfully!")
    except pymysql.MySQLError as e:
        print(f"SQL error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("In final block")
        cursor.close()  # Close the cursor to free resources

def preprocess_data(connection):
    # Load the CSV file into a DataFrame
    data_set = pd.read_csv('/Users/audii3000/Downloads/bank.csv')

    # Dynamically build the column names for SQL
    table_col_list = [f"{col} varchar(255)" for col in data_set.columns]
    
    # Build the column names and placeholders for the insert query
    just_col = ', '.join(data_set.columns)
    s_string = ', '.join(['%s'] * len(data_set.columns))

    # Create the table query
    query = f"CREATE TABLE IF NOT EXISTS dummy_table6({', '.join(table_col_list)})"
    final_query = query  # No need to replace anything
    create_table(connection, final_query, data_set, just_col, s_string)

def lambda_handler():
    print("Connecting to RDS...")
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )
        print("Connected to RDS successfully!")

        # Example Query: Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            current_time = cursor.fetchone()
            print(f"Current Database Time: {current_time}")

        preprocess_data(connection)

    except pymysql.MySQLError as e:
        print(f"Error connecting to RDS: {e}")
    finally:
        if connection:
            connection.close()
            print("Connection closed.")

lambda_handler()