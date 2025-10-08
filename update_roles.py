import requests
import os
import time

GROUP_ID = 6011967  # BTF Turkish Armed Forces
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# Roller
TARGET_ROLES_1 = [
    "Büyük Konsey",
    "Ankara Heyeti",
    "Yüksek Askerî Şûra",
    "Yönetim Kurulu"
]

TARGET_ROLES_2 = [
    "Üst Yönetim Kurulu",
    "Askeri Disiplin Kurulu",
    "Askeri Kurultay",
    "Disiplin Kurulu",
    "Başkumandan",
    "Lider"
]

def get_roles():
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()["roles"]

def get_members(role_id):
    members = []
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users?limit=100"
    while url:
        resp = session.get(url)
        if resp.status_code != 200:
            return ["Üye bilgisi alınamadı"]
        data = resp.json()
        for m in data.get("data", []):
            name = m.get("user", {}).get("name", "Bilinmiyor")
            members.append(name)
        cursor = data.get("nextPageCursor")
        if cursor:
            url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users?cursor={cursor}&limit=100"
        else:
            url = None
    return members

def format_message(target_roles):
    roles = get_roles()
    msg = ""
    for role in roles:
        if role["name"] in target_roles:
            members = get_members(role["id"])
            msg += f"**{role['name']} ({len(members)} Kişi)**\n"
            for name in members:
                msg += f"{name}\n"
            msg += "\n"
    return msg

def send_to_discord(message, message_id=None):
    data = {"content": message}
    if message_id:
        resp = requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=data)
    else:
        resp = requests.post(WEBHOOK_URL, json=data)
        if resp.status_code in [200, 201, 204]:
            return resp.json().get("id")
    return None

def main():
    msg1_id = None
    msg2_id = None

    while True:
        msg1 = format_message(TARGET_ROLES_1)
        msg2 = format_message(TARGET_ROLES_2)

        msg1_id = send_to_discord(msg1, msg1_id)
        msg2_id = send_to_discord(msg2, msg2_id)

        print("Liste güncellendi. 20 dakika bekleniyor...")
        time.sleep(1200)  # 20 dakika bekle

if __name__ == "__main__":
    main()
