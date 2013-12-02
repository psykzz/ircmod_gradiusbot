from ircutils import client
from mod_functions import ModFunctions
import ConfigParser

class ModBot(client.SimpleClient):

    def __init__(self, config_file):
        #Parse Configuration File
        config = ConfigParser.RawConfigParser()
        config.read(config_file)

        #Obtain Configuration Vaules
        self.server = config.get('Settings', 'server')
        self.port = int(config.get('Settings', 'port'))
        self.nick = config.get('Settings', 'nick')
        self.username = config.get('Settings', 'username')
        self.password = config.get('Settings', 'password')
        self.owner = config.get('Settings', 'owner')

        channels_string = config.get('Settings', 'channels')
        self.channels_join = list(filter(None, (x.strip() for x in channels_string.splitlines())))

        function_string = config.get('Settings', 'functions')
        self.function_list = list(filter(None, (x.strip() for x in function_string.splitlines())))

        self.mf = ModFunctions()

        client.SimpleClient.__init__(self, self.nick)

    def send_message_callback(self,target="",message=""):
        self.send_message(target,message)

    def message_printer(self, client, event):
        print "<{0}/{1}> {2}".format(event.source, event.target, event.message)

    def message_handler(self, client, event):
        print "<{0}/{1}> {2}".format(event.source, event.target, event.message)

        # Add any functions from the mod_functions class here that you want executed each message
        # Use if statements wherever possible to avoid executing each function unless needed
        # Pass your function the self.send_message_callback to allow it to send messages to the channel

        if event.message[0] == "@":
            self.mf.admin(event, self.send_message_callback)

        if event.message[0] == "!":
            self.mf.commands(event, self.send_message_callback)

        self.mf.ban_words(event, self.send_message_callback)

    def notice_printer(self, client, event):
        print "(NOTICE) {0}".format(event.message)

    def welcome_message(self, client, event):
        for chan in self.channels_join:
            self.join(chan)

    def bot_start(self):
        self["welcome"].add_handler(self.welcome_message)
        self["notice"].add_handler(self.notice_printer)
        self["message"].add_handler(self.message_printer)
        self["message"].add_handler(self.message_handler)
        self.connect(self.server, self.port, password=self.password)
        self.start()

if __name__ == "__main__":
    bot = ModBot('config.cfg')
    print "Bot starting..."
    bot.bot_start()