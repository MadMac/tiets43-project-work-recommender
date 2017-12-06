import numpy as np
from game_recommender import GameRecommender

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main_page():

	return render_template('index.html')

if __name__ == "__main__":
    app.run()