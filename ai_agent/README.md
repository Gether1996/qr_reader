# 🤖 AI Agent - Telegram Bot s Instagram integráciou

Automatizovaný Telegram bot na plánovanie a publikovanie príspevkov na Instagram s hlasovými príkazmi.

## 🚀 Funkcie

- **Telegram Bot** - Komunikácia cez Telegram aplikáciu
- **Instagram Integration** - Publikovanie obrázkov na Instagram
- **Plánovanie postov** - Plán publikovania na špecifický čas
- **Hlasové príkazy** - Speech-to-text integrácia (TODO)
- **Celery Tasks** - Async plánovanie a spúšťanie postov
- **Admin panel** - Spravovanie postov cez Django admin

## 📋 Požiadavky

- Python 3.11+
- Redis (pre Celery)
- Django 5.2+

## ⚙️ Inštalácia

### 1. Nainštaluj závislosti

```bash
pip install -r requirements.txt
```

### 2. Skonfiguruj premenné prostredia

Skopíruj `ai_agent/.env.example` na `.env` a vyplň:

```bash
cp ai_agent/.env.example .env
```

Potrebuješ:
- **TELEGRAM_BOT_TOKEN** - Token od @BotFather na Telegrame
- **INSTAGRAM_USERNAME** - Tvoj Instagram username
- **INSTAGRAM_PASSWORD** - Tvoj Instagram password (alebo app password)

### 3. Spusti migruje

```bash
python manage.py migrate
```

### 4. Spusti Redis server

#### S Dockerom:
```bash
docker-compose up redis
```

#### Alebo ručne na WSL:
```bash
wsl
redis-server
```

### 5. Spusti Celery worker (v novom termináli)

```bash
celery -A qr_reader_django worker -l info
```

### 6. Spusti Telegram bot (v ďalšom termináli)

```bash
python manage.py run_telegram_bot
```

## 💬 Telegram Bot Príkazy

### Základné príkazy
- `/start` - Inicializácia bota
- `/help` - Zobrazí dostupné príkazy
- `/connect_instagram` - Pripojiť Instagram účet
- `/list_posts` - Zoznam naplánovaných postov

### Plánovanie príspevkov

**Textový príkaz:**
```
Postni fotku zajtra o 10:00 - Môj nový post!
```

**Hlasový príkaz:**
Pošli hlasovú správu a bot ju spracuje (TODO: Speech-to-text)

### Formát plánovania

```
Postni [fotku/obrázok] [čas] [popis]
```

Podporované časy:
- `zajtra o 10:00`
- `o 14:30`
- `v pondelok o 9:00`
- Vlastný čas: `2025-12-25 15:30`

## 📁 Štruktúra

```
ai_agent/
├── models.py              # DB modely
├── tasks.py               # Celery tasks
├── telegram_bot.py        # Telegram bot handler
├── admin.py              # Django admin
├── migrations/            # DB migrations
├── management/
│   └── commands/
│       └── run_telegram_bot.py  # Príkaz na spustenie bota
└── .env.example          # Šablóna premenných
```

## 🔧 Modely

### TelegramChat
- Uložené informácie o Telegram chatoch/užívateľoch
- Prepojenie na Django User model

### InstagramAccount
- Informácie o Instagram účtoch
- Šifrované heslo

### ScheduledPost
- Naplánované príspevky na Instagram
- Stav publikovania (pending, scheduled, posted, failed)

### TelegramMessage
- Log Telegram správ (text, voice)
- Sledovanie spracovaných správ

## 🔐 Bezpečnosť

⚠️ **Dôležité:**
- Hesla sú uložené ako plain-text - v produkcii šifruj
- Telegram token daj do `.env` súboru
- Nikdy nechceš commita `.env` na GitHub

### Šifrovanie hesiel (TODO)

Implementuj:
```python
from cryptography.fernet import Fernet

cipher = Fernet(key)
encrypted_password = cipher.encrypt(password.encode())
```

## 🚀 Deployment

### S Docker-om:

```bash
docker-compose up
```

To spustí:
- Web aplikáciu na `http://localhost:9005`
- Redis server na `localhost:6379`

### Manuálne:

1. Spusti Redis
2. Spusti Django migrations
3. Spusti Celery worker
4. Spusti Telegram bot command

```bash
redis-server &
python manage.py migrate
celery -A qr_reader_django worker -l info &
python manage.py run_telegram_bot
```

## 📊 Admin Panel

Prístup cez:
```
http://localhost:8000/admin
```

Tam môžeš:
- Spravovať Telegram chaty
- Spravovať Instagram účty
- Sledovať naplánované posty
- Vidieť históriu správ

## 🔮 TODO/Budúce funkcie

- [ ] Speech-to-text pre hlasové príkazy
- [ ] Šifrovanie hesiel v DB
- [ ] Komplikovanejší NLP parser príkazov
- [ ] Viac Instagram formátov (Reels, Stories, Carousel)
- [ ] Notifikácie o stave publikovania
- [ ] Web UI na plánovanie
- [ ] AI prompt generator na popis príspevkov

## 🐛 Riešenie problémov

### "Connection refused" - Redis
```bash
# Skontroluj Redis
redis-cli ping
# Mali by si dostať "PONG"
```

### "Bot token invalid"
- Skontroluj `.env` súbor
- Skontroluj `TELEGRAM_BOT_TOKEN` platnosť

### "Instagram login failed"
- Overenie účtu trvá dlho (2-3 sekúndy)
- Instagram môže blokovaní boty - skúsi [App Passwords](https://www.instagram.com/accounts/access_tool/)

## 📞 Kontakt

Otázky? Vytvor Issue na GitHub!

---

Made with ❤️ for automation
