import requests
import os

# Roblox grup ID
GROUP_ID = 6011967

# Discord Webhook URL, GitHub Secrets üzerinden alınacak
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")

# Önceki mesaj ID'sini kaydetmek için dosya
LAST_MESSAGE_FILE = "last_message_id.txt"

API_ROLES_URL = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/roles"
API_MEMBERS_URL = "https://groups.roblox.com/v1/groups/{group_id}/roles/{role_id}/users?limit=100"

def get_roles():
    r = requests.get(API_ROLES_URL)
    r.raise_for_status()
    return r.json().get("roles", [])

def get_members(role_id):
    members = []
    cursor = ""
    while True:
        url = API_MEMBERS_URL.format(group_id=GROUP_ID, role_id=role_id)
        if cursor:
            url += f"&cursor={cursor}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        for m in data.get("data", []):
            username = (
                m.get("user", {}).get("username")
                if isinstance(m.get("user"), dict)
                else m.get("username", "Bilinmiyor")
            )
            members.append(username)
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return members if members else ["Üye yok"]

def build_message(roles):
    mesaj = ""
    
    # 1. Blok: Büyük Konsey → Yönetim Kurulu
    mesaj += "**Büyük Konsey → Yönetim Kurulu**\n\n"
    for role_name in ["Büyük Konsey","Ankara Heyeti","Yüksek Askerî Şûra","Yönetim Kurulu"]:
        role = next((r for r in roles if r["name"] == role_name), None)
        if role:
            members = get_members(role["id"])
            mesaj += f"**{role_name} ({len(members)} Kişi)**\n"
            for name in members:
                mesaj += f"{name}\n"
            mesaj += "\n"
    
    # 2. Blok: Üst Yönetim Kurulu → Lider
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
    # Önceki mesaj ID'sini oku
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, "r") as f:
            message_id = f.read().strip()
    
    headers = {"Content-Type": "application/json"}

    if message_id:
        # Mevcut mesajı güncelle
        r = requests.patch(f"{DISCORD_WEBHOOK}/messages/{message_id}", json={"content": content}, headers=headers)
        if r.status_code not in [200, 204]:
            print("Mesaj güncellenemedi, yeni mesaj gönderiliyor...")
            r = requests.post(DISCORD_WEBHOOK, json={"content": content}, headers=headers)
            if r.status_code == 200:
                message_id = r.json().get("id")
    else:
        # Yeni mesaj gönder
        r = requests.post(DISCORD_WEBHOOK, json={"content": content}, headers=headers)
        if r.status_code == 200:
            message_id = r.json().get("id")
    
    # Mesaj ID'sini kaydet
    if message_id:
        with open(LAST_MESSAGE_FILE, "w") as f:
            f.write(message_id)

def main():
    try:
        roles = get_roles()
        mesaj = build_message(roles)
        send_to_discord(mesaj)
        print("Liste Discord'a gönderildi veya güncellendi.")
    except Exception as e:
        print("Hata oluştu:", e)

if __name__ == "__main__":
    main()
