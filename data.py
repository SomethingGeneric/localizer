import os, yaml, pytz
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from pytz import timezone

DEFAULT_STRF = "%H:%M"
TWELVE_STRF = "%I:%M %p"


class db:
    def __init__(self, srcdir):
        if not os.path.exists(srcdir):
            os.makedirs(srcdir)
        self.srcdir = srcdir

    def write_user(self, uid, obj):
        with open(self.srcdir + os.sep + uid, "w") as f:
            f.write(yaml.dump(obj))

    def check_user_exists(self, uid):
        if uid == "" or uid is None:
            return False
        if os.path.exists(self.srcdir + os.sep + uid):
            return True
        return False

    def auth_user(self, uid, attempt):
        if self.check_user_exists(uid):
            phash = self.get_user(uid)["passw"]
            if pbkdf2_sha256.verify(attempt, phash):
                return True
        return False

    def make_user(self, uid, passw, tz):
        if self.check_user_exists(uid):
            return {"message": "error: uid in use."}
        else:
            if len(uid) < 4:
                return {"message": "error: user id too short"}
            if uid.isnumeric():
                return {
                    "message": "error: please put at least one non-number in your user id"
                }
            if len(passw) < 8:
                return {
                    "message": "error: password too short. Use at least 8 characters"
                }
            if "<" in uid or ">" in uid:
                return {"message": "error: uid contains a prohibited character"}
            if len(uid) > 15:
                return {"message": "error: user id too long"}

            if tz not in pytz.all_timezones:
                if not tz.upper() in pytz.all_timezones:
                    return {"message": "error: no such tz '" + tz + "'"}
                else:
                    tz = tz.upper()
            hashed_pw = pbkdf2_sha256.hash(passw)
            obj = {"passw": hashed_pw, "tz": tz, "watching": [], "strf": DEFAULT_STRF}
            self.write_user(uid, obj)
            return {"message": "user has been registered"}

    def get_user(self, uid):
        if self.check_user_exists(uid):
            with open(self.srcdir + os.sep + uid) as f:
                obj = yaml.safe_load(f)
            return obj
        else:
            return {"message": "not found"}

    def add_watching(self, uid, who):
        if uid != who and self.check_user_exists(uid):
            user = self.get_user(uid)
            if who not in user["watching"]:
                user["watching"].append(who)
                self.write_user(uid, user)
            return {"message": "you're now following " + who}
        else:
            return {"message": "error: why would you follow yourself?"}

    def remove_watching(self, uid, who):
        if self.check_user_exists(uid):
            user = self.get_user(uid)
            user["watching"].remove(who)
            self.write_user(uid, user)
            return {"message": "you're no longer following " + who}
        else:
            return {"message": "error: can't unfollow a user that doesn't exist."}

    def get_watching(self, uid):
        if self.check_user_exists(uid):
            return self.get_user(uid)["watching"]

    def make_times_list(self, uid, personal=False):
        if self.check_user_exists(uid):
            ref_dt = datetime.utcnow()
            obj = self.get_user(uid)
            print(ref_dt.strftime(obj['strf']))
            me = ""
            my_tz = obj["tz"]
            print(my_tz)
            my_local = timezone(my_tz)

            my_time = my_local.fromutc(ref_dt).strftime(obj['strf'])
            print(my_time)

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
                    if self.check_user_exists(uid):
                        their_tz = self.get_user(uid)["tz"]
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
        users = os.listdir(self.srcdir)
        the_list = "<ul>"
        for uid in users:
            the_list += (
                "<li><p><a class='slicklink' href='/users/"
                + uid
                + "'>"
                + uid
                + "</a>: "
                + self.get_user(uid)["tz"]
                + "</p></li><br/>"
            )
        the_list += "</ul>"
        return the_list

    def set_user_password(self, uid, newpass):
        if self.check_user_exists(uid):
            obj = self.get_user(uid)
            hashed_pw = pbkdf2_sha256.hash(newpass)
            obj["passw"] = hashed_pw
            self.write_user(uid, obj)
            return {"message": "done."}
        else:
            return {"message": f"error: no such user {uid}"}

    def set_user_tz(self, uid, newtz):
        if newtz in pytz.all_timezones or newtz.upper() in pytz.all_timezones:
            if self.check_user_exists(uid):
                obj = self.get_user(uid)
                obj["tz"] = newtz
                self.write_user(uid, obj)
                return {"message": "done."}
            else:
                return {"message": f"error: no such user {uid}"}
        else:
            return {"message": f"error: no such tz {newtz}"}

    def set_user_timetype(self, uid, normal=True):
        if self.check_user_exists(uid):
            obj = self.get_user(uid)
            obj["strf"] = DEFAULT_STRF if normal else TWELVE_STRF
            self.write_user(uid, obj)
            return {"message": f"set {uid} to {'12' if not normal else '24'}"}
        else:
            return {"message": f"error: no such user {uid}"}

    def dump_users(self):
        return os.listdir(self.srcdir)


if __name__ == "__main__":
    db = db("db")
    timezones = ["gmt", "mnt", "cnt", "eu"]

    from faker import Factory

    fake = Factory.create()

    import random

    for i in range(100):
        nuid = fake.name().split(" ")[0].lower().replace(".", "")
        tz = random.choice(timezones)
        db.make_user(nuid, tz)
