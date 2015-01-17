from mpd import MPDClient

import os.path

class MPDWrapper(MPDClient):
    def __init__(self):
        super(MPDWrapper,self).__init__()

    def prettyPrintSecs(self, secs):
        ret = ""
        ret += "%ds" % (int(secs)%60)
        m = int(secs)/60
        if m == 0: return ret
        ret = ("%dm " % (m%60)) + ret
        h = m/60
        if h == 0: return ret
        ret = ("%dh " % (h%24)) + ret
        d = h/24
        if d == 0: return ret
        return ("%dd " % d) + ret

    def timeString(self,time):
        s = time%60
        if time < 60: return "00:%02d" % s
        m = time/60
        if m < 60: return "%02d:%02d" % (m,s)
        h = m/60
        return "%02d:%02d:%02d" % (h,m,s)

    def unifySongInfo(self,info):
        ret = dict()
        ret['file']   = info['file']
        ret['artist'] = info.get('artist', '')
        ret['title']  = info.get('title', os.path.basename(ret['file']))
        if info.has_key('albumartist'):
            ret['albumartist'] = info['albumartist']
        elif info.has_key('musicbrainz_albumartistid') and \
             info['musicbrainz_albumartistid'] == \
             '89ad4ac3-39f7-470e-963a-56509c546377':
            ret['albumartist'] = 'Various Artists'
        else:
            ret['albumartist'] = ret['artist']
        ret['album']  = info.get('album', '')
        ret['time']   = int(info.get('time',0))
        ret['length'] = self.timeString(int(ret['time']))
        ret['year']   = "-"
        if info.has_key('date'):
            pos = info['date'].find("-")
            if pos != -1:
                ret['year'] = info['date'][:pos]
            else:
                ret['year'] = info['date']
        ret['track']  = '-'
        if info.has_key('track'):
            track_info = info['track']
            if type(track_info) == type(str()):
                pos = track_info.find("/")
                if pos != -1:
                    ret['track'] = track_info[:pos]
                else:
                    ret['track'] = track_info
            elif type(track_info) == type(list()) and \
            len(track_info) > 0:
                ret['track'] = track_info[0]
        ret['id'] = info['id']
        return ret
