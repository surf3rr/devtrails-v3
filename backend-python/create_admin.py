import firebase_admin
from firebase_admin import credentials, auth
import glob
import sys

def create_admin():
    try:
        cred_files = glob.glob("*firebase-adminsdk*.json")
        if not cred_files:
            print("[ERROR] No Firebase Admin SDK JSON found.")
            return

        cred = credentials.Certificate(cred_files[0])
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        email = "admin@parametric.ai"
        password = "adminpassword123"

        try:
            user = auth.get_user_by_email(email)
            print(f"[INFO] User {email} already exists. Updating password...")
            auth.update_user(user.uid, password=password)
            print("[SUCCESS] Password updated.")
        except auth.UserNotFoundError:
            print(f"[INFO] Creating new admin user: {email}")
            auth.create_user(email=email, password=password)
            print("[SUCCESS] Admin user created.")

        print(f"\n--- CREDENTIALS ---")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("-------------------")

    except Exception as e:
        print(f"[FAIL] Failed to create admin: {e}")

if __name__ == "__main__":
    create_admin()
