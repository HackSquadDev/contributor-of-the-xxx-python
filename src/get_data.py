import requests
import json


def get_repos():
    repos = requests.get(f"https://api.github.com/orgs/{org}/repos")
    repos = json.loads(repos.text)
    repos = [repo["name"] for repo in repos]
    return repos


def get_contributors():
    contributors = {}
    # solve error string indices must be integers
    for repo in get_repos():
        contributors[repo] = requests.get(
            f"https://api.github.com/repos/{org}/{repo}/contributors")
        contributors[repo] = json.loads(contributors[repo].text)
        contributors[repo] = [contributor["login"]
                             for contributor in contributors[repo]]

    return contributors


def print_contributors():
    contributors = get_contributors()
    for repo in contributors:
        print(repo, contributors[repo])
