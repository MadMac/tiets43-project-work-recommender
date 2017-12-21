import numpy as np
import sys
from annoy import AnnoyIndex

class GameRecommender(object):

    def __init__(self, fn_game_indexes='game_indexes.npy', fn_user_indexes='user_indexes.npy',
                 fn_users_list='users_list.npy', fn_games_list='games_list.npy',
                 fn_data='data.npy', fn_annoy_index='annoy_index.ann', fn_game_information='game_information.npy',
                 fn_game_mechanics='game_mechanics.npy'):
        self.file_names = {
            'game_indexes' : fn_game_indexes,
            'user_indexes' : fn_user_indexes,
            'users_list' : fn_users_list,
            'games_list' : fn_games_list,
            'data' : fn_data,
            'annoy_index' : fn_annoy_index,
            'game_information' : fn_game_information,
            'game_mechanics' : fn_game_mechanics
        }
        try:
            self.game_indexes = np.load(fn_game_indexes).item()
            self.user_indexes = np.load(fn_user_indexes).item()
            self.users_list = np.load(fn_users_list)
            self.games_list = np.load(fn_games_list)
            self.data = np.load(fn_data)
            self.game_information = np.load(fn_game_information).item()
            self.game_mechanics = np.load(fn_game_mechanics)
        except IOError:
            sys.exit("Could not load some or all of the necessary data files, please run data_generation.py first.")

    def get_recommendations(self, row_or_user, n, rating_limit=8, filters={}):
        """ Finds users who have given similar reviews as in the given vector and finds
        n game recommendations from those users

        Args:
            row_or_user: List of ratings (length has to be the same as length of games_list) or username
            n: Number of recommendations generated
            rating_limit: Only recommend games that atleast on of the similar users have rated higher than this
        Returns:
            List of game indexes that are recommended
        """
        u = AnnoyIndex(len(self.games_list))
        try:
            u.load(self.file_names['annoy_index'])
        except FileNotFoundError:
            self.build_annoy_index()
            u.load(self.file_names['annoy_index'])

        if isinstance(row_or_user, str):
            index = self.user_indexes[row_or_user]
            vec = self.data[index]
        else:
            vec = row_or_user

        r_indexes = []
        r_users = []
        i = 0
        generated_n = 10
        while len(r_indexes) < n:
            # If the number of generated neighbors is higher than
            # the number of users we have, we cannot generate as 
            # many recommendations as desired
            if (generated_n) > len(self.users_list):
                break
            # Rapidly increase the number of generated neighbors
            generated_n = generated_n * generated_n
            if isinstance(row_or_user, str):
                u_neighbors = u.get_nns_by_item(index, generated_n)
            else:
                u_neighbors = u.get_nns_by_vector(row_or_user, generated_n)

            while i < len(u_neighbors):
                neighbor = self.data[u_neighbors[i]]

                for k in range(len(neighbor)):
                    if (neighbor[k] > rating_limit and 
                        vec[k] == 0 and 
                        k not in r_indexes and 
                        self.__filter_results(k, filters)):
                        # Found a new game recommendation
                        r_indexes.append(k)
                        r_users.append(neighbor)
                        if len(r_indexes) >= n:
                            break
                i = i + 1
                if len(r_indexes) >= n:
                    break
        
        # Aggregate the similar users, and average the ratings they have given to the 
        # Recommended games, there might be some extra games in this aggregated results,
        # so we have to filter them again, and pick only the top n from those.
        a_neighbor = self.__average_similar_user_ratings(r_users)
        new_games = []
        for i in range(len(a_neighbor)):
            if vec[i] == 0 and a_neighbor[i] != 0 and self.__filter_results(i, filters):
                new_games.append((i, a_neighbor[i]))
        new_games.sort(key=lambda x: x[1], reverse=True)
        new_games = new_games[:n]
        
        for index in new_games:
            print("Game: {0:40} Simlar users rating: {1:4.3}".format(self.games_list[index[0]], index[1]))
        return new_games

    def __filter_results(self, game_index, filters):
        if 'minplayers' in filters and self.game_information[self.games_list[game_index]][0] is not None:
            if self.game_information[self.games_list[game_index]][0] < filters['minplayers']:
                return False
        if 'maxplayers' in filters and self.game_information[self.games_list[game_index]][1] is not None:
            if self.game_information[self.games_list[game_index]][1] > filters['maxplayers']:
                return False
        if 'mechanics' in filters and self.game_information[self.games_list[game_index]][2] is not None:
            for mechanic in filters['mechanics']:
                if mechanic not in self.game_information[self.games_list[game_index]][2]:
                    return False
        return True

    def __average_similar_user_ratings(self, r_users):
        combined_user = []
        for g in self.games_list:
            combined_user.append([])
        for user in r_users:
            for i in range(len(user)):
                if user[i] != 0:
                    combined_user[i].append(user[i])
        average_list = []
        for ratings in combined_user:
            if ratings != []:
                average_list.append(sum(ratings)/len(ratings))
            else:
                average_list.append(0)
        return average_list

    def build_annoy_index(self, n_trees=10):
        """ Creates the index for Annoy, also saves the index to disk
        Args:
            n_trees: Default=10, Higher values give more precision, but take longer
        """
        t = AnnoyIndex(len(self.games_list), metric='angular')
        for i in range(len(self.users_list)):
            t.add_item(i, self.data[i])
        t.build(n_trees)
        t.save(self.file_names['annoy_index'])

    def add_user(self, username, vec):
        """ Adds a new user to the data and rebuilds the AnnoyIndex
        Args:
            username: Username used for indexing
            vec: Vector of ratings for the games
        """
        self.__add_row_to_data(username, vec)
        self.__save_current_user_data()
        self.build_annoy_index()

    def __add_row_to_data(self, username, row):
        """ Adds a new user to the data
        Note: AnnoyIndex has to be generated again to search with the username
        """
        self.data = np.vstack((self.data, np.array(row)))
        self.users_list = np.append(self.users_list, username)
        self.user_indexes[username] = len(self.users_list) - 1

    def __save_current_user_data(self):
        """ Saves the current user data to disk
        """
        np.save(self.file_names['data'], self.data)
        np.save(self.file_names['users_list'], self.users_list)
        np.save(self.file_names['user_indexes'], self.user_indexes)

if __name__ == "__main__":
    # Example and simple test of the recommedations
    import random
    rec = GameRecommender()

    # Random edited row used for recommendation
    test_row = random.choice(rec.data)
    for i in range(0,4):
        test_row[random.randint(0, len(test_row)-1)] = random.randint(1, 10)
    print("Random edited vector of data recommendations:")
    print("Test Vector: {0}".format(test_row))
    r_games = rec.get_recommendations(test_row, 10)

    print("----------------------------------------------")

    # Random username used for recommendation
    r_username = random.choice(rec.users_list)
    print("Random username recommendations:")
    print("Test Username: {0}".format(r_username))
    r_games = rec.get_recommendations(r_username, 10)
