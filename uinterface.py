import pytz
from datetime import datetime
from pytz import timezone

from simpleusers import usermgr

DEFAULT_STRF = "%H:%M"
TWELVE_STRF = "%I:%M %p"


class su_interface:
    def __init__(self):
        self.db = usermgr()

    def make_user(self, uid, passw, tz):
        self.db.make_user(uid, passw)
        self.db.set_user_prop(uid, 'tz', tz)

    def set_user_tz(self, uid, newtz):
        if newtz in pytz.all_timezones or newtz.upper() in pytz.all_timezones:
            res = self.db.set_user_prop(uid, 'tz', newtz)
            if "error" in res['message']:
                return {"message": res['message']}
            else:
                return {"message": "done."}
        else:
            return {"message": f"error: no such tz {newtz}"}

    def set_user_timetype(self, uid, normal=True):
        tzstr = DEFAULT_STRF if normal else TWELVE_STRF
        res = self.db.set_user_prop(uid, 'strf', tzstr)
        if "error" in res['message']:
            return res
        else:
            return {"message": "done."}

    def make_times_list(self, uid, personal=False):
        if self.db.check_user_exists(uid):
            ref_dt = datetime.utcnow()
            obj = self.db.get_user(uid)
            me = ""
            my_tz = obj["tz"]
            my_local = timezone(my_tz)

            my_time = my_local.fromutc(ref_dt).strftime(obj['strf'])

            if personal:
                adj = "you"
            else:
                adj = "them"

            me = "For " + adj + ", it's " + my_time

            watching = self.get_watching(uid)
            if len(watching) == 0:
                if personal:
                    adj = "You're"
                else:
                    adj = "They're"
                return (
                        me
                        + "<p>"
                        + adj
                        + " not following any other users.</p><br/><p>Perhaps you'd like to see the <a class='slicklink' href='/users'>userlist</a>?</p>"
                )
            else:
                wl = me + "<ul>"
                for uid in watching:
                    if self.db.check_user_exists(uid):
                        their_tz = self.db.get_user(uid)["tz"]
                        local = timezone(their_tz)
                        their_time = local.fromutc(ref_dt).strftime(obj['strf'])
                        wl += (
                                "<li><p>For <a class='slicklink' href='/users/"
                                + uid
                                + "'>"
                                + uid
                                + "</a>, it's "
                                + their_time
                                + "</p></li><br/>"
                        )
                wl += "</ul><br/><p>Perhaps you'd like to see the <a class='slicklink' href='/users'>userlist</a>?</p>"
                return wl

    def make_user_list(self):
        users = self.db.dump_users()
        the_list = "<ul>"
        for uid in users:
            the_list += (
                    "<li><p><a class='slicklink' href='/users/"
                    + uid
                    + "'>"
                    + uid
                    + "</a>: "
                    + self.db.get_user(uid)["tz"]
                    + "</p></li><br/>"
            )
        the_list += "</ul>"
        return the_list

    def add_watching(self, uid, who):
        if uid != who and self.db.check_user_exists(uid):
            user = self.db.get_user(uid)
            if who not in user["watching"]:
                user["watching"].append(who)
                self.db.write_user(uid, user)
            return {"message": "you're now following " + who}
        else:
            return {"message": "error: why would you follow yourself?"}

    def remove_watching(self, uid, who):
        if self.db.check_user_exists(uid):
            user = self.db.get_user(uid)
            user["watching"].remove(who)
            self.db.write_user(uid, user)
            return {"message": "you're no longer following " + who}
        else:
            return {"message": "error: can't unfollow a user that doesn't exist."}

    def get_watching(self, uid):
        if self.db.check_user_exists(uid):
            return self.db.get_user(uid)["watching"]