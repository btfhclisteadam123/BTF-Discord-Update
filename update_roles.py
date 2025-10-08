import requests
import os

GROUP_ID = 6011967
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
LAST_MESSAGE_FILE = "last_message_id.txt"

API_ROLES_URL = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles"
API_MEMBERS_URL = f"https://groups.roblox.com/v1/groups/{{group_id}}/roles/{{role_id}}/users?limit=100"

def get_roles():
    response = requests.get(API_ROLES_URL)
    response.raise_for_status()
    return response.json()["roles"]

def get_members(role_id):
    members = []
    cursor = ""
    while True:
        url = API_MEMBERS_URL.format(group_id=GROUP_ID, role_id=role_id)
        if cursor:
            url += f"&cursor={cursor}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for m in data.get("data", []):
            username = (
                m.get("username")
                or (m.get("user", {}).get("username") if isinstance(m.get("user"), dict) else None)
                or "Bilinmiyor"
            )
            members.append(username)
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return members if members else ["Üye yok"]

def build_message(roles):
    mesaj = ""
    mesaj += "**Büyük Konsey → Yönetim Kurulu**\n\n"
    for role_name in ["Büyük Konsey","Ankara Heyeti","Yüksek Askerî Şûra","Yönetim Kurulu"]:
        role = next((r for r in roles if r["name"] == role_name), None)
        if role:
            members = get_members(role["id"])
            mesaj += f"**{role_name} ({len(members)} Kişi)**\n"
            for name in members:
                mesaj += f"{name}\n"
            mesaj += "\n"

    mesaj += "**Üst Yönetim Kurulu → Lider**\n\n"
    for role_name in ["Üst Yönetim Kurulu","Askeri Disiplin Kurulu","Askeri Kurultay","Disiplin Kurulu","Başkumandan","Lider"]:
        role = next((r for r in roles if r["name"] == role_name), None)
        if role:
            members = get_members(role["id"])
            mesaj += f"**{role_name} ({len(members)} Kişi)**\n"
            for name in members:
                mesaj += f"{name}\n"
            mesaj += "\n"
    return mesaj

def send_to_discord(content):
    message_id = None
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, "r") as f:
            message_id = f.read().strip()

    if message_id:
        requests.patch(f"{DISCORD_WEBHOOK}/messages/{message_id}", json={"content": content})
    else:
        r = requests.post(DISCORD_WEBHOOK, json={"content": content})
        if r.status_code in (200, 204):
            try:
                message_id = r.json()["id"]
            except Exception:
                message_id = None

    if message_id:
        with open(LAST_MESSAGE_FILE, "w") as f:
            f.write(message_id)

def main():
    roles = get_roles()
    mesaj = build_message(roles)
    send_to_discord(mesaj)
    print("Liste Discord'a gönderildi/güncellendi.")

if __name__ == "__main__":
    main()
