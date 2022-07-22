import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: [%(asctime)s] - %(message)s')
connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection_count += 1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.error(f'Cannot find an article with ID {post_id}')
      return render_template('404.html'), 404
    else:
      logging.info(f'Retrieved article "{post["title"]}"')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('Rendering the "About Us" page')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info(f'Created a new article with title "{title}"')

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def health_check():
    try:
        connection = get_db_connection()
        connection.execute('SELECT * FROM posts').fetchone()
        connection.close()
        return jsonify({'result': 'OK - healthy'})
    except:
        return jsonify({'result': 'ERROR - unhealthy'}), 500

@app.route('/metrics')
def metrics():
    conn = get_db_connection()
    cur = conn.cursor()
    post_count = cur.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    return jsonify({
        'db_connection_count': connection_count,
        'post_count': post_count,
    })

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
