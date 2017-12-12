import numpy as np
import json
from collections import OrderedDict
from game_recommender import GameRecommender
import itertools
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/")
def main_page():
	gameRecommender = GameRecommender()

	allGames = OrderedDict(sorted(gameRecommender.game_indexes.items(), key=lambda t: t[0]))

	allUsers = OrderedDict(sorted(itertools.islice(gameRecommender.user_indexes.items(), 1000), key=lambda t: t[0]))
	
	# print (gameRecommender.game_indexes)
	return render_template('index.html', games=allGames, users=allUsers)

@app.route("/get-recommendation", methods=["POST"])
def get_recommendation():
	gameRecommender = GameRecommender()
	allGames = request.get_json(force=True)

	gamesRow = []
	filters = {};
	for i in range(len(gameRecommender.games_list)):
		selectedGame = None

		for game in allGames:
			# print(game['id'])
			if i == int(game['id']):
				selectedGame = game
				# print (game)
			
			if 'minplayers' not in filters and 'minplayers' in game:
				filters['minplayers'] = int(game['minplayers'])
			if 'maxplayers' not in filters and 'maxplayers' in game:
				filters['maxplayers'] = int(game['maxplayers'])
	
		if selectedGame is None:
			gamesRow.append(0)
		else:
			gamesRow.append(int(selectedGame['rating']))

	r_games = gameRecommender.get_recommendations(gamesRow, 10, 6, filters)

	result_games = []
	for game in r_games:
		game_tuple = (gameRecommender.games_list[game[0]], game[1])
		result_games.append(game_tuple)

	print (json.dumps(result_games))
	return json.dumps(result_games)

@app.route("/get-recommendation-user", methods=["POST"])
def get_recommendation_user():
	gameRecommender = GameRecommender()

	selectedUser = request.get_json(force=True)
	if len(selectedUser) > 0:
		selectedUserString = selectedUser[0]['name']

		filters = {};
		if 'minplayers' in selectedUser[0]:
			filters['minplayers'] = int(selectedUser[0]['minplayers'])
		if 'maxplayers' in selectedUser[0]:
			filters['maxplayers'] = int(selectedUser[0]['maxplayers'])
	
		r_games = gameRecommender.get_recommendations(selectedUserString, 10, 6, filters)

		users_ratings = gameRecommender.data[gameRecommender.user_indexes[selectedUserString]]
		# gamesRow = gameRecommender.user_indexes
		users_games = []
		for i in range(len(gameRecommender.games_list)):
			if users_ratings[i] > 0:
				users_game = (gameRecommender.games_list[i], users_ratings[i])
				users_games.append(users_game)
		result_games = []
		for game in r_games:
			game_tuple = (gameRecommender.games_list[game[0]], game[1])
			result_games.append(game_tuple)

		results = [result_games, users_games]
		# print (results)
		return json.dumps(results)
	else:
		return ""

if __name__ == "__main__":
    app.run()