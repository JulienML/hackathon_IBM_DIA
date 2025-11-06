# Intelligent Help Center for PLV students (group 3)

**Table of Contents**

- [📱 Context](#-context)
- [🏗 Prerequisites](#-prerequisites)
- [👩‍💻 Start the project](#-start-the-project)
    - [🧹 Data pre-process](#-data-pre-process)
        - [👁️🐝Ⓜ️ watsonx](#️ⓜ️-watsonx)
        - [🐍 Python](#-python)
    - [RAG](#rag)
    - [Front-end](#front-end)

---

## 📱 Context
The actual Help center, relies on researches on a database with 400 cases.
To improve the access to information for students, we developed an intelligent conversational agent who anderstand the request and give the correct answer, based on the questions of the database.

---
---

## 🏗 Prerequisites
Create a `.env` file in the root of the project and add the following environment variables:

```json
MISTRAL_API_KEY="your_mistral_api_key"
CHAINLIT_AUTH_SECRET="your_chainlit_auth_secret"
```

Get the CHAINLIT_AUTH_SECRET by executing `chainlit create-secret` in your terminal.

---

## 👩‍💻 Start the project
### 🧹 Data pre-process
#### 👁️🐝Ⓜ️ watsonx
1. Create an project on watsonx (ex: Hackathon_A5)
2. Upload your dataset (csv) on watsonx
3. Clic on your dataset then on "Prepare data"
4. Delete all the columns you don't need (only keep "Title", "Contente" and "Thématiques")
5. Create a concatenate columns grouping those three columns, with " | " as separator
6. Save it and download it

#### 🐍 Python
1. Upload the file containing your data in the source/preprocessing/ folder
2. Execute the preprocessing.py file

---

### RAG


---

### Front-end


---


Start app with:
```bash
cd source/app 
chainlit run app.py
```