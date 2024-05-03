// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

const signup_btn = document.getElementById("signup-btn");
const login_btn = document.getElementById("login-btn");
const logout = document.getElementById('logout');

const firebaseConfig = {
    apiKey: "AIzaSyAz-78RvvfZq9y8M1yx-lwQSiHohzuw0FY",
    authDomain: "twitter-63278.firebaseapp.com",
    projectId: "twitter-63278",
    storageBucket: "twitter-63278.appspot.com",
    messagingSenderId: "1079117731044",
    appId: "1:1079117731044:web:775dc419d58c9e7f0988f1",
    measurementId: "G-RY11CVM2XX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

if (logout)
    logout.addEventListener('click', async () => {
        try {
            await signOut(auth);
            document.cookie = `token=;path=/;SameSite=Strict`;
            window.location.reload();
        } catch (error) {
            console.log(error);
        }
    }
    );

if (login_btn)
    login_btn.addEventListener('click', async e => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        if (!email && !password)
            return;

        try {
            const response = await signInWithEmailAndPassword(auth, email, password);

            const token = response._tokenResponse.idToken;
            document.cookie = `token=${token};path=/;SameSite=Strict`;

            setTimeout(() => {
                window.location = "/";
            }, 1000);


        } catch (error) {
            console.log(error);
        }

    });

if (signup_btn)
    signup_btn.addEventListener('click', async e => {
        e.preventDefault();

        const email = document.getElementById("signup-email").value;
        const password = document.getElementById("signup-password").value;

        if (!email && !password)
            return;

        try {
            await createUserWithEmailAndPassword(auth, email, password);

            window.location = "/login";

        } catch (error) {
            console.log(error);
        }

    });
