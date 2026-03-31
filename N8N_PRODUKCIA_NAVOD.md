# 🚀 n8n na Produkčnom Serveri - Návod na Použitie

## 📍 Prístup k n8n

**URL:** https://dqr.314.sk/n8n/

Po otvorení tejto URL sa ti zobrazí prihlasovacie okno n8n.

---

## 1️⃣ Prvé Prihlásenie (Admin)

Pri prvom spustení n8n si musel vytvoriť účet s emailom a heslom. Použi tieto údaje na prihlásenie.

**Ak si zabudol heslo:**
1. Klikni na "Forgot password?"
2. Zadaj email
3. Príde ti recovery link (ak máš nakonfigurovaný email v n8n)

---

## 2️⃣ Vytvorenie Prvého Workflow

### Krok 1: Nový Workflow
1. Po prihlásení klikni na **"+ Create Workflow"**
2. Otvorí sa prázdny canvas

### Krok 2: Pridaj Webhook Trigger
1. Klikni na **"+"** na canvase
2. Vyhľadaj **"Webhook"**
3. Vyber **"Webhook"** node
4. Nastav:
   - **HTTP Method:** POST
   - **Path:** `scan-notification` (alebo ľubovoľný názov)
5. Klikni **"Listen for Test Event"**
6. Skopíruj **Production URL** (bude vyzerať ako: `https://dqr.314.sk/n8n/webhook/scan-notification`)

### Krok 3: Pridaj Akciu (napr. Email)
1. Klikni na **"+"** za webhook node
2. Vyhľadaj akciu, naprz.:
   - **Gmail** - poslať email
   - **Slack** - správa do Slacku
   - **HTTP Request** - volať API
   - **Set** - len zapísať do logu
3. Nakonfiguruj akciu podľa potreby

### Krok 4: Ulož a Aktivuj
1. Vpravo hore klikni **"Save"**
2. Prepni prepínač na **"Active"** (vpravo hore)
3. Workflow je teraz spustený!

---

## 3️⃣ Registrácia Workflow v Django Admin

### Krok 1: Prihlás sa do Django Admin
**URL:** https://dqr.314.sk/admin/

### Krok 2: Choď do n8n Integration
1. V ľavom menu nájdi **"n8n Integration"**
2. Klikni na **"N8n Workflows"**

### Krok 3: Vytvor Nový Workflow
1. Klikni **"Add N8n Workflow"** (vpravo hore)
2. Vyplň:
   - **Name:** Scan Notification (alebo ľubovoľný názov)
   - **Workflow ID:** `scan-notification` (unikátny identifikátor)
   - **Webhook URL:** `https://dqr.314.sk/n8n/webhook/scan-notification` (URL z n8n)
   - **Description:** Pošle notifikáciu pri QR scane
   - **Is Active:** ✓ (zaškrtni)
3. Klikni **"Save"**

### Krok 4: Vytvor Automatický Trigger (voliteľné)
1. V admin paneli choď do **"N8n Triggers"**
2. Klikni **"Add N8n Trigger"**
3. Vyplň:
   - **Name:** QR Scan Auto Trigger
   - **Trigger Type:** Scan (vyber z dropdown)
   - **Workflow:** Vyber workflow čo si vytvoril
   - **Is Active:** ✓
4. Klikni **"Save"**

**Hotovo!** Teraz sa workflow automaticky spustí pri každom QR scane.

---

## 4️⃣ Test Workflow

### Manuálny Test z Django
1. Otvor: https://dqr.314.sk/n8n/workflows/
2. Nájdi svoj workflow
3. Klikni **"Spustiť"**
4. Workflow sa spustí okamžite

### Test cez QR Scan
1. Otvor mobilnú appku
2. Naskenuj QR kód
3. Workflow by sa mal automaticky spustiť
4. Skontroluj execution logs: https://dqr.314.sk/n8n/executions/

---

## 5️⃣ Monitorovanie a Debugging

### Execution Logs v Django
**URL:** https://dqr.314.sk/n8n/executions/

Tu vidíš:
- ✅ Úspešné spustenia
- ❌ Chyby
- 📊 Request/Response data
- ⏱️ Trvanie každého execution

### Execution History v n8n
1. V n8n klikni na **"Executions"** (ľavé menu)
2. Vidíš históriu všetkých spustení workflow
3. Klikni na konkrétne execution pre detail
4. Vidíš presne čo prešlo každým nodom

---

## 6️⃣ Najčastejšie Use Cases

### Use Case 1: Email pri QR Scane
**n8n Workflow:**
```
Webhook → Filter (len arrivals) → Gmail → Respond
```

**Použitie:**
Pri príchode zamestnanca ti príde email s časom a lokáciou.

---

### Use Case 2: Slack Notifikácia
**n8n Workflow:**
```
Webhook → Set (formatuj správu) → Slack → Respond
```

**Použitie:**
Každý scan sa automaticky zapíše do Slack kanála #attendance.

---

### Use Case 3: Denný Report
**n8n Workflow:**
```
Schedule (17:00) → HTTP Request (Django API) → Gmail
```

**Použitie:**
Každý deň o 17:00 dostaneš email so zhrnutím dochádzky.

---

### Use Case 4: Dovolenka - Schvaľovanie
**n8n Workflow:**
```
Webhook → Gmail (s approve/reject linkami) → Wait → HTTP Request (update Django)
```

**Použitie:**
Pri žiadosti o dovolenku dostane manažér email s linkami na schválenie/zamietnutie.

---

## 7️⃣ Pridanie Ďalších Používateľov

### V n8n
1. Klikni na **Settings** (⚙️ vľavo dole)
2. Vyber **"Users"**
3. Klikni **"Invite User"**
4. Zadaj email
5. Použi rolu:
   - **Owner** - plný prístup
   - **Admin** - spravovanie workflows
   - **Member** - len spúšťanie workflows

---

## 8️⃣ Bezpečnosť

### Webhook Security
Pri vytváraní webhooku v Django admin môžeš nastaviť **Secret Key**:
1. V admin → N8n Webhooks
2. Nastav `secret_key` (napr. náhodný reťazec)
3. n8n musí v requeste posielať tento key ako `X-N8N-Signature`

### HTTPS
Produkčný server by mal mať SSL certifikát (https://). Všetky komunikácie medzi n8n a Django sú potom šifrované.

---

## 9️⃣ Riešenie Problémov

### Workflow sa nespúšťa
1. ✅ Je workflow **Active** v n8n?
2. ✅ Je workflow **Is Active** v Django admin?
3. ✅ Je trigger **Is Active** v Django admin?
4. ✅ Je Webhook URL správna?

### Vidím chyby v Execution Logs
1. Otvor https://dqr.314.sk/n8n/executions/
2. Klikni na chybné execution
3. Pozri **Error Message**
4. Skontroluj **Request Data** - boli správne data poslané?

### n8n je pomalé
1. Skontroluj Docker containers: `docker ps`
2. Pozri logy: `docker logs qrreader-n8n-1`
3. Reštartuj: `docker-compose restart n8n`

---

## 🔟 Pokročilé Funkcie

### Credentials v n8n
Pre Gmail, Slack, API keys:
1. Settings → Credentials
2. Add Credential
3. Vyber službu (Gmail, Slack, atď.)
4. Autorizuj prístup

### Variables v n8n
Pre citlivé údaje (API keys):
1. Settings → Variables
2. Add Variable
3. Použi v workflow ako `{{$vars.nazov}}`

### Error Handling
Pridaj **Error Trigger** node:
1. Zachytí chyby vo workflow
2. Pošle notifikáciu pri chybe
3. Loguje do súboru

---

## 📚 Ďalšie Resources

- **n8n Dokumentácia:** https://docs.n8n.io/
- **n8n Community:** https://community.n8n.io/
- **Workflow Templates:** https://n8n.io/workflows/
- **Django n8n Integration README:** Na serveri v `/app/n8n_integration/README.md`

---

## 💡 Tipy

1. **Začni jednoducho** - Najprv vytvor jednoduchý workflow (napr. len log)
2. **Testuj v n8n** - Použij "Execute Workflow" pre manual testing
3. **Monitoruj executions** - Pravidelne kontroluj execution logs
4. **Používaj Error Handling** - Pridaj Error Trigger do každého workflow
5. **Dokumentuj workflows** - Pridaj poznámky a popis do každého workflow

---

## ✅ Quick Checklist

- [ ] Prihlásiť sa do n8n: https://dqr.314.sk/n8n/
- [ ] Vytvoriť prvý workflow
- [ ] Aktivovať workflow v n8n
- [ ] Zaregistrovať workflow v Django admin
- [ ] Vytvoriť trigger (voliteľné)
- [ ] Otestovať manuálne
- [ ] Otestovať automaticky (scan QR)
- [ ] Skontrolovať execution logs
- [ ] Profit! 🎉

---

**Ak niečo nefunguje, skontroluj execution logs na https://dqr.314.sk/n8n/executions/ - tam vidíš presne čo sa stalo a kde je problém!** 🔍
