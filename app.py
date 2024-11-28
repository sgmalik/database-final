#River Bumpas & Surya Malik
#CS 2500 Final Project

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template, make_response
import base64
import io




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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto text-center py-10">
            <h1 class="text-4xl font-bold text-gray-800 mb-6">Welcome to the Basketball Database App!</h1>
            <div class="flex justify-center space-x-4">
                <a href="/query" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-700">Query Page</a>
                <a href="/edit_data" class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-700">Edit Data Page</a>
                <a href="/graph" class="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-700">Graph Page</a>
            </div>
        </div>
    </body>
    </html>
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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-10">
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Query the Database</h1>
            <form method="POST" class="bg-white p-6 rounded-lg shadow-md">
                <label for="table" class="block text-gray-700 font-medium mb-2">Select Table:</label>
                <select name="table" id="table" onchange="this.form.submit()" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select a table...</option>
                    <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
                    <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
                    <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
                </select>
                
                <label for="column" class="block text-gray-700 font-medium mb-2">Select Column:</label>
                <select name="column" id="column" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select a column...</option>
                    {" ".join(f'<option value="{col}">{col}</option>' for col in columns)}
                </select>
                
                <label for="stat" class="block text-gray-700 font-medium mb-2">Select Statistic:</label>
                <select name="stat" id="stat" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select a statistic...</option>
                    <option value="min">Minimum</option>
                    <option value="max">Maximum</option>
                    <option value="mean">Mean</option>
                    <option value="median">Median</option>
                    <option value="stddev">Standard Deviation</option>
                </select>
                
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">Calculate</button>
            </form>
        </div>
    </body>
    </html>
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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto py-10">
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Edit Data</h1>
            <form method="POST" class="bg-white p-6 rounded-lg shadow-md">
                <label for="table" class="block text-gray-700 font-medium mb-2">Select Table:</label>
                <select name="table" id="table" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select a table...</option>
                    <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
                    <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
                    <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
                </select>
                
                <label for="action" class="block text-gray-700 font-medium mb-2">Select Action:</label>
                <select name="action" id="action" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select an action...</option>
                    <option value="add" {"selected" if action == "add" else ""}>Add Record</option>
                    <option value="remove" {"selected" if action == "remove" else ""}>Remove Record</option>
                    <option value="modify" {"selected" if action == "modify" else ""}>Modify Record</option>
                </select>
                
                <button type="submit" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700">Submit</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/graph')
def graph(): 
    plt.switch_backend('Agg') # ensures that the graph is not displayed in the browser and is saved as an image
    team_name = 'Los Angeles Lakers'
    teams = get_teams()
    wins = get_team_wins(team_name)

    # Ensure the data is in the correct format
    df = pd.DataFrame(wins, columns=['Year', 'Wins'])

    # Check if the DataFrame is created correctly
    print(df.head())

    # Create a simple line plot using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(df['Year'], df['Wins'], marker='o')
    plt.xlabel('Year')
    plt.ylabel('Wins')
    plt.title(f'{team_name} Wins Over the Years')

    # Convert the graph to a base64 encoded string
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Return the image as a response with a type of image/png
    return make_response(img.read()), 200, {'Content-Type': 'image/png'}


def get_teams():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM team")
    teams = cursor.fetchall()
    return [team[0] for team in teams]
    conn.close()

def get_team_wins(team_name):
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT year, SUM(wins) as total_wins
    FROM (
        SELECT strftime('%Y', game_date) as year, COUNT(*) as wins
        FROM game
        WHERE team_name_home = ? AND wl_home = 'W'
        GROUP BY year
        UNION ALL
        SELECT strftime('%Y', game_date) as year, COUNT(*) as wins
        FROM game
        WHERE team_name_away = ? AND wl_home = 'L'
        GROUP BY year
    )
    GROUP BY year
    ORDER BY year
    '''
    cursor.execute(query, (team_name, team_name))
    result = cursor.fetchall()
    conn.close()
    return result


if __name__ == '__main__':
    app.run(debug=True)


