from flask import Flask, render_template
import random

app = Flask(__name__)
# list of cat images

@app.route('/')

def index():
	return render_template('index.html')
	
if __name__ == "__main__":
	app.run(host="0.0.0.0")
