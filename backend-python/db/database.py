import firebase_admin
from firebase_admin import firestore
import time
import os

def get_firestore_client():
    try:
        # Check if Firebase app is initialized
        app = firebase_admin.get_app()
        # Return the real Firestore client
        client = firestore.client()
        return client
    except ValueError:
        # ValueError means no app initialized — use mock
        print("Using MockFirestoreClient fallback. Setup firebase credentials to use real firestore.")
        return MockFirestoreClient()
    except Exception as e:
        print(f"Firestore client error: {e}. Falling back to mock.")
        return MockFirestoreClient()

class MockFirestoreClient:
    def collection(self, name):
        return MockCollection(name)

class MockCollection:
    def __init__(self, name):
        self.name = name
    def document(self, id=None):
        return MockDocument(id or f"mock_{int(time.time())}")
    def where(self, *args):
        return self
    def limit(self, *args):
        return self
    def order_by(self, *args, **kwargs):
        return self
    def stream(self):
        return []
    def add(self, data):
        print(f"[MOCK FIRESTORE] Added to {self.name}: {data}")
        mock_doc = MockDocument(f"mock_{int(time.time())}")
        return (None, mock_doc)

class MockDocument:
    def __init__(self, id):
        self.id = id
    def set(self, data, merge=False):
        print(f"[MOCK FIRESTORE] Set {self.id}: {data}")
    def get(self):
        return MockSnapshot(self.id, {})
    def update(self, data):
        print(f"[MOCK FIRESTORE] Update {self.id}: {data}")

class MockSnapshot:
    def __init__(self, id, data):
        self.id = id
        self._data = data
        self.exists = False
    def to_dict(self):
        return self._data
