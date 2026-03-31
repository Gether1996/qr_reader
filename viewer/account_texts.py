def _normalize_language_code(language_code):
    if not language_code:
        return 'en'
    return language_code.split('-')[0].lower()


def _get_text(language_code, variants):
    normalized = _normalize_language_code(language_code)
    return variants.get(normalized, variants['en'])


def get_employee_invite_texts(language_code):
    return {
        'subject': _get_text(language_code, {
            'sk': 'Nastavte si heslo pre svoj zamestnanecky ucet',
            'de': 'Legen Sie Ihr Passwort fuer Ihr Mitarbeiterkonto fest',
            'es': 'Configura la contrasena de tu cuenta de empleado',
            'en': 'Set your password for your employee account',
        }),
        'success_message': _get_text(language_code, {
            'sk': 'Zamestnanec bol vytvoreny a odoslali sme mu email s linkom na nastavenie hesla.',
            'de': 'Der Mitarbeiter wurde erstellt und wir haben ihm einen Link zum Festlegen des Passworts per E-Mail gesendet.',
            'es': 'Se ha creado el empleado y hemos enviado por correo electronico un enlace para configurar la contrasena.',
            'en': 'The employee was created and we sent them an email with a link to set their password.',
        }),
        'send_failed_message': _get_text(language_code, {
            'sk': 'Nepodarilo sa odoslat email s linkom na nastavenie hesla.',
            'de': 'Die E-Mail mit dem Link zum Festlegen des Passworts konnte nicht gesendet werden.',
            'es': 'No se pudo enviar el correo con el enlace para configurar la contrasena.',
            'en': 'Failed to send the password setup email.',
        }),
        'title': _get_text(language_code, {
            'sk': 'Nastavenie hesla pre vas ucet',
            'de': 'Passwort fuer Ihr Konto festlegen',
            'es': 'Configura la contrasena de tu cuenta',
            'en': 'Set your password for your account',
        }),
        'hello': _get_text(language_code, {
            'sk': 'Vitajte',
            'de': 'Willkommen',
            'es': 'Bienvenido',
            'en': 'Welcome',
        }),
        'intro': _get_text(language_code, {
            'sk': 'Vasa firma vam vytvorila ucet v QR Attendance System.',
            'de': 'Ihr Unternehmen hat ein Konto fuer Sie im QR Attendance System erstellt.',
            'es': 'Tu empresa ha creado una cuenta para ti en el QR Attendance System.',
            'en': 'Your company created an account for you in the QR Attendance System.',
        }),
        'cta_text': _get_text(language_code, {
            'sk': 'Ak chcete aktivovat pristup, kliknite na tlacidlo nizsie a nastavte si svoje heslo.',
            'de': 'Um Ihren Zugang zu aktivieren, klicken Sie auf die Schaltflaeche unten und legen Sie Ihr Passwort fest.',
            'es': 'Para activar tu acceso, haz clic en el boton de abajo y configura tu contrasena.',
            'en': 'To activate your access, click the button below and set your password.',
        }),
        'button_label': _get_text(language_code, {
            'sk': 'Nastavit heslo',
            'de': 'Passwort festlegen',
            'es': 'Configurar contrasena',
            'en': 'Set Password',
        }),
        'fallback_label': _get_text(language_code, {
            'sk': 'Alebo skopirujte a vlozte tento odkaz do prehliadaca:',
            'de': 'Oder kopieren Sie diesen Link und fuegen Sie ihn in Ihren Browser ein:',
            'es': 'O copia y pega este enlace en tu navegador:',
            'en': 'Or copy and paste this link into your browser:',
        }),
        'expiry_notice': _get_text(language_code, {
            'sk': 'Tento odkaz vyprsi o 24 hodin.',
            'de': 'Dieser Link laeuft in 24 Stunden ab.',
            'es': 'Este enlace caducara en 24 horas.',
            'en': 'This link will expire in 24 hours.',
        }),
        'ignore_notice_title': _get_text(language_code, {
            'sk': 'Neocakavali ste tento email?',
            'de': 'Haben Sie diese E-Mail nicht erwartet?',
            'es': 'No esperabas este correo?',
            'en': "Didn't expect this email?",
        }),
        'ignore_notice_text': _get_text(language_code, {
            'sk': 'Ak ste tento ucet neocakavali, kontaktujte svoju firmu. Kym si heslo nenastavite, do uctu sa neprihlasite.',
            'de': 'Falls Sie dieses Konto nicht erwartet haben, kontaktieren Sie bitte Ihr Unternehmen. Ohne gesetztes Passwort koennen Sie sich nicht anmelden.',
            'es': 'Si no esperabas esta cuenta, contacta con tu empresa. No podras iniciar sesion hasta que configures una contrasena.',
            'en': 'If you did not expect this account, please contact your company. You will not be able to sign in until you set a password.',
        }),
        'meta_company': _get_text(language_code, {
            'sk': 'Firma',
            'de': 'Firma',
            'es': 'Empresa',
            'en': 'Company',
        }),
        'meta_email': _get_text(language_code, {
            'sk': 'Email',
            'de': 'E-Mail',
            'es': 'Correo electronico',
            'en': 'Email',
        }),
        'meta_created_for': _get_text(language_code, {
            'sk': 'Vytvorene pre',
            'de': 'Erstellt fuer',
            'es': 'Creado para',
            'en': 'Created for',
        }),
        'meta_request_time': _get_text(language_code, {
            'sk': 'Cas odoslania',
            'de': 'Sendezeit',
            'es': 'Hora del envio',
            'en': 'Sent at',
        }),
        'footer_text': _get_text(language_code, {
            'sk': 'Toto je automaticka sprava z QR Attendance System. Na tento email neodpovedajte.',
            'de': 'Dies ist eine automatische Nachricht des QR Attendance System. Bitte antworten Sie nicht auf diese E-Mail.',
            'es': 'Este es un mensaje automatico del QR Attendance System. No respondas a este correo.',
            'en': 'This is an automated message from your QR Attendance System. Please do not reply to this email.',
        }),
    }


def get_user_password_setup_texts(language_code):
    return {
        'title': _get_text(language_code, {
            'sk': 'Nastavte si heslo',
            'de': 'Passwort festlegen',
            'es': 'Configura tu contrasena',
            'en': 'Set Your Password',
        }),
        'subtitle': _get_text(language_code, {
            'sk': 'Pred prvym prihlasenim si musite nastavit heslo pre svoj zamestnanecky ucet.',
            'de': 'Bevor Sie sich erstmals anmelden, muessen Sie ein Passwort fuer Ihr Mitarbeiterkonto festlegen.',
            'es': 'Antes de iniciar sesion por primera vez, debes configurar una contrasena para tu cuenta de empleado.',
            'en': 'Before your first sign in, you need to set a password for your employee account.',
        }),
        'requirements_title': _get_text(language_code, {
            'sk': 'Poziadavky na heslo',
            'de': 'Passwortanforderungen',
            'es': 'Requisitos de la contrasena',
            'en': 'Password Requirements',
        }),
        'requirement_length': _get_text(language_code, {
            'sk': 'Minimalne 10 znakov',
            'de': 'Mindestens 10 Zeichen',
            'es': 'Minimo 10 caracteres',
            'en': 'At least 10 characters',
        }),
        'requirement_uppercase': _get_text(language_code, {
            'sk': 'Aspoň jedno velke pismeno',
            'de': 'Mindestens ein Grossbuchstabe',
            'es': 'Al menos una letra mayuscula',
            'en': 'At least one uppercase letter',
        }),
        'requirement_match': _get_text(language_code, {
            'sk': 'Obe hesla sa musia zhodovat',
            'de': 'Beide Passwoerter muessen uebereinstimmen',
            'es': 'Ambas contrasenas deben coincidir',
            'en': 'Both password fields must match',
        }),
        'activate_button': _get_text(language_code, {
            'sk': 'Aktivovat ucet',
            'de': 'Konto aktivieren',
            'es': 'Activar cuenta',
            'en': 'Activate Account',
        }),
        'back_to_login': _get_text(language_code, {
            'sk': 'Spat na prihlasenie',
            'de': 'Zurueck zum Login',
            'es': 'Volver al inicio de sesion',
            'en': 'Back to Login',
        }),
        'invalid_link': _get_text(language_code, {
            'sk': 'Tento link na nastavenie hesla je neplatny alebo uz vyprsal.',
            'de': 'Dieser Link zum Festlegen des Passworts ist ungueltig oder bereits abgelaufen.',
            'es': 'Este enlace para configurar la contrasena no es valido o ya ha caducado.',
            'en': 'This password setup link is invalid or has expired.',
        }),
        'success_message': _get_text(language_code, {
            'sk': 'Heslo bolo uspesne nastavene. Teraz sa mozete prihlasit.',
            'de': 'Das Passwort wurde erfolgreich festgelegt. Sie koennen sich jetzt anmelden.',
            'es': 'La contrasena se ha configurado correctamente. Ya puedes iniciar sesion.',
            'en': 'Your password has been set successfully. You can now sign in.',
        }),
        'required_fields': _get_text(language_code, {
            'sk': 'Obe polia hesla su povinne.',
            'de': 'Beide Passwortfelder sind erforderlich.',
            'es': 'Ambos campos de contrasena son obligatorios.',
            'en': 'Both password fields are required.',
        }),
        'passwords_mismatch': _get_text(language_code, {
            'sk': 'Hesla sa nezhoduju.',
            'de': 'Die Passwoerter stimmen nicht ueberein.',
            'es': 'Las contrasenas no coinciden.',
            'en': 'Passwords do not match.',
        }),
        'password_length_error': _get_text(language_code, {
            'sk': 'Heslo musi mat aspon 10 znakov.',
            'de': 'Das Passwort muss mindestens 10 Zeichen lang sein.',
            'es': 'La contrasena debe tener al menos 10 caracteres.',
            'en': 'Password must be at least 10 characters long.',
        }),
        'password_uppercase_error': _get_text(language_code, {
            'sk': 'Heslo musi obsahovat aspon jedno velke pismeno.',
            'de': 'Das Passwort muss mindestens einen Grossbuchstaben enthalten.',
            'es': 'La contrasena debe contener al menos una letra mayuscula.',
            'en': 'Password must contain at least one uppercase letter.',
        }),
    }


def get_scan_mode_texts(language_code):
    return {
        'home_office': _get_text(language_code, {
            'sk': 'Home Office',
            'de': 'Homeoffice',
            'es': 'Trabajo desde casa',
            'en': 'Home Office',
        }),
        'business_trip': _get_text(language_code, {
            'sk': 'Pracovna cesta',
            'de': 'Dienstreise',
            'es': 'Viaje de negocios',
            'en': 'Business Trip',
        }),
        'no_qr': _get_text(language_code, {
            'sk': 'Bez QR',
            'de': 'Ohne QR',
            'es': 'Sin QR',
            'en': 'No QR',
        }),
        'choose_one_mobile_mode': _get_text(language_code, {
            'sk': 'Vyberte naraz iba jeden mobilny pracovny rezim.',
            'de': 'Waehlen Sie jeweils nur einen mobilen Arbeitsmodus aus.',
            'es': 'Elige solo un modo de trabajo movil a la vez.',
            'en': 'Choose only one mobile work mode at a time.',
        }),
    }
