from pprint import pprint
from logique import get_movie_details

print("Test film existant :")
pprint(get_movie_details(550))

print("\nTest film inexistant :")
pprint(get_movie_details(99999999))