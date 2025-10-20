import os

import firebase_admin
from firebase_admin import credentials

# Firebase Admin SDK 초기화
print(os.getenv("FIREBASE_CREDENTIAL_DIR"))
FIREBASE_CRED = credentials.Certificate(os.getenv("FIREBASE_CREDENTIAL_DIR"))
firebase_admin.initialize_app(FIREBASE_CRED)
