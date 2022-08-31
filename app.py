import time

from flask import (
    Flask,
    render_template,
    request,
    make_response,
    redirect,
)
import flask_login
from pytz import timezone
from datetime import datetime

from data import db

app = Flask(__name__)
app.secret_key = "SuperStrongAndComplicated"

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

db = db("db")


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(uid):
    if not db.check_user_exists(uid):
        return
    user = User()
    user.id = uid
    return user


@login_manager.request_loader
def request_loader(request):
    uid = request.form.get("uid")
    if not db.check_user_exists(uid):
        return
    user = User()
    user.id = uid
    return user


emojis = "🕐🕜🕑🕝🕒🕞🕓🕟🕔🕠🕕🕡🕖🕢🕗🕣🕘🕤🕙🕥🕚🕦🕛🕧"


# Adapted from https://stackoverflow.com/a/67467442
def get_emoji_of_time(h, m):
    hm = int(h + m / 30 + 0.5)
    try:
        return f"{emojis[hm]}"
    except:
        return "🕒"


def get_emoji_for_user(username):
    if db.check_user_exists(username):
        obj = db.get_user(username)
        tz = obj["tz"]
        local_tz = timezone(tz)
        utc = datetime.utcnow()
        hm = local_tz.fromutc(utc).strftime("%H:%M")
        h, m = hm.split(":")
        h = int(h)
        m = int(m)
        return get_emoji_of_time(h, m)


def get_emoji_of_current():
    h = time.localtime().tm_hour
    m = time.localtime().tm_min
    return get_emoji_of_time(h, m)


@app.route("/")
def main():
    extra = ""
    clear_msg = False
    msg = request.cookies.get("msg")
    emoji = get_emoji_of_current()

    if msg is not None:
        extra = '<p style="color:red;">' + msg + "</p>"
        clear_msg = True

    if not flask_login.current_user.is_authenticated:
        p_title = "Home"
        p_content = extra + render_template("signin.html")
    else:
        user = flask_login.current_user.id
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
        emoji = get_emoji_for_user(user)

    resp = make_response(
        render_template(
            "page.html",
            page_title=p_title,
            content=p_content,
            emoji=emoji,
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
    emoji = get_emoji_of_current()

    if flask_login.current_user.is_authenticated:
        emoji = get_emoji_for_user(flask_login.current_user.id)

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
            emoji=emoji,
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
        emoji = get_emoji_of_current()

        if flask_login.current_user.is_authenticated:
            emoji = get_emoji_for_user(flask_login.current_user.id)

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
                emoji=emoji,
            )
        )

        if clear_msg:
            resp.delete_cookie("msg")

        return resp
    else:
        emoji = get_emoji_of_current()

        if flask_login.current_user.is_authenticated:
            emoji = get_emoji_for_user(flask_login.current_user.id)
        return render_template(
            "page.html",
            page_title="Not found",
            content="<p>No such user " + uid + "</p>",
            emoji=emoji,
        )


@app.route("/register", methods=["GET", "POST"])
def handle_signup():
    if request.method == "GET":
        if flask_login.current_user.is_authenticated:
            resp = make_response(redirect("/"))
            resp.set_cookie(
                "msg", "Please sign out first if you'd like to make a new account."
            )
            return resp
        else:
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":

        msg = request.cookies.get("msg")
        hmsg = ""
        if msg is not None:
            hmsg = "<p style='color:red;'>" + msg + "</p>"

        resp = make_response(
            render_template(
                "page.html",
                page_title="Login",
                emoji=get_emoji_of_current(),
                content=hmsg + render_template("signin.html"),
            )
        )

        if msg is not None:
            resp.delete_cookie("msg")

        return resp

    uid = request.form["uid"]
    if db.check_user_exists(uid) and db.auth_user(uid, request.form["passwd"]):
        user = User()
        user.id = uid
        flask_login.login_user(user, remember=True)
        return redirect("/")
    else:
        resp = make_response(redirect("/login"))
        resp.set_cookie("msg", "Login failed.")
        return resp


@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect("/")


@login_manager.unauthorized_handler
def unauthorized_handler():
    return "Unauthorized", 401


@app.route("/follow/<uid>", methods=["POST", "GET"])
def handle_follow(uid):
    if flask_login.current_user.is_authenticated:
        user = flask_login.current_user.id
        db.add_watching(user, uid)

        resp = make_response(redirect(request.referrer))
        resp.set_cookie("msg", "You're now following " + uid)
        return resp
    else:
        resp = make_response(redirect(request.referrer))
        resp.set_cookie("msg", "Please sign in first.")
        return resp


@app.route("/unfollow/<uid>")
def handle_unfollow(uid):
    if flask_login.current_user.is_authenticated:
        user = flask_login.current_user.id
        db.remove_watching(user, uid)

        resp = make_response(redirect(request.referrer))
        resp.set_cookie("msg", "You're now following " + uid)
        return resp
    else:
        resp = make_response(redirect(request.referrer))
        resp.set_cookie("msg", "Please sign in first.")
        return resp


@app.route("/passwordex")
def dump_expg():
    emoji = get_emoji_of_current()

    if flask_login.current_user.is_authenticated:
        emoji = get_emoji_for_user(flask_login.current_user.id)
    return render_template(
        "page.html",
        page_title="Password Information",
        emoji=emoji,
        content=render_template("pws.html"),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
