// Import and configure the Firebase SDK
// These scripts are made available when the app is served or deployed on Firebase Hosting
// If you do not serve/host your project using Firebase Hosting see https://firebase.google.com/docs/web/setup
// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/6.3.4/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/6.3.4/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in the
// messagingSenderId.
// firebase.initializeApp({
//   'messagingSenderId': '381198843122'
// });
var firebaseConfig = {
        apiKey: "AIzaSyAr4HwW7ISVnZf_3xP7FZuZ1X9Fs_J_HbA",
       authDomain: "trunkatdriver.firebaseapp.com",
       databaseURL: "https://trunkatdriver.firebaseio.com",
       projectId: "trunkatdriver",
       storageBucket: "",
       messagingSenderId: "381198843122",
       appId: "1:381198843122:web:6170940620fc77f5"
    };
    // Initialize Firebase
firebase.initializeApp(firebaseConfig);
// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
