from flask import Flask,render_template,request,make_response,redirect

from datetime import datetime

app = Flask(__name__)


@app.route("/")
def main():
    user = request.cookies.get('uid')

    if user is None:
        p_title = "Home"
        p_content = render_template("signin.html")
    else:
        p_title = "Saved data for " + user
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        p_content = render_template("logout.html") + "<br/><p>Server time is: " + current_time + "</p>"

    return render_template("page.html", page_title=p_title, content=p_content)

@app.route("/dologin", methods=["POST"])
def handle_login():
    user = request.form['nm']
    resp = make_response(redirect("/"))
    resp.set_cookie('uid', user)
    return resp

@app.route("/dologout", methods=["POST", "GET"])
def handle_logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie('uid')
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090, debug=True)