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


if __name__ == "__main__":
    db = db("db")
    print(db.check_user("matt"))
    db.make_user("matt", "est")
    print(db.check_user("matt"))
    print(str(db.get_user("matt")))
    db.add_watching("matt","joe")
    print(str(db.get_user("matt")))
    db.add_watching("matt", "mama")
    print(str(db.get_user("matt")))