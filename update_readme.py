import os
import re
import requests

WAKATIME_API_KEY = os.environ.get("WAKATIME_API_KEY")
NOTION_KEY = os.environ.get("NOTION_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")


def update_hello(readme):
    hello_data = requests.get(
        "https://raw.githubusercontent.com/larryh12/larryh12/main/public/meta.json"
    ).json()["hello"]

    hello_str = f"\n\n## {hello_data['head']}\n\n"
    for line in hello_data["body"]:
        hello_str += f"{line}\n\n"

    return re.sub(
        f"<!--DIV:hello-->[\\s\\S]+<!--/DIV:hello-->",
        f"<!--DIV:hello-->{hello_str}<!--/DIV:hello-->",
        readme,
    )


def update_tech(readme):
    tech_data = requests.get(
        "https://raw.githubusercontent.com/larryh12/larryh12/main/public/meta.json"
    ).json()["tech"]

    tech_str = f"\n\n## {tech_data['head']}\n\n"
    for item in tech_data["body"]:
        tech_str += f"<img src='https://cdn.simpleicons.org/{item['slug']}' title='{item['title']}' width='48' height='48'/>&nbsp;&nbsp;&nbsp;\n"

    return re.sub(
        f"<!--DIV:tech-->[\\s\\S]+<!--/DIV:tech-->",
        f"<!--DIV:tech-->{tech_str}<!--/DIV:tech-->",
        readme,
    )


def update_waka(readme):
    waka_str = f"\n\n## 📊 My Dev Hours\n\n"

    response = requests.get(
        f"https://wakatime.com/api/v1/users/current/stats?api_key={WAKATIME_API_KEY}"
    ).json()
    langs = response["data"]["languages"][:5]
    lang_name_pad = len(max((str(lang["name"]) for lang in langs), key=len))
    lang_text_pad = len(max((str(lang["text"]) for lang in langs), key=len))

    waka_str += f"```py\n{str('Total Time').ljust(lang_name_pad)}  {response['data']['human_readable_total_including_other_language']}\n\n"
    for lang in langs:
        lang_str = (
            f"{lang['name'].ljust(lang_name_pad)}  "
            + f"{lang['text'].ljust(lang_text_pad)}  "
            + f"{str(round(lang['percent']/2)*'█').ljust(round(langs[0]['percent']/2))}  "
            + f"{lang['percent']}%\n"
        )
        waka_str += lang_str

    return re.sub(
        f"<!--DIV:waka-->[\\s\\S]+<!--/DIV:waka-->",
        f"<!--DIV:waka-->{waka_str}```\n<!--/DIV:waka-->",
        readme,
    )


def update_blog(readme):
    blog_str = f"\n\n## 📝 Latest Blog Posts\n\n"

    response = requests.post(
        f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
        headers={
            "Authorization": f"Bearer {NOTION_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        json={
            "filter": {"property": "Published", "date": {"is_not_empty": True}},
            "sorts": [{"property": "Published", "direction": "descending"}],
        },
    ).json()

    public_pages = list(
        filter(lambda page: page["public_url"] is not None, response["results"])
    )
    for page in public_pages:
        blog_str += f"- [{page['properties']['Name']['title'][0]['plain_text']}]({page['public_url']})\n"

    return re.sub(
        f"<!--DIV:blog-->[\\s\\S]+<!--/DIV:blog-->",
        f"<!--DIV:blog-->{blog_str}\n<!--/DIV:blog-->",
        readme,
    )


def update_qotd(readme):
    response = requests.get("https://zenquotes.io/api/today")

    if response.status_code == 200:
        if response.json()[0]["a"] != "zenquotes.io":
            qotd_str = f"\n\n## 💡 Quote of the Day\n\n" + response.json()[0]["h"]

    return re.sub(
        f"<!--DIV:qotd-->[\\s\\S]+<!--/DIV:qotd-->",
        f"<!--DIV:qotd-->{qotd_str}\n<!--/DIV:qotd-->",
        readme,
    )


if __name__ == "__main__":
    with open("./README.md", "r") as f:
        readme = f.read()

    readme = update_hello(readme)
    readme = update_tech(readme)
    readme = update_waka(readme)
    readme = update_blog(readme)
    readme = update_qotd(readme)

    with open("./README.md", "w") as f:
        f.write(readme)
