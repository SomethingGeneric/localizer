import os

class db:

    def __init__(self, srcdir):
        if not os.path.exists(srcdir):
            os.makedirs(srcdir)
        self.srcdir = srcdir

    def check_user(self, uid):
        if os.path.exists(self.srcdir + os.sep + uid):
            return True
        return False
