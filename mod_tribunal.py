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

        # Spam config, the default here is to alert of more then 5 messages in a 10 second burst, gaining 5 points for each infraction
        self._spam_message_rate = config.get('spam_message_rate', 5)
        self._spam_message_per_sec = config.get('spam_message_per_sec', 10)
        self._points_per_infraction = config.get('points_per_infraction', 5)
        self._point_deduction_rate = config.get('point_deduction_rate', 5)


        # regex for finding urls
        self.__url_regex_pattern = r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+' 
        self._url_regex_pattern = re.compile(self.__url_regex_pattern)

        # callback messaging function to message through IRC
        self._callback_message_func = callback_message_func

    def _send(self, target, message):
        return self._callback_message_func(target, message)

    def requires_action(self, name, limit=50):
        if self._user_points[name] > limit:
            return True
        return False
        
    def _add_points(self, name, points=1):
        if name not in self._user_points:
            self._user_points[name] = points
        else:
            self._user_points[name] += points
            
    def _remove_points(self, name, points=1):
        if name not in self._user_points:
            self._user_points[name] = points
        else:
            self._user_points[name] += points

    def check_messages(self, client, event):
        local_score = 0
        error_log = []
        # check was there all caps
        if _check_for_allcaps(event):
            local_score += self._points_per_infraction        # 5 points for all caps
            error_log.append('Using AllCaps')
        # check for spam :(
        if _check_for_individual_spam(event):
            local_score += self._points_per_infraction        # 5 points for all the things!
            error_log.append('Spamming in chat')
        # check for spamming urls 5 maybe too many?
        if _capture_urls(event) > 5:
            local_score += 1
            error_log.append('Spamming URLS')

        if local_score > 0:
            self._add_points(event.source, local_score)
            self._send(event.source, 'OMFG N00B u dun goofed, if you dont stop this shit! >>  '+[error for error in error_log])
        else:
            self._remove_points(event.source, self._point_deduction_rate)
        
    def _check_for_allcaps(self, event):
        return all(word.isupper() for word in event.message)

    def _check_for_individual_spam(self, event):
        now = datetime.datetime.now()
        allowance = self._spam_message_rate
        if event.source in self.user_spam:
            time_passed = now - self.user_spam[event.source][1]
            allowance = self.user_spam[event.source][0]
            allowance += time_passed.seconds * (self._spam_message_rate / self._spam_message_per_sec)
            if allowance > self._spam_message_rate:
                allowance = self._spam_message_rate
            allowance -= 1
            self.user_spam[event.source] = (allowance, now)
        else:
            self.user_spam[event.source] = (allowance, now)
        if (allowance > 1):
            return True 
        else:
            return False 

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


        
        
