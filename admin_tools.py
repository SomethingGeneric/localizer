from data import db
import sys

db = db("db")

if sys.argv[1] == "password":
    user = sys.argv[2]
    new = sys.argv[3]
    if db.check_user_exists(user):
        db.set_user_password(user, new)
        print(f"Set new password for {user}")
    else:
        print(f"No such user {user}")
elif sys.argv[1] == "register":
    uid = sys.argv[2]
    passw = sys.argv[3]
    tz = sys.argv[4]
    res = db.make_user(uid, passw, tz)
    print(res['message'])