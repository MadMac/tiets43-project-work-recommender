import numpy as np
from annoy import AnnoyIndex

class GameRecommender(object):

    def __init__(self, fn_game_indexes='game_indexes.npy', fn_user_indexes='user_indexes.npy',
                 fn_users_list='users_list.npy', fn_games_list='games_list.npy',
                 fn_data='data.npy', fn_annoy_index='annoy_index.ann'):
        self.file_names = {
            'game_indexes' : fn_game_indexes,
            'user_indexes' : fn_user_indexes,
            'users_list' : fn_users_list,
            'games_list' : fn_games_list,
            'data' : fn_data,
            'annoy_index' : fn_annoy_index
        }
        self.game_indexes = np.load(fn_game_indexes).item()
        self.user_indexes = np.load(fn_user_indexes).item()
        self.users_list = np.load(fn_users_list)
        self.games_list = np.load(fn_games_list)
        self.data = np.load(fn_data)

    def recommendations_by_username(self, username, n, rating_limit=8):
        """ Uses the generated index for finding nearest neighbors and then tries
        to find game recommendations from those users

        Args:
            username: Username string from the dataset
            n: Number of recommendations generated
            rating_limit: Only recoomend games that atleast on of the similar users have rated higher than this value
        Returns:
            List of game recommendations indexes
        """
        index = self.user_indexes[username]
        user_row = self.data[index]
        u = AnnoyIndex(len(self.games_list))
        u.load(self.file_names['annoy_index'])

        r_indexes = []
        r_users = []
        i = 0
        while len(r_indexes) < n:
            # If the number of generated neighbors is higher than
            # the number of users we have, we cannot generate as 
            # many recommendations as desired
            if (i+100) > len(self.users_list):
                break
            u_neighbors = u.get_nns_by_item(index, i+100)
            while i < len(u_neighbors):
                neighbor = self.data[u_neighbors[i]]
                for k in range(len(neighbor)):
                    if neighbor[k] > rating_limit and user_row[k] == 0 and k not in r_indexes:
                        r_indexes.append(k)
                        r_users.append(neighbor)
                        if len(r_indexes) >= n:
                            break
                i = i + 1
                if len(r_indexes) >= n:
                    break
        
        # Aggregate the similar users, and average the ratings they have given to the 
        # Recommended games
        a_neighbor = self.__average_similar_user_ratings(r_users)
        new_games = []
        for i in range(len(a_neighbor)):
            if user_row[k] == 0 and a_neighbor[i] != 0:
                new_games.append((i, a_neighbor[i]))
        new_games.sort(key=lambda x: x[1], reverse=True)
        new_games = new_games[:n]
        
        for index in new_games:
            print("Game: {0:40} Simlar users rating: {1:4.3}".format(self.games_list[index[0]], index[1]))
        return new_games

    def recommendations_by_vector(self, vec, n, rating_limit=8):
        """ Finds users who have given similar reviews as in the given vector and finds
        n game recommendations from those users

        Args:
            vec: List of ratings (length has to be the same as length of games_list)
            n: Number of recommendations generated
            rating_limit: Only recommend games that atleast on of the similar users have rated higher than this
        Returns:
            List of game indexes that are recommended
        """
        u = AnnoyIndex(len(self.games_list))
        u.load(self.file_names['annoy_index'])

        r_indexes = []
        r_users = []
        i = 0
        while len(r_indexes) < n:
            # If the number of generated neighbors is higher than
            # the number of users we have, we cannot generate as 
            # many recommendations as desired
            if (i+100) > len(self.users_list):
                break
            u_neighbors = u.get_nns_by_vector(vec, i+100)
            while i < len(u_neighbors):
                neighbor = self.data[u_neighbors[i]]
                for k in range(len(neighbor)):
                    if neighbor[k] > rating_limit and vec[k] == 0 and k not in r_indexes:
                        r_indexes.append(k)
                        r_users.append(neighbor)
                        if len(r_indexes) >= n:
                            break
                i = i + 1
                if len(r_indexes) >= n:
                    break
        
        # Aggregate the similar users, and average the ratings they have given to the 
        # Recommended games
        a_neighbor = self.__average_similar_user_ratings(r_users)
        new_games = []
        for i in range(len(a_neighbor)):
            if vec[k] == 0 and a_neighbor[i] != 0:
                new_games.append((i, a_neighbor[i]))
        new_games.sort(key=lambda x: x[1], reverse=True)
        new_games = new_games[:n]
        
        for index in new_games:
            print("Game: {0:40} Simlar users rating: {1:4.3}".format(self.games_list[index[0]], index[1]))
        return new_games

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
        t = AnnoyIndex(len(self.games_list))
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
    r_games = rec.recommendations_by_vector(test_row, 10)

    print("----------------------------------------------")

    # Random username used for recommendation
    r_username = random.choice(rec.users_list)
    print("Random username recommendations:")
    print("Test Username: {0}".format(r_username))
    r_games = rec.recommendations_by_username(r_username, 10)
