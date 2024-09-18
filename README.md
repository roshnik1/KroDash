# KroDash: Retail Data Web Dashboard

The Kroger Retail Data Dashboard provides an interactive visualization and analysis of Kroger’s retail data, offering insights into sales performance, customer behavior, and inventory management. This dashboard is designed to help stakeholders make informed decisions by providing a comprehensive overview of key metrics and trends in retail operations.

## Initial Questions

- What are Kroger's overall sales trends over the past few years?  
- Which product categories contribute the most to total sales?  
- How do sales vary across different divisions?  
- What are the key customer demographics and their purchasing behavior?  
- Are there any noticeable patterns in inventory turnover?  

## Dashboard Overview
![Dashboard Overview](images/dashboard-overview.jpg)

## Features

- **Sales Performance Analysis:** Visualize sales trends over time, including total sales, sales by product department, and sales by store location.
- **Inventory Management:** Track inventory levels, identify top-selling products, and monitor stock levels to optimize inventory management.
- **Interactive Filters:** Use interactive filters to drill down into specific years, product categories, and divisions.
- **Data Visualization:** Includes charts and graphs to represent data intuitively and facilitate quick analysis.

## Technologies

- **Backend:** Flask for web development and SQLAlchemy for ORM.
- **Frontend:** HTML, CSS, and JavaScript for a dynamic user interface; Bootstrap for responsive design and styling.
- **Deployment:** Hosted on Heroku with data stored in Azure PostgreSQL.

## Installation
>**Note:** To run this repository, you need to have PostgreSQL installed on your local machine or use a cloud-based PostgreSQL service such as Heroku Postgres, Amazon RDS, Google Cloud SQL, or Azure Database for PostgreSQL. This project specifically uses Azure Database for PostgreSQL. Ensure PostgreSQL is properly set up and accessible, then update the project's configuration file with the appropriate database connection details.

Follow these steps to set up KroDash on your local machine:

**1. Clone repository:** `git clone https://github.com/roshnik1/KroDash.git`

**2. Navigate into project directory:** `cd KroDash`

**3. Install Python dependencies:** `pip install -r requirements.txt`

**4. Start the application with:** `flask run`

**5. Finally, navigate to:**  `http://127.0.0.1:5000/`
