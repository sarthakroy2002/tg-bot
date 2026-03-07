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

def get_token():
    with open(".tg_token", "r") as f:
        return f.read().strip()

def get_serpapi():
    with open(".serpapi", "r") as f:
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

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
