import os
import requests
import json

query = """{

  viewer {

    repositories{
        totalCount
    }

    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }


    contributionsCollection {
      contributionCalendar {
        weeks{
            contributionDays{
                color, contributionCount, contributionLevel
            }
        }
      }
    }

    repositories{
        nodes{
           stargazerCount,forkCount
        }
    }

   }

}"""

GITHUB_GRAPH_QL_ENDPOINT = os.environ["GITHUB_GRAPH_QL_URL"]

headers = {
    "Authorization": os.environ["ACCESS_TOKEN"],
    "Content-Type": "application/json"

}


class GithubData:

    def __init__(self):

        self.github_url = GITHUB_GRAPH_QL_ENDPOINT
        self.response = requests.post(self.github_url, json={"query": query}, headers=headers)

    def checking_response(self):

        if self.response.status_code == 200:
            print("the data is retrieved successfully")

            return 0

        else:
            print(f"Query failed with status code {self.response.status_code}: {self.response.text}")
            return 1

    def fetching_required_data(self):

        github_data = self.response.json()

        # repository count
        repository_count = github_data["data"]["viewer"]["repositories"]["totalCount"]

        # to get total stars
        total_stars = sum([star["stargazerCount"] for star in github_data["data"]["viewer"]["repositories"]["nodes"]])

        # to total forks
        total_forks = sum([star["forkCount"] for star in github_data["data"]["viewer"]["repositories"]["nodes"]])

        # total Contribution
        total_contribution = github_data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"][
            "totalContributions"]

        return repository_count, total_stars, total_forks, total_contribution
