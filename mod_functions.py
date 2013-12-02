class ModFunctions():

    def __init__(self):
        print

    def admin(self, event, message_callback_function):
        message_callback_function(event.target, "Command was " + event.message.split("@")[1])

    def commands(self, event, message_callback_function):
        message_callback_function(event.target, "Command was " + event.message.split("!")[1])

    def ban_words(self, event, message_callback_function):
        message_callback_function(event.target, event.source + " said " + event.message)

    def stats_tracker(self, event):
        print "STATS"
