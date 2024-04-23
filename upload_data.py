import psycopg2
import os

# Establish connection to PostgreSQL Azure database
conn = psycopg2.connect(user="roshnik", 
                        password="Hello123#", 
                        host="retail-data.postgres.database.azure.com", 
                        port=5432, 
                        database="postgres")
# Create a cursor object
cur = conn.cursor()

# Construct the DROP TABLE query
drop_query = f"DROP TABLE IF EXISTS transactions"

# Execute the DROP TABLE query
cur.execute(drop_query)

# Commit the transaction
conn.commit()

# Define table creation queries
table_queries = [
    """
    CREATE TABLE IF NOT EXISTS "households" (
        HSHD_NUM INTEGER PRIMARY KEY,
        L BOOLEAN,
        AGE_RANGE VARCHAR(5),
        MARITAL VARCHAR(10),
        INCOME_RANGE VARCHAR(10),
        HOMEOWNER VARCHAR(10),
        HSHD_COMPOSITION VARCHAR(25),
        HH_SIZE VARCHAR(5),
        CHILDREN VARCHAR(5)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS "products" (
        PRODUCT_NUM INTEGER PRIMARY KEY,
        DEPARTMENT VARCHAR(10),
        COMMODITY VARCHAR(25),
        BRAND_TY VARCHAR(10),
        NATURAL_ORGANIC_FLAG VARCHAR(1)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS "transactions" (
        ID SERIAL PRIMARY KEY,
        BASKET_NUM INTEGER,
        HSHD_NUM INTEGER REFERENCES "households" (HSHD_NUM),
        PURCHASE DATE,
        PRODUCT_NUM INTEGER REFERENCES "products" (PRODUCT_NUM),
        SPEND NUMERIC,
        UNITS INTEGER,
        STORE_R VARCHAR(10),
        WEEK_NUM INTEGER,
        YEAR INTEGER
    )
    """
]

# Execute table creation queries
for query in table_queries:
    cur.execute(query)

# Commit the transaction
conn.commit()

# Define the path to the data folder
data_folder = os.path.join(os.path.dirname(__file__), 'data')

# Load data into tables using COPY command
def load_data_using_copy(conn, table_name, file_path):
    # Exclude the 'ID' column from the COPY command if the table is 'transactions'
    if table_name == 'transactions':
        copy_command = f"COPY {table_name} (BASKET_NUM, HSHD_NUM, PURCHASE, PRODUCT_NUM, SPEND, UNITS, STORE_R, WEEK_NUM, YEAR) FROM STDIN WITH CSV HEADER"
    else:
        copy_command = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
    with open(file_path, 'r') as f:
        with conn.cursor() as cur:
            cur.copy_expert(sql=copy_command, file=f)

# Load data for households table
households_csv_path = os.path.join(data_folder, 'households.csv')
load_data_using_copy(conn, 'households', households_csv_path)

# Load data for products table
products_csv_path = os.path.join(data_folder, 'products.csv')
load_data_using_copy(conn, 'products', products_csv_path)

# Load data for transactions table
transactions_csv_path = os.path.join(data_folder, 'transactions.csv')
load_data_using_copy(conn, 'transactions', transactions_csv_path)

# Commit the transaction
conn.commit()

# Close cursor and connection
cur.close()
conn.close()
