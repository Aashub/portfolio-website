from flask import Flask, render_template, request, session, redirect, url_for
import requests
import os
from github_graph import GithubData
from data import github_data
from datetime import date, datetime
from smtplib import SMTP
from email.message import EmailMessage

EMAIL = os.environ["EMAIL"]
password = os.environ["PASSWORD"]
PER_EMAIL = os.environ["PER_EMAIL"]
SECRET_KEY = os.urandom(24).hex()


# repository count
repository_count = github_data["data"]["viewer"]["repositories"]["totalCount"]

# to get total stars
total_stars = sum([star["stargazerCount"] for star in github_data["data"]["viewer"]["repositories"]["nodes"]])

# to total forks
total_forks = sum([star["forkCount"] for star in github_data["data"]["viewer"]["repositories"]["nodes"]])

# total Contribution
total_contribution = github_data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"][
    "totalContributions"]

graph_contribution_list = github_data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]["weeks"]

month_label_list = []

for week in graph_contribution_list:
    first_day = week["contributionDays"][0]["date"]

    formated_date = datetime.strptime(first_day, "%Y-%m-%d")  # converting each week first date into datetime format
    month = formated_date.strftime("%b")  # changing the formated date into this format "Jul Aug"

    if month not in month_label_list:
        month_label_list.append(month)

    else:
        month_label_list.append("")

response_list = [repository_count, total_stars, total_forks, total_contribution]


# fetch_data = GithubData()
#
# print(fetch_data.response.json())
# response_status = fetch_data.checking_response()
#
# if response_status == 0:
#     repo_count, overall_stars, overall_forks, overall_contribution, graph_contribution_list = fetch_data.fetching_required_data()
#     response_list = [repo_count, overall_stars, overall_forks, overall_contribution]
#
# elif response_status == 1:
#     print("please check the above error")


def send_mail(message_data_dict):
    """this function will create the secure connection between sender and receiver using smtp module and take input of weather condition and send the mail."""

    msg = EmailMessage()


    msg["Subject"] = message_data_dict["subject"]
    msg["From"] = EMAIL
    msg["To"] = PER_EMAIL
    msg["Reply-To"] = message_data_dict["email"]
    msg.set_content(message_data_dict["message_content"])

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with SMTP(smtp_server, smtp_port) as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=password)

        connection.send_message(msg)


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/', methods=['GET'])
def home():
    """the decorator and this function will help in render the home page of website."""

    return render_template("index.html", contribution_highlights=response_list,
                           contribution_graph=graph_contribution_list, num_of_weeks=len(graph_contribution_list),
                           months_label=month_label_list, current_page=True)


@app.route('/projects', methods=['GET'])
def projects():
    return render_template("projects.html")


@app.route('/about_me', methods=['GET'])
def about_me():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """this route is responsible for rendering the contact page."""

    if request.method == 'POST':
        message_data_dict = {

            "name": request.form['name'],
            "email": request.form['email'],
            "subject": request.form['subject'],
            "message_content": request.form['message']

        }

        send_mail(message_data_dict)

        # Setting a temporary flag in the session

        session['mail_sent'] = True
        return redirect(url_for('contact'))  # once the message sent successful this will render contact.html page and show succesful sent message

    # Check if the flag exists in the session
    show_success = session.pop('mail_sent', False)

    return render_template("contact.html", show_success = show_success)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
