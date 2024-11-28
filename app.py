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

def navbar():
    return '''
    <nav class="bg-blue-500 p-4">
        <div class="container mx-auto flex justify-between">
            <a href="/" class="text-white font-bold">Home</a>
            <div>
                <a href="/query" class="text-white ml-4">Query Page</a>
                <a href="/edit_data" class="text-white ml-4">Edit Data</a>
                <a href="/graph" class="text-white ml-4">Graph Page</a>
            </div>
        </div>
    </nav>
    '''

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
    result = None
    selected_table = None
    selected_column = None
    selected_stat = None
    if request.method == 'POST':
        selected_table = request.form.get('table')
        selected_column = request.form.get('column')
        selected_stat = request.form.get('stat')

        if not selected_column or not selected_stat:
            # If column or stat is not selected, show the form again
            return render_query_form(selected_table=selected_table, result=result)


        conn = connect_db()
        cursor = conn.cursor()

        query = None  # Initialize query with None

        # Possible queries
        if selected_stat == 'min':
            query = f"SELECT MIN({selected_column}) FROM {selected_table}"
        elif selected_stat == 'max':
            query = f"SELECT MAX({selected_column}) FROM {selected_table}"
        elif selected_stat == 'mean':
            query = f"SELECT AVG({selected_column}) FROM {selected_table}"
        elif selected_stat == 'median':
            df = pd.read_sql_query(f"SELECT {selected_column} FROM {selected_table}", conn)
            median = df[selected_column].median()
            result = f"The median of {selected_column} is {median}"
        elif selected_stat == 'stddev':
            query = f"SELECT STDDEV({selected_column}) FROM {selected_table}"

        # If there is a query, (excluding median) execute it and print the result to the page
        if query:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            result = f"The {selected_stat} of {selected_column} is {result}"
        conn.close()

    # Initial GET request or if no table is selected
    return render_query_form(selected_table=selected_table, result=result)

def render_query_form(selected_table=None, result=None):
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
        {navbar()}
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
            {'<p class="mt-4 text-lg font-medium">' + result + '</p>' if result else ''}
        </div>
    </body>
    </html>
    '''

@app.route('/edit_data', methods=['GET', 'POST'])
def edit_data():
    selected_table = request.form.get('table')
    action = request.form.get('action')
    result_message = None
    initial_records = None
    updated_records = None

    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()

        if selected_table and action:
            cursor.execute(f"SELECT * FROM {selected_table}")
            initial_records = cursor.fetchall()

            if action == 'add':
                # Add logic: Insert a new record (placeholder values for now)
                cursor.execute(f"INSERT INTO {selected_table} VALUES (?, ?, ?)", ('Sample1', 'Sample2', 'Sample3'))
                result_message = f"Record added to {selected_table}."
            elif action == 'remove':
                # Remove logic: Delete the first record
                cursor.execute(f"DELETE FROM {selected_table} WHERE rowid = (SELECT MIN(rowid) FROM {selected_table})")
                result_message = f"Record removed from {selected_table}."
            elif action == 'modify':
                # Modify logic: Update the first record (placeholder update)
                cursor.execute(f"UPDATE {selected_table} SET column1 = ? WHERE rowid = (SELECT MIN(rowid) FROM {selected_table})", ('UpdatedValue',))
                result_message = f"Record modified in {selected_table}."

            conn.commit()
            cursor.execute(f"SELECT * FROM {selected_table}")
            updated_records = cursor.fetchall()
            conn.close()

    return render_edit_form(selected_table, action, result_message, initial_records, updated_records)
    

def render_edit_form(selected_table=None, action=None, message=None, initial_records=None, updated_records=None):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        {navbar()}
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
            {'<p class="mt-4 text-lg font-medium text-green-600">' + message + '</p>' if message else ''}
            <h2 class="mt-6 text-xl font-bold text-gray-700">Initial Records:</h2>
            <pre class="bg-gray-200 p-4 rounded">{initial_records}</pre>
            <h2 class="mt-6 text-xl font-bold text-gray-700">Updated Records:</h2>
            <pre class="bg-gray-200 p-4 rounded">{updated_records}</pre>
        </div>
    </body>
    </html>
    '''

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    teams = get_teams()
    team_name = request.form.get('team') if request.method == 'POST' else None

    if team_name:
        wins = get_team_wins(team_name)
        df = pd.DataFrame(wins, columns=['Year', 'Wins'])

        # Generate the graph
        plt.switch_backend('Agg')
        plt.figure(figsize=(10, 5))
        plt.plot(df['Year'], df['Wins'], marker='o')
        plt.xlabel('Year')
        plt.ylabel('Wins')
        plt.title(f'{team_name} Wins Over the Years')

        # Convert graph to a base64 string for embedding in HTML
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        graph_url = base64.b64encode(img.getvalue()).decode('utf8')

        graph_image = f'<img src="data:image/png;base64,{graph_url}" alt="Graph">'
    else:
        graph_image = '<p class="text-red-500">Please select a team to view the graph.</p>'

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        {navbar()}
        <div class="container mx-auto py-10">
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Team Wins Graph</h1>
            <form method="POST" class="bg-white p-6 rounded-lg shadow-md">
                <label for="team" class="block text-gray-700 font-medium mb-2">Select Team:</label>
                <select name="team" id="team" class="block w-full p-2 border rounded mb-4">
                    {" ".join(f'<option value="{team}" {"selected" if team == team_name else ""}>{team}</option>' for team in teams)}
                </select>
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">View Graph</button>
            </form>
            <div class="mt-6">
                {graph_image}
            </div>
        </div>
    </body>
    </html>
    '''


def get_teams():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM team")
    teams = cursor.fetchall()
    conn.close()
    return [team[0] for team in teams]

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


