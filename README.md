# Welcome to the IBM Hackathon! 🎉

This repository serves as a template to help you get started quickly.  
Follow the project structure, fork the repo, and clone it locally to begin.

---

## 1. Fork the Repository

1. Click **Fork** (top right) to create a copy under your own account
2. Make sure the fork is **public**  
   If it isn't, go to:  
   **Settings → Change repository visibility → Public**

---

## 2. Clone the Repository

Once you have forked the repository:

```bash
# Clone your fork (replace <your-user> and <repo> with your info)
git clone https://github.com/<your-user>/<repo>.git

# Move into the project folder
cd <repo>
```

---

## 3. Contribute

### Create a new branch for each feature or fix:

```bash
git checkout -b feature/my-awesome-feature
```

### Commit your changes:

```bash
git add .
git commit -m "Add: my awesome feature"
git push origin feature/my-awesome-feature
```

---

## 4. Quick Rules

✅ Keep your fork **public** during the hackathon  
✅ Follow the **template's structure**  
❓ For any questions: contact **kryptosphere@devinci.fr**

---

## 5. Have Fun and Good Luck!

Good luck during the IBM Hackathon — build, learn, and most importantly: **have fun!** 🚀

---

Create a `.env` file in the root of the project and add the following environment variables:

```json
MISTRAL_API_KEY="your_mistral_api_key"
CHAINLIT_AUTH_SECRET="your_chainlit_auth_secret"
```

Get the CHAINLIT_AUTH_SECRET by executing `chainlit create-secret` in your terminal.

Start app with:
```bash
cd source/app 
chainlit run app.py
```