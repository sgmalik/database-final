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
    # Variables to store selected table and action
    selected_table = request.args.get('table') or request.form.get('table')
    action = request.args.get('action') or request.form.get('action')
    # request.args.get() is used to get the value of a query parameter in the URL of a GET request, while request.form.get() is used to get the value of a form field in a POST request.

    # we use GET requests to handle our actions (ie. which table and what action we want to preform), and POST requests to handle the form submissions
    
    # Initialize result variables
    result_message = None
    # initial_record = None  # Single record for Modify
    # updated_record = None
    columns = []

    if selected_table:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch column names for the selected table
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = [column[1] for column in cursor.fetchall()]  # Fetch column names

        if action == 'modify' and request.method == 'POST':
            # Fetch the primary key value
            record_id = request.form.get('recordIDModify')

            # # Fetch initial state of the record
            # cursor.execute(f"SELECT * FROM {selected_table} WHERE id = ?", (record_id,))
            # initial_record = cursor.fetchone()

            # Prepare SQL for updating the record
            updates = ', '.join([f"{col} = ?" for col in columns])
            values = [request.form.get(f'modify_{col}') for col in columns]
            values.append(record_id)

            # Execute the update
            if selected_table == 'game':
                cursor.execute(f"UPDATE {selected_table} SET {updates} WHERE game_id = ?", values)
            elif selected_table == 'player':
                cursor.execute(f"UPDATE {selected_table} SET {updates} WHERE player_id = ?", values)
            elif selected_table == 'team':
                cursor.execute(f"UPDATE {selected_table} SET {updates} WHERE id = ?", values)
            # need to fix here as well, not every table has id column, need to somehow figure out which column is primary key and save that column name to insert here
            conn.commit()

            # # Fetch updated state of the record
            # cursor.execute(f"SELECT * FROM {selected_table} WHERE id = ?", (record_id,))
            # updated_record = cursor.fetchone()

            result_message = f"Record {record_id} modified in {selected_table}."
        conn.close()

    return render_edit_form(selected_table, action, result_message)

def render_edit_form(selected_table=None, action=None, message=None, initial_record=None, updated_record=None):
    columns = []
    pk_column = None
    pk_vals = []

    if selected_table:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch column names
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = [column[1] for column in cursor.fetchall()]

        # Fetch primary key values
        if selected_table == 'game':
            pk_column = columns[4] # game_id
        else:
            pk_column = columns[0] # first col is pk for player and team
        if pk_column:
            cursor.execute(f"SELECT {pk_column} FROM {selected_table}")
            pk_vals = [val[0] for val in cursor.fetchall()]
        conn.close()

    # Render form
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
            
            <!-- Table and Action Selection -->
            <form method="GET" class="bg-white p-6 rounded-lg shadow-md">
                <label for="table" class="block text-gray-700 font-medium mb-2">Select Table:</label>
                <select name="table" id="table" class="block w-full p-2 border rounded mb-4">
                    <option value="">Select a table...</option>
                    <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
                    <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
                    <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
                </select>

                <div class="flex space-x-4">
                    <button type="submit" name="action" value="add" class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700">Add</button>
                    <button type="submit" name="action" value="modify" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">Modify</button>
                    <button type="submit" name="action" value="remove" class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-700">Remove</button>
                </div>
            </form>

            <!-- Render fields dynamically based on the action -->
            <form method="POST" class="mt-6">
                {'<h2 class="text-lg font-bold text-gray-700 mb-4">Add New Record</h2>' +
                 ''.join(f'<label for="add_{col}" class="block text-gray-700 font-medium mb-2">{col}:</label><input type="text" name="add_{col}" class="block w-full p-2 border rounded mb-4">' for col in columns)
                 if action == 'add' else ''}

                {'<h2 class="text-lg font-bold text-gray-700 mb-4">Modify Record</h2>' +
                 f'<p class="text-gray-700 font-medium mb-2">Select a record to modify:</p><select name="recordIDModify" class="block w-full p-2 border rounded mb-4">' +
                 ''.join(f'<option value="{pk}">{pk}</option>' for pk in pk_vals) +
                 '</select>' +
                 ''.join(f'<label for="modify_{columns[i]}" class="block text-gray-700 font-medium mb-2">{columns[i]}:</label><input type="text" name="modify_{columns[i]}" class="block w-full p-2 border rounded mb-4">' for i in range(1, len(columns)))
                 if action == 'modify' else ''}

                {'<h2 class="text-lg font-bold text-gray-700 mb-4">Remove Record</h2>' +
                 f'<p class="text-gray-700 font-medium mb-2">Select a record to remove:</p><select name="recordID" class="block w-full p-2 border rounded mb-4">' +
                 ''.join(f'<option value="{pk}">{pk}</option>' for pk in pk_vals) +
                 '</select>' if action == 'remove' else ''}

                {'<button type="submit" class="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-700 mt-4">Submit</button>' if action else ''}
            </form>

            <!-- Display Result Messages -->
            {'<p class="mt-4 text-lg font-medium text-green-600">' + message + '</p>' if message else ''}

            <!-- Initial and Updated Records for Modify -->
            {'<h2 class="mt-6 text-xl font-bold text-gray-700">Initial Record:</h2>' +
             f'<pre class="bg-gray-200 p-4 rounded">{initial_record}</pre>'
             if action == 'modify' and initial_record else ''}

            {'<h2 class="mt-6 text-xl font-bold text-gray-700">Updated Record:</h2>' +
             f'<pre class="bg-gray-200 p-4 rounded">{updated_record}</pre>'
             if action == 'modify' and updated_record else ''}
        </div>
    </body>
    </html>
    '''

# initial and updated record logic not working, need to either:
# a) make it so that you can't edit a PK field
# b) make it so that if the PK field is edited, the updated PK is displayed in the updated record

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    teams = get_teams()
    team_name = request.form.get('team') if request.method == 'POST' else None
    players = get_players()
    player_name = request.form.get('player') if request.method == 'POST' else None

    if team_name:
        wins = get_team_wins(team_name)
        df = pd.DataFrame(wins, columns=['Year', 'Wins'])

        # Generate the graph
        plt.switch_backend('Agg')
        plt.figure(figsize=(20, 8))
        plt.bar(df['Year'], df['Wins'], color='blue')
        plt.xlabel('Year')
        plt.ylabel('Wins')
        plt.title(f'{team_name} Wins Over the Years')
        plt.xticks(rotation=60)

        # Convert graph to a base64 string for embedding in HTML
        img = io.BytesIO() # Create a BytesIO object to store the image
        plt.savefig(img, format='png') # Save the image to the BytesIO object
        img.seek(0) # Move the cursor to the start of the BytesIO object
        plt.close() # Close the plot to free up memory
        graph_url = base64.b64encode(img.getvalue()).decode('utf8') # Encode the image as a base64 string

        graph_image = f'<img src="data:image/png;base64,{graph_url}" alt="Graph">' # Embed the graph in the HTML
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
                <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">View Team Graph</button>
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

def get_players():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM player")
    players = cursor.fetchall()
    conn.close()
    return [player[0] + ' ' + player[1] for player in players]

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

def get_player_weights(first_name, last_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT year, weight FROM player WHERE first_name=? AND last_name=?", (first_name, last_name))
    result = cursor.fetchall()
    conn.close()
    return result


if __name__ == '__main__':
    app.run(debug=True)


