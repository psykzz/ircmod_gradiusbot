import re

class ModFunctions():

    def __init__(self):
        print

    def admin(self, event, message_callback_function):
        # Remember this block is taking place inside a private message conversation
        # All messages need to be sent to source and not target since target is the bot
        message_callback_function(event.source, "I've recieved your PM")

    def commands(self, event, message_callback_function):
        print

    def flag_words(self, event, message_callback_function):
        print

    def flag_urls(self, event, message_callback_function):
        bad_urls = []
        print

    def check_for_spam(self, event, message_callback_function):
        print

    def stats_tracker(self, event):
        print "STATS"
