import os,yaml


class db:

    def __init__(self, srcdir):
        if not os.path.exists(srcdir):
            os.makedirs(srcdir)
        self.srcdir = srcdir

    def check_user(self, uid):
        if os.path.exists(self.srcdir + os.sep + uid):
            return True
        return False

    def make_user(self, uid, tz):
        if self.check_user(uid):
            return False
        else:
            obj = {
                "tz": tz,
                "watching": []
            }
            with open(self.srcdir + os.sep + uid, "w") as f:
                f.write(yaml.dump(obj))
            return True

    def get_user(self, uid):
        if self.check_user(uid):
            with open(self.srcdir + os.sep + uid) as f:
                obj = yaml.safe_load(f)
            return obj
        else:
            return {"message": "not found"}

    def add_watching(self, uid, who):
        if self.check_user(uid):
            user = self.get_user(uid)
            user['watching'].append(who)
            with open(self.srcdir + os.sep + uid, "w") as f:
                f.write(yaml.dump(user))

    def get_watching(self, uid):
        if self.check_user(uid):
            return self.get_user(uid)['watching']

    def make_times_list(self, uid):
        if self.check_user(uid):
            watching = self.get_watching(uid)
            if len(watching) == 0:
                return "<p>You've not added anyone</p>"
            else:
                wl = "<ul>"
                for uid in watching:
                    wl += "<li><p>" + uid + ": " + self.get_user(uid)['tz'] + "</p></li>"
                wl += "</ul>"
                return wl

    def make_user_list(self):
        users = os.listdir(self.srcdir)
        the_list = "<ul>"
        for uid in users:
            the_list += "<li><p>" + uid + ": " + self.get_user(uid)['tz'] + "</p></li><br/>"
        the_list += "</ul>"
        return the_list


if __name__ == "__main__":
    db = db("db")
    timezones = ["gmt", "mnt", "cnt", "eu"]

    from faker import Factory
    fake = Factory.create()

    import random

    for i in range(100):
        nuid = fake.name().split(" ")[0].lower().replace(".","")
        tz = random.choice(timezones)
        db.make_user(nuid,tz)