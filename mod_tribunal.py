from __future__ import division   # Why is this not standard.

import datetime
import re

class Tribunal(object):
    """System for keeping players in check"""
    def __init__(self, config, callback_message_func):
        super(Tribunal, self).__init__()

        # We need someway of keeping track if someone is being bad.
        self._user_points   = dict()        # single values         ['psykzz'] = 0
        self._user_spam     = dict()        # of tuples             ['psykzz'] = (10,timestamp)
        self._common_urls   = dict()        # single values         ['google.com'] = 5
        self._blocked_urls  = set()         # single values         ('google.com',)

        # Spam config, the default here is to alert of more then 5 messages in a 10 second burst, gaining 5 points for each infraction
        self._spam_message_rate = config.get('spam_message_rate', 5)
        self._spam_message_per_sec = config.get('spam_message_per_sec', 10)
        self._points_per_infraction = config.get('points_per_infraction', 5)
        self._point_deduction_rate = config.get('point_deduction_rate', 5)
        self._allcap_percent_threshold = float(config.get('allcap_percent_threshold', 1))
        self._allcap_min_length = config.get('allcap_min_length', 3)

        # regex for finding urls
        self.__url_regex_pattern = r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+'
        self._url_regex_pattern = re.compile(self.__url_regex_pattern)

        # callback messaging function to message through IRC
        self._callback_message_func = callback_message_func

    def _send(self, target, message):
        return self._callback_message_func(target, message)

    def requires_action(self, name, limit=50):
        if self._get_points(name) > limit:
            return True
        return False

    ''' URL System '''
    def add_url(self, url):
        self._blocked_urls.add(url)

    def remove_url(self, url):
        self._blocked_urls.discard(url)     # only need to remove once, as its only added once.

    def check_url(self, url):
        if url in self._blocked_urls:
            return True
        return False

    ''' Point System '''
    def _get_points(self, name):
        if name is None:
            return
        if name not in self._user_points:
            return 0
        return self._user_points[name]

    def _set_points(self, name, points):
        if name is None:
            return
        if points is None:
            return
        self._user_points[name] = points

    def _add_points(self, name, points=1):
        if name not in self._user_points:
            self._user_points[name] = points
        else:
            self._user_points[name] += points

    def _remove_points(self, name, points=1):
        if name not in self._user_points:
            self._user_points[name] = 0
        else:
            self._user_points[name] -= points

    def check_messages(self, client, event):
        local_score = 0
        error_log = []

        # check was there all caps
        if self._check_for_allcaps(event):
            local_score += self._points_per_infraction        # 5 points for all caps
            error_log.append('Using AllCaps')

        # check for spam :(
        spam = self._check_for_individual_spam(event)
        self._send(event.target, str(spam))
        if spam is False:       # Stupid that its false but i want to try and be clever...
            local_score += self._points_per_infraction        # 5 points for all the things!
            error_log.append('Spamming in chat')


        # Just do the URL check...
        self._capture_urls(event)
        # check for spamming urls 5 maybe too many?
        '''
        if self._capture_urls(event) > 5:
            local_score += 1
            error_log.append('Spamming URLS')
        '''

        if local_score > 0:
            self._add_points(event.source, local_score)
            self._send(event.source, 'OMFG N00B u dun goofed, if you dont stop this shit! Points : {}, errors : {}'.format(self._get_points(event.source), error_log))
        else:
            self._remove_points(event.source, self._point_deduction_rate)

    def _check_for_allcaps(self, event):
        if len(event.message) <= self._allcap_min_length:
            return False
        _len = sum(1 for word in event.message if word.isalpha())       # Ignore none alpha characters
        _caps = sum(1 for word in event.message if word.isupper())      # Count the number of upper case characters.
        return ((_caps / _len) >= self._allcap_percent_threshold)

    def _check_for_individual_spam(self, event):
        now = datetime.datetime.now()
        allowance = self._spam_message_rate
        if event.source in self._user_spam:
            time_passed = now - self._user_spam[event.source][1]
            allowance = self._user_spam[event.source][0]
            allowance += time_passed.seconds * (self._spam_message_rate / self._spam_message_per_sec)
            if allowance > self._spam_message_rate:
                allowance = self._spam_message_rate
            allowance -= 1
            self._user_spam[event.source] = (allowance, now)
        else:
            self._user_spam[event.source] = (allowance, now)
        if (allowance < 1):
            return False
        else:
            return allowance

    ''' I think this whole system needs to be reworked '''
    def _capture_urls(self, event, return_urls=False):
        # not sure if convert to string is needed.
        urls = self._url_regex_pattern.findall( str(event.message) )
        for url in urls:
            if url in self._capture_urls:
                self._capture_urls[url] += 1
            else:
                self._capture_urls[url] = 1

        # Maybe helpful later
        if return_urls:
            return urls
        else:
            return len(urls)

    def _save_urls(self):
        pass




