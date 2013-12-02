import re

class ModFunctions():

    def __init__(self):
        print

    def admin(self, event, message_callback_function):
        message_callback_function(event.target, "Command was " + event.message.split("@")[1])

    def commands(self, event, message_callback_function):
        message_callback_function(event.target, "Command was " + event.message.split("!")[1])

    def flag_words(self, event, message_callback_function):
        message_callback_function(event.target, event.source + " said " + event.message)

    def flag_urls(self, event, message_callback_function):
        bad_urls = []
        message_callback_function(event.target, event.source + " said " + event.message)

    def check_for_spam(self, event, message_callback_function):
        message_callback_function(event.target, event.source + " said " + event.message)

    def stats_tracker(self, event):
        print "STATS"
