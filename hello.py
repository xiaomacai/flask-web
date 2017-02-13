from flask import Flask
from flask import render_template
from flask_script import Manager


app = Flask(__name__)
manager = Manager(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<username>')
def user(username):
    return render_template('user.html', name=username)


if __name__ == '__main__':
    manager.run()