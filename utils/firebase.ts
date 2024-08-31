import { initializeApp } from "firebase/app";
import { getStorage ,ref,getDownloadURL} from "firebase/storage";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: "AIzaSyBcssHbgb5l8Y5QUrV1DnajldZYJ2eAHWo",
    authDomain: "colorise-9dc75.firebaseapp.com",
    projectId: "colorise-9dc75",
    storageBucket: "colorise-9dc75.appspot.com",
    messagingSenderId: "521709902533",
    appId: "1:521709902533:web:9c00b4e14c0c6e2fa66eac",
    measurementId: "G-S3WRJ3YWVR"
}

const app = initializeApp(firebaseConfig);
export const storage = getStorage(app);
export const firestore = getFirestore(app); 
