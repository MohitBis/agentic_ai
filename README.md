# agentic-ai-cicd-bot
Agentic AI implementation of CICD 

# Pre-requisite

1. Setup an auth layer using mongo DB 
  ```
  podman run -d --name mongod -p 27017:27017 mongo
  podman exec -it mongod mongosh
  ```

2. Create a user with admin role
  ```
  use jenkins_ai
  
  db.users.insertOne({ "username": "dev", "password": "admin@123", "role": "admin" })
  
  db.users.find().pretty()
  ```
3. Run LLM from ollama ( Install ollama first)

  ```
  ollama run llama3
  ```

# To run the UI Bot (frontend) code
1. source venv/bin/activate
2. git clone git@github.ibm.com:Pavan-Govindraj/agentic-ai-cicd-bot.git
3. cd agentic-ai-cicd-bot/
4. pip install -r backend/requirements.txt
5. pip install -r frontend/requirements.txt
6. cd frontend
7. streamlit run app.py
