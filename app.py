import os
import csv
import psycopg2
import time
import pandas as pd
import plotly
import plotly.express as px
import json
import csv
from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, ForeignKey
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.utils import secure_filename
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# Define the SQLAlchemy database URI
DATABASE_URI = 'postgresql+psycopg2://roshnik:Hello123#@retail-data.postgres.database.azure.com:5432/postgres'

# Configure the Flask app with SQLAlchemy database URI
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

# Suppress SQLAlchemy's track modifications feature
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# Initialize Flask-Migrate with the Flask app and SQLAlchemy
migrate = Migrate(app, db)

# Create the engine for SQLAlchemy
engine = db.create_engine(DATABASE_URI)

# Create a session maker for SQLAlchemy
Session = sessionmaker(bind=engine)

# Create a session object
session = Session()

relative_path = os.path.dirname(__file__)

# Use forward slashes for file paths, even on Windows
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_FOLDER'] = os.path.join(relative_path, 'uploads')
 
class Households(db.Model):
    __tablename__ = 'households'

    # Convert column names to lowercase
    hshd_num = db.Column(db.Integer, primary_key=True)
    l = db.Column(db.Boolean)
    age_range = db.Column(db.String(5))
    marital = db.Column(db.String(10))
    income_range = db.Column(db.String(10))
    homeowner = db.Column(db.String(10))
    hshd_composition = db.Column(db.String(25))
    hh_size = db.Column(db.String(5))
    children = db.Column(db.String(5))

    # Define foreign key relationship with Transactions
    transactions = relationship("Transactions", back_populates="household")

class Products(db.Model):
    __tablename__ = 'products'

    # Convert column names to lowercase
    product_num = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(10))
    commodity = db.Column(db.String(25))
    brand_ty = db.Column(db.String(10))
    natural_organic_flag = db.Column(db.String(1))

    # Define foreign key relationship with Transactions
    transactions = relationship("Transactions", back_populates="product")

class Transactions(db.Model):
    __tablename__ = 'transactions'

    # Convert column names to lowercase
    id = db.Column(db.Integer, primary_key=True)
    basket_num = db.Column(db.Integer)
    hshd_num = db.Column(db.Integer, db.ForeignKey('households.hshd_num'))
    purchase = db.Column(db.Date)
    product_num = db.Column(db.Integer, db.ForeignKey('products.product_num'))
    spend = db.Column(db.Numeric)
    units = db.Column(db.Integer)
    store_r = db.Column(db.String(10))
    week_num = db.Column(db.Integer)
    year = db.Column(db.Integer)

    # Define relationships
    household = relationship("Households", back_populates="transactions")
    product = relationship("Products", back_populates="transactions")

@app.route('/')
def redirect_login():
    return redirect(url_for('login'))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/predictive_modeling', methods=['GET', 'POST'])
def predictive_modeling():
    global name
    if request.method == 'POST':
        name = request.form.get('name') 
    return render_template('predictive_modeling.html', name = name)


@app.route('/example_pull', methods=['GET', 'POST'])
def example_pull():
    global name
    name = ""
    if request.method == 'POST':
        name = request.form.get('name') 
    else:
        # Ensure name is not empty if it hasn't been set
        if not name:
            name = "Guest"
    
    household_10 = session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.hshd_num == Households.hshd_num).\
        join(Products, Products.product_num == Transactions.product_num).\
        filter(Households.hshd_num == 10).all()
    
    print("Household Data:", household_10)  # Add this debug statement

    return render_template('example_pull.html', name = name, households = household_10)  

@app.route('/search_input', methods=['GET', 'POST'])
def search_input():
    global name
    name = ""
    if request.method == 'POST':
        name = request.form.get('name') 
    else:
        # Ensure name is not empty if it hasn't been set
        if not name:
            name = "Guest"
    return render_template('search_input.html', name = name, hhs = hhs)

@app.route('/search_pull', methods=['GET', 'POST'])
def search_pull():
    global name
    name = ""
    if request.method == 'POST':
        name = request.form.get('name') 
    else:
        # Ensure name is not empty if it hasn't been set
        if not name:
            name = "Guest"
    selected_num = request.form['hh']

    household_search = session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.hshd_num == Households.hshd_num).\
        join(Products, Products.product_num == Transactions.product_num).\
        filter(Households.hshd_num == selected_num).all()

    return render_template('search_pull.html', name = name, households = household_search, hhs = hhs, selected_num = selected_num)  

@app.route('/upload', methods=['GET', 'POST'])
def upload(methods=['GET', 'POST']):
    global name
    name = ""
    if request.method == 'POST':
        name = request.form.get('name') 
    else:
        # Ensure name is not empty if it hasn't been set
        if not name:
            name = "Guest"
    return render_template('upload.html', name = name)
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    global name
    name = ""
    if request.method == 'POST':
        name = request.form.get('name') 
    else:
        # Ensure name is not empty if it hasn't been set
        if not name:
            name = "Guest"
    
    if request.method == 'POST':
        f = request.files['file']
        newFileName = fileNameAppend(secure_filename(f.filename))

        # Create the uploads directory if it doesn't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the file to the uploads directory
        f.save(os.path.join(upload_dir, secure_filename(newFileName)))

        tableString = readNewCSVData(os.path.join(upload_dir, secure_filename(newFileName)))

    return render_template('uploaded.html', name = name, tableString = tableString)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global name
    global hhs
    hhst = session.query(Households.hshd_num).order_by(Households.hshd_num).all()
    i = 0
    hhs = [item[i] for item in hhst]

    if request.method == 'POST':
        name = request.form.get('name') 

    sales_graph, region_graph, commodity_graph = get_graphs()

    if name:
        return render_template('dashboard.html', name = name, 
        sales_graph = sales_graph,
        region_graph = region_graph, 
        commodity_graph = commodity_graph)
    else:
        return redirect(url_for('login'))

def readNewCSVData(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f)
        i = 0
        tableType = 0
        readSuccess = False #if header matches
        rows = []
        for line in csv_reader:
            print("Reading line:", line)  # Debugging statement

            #set table type by reading first header in first line
            if i == 0:
                print("Checking header:", line[0])  # Debugging statement
                if line[0].upper() == 'HSHD_NUM': #households
                    tableType = 1
                    readSuccess = True
                    print("Header matched: 'HSHD_NUM'")  # Debugging statement
                elif line[0].upper() == 'BASKET_NUM': #transactions
                    tableType = 2
                    readSuccess = True
                    print("Header matched: 'BASKET_NUM'")  # Debugging statement
                elif line[0].upper() == 'PRODUCT_NUM': #products
                    tableType = 3
                    readSuccess = True
                    print("Header matched: 'PRODUCT_NUM'")  # Debugging statement

            if readSuccess:
                if i > 0:
                    rows.append(line)
                    print("Added row to rows list:", line)  # Debugging statement
            i += 1

        if readSuccess and len(rows) > 0:
            print("Preparing to write data for table type:", tableType)  # Debugging statement
            returnMessage = writeNewCSVData(tableType, rows)
            tableString = ''
            if returnMessage == 1:
                tableString = 'Households'
            elif returnMessage == 2:
                tableString = 'Transactions'
            elif returnMessage == 3:
                tableString = 'Products'
            print("Update successful for table:", tableString)  # Debugging statement
            return 'Updated table "' + tableString + '"'
        else:
            print("Error: Headers do not meet expectation or no rows found")  # Debugging statement
            return 'Error in reading CSV file, headers do not meet expectation'

def writeNewCSVData(tableType, rows):
    try:
        if tableType == 1:  # households
            for row in rows:
                newRow = Households(
                    hshd_num=row[0],
                    l=boolFix(row[1]),
                    age_range=row[2],
                    marital=row[3],
                    income_range=row[4],
                    homeowner=row[5],
                    hshd_composition=row[6],
                    hh_size=row[7],
                    children=row[8]
                )
                session.add(newRow)
        elif tableType == 2:  # transactions
            for row in rows:
                newRow = Transactions(
                    basket_num=row[0],
                    hshd_num=row[1],
                    purchase=row[2],
                    product_num=row[3],
                    spend=row[4],
                    units=row[5],
                    store_r=row[6],
                    week_num=row[7],
                    year=row[8]
                )
                session.add(newRow)
        elif tableType == 3:  # products
            for row in rows:
                newRow = Products(
                    product_num=row[0],
                    department=row[1],
                    commodity=row[2],
                    brand_ty=row[3],
                    natural_organic_flag=row[4]
                )
                session.add(newRow)

        session.commit()
        return tableType  # Returning tableType might not be necessary
    except SQLAlchemyError as ex:
        session.rollback()
        error_message = f"Error updating table type {tableType}: {str(ex)}"
        app.logger.error(error_message)
        return error_message

def fileNameAppend(filename):
    name, ext = os.path.splitext(filename)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    return "{name}_{id}{ext}".format(name=name, id=timestr, ext=ext)

def boolFix(obj):
    if obj == 'TRUE' or '1':
        return True
    else:
        return False

def get_graphs():
    sales = sales_graph()
    region = region_graph()
    commodity = commodity_graph()

    return sales, region, commodity

def sales_graph():
    sales_region = session.query(func.count(Transactions.spend), Transactions.year, Transactions.store_r).\
        filter(Transactions.year < 2021).\
        group_by(Transactions.year, Transactions.store_r)

    sales_df = pd.read_sql(sales_region.statement.compile(engine), session.bind)
    
    sales_fig = px.bar(sales_df, x='year', y='count_1', 
    color='store_r', barmode='group',
    labels = {
        "year": "Year",
        "count_1": "Total Sales"
    })
    sales_fig.update_layout(title_text="Sales per Year", title_x=0.5)
    sales_graphJSON = json.dumps(sales_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return sales_graphJSON

def region_graph():
    households_region = session.query(func.count(Households.hshd_num), Transactions.store_r).\
        join(Transactions, Transactions.hshd_num == Households.hshd_num).\
        group_by(Transactions.store_r)

    region_df = pd.read_sql(households_region.statement.compile(engine), session.bind)
    
    region_fig = px.bar(region_df, x='store_r', y='count_1',
    labels = {
        "store_r": "Store Region",
        "count_1": "Number of stores"
    })
    region_fig.update_traces(marker_color="#007bff")
    region_fig.update_layout(title_text="Stores per Division", title_x=0.5)
    region_graphJSON = json.dumps(region_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return region_graphJSON

def commodity_graph():
    households_commodity = session.query(func.count(Products.commodity), Products.commodity).\
        join(Transactions, Transactions.product_num == Products.product_num).\
        group_by(Products.commodity)

    commodity_df = pd.read_sql(households_commodity.statement.compile(engine), session.bind)
    commodity_df.loc[commodity_df['count_1'] < 10000, 'commodity'] = "Other Commodities"
    
    commodity_fig = px.pie(commodity_df, values='count_1', names='commodity', width=1000, height=800)
    commodity_fig.update_layout(title_text="Commodity Purchase (%of Total Sales)", title_x=0.5)
    commodity_graphJSON = json.dumps(commodity_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return commodity_graphJSON

if __name__ == '__main__':
   app.run()
