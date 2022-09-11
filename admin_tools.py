import sys

from uinterface import su_interface

su = su_interface()

if sys.argv[1] is None or sys.argv[1] == "":
    print("Usage: 'password <uid> <new' or 'register <uid> <password> <timezone>' or 'reset_timetype' (CAREFUL!)")

if sys.argv[1] == "password":
    user = sys.argv[2]
    new = sys.argv[3]
    if su.db.check_user_exists(user):
        su.db.set_user_password(user, new)
        print(f"Set new password for {user}")
    else:
        print(f"No such user {user}")
elif sys.argv[1] == "register":
    uid = sys.argv[2]
    passw = sys.argv[3]
    tz = sys.argv[4]
    res = su.make_user(uid, passw, tz)
    print(res['message'])
elif sys.argv[1] == "reset_timetype":
    if input("Are you sure you want to reset timetype for *EVERYONE*? (y/N): ") == "y":
        users = su.db.dump_users()
        for uid in users:
            su.set_user_timetype(uid) # type 'normal' (24hr) is implied
            print(f"Fixed {uid}")
        print("Done.")
    else:
        print("No changes made")