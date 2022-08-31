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
