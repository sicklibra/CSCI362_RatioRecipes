// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getFunctions, httpsCallable } from 'firebase/functions';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCa5cf6KPltX7fdTXEegyL8bRhrT1ifyc8",
  authDomain: "ratiorecipes-539cd.firebaseapp.com",
  projectId: "ratiorecipes-539cd",
  storageBucket: "ratiorecipes-539cd.firebasestorage.app",
  messagingSenderId: "1093323392107",
  appId: "1:1093323392107:web:753c14cab1ed7e41169d2e",
  measurementId: "G-33XY51CQ9J"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);
const firestore = getFirestore(app);
// Initialize and export the Firebase Authentication instance so the app can
// sign up, sign in, and sign out users using email/password.
const auth = getAuth(app);

// Export projectId for code that needs to build function URLs or reference the project
const projectId = firebaseConfig.projectId;

export { firestore, auth, projectId };