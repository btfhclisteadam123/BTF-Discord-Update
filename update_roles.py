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

# Tüm roller
def get_roles():
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()["roles"]

# Bir role ait üyeleri al
def get_members(role_id):
    members = []
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users?limit=100"
    while url:
        resp = session.get(url)
        resp.raise_for_status()
        data = resp.json()
        for m in data.get("data", []):
            if "user" in m and "name" in m["user"]:
                members.append(m["user"]["name"])
            else:
                members.append("Bilinmiyor")
        cursor = data.get("nextPageCursor")
        if cursor:
            url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles/{role_id}/users?cursor={cursor}&limit=100"
        else:
            url = None
    return members

# Mesaj formatla
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

# Discord’a gönder veya güncelle
def send_to_discord(message, message_id=None):
    data = {"content": message}
    try:
        if message_id:
            resp = requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=data)
            return message_id
        else:
            resp = requests.post(WEBHOOK_URL, json=data)
            resp.raise_for_status()
            try:
                return resp.json().get("id")
            except:
                return None
    except Exception as e:
        print(f"Discord gönderme hatası: {e}")
        return None

def main():
    message_id_1 = None
    message_id_2 = None

    while True:
        # 1. Mesaj: Büyük Konsey → Yönetim Kurulu
        msg1 = format_message(TARGET_ROLES_1)
        message_id_1 = send_to_discord(msg1, message_id_1)

        # 2. Mesaj: Üst Yönetim Kurulu → Lider
        msg2 = format_message(TARGET_ROLES_2)
        message_id_2 = send_to_discord(msg2, message_id_2)

        print("Mesajlar güncellendi. 20 dakika bekleniyor...")
        time.sleep(1200)  # 1200 saniye = 20 dakika

if __name__ == "__main__":
    main()
