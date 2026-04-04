import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
// Replace these with actual config from Firebase Console when ready.
const firebaseConfig = {
  apiKey: "MOCK_API_KEY",
  authDomain: "mock-parametric.firebaseapp.com",
  projectId: "mock-parametric",
  storageBucket: "mock-parametric.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456:web:12345"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
