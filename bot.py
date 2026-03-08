import random
import time
import platform
import socket
import psutil
import requests
import whois
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from serpapi import GoogleSearch
import qrcode
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import subprocess
import math
import re
from datetime import datetime

def get_token():
    with open(".tg_token", "r") as f:
        return f.read().strip()

def get_serpapi():
    with open(".serpapi", "r") as f:
        return f.read().strip()

def get_github_token():
    with open(".github_token") as f:
        return f.read().strip()

TOKEN = get_token()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_cmd(update, context)


# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
Available Commands:

/anyone - Why do you ask
/eightball - Magic 8ball
/flipcoin - Flip a coin
/help - Show commands
/luck - Lucky number
/neo - System specs
/ping - Ping bot
/run - Runs :)
/uid - Get chat/user IDs
/urb [term] - Urban dictionary definition
/whois [site] - Whois lookup
/google or /g [query] - Get top 5 Google results
/qrg [text] - Generates a QR Code
/gh - GitHub user lookup
/ghrepo - GitHub repository stats
/devicespecs - Get device specs from GSMArena
/ip - IP lookup
/repo - GitHub repo search
/commit - Latest commits of repo
/yaap - Latest YAAP build for device
/pixelos - PixelOS official device info
/carbon - Generate Carbon code image
/todo - check all todos
/wiki - Search Wikipedia
/calc - Calculator
/yearleft - Year progress and remaining time
/dump - Dump firmware

"""
    await update.message.reply_text(text)


# /anyone
async def anyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Why do you ask?")


# /eightball
async def eightball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses = [
        "Yes",
        "No",
        "Maybe",
        "Definitely",
        "Ask again later",
        "Absolutely not",
        "Without a doubt"
    ]
    await update.message.reply_text(random.choice(responses))


# /flipcoin
async def flipcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["Heads", "Tails"]))


# /luck
async def luck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    await update.message.reply_text(f"Your lucky number today is: {number}")


# /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("Pinging...")
    end = time.time()
    latency = (end - start) * 1000
    await msg.edit_text(f"Pong! `{latency:.2f} ms`", parse_mode="Markdown")


# /run
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃 Running...")


# /uid
async def uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    text = f"""
Your ID: {user_id}
Chat ID: {chat_id}
"""

    if update.message.reply_to_message:
        replied_id = update.message.reply_to_message.from_user.id
        text += f"Replied User ID: {replied_id}"

    await update.message.reply_text(text)


# /neo (system specs)
async def neo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if platform.system().lower() == "linux":
        try:
            result = subprocess.run(
                ["neofetch", "--stdout"],
                capture_output=True,
                text=True
            )

            output = result.stdout

            if not output.strip():
                raise Exception("No output")

            await update.message.reply_text(
                f"<pre>{output}</pre>",
                parse_mode="HTML"
            )
            return

        except Exception:
            await update.message.reply_text(
                "Neofetch not installed on this system."
            )
            return

    # fallback for non-linux systems
    cpu = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    os_name = platform.system() + " " + platform.release()
    hostname = socket.gethostname()

    text = f"""
System Information

OS: {os_name}
CPU: {cpu}
RAM: {ram} GB
Hostname: {hostname}
"""

    await update.message.reply_text(text)


# /urb
async def urb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /urb <term>")
        return

    term = " ".join(context.args)
    url = f"https://api.urbandictionary.com/v0/define?term={term}"

    r = requests.get(url).json()

    if not r["list"]:
        await update.message.reply_text("No definition found.")
        return

    definition = r["list"][0]["definition"]

    await update.message.reply_text(
        f"Urban Dictionary: {term}\n\n{definition[:1000]}"
    )


# /whois
async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /whois <domain>")
        return

    domain = context.args[0]

    try:
        data = whois.whois(domain)

        text = f"""
Domain: {domain}
Registrar: {data.registrar}
Creation Date: {data.creation_date}
Expiration Date: {data.expiration_date}
Name Servers: {data.name_servers}
"""

        await update.message.reply_text(text)

    except:
        await update.message.reply_text("WHOIS lookup failed.")


async def google(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /google <query>")
        return

    query = " ".join(context.args)

    params = {
        "engine": "google",
        "q": query,
        "api_key": get_serpapi()
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" not in results:
        await update.message.reply_text("No results found.")
        return

    text = f"Top Google results for: {query}\n\n"

    for i, r in enumerate(results["organic_results"][:5], start=1):
        title = r.get("title")
        link = r.get("link")

        text += f"{i}. {title}\n{link}\n\n"

    await update.message.reply_text(text)

async def qrg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /qrg <text>")
        return

    text = " ".join(context.args)

    qr = qrcode.make(text)

    bio = BytesIO()
    bio.name = "qrcode.png"
    qr.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption=f"QR for:\n{text}")

async def gh(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /gh <username>")
        return

    username = context.args[0]

    url = f"https://api.github.com/users/{username}"
    r = requests.get(url)

    if r.status_code != 200:
        await update.message.reply_text("GitHub user not found.")
        return

    data = r.json()

    text = f"""
GitHub User: {data['login']}

Name: {data.get('name')}
Bio: {data.get('bio')}
Public Repos: {data['public_repos']}
Followers: {data['followers']}
Following: {data['following']}
Location: {data.get('location')}

Profile:
https://github.com/{username}
"""

    await update.message.reply_text(text)

async def ghrepo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /ghrepo <user/repo>")
        return

    repo = context.args[0]

    url = f"https://api.github.com/repos/{repo}"
    r = requests.get(url)

    if r.status_code != 200:
        await update.message.reply_text("Repository not found.")
        return

    data = r.json()

    text = f"""
Repository: {data['full_name']}

Description: {data.get('description')}

Stars: {data['stargazers_count']}
Forks: {data['forks_count']}
Open Issues: {data['open_issues_count']}
Language: {data.get('language')}

Repo URL:
{data['html_url']}
"""

    await update.message.reply_text(text)

async def devicespecs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /devicespecs <device name>")
        return

    query = " ".join(context.args)

    # Search GSMArena
    search_url = f"https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={query}"
    r = requests.get(search_url)

    soup = BeautifulSoup(r.text, "lxml")

    phone = soup.select_one(".makers ul li a")

    if not phone:
        await update.message.reply_text("Device not found.")
        return

    link = "https://www.gsmarena.com/" + phone["href"]

    # Open phone page
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "lxml")

    name = soup.select_one("h1.specs-phone-name-title").text

    specs = {}

    for row in soup.select("table tr"):
        key = row.select_one("td.ttl")
        val = row.select_one("td.nfo")

        if key and val:
            specs[key.text] = val.text

    text = f"📱 {name}\n\n"

    fields = [
        "Technology",
        "Announced",
        "Status",
        "Dimensions",
        "Weight",
        "Build",
        "SIM",
        "Display",
        "OS",
        "Chipset",
        "CPU",
        "GPU",
        "Memory",
        "Main Camera",
        "Selfie camera",
        "Battery"
    ]

    for f in fields:
        if f in specs:
            text += f"{f}: {specs[f]}\n"

    text += f"\nFull specs:\n{link}"

    await update.message.reply_text(text[:4000])

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /ip <ip address>")
        return

    ip = context.args[0]

    url = f"http://ip-api.com/json/{ip}"
    r = requests.get(url).json()

    if r["status"] != "success":
        await update.message.reply_text("Invalid IP address.")
        return

    text = f"""
IP: {r['query']}

Country: {r['country']}
Region: {r['regionName']}
City: {r['city']}

ISP: {r['isp']}
Org: {r['org']}

Timezone: {r['timezone']}
"""

    await update.message.reply_text(text)

async def repo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /repo <search term>")
        return

    query = " ".join(context.args)

    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"

    r = requests.get(url).json()

    if "items" not in r:
        await update.message.reply_text("No results found.")
        return

    text = f"Top GitHub repos for: {query}\n\n"

    for repo in r["items"][:5]:
        text += f"""
{repo['full_name']}
⭐ {repo['stargazers_count']} | Forks {repo['forks_count']}
{repo['html_url']}

"""

    await update.message.reply_text(text)

async def commit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /commit <user/repo>")
        return

    repo = context.args[0]

    url = f"https://api.github.com/repos/{repo}/commits"
    r = requests.get(url)

    if r.status_code != 200:
        await update.message.reply_text("Repository not found.")
        return

    commits = r.json()

    repo_name = repo.split("/")[-1]

    text = f"""<b>Repo:</b> <a href="https://github.com/{repo}">{repo_name}</a>\n"""

    for c in commits[:10]:

        msg = c["commit"]["message"].split("\n")[0]
        author = c["commit"]["author"]["name"]
        sha = c["sha"][:7]

        link = f"https://github.com/{repo}/commit/{c['sha']}"

        date_str = c["commit"]["author"]["date"]
        commit_time = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)

        diff = now - commit_time
        hours = int(diff.total_seconds() // 3600)

        if hours < 1:
            time_text = "just now"
        elif hours < 24:
            time_text = f"{hours} hours ago"
        else:
            days = hours // 24
            time_text = f"{days} days ago"

        text += f"""
<b><a href="{link}">{sha}</a> - {msg}</b>
👤 {author} | 🕒 {time_text}
"""

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

def get_date(filename):
    if filename.endswith(".zip"):
        date = filename.split("-")[-1].replace(".zip", "")
        if len(date) == 8:
            return f"{date[:4]}-{date[4:6]}-{date[6:]}"
    return None


async def yaap(update, context):

    if not context.args:
        await update.message.reply_text("Provide a device codename!\nUsage: /yaap <device>")
        return

    device = context.args[0]

    try:
        # get OTA branches
        branch_url = f"https://raw.githubusercontent.com/YAAP/device-info/master/{device}/{device}.json"
        branch_data = requests.get(branch_url).json()

        gapps_branch = branch_data["ota-branch"]
        vanilla_branch = branch_data["ota-branch-vanilla"]

        # fetch build info
        gapps_url = f"https://raw.githubusercontent.com/YAAP/ota-info/{gapps_branch}/{device}/{device}.json"
        vanilla_url = f"https://raw.githubusercontent.com/YAAP/ota-info/{vanilla_branch}/{device}/{device}.json"

        gapps_data = requests.get(gapps_url).json()
        vanilla_data = requests.get(vanilla_url).json()

        gapps_filename = gapps_data["response"][0]["filename"]
        vanilla_filename = vanilla_data["response"][0]["filename"]

        date = get_date(gapps_filename) or get_date(vanilla_filename) or "Unknown"

        text = f"""
Latest YAAP Releases for {device} ({date})
"""

        gapps_link = f"https://mirror.codebucket.de/yaap/{device}/{gapps_filename}"
        vanilla_link = f"https://mirror.codebucket.de/yaap/{device}/vanilla/{vanilla_filename}"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("GApps", url=gapps_link)],
            [InlineKeyboardButton("Vanilla", url=vanilla_link)]
        ])

        await update.message.reply_text(text, reply_markup=keyboard)

    except Exception:
        await update.message.reply_text("Failed to fetch YAAP build information.")

async def pixelos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /pixelos <device codename>")
        return

    device = context.args[0]

    url = f"https://raw.githubusercontent.com/PixelOS-AOSP/official_devices/refs/heads/sixteen/API/devices/{device}.json"

    try:
        r = requests.get(url)

        if r.status_code != 200:
            await update.message.reply_text("Device not found in PixelOS official list.")
            return

        data = r.json()

        model = data.get("model", "Unknown")
        codename = data.get("codename", device)
        version = data.get("version", "Unknown")
        last_updated = data.get("last_updated", "Unknown")

        download_link = data.get("download_link")
        archive_link = data.get("archive")

        maintainers_text = ""

        maintainers = data.get("maintainer", [])

        if maintainers:
            for m in maintainers:
                name = m.get("display_name", "Unknown")
                tg = m.get("telegram")

                if tg:
                    maintainers_text += f'• <a href="https://t.me/{tg}">{name}</a>\n'
                else:
                    maintainers_text += f'• {name}\n'
        else:
            maintainers_text = "Unknown"

        text = f"""
<b>PixelOS Device Information</b>

<b>Model:</b> {model}
<b>Codename:</b> {codename}
<b>Version:</b> {version}
<b>Last Updated:</b> {last_updated}

<b>Maintainers:</b>
{maintainers_text}
"""

        buttons = []

        if download_link:
            buttons.append([InlineKeyboardButton("⬇️ Download", url=download_link)])

        if archive_link:
            buttons.append([InlineKeyboardButton("📦 Archive", url=archive_link)])

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    except Exception:
        await update.message.reply_text("Failed to fetch PixelOS device info.")

async def carbon(update: Update, context: ContextTypes.DEFAULT_TYPE):

    code = None

    # if replying to a message
    if update.message.reply_to_message:
        code = update.message.reply_to_message.text

    # if text provided
    elif context.args:
        code = " ".join(context.args)

    if not code:
        await update.message.reply_text(
            "Usage:\n/carbon <code>\nor reply to a message with /carbon"
        )
        return

    url = "https://carbonara.solopov.dev/api/cook"

    try:
        r = requests.post(url, json={"code": code})

        if r.status_code != 200:
            raise Exception("Failed")

        img = BytesIO(r.content)
        img.name = "carbon.png"

        await update.message.reply_photo(img)

    except Exception:
        await update.message.reply_text("Failed to generate Carbon image.")

def get_superadmin():
    try:
        with open(".admin", "r") as f:
            return int(f.read().strip())
    except:
        return None


def read_todos():
    try:
        with open("todo.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []


def write_todos(tasks):
    with open("todo.txt", "w") as f:
        for task in tasks:
            f.write(task + "\n")

async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    superadmin = get_superadmin()

    tasks = read_todos()

    # SHOW TODO LIST
    if not context.args:
        if not tasks:
            await update.message.reply_text("TODO list is empty.")
            return

        text = "TODO List\n\n"

        for i, task in enumerate(tasks, start=1):
            text += f"{i}. {task}\n"

        await update.message.reply_text(text)
        return

    cmd = context.args[0]

    # ADD TASK
    if cmd == "add":

        if user_id != superadmin:
            await update.message.reply_text("Only superadmin can add tasks.")
            return

        task = " ".join(context.args[1:])

        if not task:
            await update.message.reply_text("Usage: /todo add <task>")
            return

        tasks.append(task)
        write_todos(tasks)

        await update.message.reply_text("Task added.")
        return

    # MARK DONE
    if cmd == "done":

        if user_id != superadmin:
            await update.message.reply_text("Only superadmin can remove tasks.")
            return

        if len(context.args) < 2:
            await update.message.reply_text("Usage: /todo done <task number>")
            return

        try:
            num = int(context.args[1]) - 1
        except:
            await update.message.reply_text("Invalid number.")
            return

        if num < 0 or num >= len(tasks):
            await update.message.reply_text("Task number not found.")
            return

        removed = tasks.pop(num)
        write_todos(tasks)

        await update.message.reply_text(f"Completed: {removed}")

async def wiki(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /wiki <search term>")
        return

    query = " ".join(context.args)

    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query

        r = requests.get(url)

        if r.status_code != 200:
            await update.message.reply_text("No Wikipedia page found.")
            return

        data = r.json()

        title = data.get("title", query)
        summary = data.get("extract", "No summary available.")
        page_url = data.get("content_urls", {}).get("desktop", {}).get("page")

        text = f"""
<b>{title}</b>

{summary}

🔗 <a href="{page_url}">Read full article</a>
"""

        # telegram message limit protection
        if len(text) > 4000:
            text = text[:3900] + "..."

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception:
        await update.message.reply_text("Failed to fetch Wikipedia article.")

# Calculator
allowed_names = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "pi": math.pi,
    "e": math.e
}

def safe_eval(expr):

    expr = expr.replace("^", "**")

    code = compile(expr, "<calc>", "eval")

    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"{name} not allowed")

    return eval(code, {"__builtins__": {}}, allowed_names)


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage: /calc <expression>\nExample: /calc (5+3)*10"
        )
        return

    expr = " ".join(context.args)

    try:
        result = safe_eval(expr)

        await update.message.reply_text(
            f" <b>{expr}</b>\n= <code>{result}</code>",
            parse_mode="HTML"
        )

    except Exception:
        await update.message.reply_text("Invalid calculation.")

# Time left in year
async def yearleft(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now()

    start = datetime(now.year, 1, 1)
    end = datetime(now.year + 1, 1, 1)

    total_seconds = (end - start).total_seconds()
    passed_seconds = (now - start).total_seconds()
    remaining_seconds = (end - now).total_seconds()

    percent = (passed_seconds / total_seconds) * 100

    days = int(remaining_seconds // 86400)
    months = days // 30
    minutes = int(remaining_seconds // 60)
    seconds = int(remaining_seconds)

    # progress bar
    bar_length = 20
    filled = int(percent / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    text = f"""
📅 <b>{now.year} Progress</b>

{bar}
{percent:.2f}% completed

<b>⏳ Time Left</b>
{months} months
{days} days
{minutes} minutes
{seconds} seconds
"""

    await update.message.reply_text(text, parse_mode="HTML")

async def dump(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    admin = get_superadmin()

    if user_id != admin:
        await update.message.reply_text("Only superadmin can trigger dumps.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /dump <firmware link>")
        return

    link = context.args[0]

    token = get_github_token()

    url = "https://api.github.com/repos/sarthakroy2002/Dumpr-Workflow/actions/workflows/dumper.yml/dispatches"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "link": link
        }
    }

    r = requests.post(url, json=payload, headers=headers)

    if r.status_code == 204:
        await update.message.reply_text(
            "🚀 Dumper workflow triggered.\n\n"
            "Check status:\n"
            "https://github.com/sarthakroy2002/Dumpr-Workflow/actions"
        )
    else:
        await update.message.reply_text("Failed to trigger workflow.")

# Main
def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("anyone", anyone))
    app.add_handler(CommandHandler("eightball", eightball))
    app.add_handler(CommandHandler("flipcoin", flipcoin))
    app.add_handler(CommandHandler("luck", luck))
    app.add_handler(CommandHandler("neo", neo))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("uid", uid))
    app.add_handler(CommandHandler("urb", urb))
    app.add_handler(CommandHandler("whois", whois_lookup))
    app.add_handler(CommandHandler("google", google))
    app.add_handler(CommandHandler("g", google))
    app.add_handler(CommandHandler("qrg", qrg))
    app.add_handler(CommandHandler("gh", gh))
    app.add_handler(CommandHandler("ghrepo", ghrepo))
    app.add_handler(CommandHandler("devicespecs", devicespecs))
    app.add_handler(CommandHandler("ip", ip))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("commit", commit))
    app.add_handler(CommandHandler("yaap", yaap))
    app.add_handler(CommandHandler("pixelos", pixelos))
    app.add_handler(CommandHandler("carbon", carbon))
    app.add_handler(CommandHandler("todo", todo))
    app.add_handler(CommandHandler("wiki", wiki))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("yearleft", yearleft))
    app.add_handler(CommandHandler("dump", dump))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
