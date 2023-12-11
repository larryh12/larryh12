import re
import requests


def update_quote(readme):
    try:
        response = requests.get("https://zenquotes.io/api/today")
        response_data = response.json()[0]

        q = response_data.get("q", "")
        a = response_data.get("a", "")

        quote_str = ""

        if response.status_code == 200 and a != "zenquotes.io":
            quote_str = f"<p align='center'><em>&ldquo;{q}&rdquo;</em>&mdash;{a}</p>"

        return re.sub(
            r"<!--Quote-->[\s\S]+<!--/Quote-->",
            f"<!--Quote-->\n{quote_str}\n<!--/Quote-->",
            readme,
        )
    except requests.RequestException:
        print("Error fetching quote.")
        return readme


if __name__ == "__main__":
    with open("./README.md", "r") as f:
        readme = f.read()

    readme = update_quote(readme)

    with open("./README.md", "w") as f:
        f.write(readme)
