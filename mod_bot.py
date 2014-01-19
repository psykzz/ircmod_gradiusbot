from ircutils import client
from mod_functions import ModFunctions
from mod_tribunal import Tribunal
import ConfigParser
import sys, traceback

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
        self.mod_chan = config.get('Settings', 'mod_channel')

        channels_string = config.get('Settings', 'channels')
        self.channels_join = list(filter(None, (x.strip() for x in channels_string.splitlines())))

        self.mf = ModFunctions()

        tribunal_config = {
            'spam_message_rate'         : config.getint('Tribunal', 'spam_message_rate'),
            'spam_message_per_sec'      : config.getint('Tribunal', 'spam_message_per_sec'),
            'points_per_infraction'     : config.getint('Tribunal', 'points_per_infraction'),
            'point_deduction_rate'      : config.getint('Tribunal', 'point_deduction_rate'),
            'allcap_percent_threshold'  : config.getfloat('Tribunal', 'allcap_percent_threshold'),
            'allcap_min_length'         : config.getfloat('Tribunal', 'allcap_min_length'),
            }
        self.tribunal = Tribunal(tribunal_config, self.send_message_callback)

        client.SimpleClient.__init__(self, self.nick)

    def send_message_callback(self, target="", message=""):
        self.send_message(target, message)

    def message_printer(self, client, event):
        print "<{0}/{1}> {2}".format(event.source, event.target, event.message)

    def message_handler(self, client, event):
        # Add any functions from the mod_functions class here that you want executed each message
        # Use if statements wherever possible to avoid executing each function unless needed
        # Pass your function the self.send_message_callback to allow it to send messages to the channel

        # Blanket try/except block, other methods should implement more specific error checking
        try:
            # Check for private messages, execute things here that you don't want in main channel.
            if event.target == self.nick:
                if event.message[0] == "@":
                    self.mf.admin(event, self.send_message_callback)


            if event.message[0] == "!":
                self.mf.commands(event, self.send_message_callback)

            self.mf.flag_urls(event, self.send_message_callback)

            # Only moderate people other then the bot. Might want to add this to the tribunal system
            # and make it so that it doesnt moderate the +O or +V. Not sure.
            if event.target != self.nick:
                self.tribunal.check_messages(client, event)

        except:
            print "A generic error has occured:\n", traceback.format_exc()
            self.send_message(self.mod_chan, "A generic error has occured: " + str(sys.exc_info()))


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
