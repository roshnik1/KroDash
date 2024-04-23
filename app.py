import os
import csv
import time
import pandas as pd
import plotly
import plotly.express as px
import json
import csv
from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
from sqlalchemy.orm import relationship

app = Flask(__name__)

DATABASE_URI = "postgresql+psycopg2://postgres:Password123@127.0.0.1:5432/test"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

db = SQLAlchemy(app)
migrate = Migrate(app, db)
engine = db.create_engine(DATABASE_URI)
Session = sessionmaker(bind = engine)
session = Session()

relative_path = os.path.dirname(__file__)

# Use forward slashes for file paths, even on Windows
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_FOLDER'] = os.path.join(relative_path, 'uploads')

class Households(db.Model):
    __tablename__ = '400_households'
    HSHD_NUM = db.Column(db.Integer, primary_key=True)
    L = db.Column(db.Boolean)
    AGE_RANGE = db.Column(db.String(5))
    MARITAL = db.Column(db.String(10))
    INCOME_RANGE = db.Column(db.String(10))
    HOMEOWNER = db.Column(db.String(10))
    HSHD_COMPOSITION = db.Column(db.String(25))
    HH_SIZE = db.Column(db.String(5))
    CHILDREN = db.Column(db.String(5))
    
    def __str__(self):
        return self.HSHD_NUM
    
class Products(db.Model):
    __tablename__ = '400_products'
    PRODUCT_NUM = db.Column(db.Integer, primary_key=True)
    DEPARTMENT = db.Column(db.String(10))
    COMMODITY = db.Column(db.String(25))
    BRAND_TY = db.Column(db.String(10))
    NATURAL_ORGANIC_FLAG = db.Column(db.String(1))

class Transactions(db.Model):
    __tablename__ = '400_transactions'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BASKET_NUM = db.Column(db.Integer)
    HSHD_NUM = db.Column(db.Integer, db.ForeignKey('400_households.HSHD_NUM'))
    PRODUCT_NUM = db.Column(db.Integer, db.ForeignKey('400_products.PRODUCT_NUM'))
    PURCHASE = db.Column(db.Date)
    SPEND = db.Column(db.Numeric)
    UNITS = db.Column(db.Integer)
    STORE_R = db.Column(db.String(10))
    WEEK_NUM = db.Column(db.Integer)
    YEAR = db.Column(db.Integer)

    # Define relationships
    household = relationship("Households", foreign_keys=[HSHD_NUM])
    product = relationship("Products", foreign_keys=[PRODUCT_NUM])

# Create tables
with app.app_context():
    db.create_all()

def import_csv_data(csv_file, model_class):
    with app.app_context():
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Convert 'True' and 'False' strings to boolean values
                for key, value in row.items():
                    if value.lower() == 'true':
                        row[key] = True
                    elif value.lower() == 'false':
                        row[key] = False
                try:
                    db.session.add(model_class(**row))
                except Exception as e:
                    print(f"Error importing data from {csv_file}: {e}")
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error committing data to the database: {e}")

def initialize_database():
    data_folder = os.path.join(app.root_path, 'data')
    for filename in os.listdir(data_folder):
        if filename.endswith('.csv'):
            if 'households' in filename:
                import_csv_data(os.path.join(data_folder, filename), Households)
            elif 'products' in filename:
                import_csv_data(os.path.join(data_folder, filename), Products)
            elif 'transactions' in filename:
                import_csv_data(os.path.join(data_folder, filename), Transactions)

initialize_database()

# Create tables
with app.app_context():
    db.create_all()

# from models import Households, Transactions, Products

@app.route('/')
def redirect_login():
    return redirect(url_for('login'))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/predictive_modeling')
def predictive_modeling():
    return render_template('predictive_modeling.html', name = name)


@app.route('/example_pull')
def example_pull():
    household_10 = db.session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        join(Products, Products.PRODUCT_NUM == Transactions.PRODUCT_NUM).\
        filter(Households.HSHD_NUM == 10).all()
    
    # Print the variable to the console
    print(household_10)

    return render_template('example_pull.html', name = name, households = household_10)  

@app.route('/search_input', methods=['GET', 'POST'])
def search_input():
    return render_template('search_input.html', name = name, hhs = hhs)

@app.route('/search_pull', methods=['GET', 'POST'])
def search_pull():
    selected_num = request.form['hh']

    household_search = session.query(Households, Transactions, Products).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        join(Products, Products.PRODUCT_NUM == Transactions.PRODUCT_NUM).\
        filter(Households.HSHD_NUM == selected_num).all()

    return render_template('search_pull.html', name = name, households = household_search, hhs = hhs, selected_num = selected_num)  

@app.route('/upload')
def upload():
    return render_template('upload.html', name = name)
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        newFileName = fileNameAppend(secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(newFileName)))
        tableString = readNewCSVData(app.config['UPLOAD_FOLDER'] + '\\' + secure_filename(newFileName))
    return render_template('uploaded.html', name = name, tableString = tableString)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global name
    global hhs
    hhst = session.query(Households.HSHD_NUM).order_by(Households.HSHD_NUM).all()
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
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        i = 0
        tableType = 0
        readSuccess = False #if header matches
        rows = []
        for line in csv_reader:

            #set table type by reading first header in first line
            if i == 0 and line[0].lower() == 'hshd_num': #households
                tableType = 1
                readSuccess = True
            elif i == 0 and line[0].lower() == 'basket_num': #transactions
                tableType = 2
                readSuccess = True
            elif i == 0 and line[0].lower() == 'product_num': #products
                tableType = 3
                readSuccess = True

            if readSuccess == True:
                if i > 0:
                    rows.append(line)
            i += 1

        if readSuccess == True and len(rows) > 0:
            returnMessage = writeNewCSVData(tableType, rows)
            tableString = ''
            if returnMessage == 1:
                tableString = 'Households'
            elif returnMessage == 2:
                tableString = 'Transactions'
            elif returnMessage == 3:
                tableString = 'Products'
            return('Updated table "'+tableString+'"')
        else:
            return('Error in reading CSV file, headers do not meet expectation')

def writeNewCSVData(tableType, rows):
    newRows = []

    if tableType == 1: #households
        for row in rows:
            print(row)
            newRow = Households(HSHD_NUM = row[0], L = boolFix(row[1]), AGE_RANGE = row[2], MARITAL = row[3], INCOME_RANGE = row[4], HOMEOWNER = row[5], HSHD_COMPOSITION = row[6], HH_SIZE = row[7], CHILDREN = row[8])
            newRows.append(newRow)
    elif tableType == 2: #transactions
        for row in rows:
            newRow = Transactions(BASKET_NUM = row[0], HSHD_NUM = row[1], PURCHASE = row[2], PRODUCT_NUM = row[3], SPEND = row[4], UNITS = row[5], STORE_R = row[6], WEEK_NUM = row[7], YEAR = row[8])
            newRows.append(newRow)
    elif tableType == 3: #products
        for row in rows:
            newRow = Products(PRODUCT_NUM = row[0], DEPARTMENT = row[1], COMMODITY = row[2], BRAND_TY = row[3], NATURAL_ORGANIC_FLAG = row[4])
            newRows.append(newRow)

    for newRow in newRows:
        session.add(newRow)

    try:
        session.commit()
    except Exception as ex:
        app.logger.error(f"{ex.__class__.__name__}: {ex}")
        session.rollback()

    return tableType

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
    sales_region = session.query(func.count(Transactions.SPEND), Transactions.YEAR, Transactions.STORE_R).\
        filter(Transactions.YEAR < 2021).\
        group_by(Transactions.YEAR, Transactions.STORE_R)

    sales_df = pd.read_sql(sales_region.statement.compile(engine), session.bind)
    
    sales_fig = px.bar(sales_df, x='YEAR', y='count_1', 
    color='STORE_R', barmode='group',
    labels = {
        "YEAR": "Year",
        "count_1": "Total Sales"
    })
    sales_fig.update_layout(title_text="Sales per Year", title_x=0.5)
    sales_graphJSON = json.dumps(sales_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return sales_graphJSON

def region_graph():
    households_region = session.query(func.count(Households.HSHD_NUM), Transactions.STORE_R).\
        join(Transactions, Transactions.HSHD_NUM == Households.HSHD_NUM).\
        group_by(Transactions.STORE_R)

    region_df = pd.read_sql(households_region.statement.compile(engine), session.bind)
    
    region_fig = px.bar(region_df, x='STORE_R', y='count_1',
    labels = {
        "STORE_R": "Store Region",
        "count_1": "Number of stores"
    })
    region_fig.update_traces(marker_color="#007bff")
    region_fig.update_layout(title_text="Stores per Division", title_x=0.5)
    region_graphJSON = json.dumps(region_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return region_graphJSON

def commodity_graph():
    households_commodity = session.query(func.count(Products.COMMODITY), Products.COMMODITY).\
        join(Transactions, Transactions.PRODUCT_NUM == Products.PRODUCT_NUM).\
        group_by(Products.COMMODITY)

    commodity_df = pd.read_sql(households_commodity.statement.compile(engine), session.bind)
    commodity_df.loc[commodity_df['count_1'] < 10000, 'COMMODITY'] = "Other Commodities"
    
    commodity_fig = px.pie(commodity_df, values='count_1', names='COMMODITY', width=1000, height=800)
    commodity_fig.update_layout(title_text="Commodity Purchase (%of Total Sales)", title_x=0.5)
    commodity_graphJSON = json.dumps(commodity_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return commodity_graphJSON

if __name__ == '__main__':
   app.run()
