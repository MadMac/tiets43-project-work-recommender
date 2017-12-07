import numpy as np
import json
from collections import OrderedDict
from game_recommender import GameRecommender

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def main_page():
	gameRecommender = GameRecommender()

	allGames = OrderedDict(sorted(gameRecommender.game_indexes.items(), key=lambda t: t[0]))
	# print (gameRecommender.game_indexes)
	return render_template('index.html', games=allGames)

@app.route("/get-recommendation", methods=["POST"])
def get_recommendation():
	gameRecommender = GameRecommender()
	allGames = request.get_json(force=True)
	print (allGames)

	gamesRow = []

	for i in range(len(gameRecommender.games_list)):
		selectedGame = None

		for game in allGames:
			# print(game['id'])
			if i == int(game['id']):
				selectedGame = game
				# print (game)
	
		if selectedGame is None:
			gamesRow.append(0)
		else:
			gamesRow.append(int(selectedGame['rating']))
	print (len(gamesRow))
	print (len(gameRecommender.game_indexes))
	r_games = gameRecommender.recommendations_by_vector(gamesRow, 10)


	return "test"

if __name__ == "__main__":
    app.run()