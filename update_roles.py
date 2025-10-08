import os
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Örnek: Roller ve üyeleri burada çektiğinizi varsayalım
roles_list = {
    "Büyük Konsey": ["Üye1", "Üye2", "Üye3"],
    "Ankara Heyeti": ["Üye1", "Üye2"],
    "Yüksek Askerî Şûra": ["Üye1"],
    "Yönetim Kurulu": ["Üye1", "Üye2"],
    "Üst Yönetim Kurulu": ["Üye1"],
    "Askeri Disiplin Kurulu": ["Üye1"],
    "Askeri Kurultay": ["Üye1"],
    "Disiplin Kurulu": ["Üye1"],
    "Başkumandan": ["Üye1"],
    "Lider": ["Üye1", "Üye2"]
}

# Mesajı oluştur
def create_discord_message(roles):
    msg_parts = []
    # 2 mesaja bölmek için listeleri ayırabiliriz
    first_half_roles = ["Büyük Konsey","Ankara Heyeti","Yüksek Askerî Şûra","Yönetim Kurulu"]
    second_half_roles = ["Üst Yönetim Kurulu","Askeri Disiplin Kurulu","Askeri Kurultay","Disiplin Kurulu","Başkumandan","Lider"]

    def build_section(role_names):
        lines = []
        for role in role_names:
            members = roles.get(role, [])
            lines.append(f"**{role} ({len(members)} Kişi)**")
            for m in members:
                lines.append(f"- {m}")
            lines.append("")  # boş satır
        return "\n".join(lines)

    return build_section(first_half_roles), build_section(second_half_roles)

first_msg, second_msg = create_discord_message(roles_list)

# Discord'a gönder
requests.post(WEBHOOK_URL, json={"content": first_msg})
requests.post(WEBHOOK_URL, json={"content": second_msg})
