from datetime import datetime
import time

from flask import Flask, render_template, request, make_response, redirect

from data import db
from session import sessionmgr

app = Flask(__name__)
db = db("db")
sessionmgr = sessionmgr()

emojis = "🕐🕜🕑🕝🕒🕞🕓🕟🕔🕠🕕🕡🕖🕢🕗🕣🕘🕤🕙🕥🕚🕦🕛🕧"


# Adapted from https://stackoverflow.com/a/67467442
def get_emoji_of_time(h, m):
    hm = int(h + m / 30 + 0.5)
    return f"{emojis[hm]}"


def get_emoji_of_current():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    return get_emoji_of_time(h, m)


@app.route("/")
def main():
    extra = ""
    clear_msg = False

    skey = request.cookies.get("skey")
    msg = request.cookies.get("msg")

    if msg is not None:
        extra = '<p style="color:red;">' + msg + "</p>"
        clear_msg = True

    if skey is None:
        p_title = "Home"
        p_content = extra + render_template("signin.html")
    else:
        user = sessionmgr.get_user_by_session(skey)
        if user != "":
            p_title = "Hi, " + user
            now = datetime.utcnow()
            current_time = now.strftime("%H:%M:%S")
            p_content = (
                extra
                + render_template("logout.html")
                + "<br/><p>UTC is: "
                + current_time
                + "</p>"
                + db.make_times_list(user, True)
            )


        else:
            p_title = "Home"
            p_content = extra + render_template("signin.html")

    resp = make_response(
        render_template(
            "page.html",
            page_title=p_title,
            content=p_content,
            emoji=get_emoji_of_current(),
        )
    )

    if clear_msg:
        resp.delete_cookie("msg")

    return resp


@app.route("/users")
def show_users():
    extra = ""
    clear_msg = False
    msg = request.cookies.get("msg")

    if msg is not None:
        extra = '<p style="color:red;">' + msg + "</p>"
        clear_msg = True

    p_title = "User List"

    p_content = extra + db.make_user_list()

    resp = make_response(
        render_template(
            "page.html",
            page_title=p_title,
            content=p_content,
            emoji=get_emoji_of_current(),
        )
    )

    if clear_msg:
        resp.delete_cookie("msg")

    return resp


@app.route("/users/<uid>")
def show_user(uid):
    if db.check_user_exists(uid):
        extra = ""
        clear_msg = False
        msg = request.cookies.get("msg")

        if msg is not None:
            extra = '<p style="color:red;">' + msg + "</p>"
            clear_msg = True

        p_title = "User - " + uid

        p_content = extra + "<h2>Timezone: " + db.get_user(uid)["tz"] + "</h2>"
        p_content += "<a href='/follow/" + uid + "'>Follow " + uid + "</a><br/>"
        p_content += db.make_times_list(uid)

        resp = make_response(
            render_template(
                "page.html",
                page_title=p_title,
                content=p_content,
                emoji=get_emoji_of_current(),
            )
        )

        if clear_msg:
            resp.delete_cookie("msg")

        return resp
    else:
        return render_template("page.html", page_title="Not found", content="<p>No such user " + uid + "</p>", emoji=get_emoji_of_current())


@app.route("/register", methods=["GET", "POST"])
def handle_signup():
    if request.method == "GET":
        extra = ""
        clear_msg = False
        msg = request.cookies.get("msg")

        if msg is not None:
            extra = '<p style="color:red;">' + msg + "</p>"
            clear_msg = True

        resp = make_response(
            render_template(
                "page.html",
                page_title="Register",
                emoji=get_emoji_of_current(),
                content=extra + render_template("register.html"),
            )
        )
        if clear_msg:
            resp.delete_cookie("msg")

        return resp
    if request.method == "POST":
        uid = request.form["uid"]
        tz = request.form["tz"]
        passw = request.form["passw"]
        res = db.make_user(uid, passw, tz)
        if "error" in res["message"]:
            resp = make_response(redirect("/register"))
            resp.set_cookie("msg", res["message"])
            return resp
        else:
            resp = make_response(redirect("/"))
            resp.set_cookie("msg", "User account created!")
            return resp


@app.route("/dologin", methods=["POST", "GET"])
def handle_login():
    if request.method == "GET":
        return "Go away."
    else:
        given_uid = request.form["nm"]
        passw = request.form['passwd']

        resp = make_response(redirect("/"))

        if db.auth_user(given_uid, passw):
            resp.set_cookie("skey", sessionmgr.make_session(given_uid))
        else:
            resp.set_cookie("msg", "Auth failed for " + given_uid)

        return resp


@app.route("/dologout", methods=["POST", "GET"])
def handle_logout():
    resp = make_response(redirect("/"))
    skey = request.cookies.get("skey")
    resp.delete_cookie("skey")
    sessionmgr.destroy_session(sessionmgr.get_user_by_session(skey))
    return resp

@app.route("/follow/<uid>", methods=["POST", "GET"])
def handle_follow(uid):
    skey = request.cookies.get('skey')
    user = sessionmgr.get_user_by_session(skey)

    if user != "":
        db.add_watching(user, uid)
        return "You're now following " + uid
    else:
        return "Please sign in first."

@app.route("/unfollow/<uid>")
def handle_unfollow(uid):
    skey = request.cookies.get('skey')
    user = sessionmgr.get_user_by_session(skey)

    if user != "":
        db.remove_watching(user, uid)
        return "You're no longer following " + uid
    else:
        return "Please sign in first."

@app.route("/passwordex")
def dump_expg():
    return render_template("page.html", page_title="Password Information", emoji=get_emoji_of_current(), content=render_template("pws.html"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
