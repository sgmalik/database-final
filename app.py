#River Bumpas & Surya Malik
#CS 2500 Final Project

import sqlite3
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)
# Define database
DATABASE = 'final_project.db'

# Helper function to connect to the database
def connect_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Route to the home page
@app.route('/')
def home():
    return '''
    <h1>Welcome to the Basketball Database App!</h1>
    <a href="/query">Go to Query Page</a>
    <a href="/edit_data">Go to Edit Data Page</a>
'''

# Route to the query page
@app.route('/query', methods=['GET', 'POST'])
def query():
    # If the request is POST, the user has submitted the form and we process the data
    if request.method == 'POST':
        table = request.form.get('table')
        column = request.form.get('column')
        stat = request.form.get('stat')

        if not column or not stat:
            # If column or stat is not selected, show the form again
            return render_query_form(table)


        conn = connect_db()
        cursor = conn.cursor()

        query = None  # Initialize query with None

        # Possible queries
        if stat == 'min':
            query = f"SELECT MIN({column}) FROM {table}"
        elif stat == 'max':
            query = f"SELECT MAX({column}) FROM {table}"
        elif stat == 'mean':
            query = f"SELECT AVG({column}) FROM {table}"
        elif stat == 'median':
            df = pd.read_sql_query(f"SELECT {column} FROM {table}", conn)
            median = df[column].median()
            return f"The median of {column} is {median}"
        elif stat == 'stddev':
            query = f"SELECT STDDEV({column}) FROM {table}"

        # If there is a query, (excluding median) execute it and print the result to the page
        if query:
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            return f"The {stat} of {column} is {result[0]}"
        else:
            conn.close()
            return "Invalid statistic selected."

    # Initial GET request or if no table is selected
    return render_query_form()

def render_query_form(selected_table=None):
    conn = connect_db()
    cursor = conn.cursor()

    columns = []
    if selected_table:
        # Get numeric columns from the selected table
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = [description[1] for description in cursor.fetchall() if description[2] in ('INTEGER', 'REAL')]

    conn.close()

    # Return form with table selected and column dropdown populated
    return f'''
        <form method="POST">
            <!-- Table dropdown -->
            <label for="table">Select Table:</label>
            <select name="table" id="table" onchange="this.form.submit()">
                <option value="">Select a table...</option>
                <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
                <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
                <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
            </select>
            <br><br>
            <!-- Column dropdown --> 
            <label for="column">Select Column:</label>
            <select name="column" id="column">
                <option value="">Select a column...</option>
                <!-- Using the columns list above that is made once the table is selected to populate the column dropdown -->
                {" ".join(f'<option value="{col}">{col}</option>' for col in columns)}
            </select>
            <br><br>
            <!-- Stat dropdown -->
            <label for="stat">Select Statistic:</label>
            <select name="stat" id="stat">
                <option value="">Select a statistic...</option>
                <option value="min">Minimum</option>
                <option value="max">Maximum</option>
                <option value="mean">Mean</option>
                <option value="median">Median</option>
                <option value="stddev">Standard Deviation</option>
            </select>
            <br><br>
            <!-- Once submitted, the form will follow the POST route and execute the query -->
            <input type="submit" value="Calculate">
        </form>
 
       '''
@app.route('/edit_data', methods=['GET', 'POST'])
def edit_data():
    # Grabbing selected values from the form
    selected_table = request.form.get('table')
    action = request.form.get('action')

    # If the form has been submitted, go here
    if request.method == 'POST':
        # Checking if user has selected a table and an action
        if not selected_table or not action:
            return render_edit_form(selected_table=selected_table, action=action) + "<p>Please select both a table and an action.</p>"
        
        # TODO: Add logic to handle the selected action (add, remove, modify)
        return f"Action '{action}' selected for table '{selected_table}'."

    return render_edit_form()
    

def render_edit_form(selected_table=None, action=None):
    return f'''
    <form method="POST">
        <!-- Table dropdown -->
        <label for="table">Select Table:</label>
        <select name="table" id="table">
            <option value="">Select a table...</option>
            <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
            <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
            <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
        </select>
        
        <!-- Action dropdown -->
        <label for="action">Select Action:</label>
        <select name="action" id="action">
            <option value="">Select an action...</option>
            <option value="add" {"selected" if action == "add" else ""}>Add Record</option>
            <option value="remove" {"selected" if action == "remove" else ""}>Remove Record</option>
            <option value="modify" {"selected" if action == "modify" else ""}>Modify Record</option>
        </select>
        
        <button type="submit">Submit</button>
    </form>
    '''



if __name__ == '__main__':
    app.run(debug=True)


