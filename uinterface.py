from datetime import datetime

import pytz
from pytz import timezone, all_timezones
from dateutil import parser

from simpleusers import usermgr

DEFAULT_STRF = "%H:%M"
TWELVE_STRF = "%I:%M %p"


class su_interface:
    def __init__(self):
        self.db = usermgr()

    def make_user(self, uid, passw, tz):
        if tz in all_timezones:
            self.db.make_user(uid, passw)
            self.db.set_user_prop(uid, "tz", tz)
            self.db.set_user_prop(uid, "strf", DEFAULT_STRF)
            self.db.set_user_prop(uid, "watching", [])
            return {"message": "ok"}
        else:
            return {"message": "error: Bad Timezone"}

    def set_user_tz(self, uid, newtz):
        if newtz in pytz.all_timezones or newtz.upper() in pytz.all_timezones:
            res = self.db.set_user_prop(uid, "tz", newtz)
            if "error" in res["message"]:
                return {"message": res["message"]}
            else:
                return {"message": "done."}
        else:
            return {"message": f"error: no such tz {newtz}"}

    def set_user_timetype(self, uid, normal=True):
        tzstr = DEFAULT_STRF if normal else TWELVE_STRF
        res = self.db.set_user_prop(uid, "strf", tzstr)
        if "error" in res["message"]:
            return res
        else:
            return {"message": "done."}

    def make_times_list(self, uid, personal=False, at_time=""):
        if self.db.check_user_exists(uid):

            obj = self.db.get_user(uid)
            my_tz = obj["tz"]
            my_local = timezone(my_tz)
            
            ref_dt = datetime.utcnow()

            my_time = my_local.fromutc(ref_dt).strftime(obj["strf"])

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
                wl = me
                if "them" in me:
                    wl += "<p>Here's a list of the users they're following:</p>"
                wl += "<ul>"

                sadj = " it's "

                for uid in watching:
                    if self.db.check_user_exists(uid):
                        their_tz = self.db.get_user(uid)["tz"]
                        local = timezone(their_tz)
                        their_time = local.fromutc(ref_dt).strftime(obj["strf"])
                        wl += (
                            "<li><p>For <a class='slicklink' href='/users/"
                            + uid
                            + "'>"
                            + uid
                            + "</a>,"
                            + sadj
                            + their_time
                            + "</p></li><br/>"
                        )

                wl += "</ul><br/>"

                if personal:
                    wl += open("templates/plan.html").read() + "<br/>"

                wl += "<p>Perhaps you'd like to see the <a class='slicklink' href='/users'>userlist</a>?</p>"
                return wl

    def make_plan(self, myuid, tstr):
        naive_local_dt = parser.parse(tstr)
        obj = self.db.get_user(myuid)
        local_tz = timezone(obj["tz"])

        plan = f"<p>For you, it will be {local_tz.localize(naive_local_dt).strftime(DEFAULT_STRF)}</p>"
        plan += f"<p>In UTC, it will be {local_tz.localize(naive_local_dt).astimezone(pytz.UTC).strftime(DEFAULT_STRF)}</p><ul>"

        for uid in obj["watching"]:
            their_tz = timezone(self.db.get_user(uid)["tz"])
            plan += f"<li><p>For <a class='slicklink' href='/users/{uid}'>{uid}</a> it will be {local_tz.localize(naive_local_dt).astimezone(their_tz).strftime(DEFAULT_STRF)}</p></li><br/>"

        plan += "</ul>"
        return plan

    def make_user_list(self, myuid=None):
        users = self.db.dump_users()
        the_list = "<ul>"
        ref_dt = datetime.utcnow()

        pref_strf = DEFAULT_STRF

        if myuid is not None:
            my_user = self.db.get_user(myuid)
            if "strf" in my_user:
                pref_strf = my_user["strf"]

        for uid in users:
            user_tz = self.db.get_user(uid)["tz"]
            tzobj = timezone(user_tz)
            the_list += (
                "<li><p><a class='slicklink' href='/users/"
                + uid
                + "'>"
                + uid
                + "</a>: "
                + user_tz
                + " : "
                + tzobj.fromutc(ref_dt).strftime(pref_strf)
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
