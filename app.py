from flask import Flask, render_template, request, make_response, redirect

from datetime import datetime

from data import db

app = Flask(__name__)
db = db("db")


@app.route("/")
def main():
    p_content = ""
    p_title = ""
    extra = ""
    clear_msg = False

    user = request.cookies.get('uid')
    msg = request.cookies.get('msg')

    if msg is not None:
        extra = '<p style="color:red;">' + msg + "</p>"
        clear_msg = True

    if user is None:
        p_title = "Home"
        p_content = extra + render_template("signin.html")
    else:
        p_title = "Saved data for " + user
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        p_content = extra + render_template("logout.html") + "<br/><p>Server time is: " + current_time + "</p>"
        p_content += "<h2>Your data:</h2><pre><code>" + str(db.get_user(user)) + "</code></pre>"

    resp = make_response(render_template("page.html", page_title=p_title, content=p_content))

    if clear_msg:
        resp.delete_cookie('msg')

    return resp


@app.route("/dologin", methods=["POST"])
def handle_login():
    given_uid = request.form['nm']
    resp = make_response(redirect("/"))

    if db.check_user(given_uid):
        resp.set_cookie('uid', given_uid)
    else:
        resp.set_cookie('msg', 'No such user ' + given_uid)

    return resp


@app.route("/dologout", methods=["POST", "GET"])
def handle_logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie('uid')
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)
