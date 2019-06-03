import tweepy
from game import Game
import os


game = Game()
game.step()
snapshot = game.ascii_snapshot()
print(snapshot)
print(f'{len(snapshot)} characters')

auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)
api.update_status(snapshot)
