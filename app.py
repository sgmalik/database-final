import sqlite3
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
            return render_form(table)


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
            query = f"SELECT MEDIAN({column}) FROM {table}"
        elif stat == 'stddev':
            query = f"SELECT STDDEV({column}) FROM {table}"

        # If there is a query, execute it and print the result to the page
        if query:
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            return f"The {stat} of {column} is {result[0]}"
        else:
            conn.close()
            return "Invalid statistic selected."

    # Initial GET request or if no table is selected
    return render_form()

def render_form(selected_table=None):
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
            <label for="table">Select Table:</label>
            <select name="table" id="table" onchange="this.form.submit()">
                <option value="">Select a table...</option>
                <option value="game" {"selected" if selected_table == "game" else ""}>Game</option>
                <option value="player" {"selected" if selected_table == "player" else ""}>Player</option>
                <option value="team" {"selected" if selected_table == "team" else ""}>Team</option>
            </select>
            <br><br>
            <label for="column">Select Column:</label>
            <select name="column" id="column">
                <option value="">Select a column...</option>
                {" ".join(f'<option value="{col}">{col}</option>' for col in columns)}
            </select>
            <br><br>
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
            <input type="submit" value="Calculate">
        </form>
    '''

        


if __name__ == '__main__':
    app.run(debug=True)


