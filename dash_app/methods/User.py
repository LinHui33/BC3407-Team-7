from flask_login import UserMixin

# Create User class with UserMixin # Todo: place in methods folder
class User(UserMixin):
    def __init__(self, username, access_level, password):
        self.username = username
        self.access_level = access_level
        self.password = password
        self.authenticated = False

    def get_id(self):
        return (self.username)

    def get_access_level(self):
        return (self.access_level)
