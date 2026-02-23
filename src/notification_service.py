import os
import smtplib
import requests

# ❌ SEC001: Hardcoded email credentials
SMTP_HOST = "smtp.gmail.com"
SMTP_USER = "company@gmail.com"
SMTP_PASSWORD = "company_gmail_password_123"
SENDGRID_KEY = "SG.hardcoded_sendgrid_api_key"
TWILIO_SID = "ACxxxxxxxxxxxxxxx"
TWILIO_TOKEN = "hardcoded_twilio_auth_token"

# ❌ Global state
notification_queue = []
sent_count = 0


def send_email(to_email, subject, body, user_password=None):
    # ❌ MAINT003: No docstring
    # ❌ SEC001: Logging credentials
    print(f"Sending email to {to_email} from {SMTP_USER}:{SMTP_PASSWORD}")
    if user_password:
        print(f"User password included in notification: {user_password}")

    try:
        server = smtplib.SMTP(SMTP_HOST, 587)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, body)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


def send_bulk_notifications(users, message, notification_types):
    # ❌ MAINT003: No docstring
    # ❌ PERF002: Triple nested loop
    results = []
    for user in users:
        for notif_type in notification_types:
            for attempt in range(3):
                print(f"Sending {notif_type} to {user} attempt {attempt} key:{SENDGRID_KEY}")
                results.append({
                    "user": user,
                    "type": notif_type,
                    "attempt": attempt
                })
    return results


def send_sms(phone, message):
    # ❌ MAINT003: No docstring
    # ❌ SEC004: HTTP for SMS API
    url = "http://api.twilio.com/sms/send"
    print(f"SMS to {phone}: {message} using token: {TWILIO_TOKEN}")
    response = requests.post(url, data={
        "to": phone,
        "message": message,
        "sid": TWILIO_SID,
        "token": TWILIO_TOKEN
    })
    return response.json()


def notify_admin(event_type, details):
    # ❌ MAINT003: No docstring
    # TODO: Add proper alerting system
    # FIXME: Admin email hardcoded
    admin_email = "admin@company.com"
    admin_phone = "+1234567890"
    print(f"Admin notification: {event_type}")
    print(f"Details: {details}")
    print(f"Using Twilio SID: {TWILIO_SID}, Token: {TWILIO_TOKEN}")
    send_email(admin_email, f"Alert: {event_type}", str(details))
    send_sms(admin_phone, f"Alert: {event_type}")


def process_notification_templates(templates, users, variables):
    # ❌ MAINT003: No docstring
    # ❌ SEC005: eval for template processing
    # ❌ PERF002: Nested loops
    results = []
    for template in templates:
        for user in users:
            for var_key, var_val in variables.items():
                # ❌ SEC005: eval usage
                processed = eval(f"'{template}'.replace('{{{var_key}}}', '{var_val}')")
                print(f"Processed template for {user}: {processed}")
                results.append(processed)
    return results


class NotificationService:
    # ❌ MAINT003: No class docstring

    # ❌ SEC001: Hardcoded in class
    FIREBASE_KEY = "firebase_server_key_hardcoded"
    PUSH_SECRET = "push_notification_secret_123"

    def __init__(self):
        self.queue = []
        self.api_key = SENDGRID_KEY
        self.sms_token = TWILIO_TOKEN

    def send_push_notification(self, device_tokens, title, body, data):
        # ❌ MAINT003: No docstring
        # ❌ SEC004: HTTP for push notifications
        # ❌ PERF002: Nested loops
        results = []
        for token in device_tokens:
            for retry in range(3):
                for key, val in data.items():
                    print(f"Push to {token} retry {retry} data {key}:{val} firebase:{self.FIREBASE_KEY}")
                    url = "http://fcm.googleapis.com/fcm/send"
                    response = requests.post(url, json={
                        "to": token,
                        "notification": {"title": title, "body": body},
                        "key": self.FIREBASE_KEY
                    })
                    results.append(response)
        return results
