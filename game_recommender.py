import numpy as np
from annoy import AnnoyIndex

class GameRecommender(object):

    def __init__(self):
        """ Tries to load the necessary data when the object is created
        Throws:
            FileNotFoundError: If some of the necessary files are not found
        """
        self.game_indexes = np.load('game_indexes.npy').item()
        self.user_indexes = np.load('user_indexes.npy').item()
        self.users_list = np.load('users_list.npy')
        self.games_list = np.load('games_list.npy')
        self.data = np.load('data.npy')

    def create_annoy_index(self):
        """ Creates the index for Annoy, also saves the index to disk
        """
        t = AnnoyIndex(len(self.games_list))
        for i in range(len(self.users_list)):
            t.add_item(i, self.data[i])
        t.build(10)
        t.save('annoy_index.ann')

    def recommendations_by_username(self, username, n):
        """ Uses the generated index for finding nearest neighbors and then tries
        to find game recommendations from those users

        Args:
            username: Username string from the dataset
            n: number of game recommendations generated
        Returns:
            List of game recommendations indexes
        """
        index = self.user_indexes[username]
        user_row = self.data[index]
        u = AnnoyIndex(len(self.games_list))
        u.load('annoy_index.ann')

        r_indexes = []
        i = 0
        while len(r_indexes) < n:
            u_neighbors = u.get_nns_by_item(index, i+100)
            while i < len(u_neighbors):
                neighbor = self.data[u_neighbors[i]]
                for k in range(len(neighbor)):
                    if neighbor[k] != 0 and user_row[k] == 0 and k not in r_indexes:
                        r_indexes.append(k)
                        if len(r_indexes) >= n:
                            break
                i = i + 1
                if len(r_indexes) >= n:
                    break
        #for index in r_indexes:
        #    print(self.games_list[index])
        return r_indexes

    def recommendations_by_vector(self, vec, n):
        """ TODO Annoy has a function that searches neighbors by given vector,
        so searches can be done without adding an user to the data
        """
        pass

    def add_item_to_annoy(self, username, vector):
        """ TODO Annoy has a function that adds vector to the generated index,
        the index then has to be saved on disk, but it means that theres no need
        for a full generation of the index again (If the number of games doesn't change)
        """
        pass

    def add_row_to_data(self, username, row):
        """ Adds a new user to the data
        Note: AnnoyIndex has to be generated again to search with the username
        """
        self.data = np.vstack((self.data, np.array(row)))
        self.users_list.append(username)
        self.user_indexes[username] = len(self.users_list) - 1

    def save_current_user_data(self):
        """ Saves the current user data to disk
        """
        np.save('data.npy', self.data)
        np.save('users_list.npy', self.users_list)
        np.save('user_indexes.npy', self.user_indexes)
