import os,random,string


class sessionmgr:

    def __init__(self):
        self.srcdir = ".sessions"
        if not os.path.exists(self.srcdir):
            os.makedirs(self.srcdir)

    def make_session(self, uid):
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
        with open(self.srcdir + os.sep + uid, "w") as f:
            f.write(key)
        return key

    def check_session(self, uid, ikey):
        if os.path.exists(self.srcdir + os.sep + uid):
            key = open(self.srcdir + os.sep + uid).read().strip()
            if key == ikey:
                return True
        return False

    def get_user_by_session(self, ikey):
        for fn in os.listdir(self.srcdir):
            if open(self.srcdir + os.sep + fn).read().strip() == ikey:
                return fn
        return ""

    def destroy_session(self, uid):
        if os.path.exists(self.srcdir + os.sep + uid):
            os.remove(self.srcdir + os.sep + uid)