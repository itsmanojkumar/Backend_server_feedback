from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

form_storage=[]
feedbackinput=[]

users = {
    "manager1": {"password": "pass123", "role": "manager"},
    "employee1": {"password": "employee123", "role": "employee"},
}

class FeedbackItem(BaseModel):
    message: str

class feedbackFormat(BaseModel):
    name:str
    feedback:List[FeedbackItem]

class LoginRequest(BaseModel):
    username: str
    password: str

class formdata(BaseModel):
    # Replace with your actual fields, for example:
    name: str
    strengths:str
    improve: str
    # sentiment:str

   # allow_origins=["http://localhost:3000","http://127.0.0.1:3000","https://your-frontend.onrender.com","https://backend-server-feedback.onrender.com"], 
    #  # Update as needed 
# Enable CORS for frontend (e.g., Next.js running on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GET endpoint (optional - for debugging or testing)
@app.get("/api/data")
async def get_data():
    return {
        "message": "Query parameters received",
        "data": form_storage
    }

# POST endpoint to receive form data (e.g., from <form> or JS FormData)

@app.delete("/api/data/{id}/")
async def delete(id:int):
    if 0 <= id < len(form_storage):
        deleted_item = form_storage.pop(id)
        return {"message": f"Item at index {id} deleted", "deleted": deleted_item}
    else:
        return HTTPException(status_code=404, detail="Item not found")






@app.post("/api/data")
async def receive_data(form: formdata):
    print("Received data:", form)
    form_storage.append(form)
    users[form.name] = {
    "password": form.name + "123",
    "role": "employee"
    }
    print("form storage:",form_storage)
    print("users:", users)
    return {"message": "Data received successfully!", "received": form}
# print(form)


# @app.post("/login")
# async def login(request:LoginRequest):
    # user=users.get(request.username)
    # print("hi")
    # if not user or user["password"] !=request.password:
        # raise HTTPException(status_code=401, detail="Invalid username or password")
    # print("User login successful")
    # return {"message": "Login successful"}
# 
@app.post("/login")
async def login(request: LoginRequest):
    user = users.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "role": user["role"], "username": request.username}

@app.post("/feedback")
async def feedbackform(payload:feedbackFormat):
    for existing in feedbackinput:
       if existing["name"] == payload.name:
            # Convert each FeedbackItem to a dict before appending
            new_feedback = [fb.model_dump() for fb in payload.feedback]
            existing["feedback"].extend(new_feedback)
            return {"message": "Feedback appended"}

    # Store the entire payload as a dict
    feedbackinput.append(payload.model_dump())
    return {"message": "Data received successfully"}


@app.get("/feedback")
async def feeddata():
    return {"feedback":feedbackinput}


@app.get("/feedback/{username}")
async def get_feedback(username: str):
    # Check if user exists in users dict
    user = users.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find all feedback entries where "name" matches username (case insensitive)
    matched_feedbacks = [fb for fb in feedbackinput if fb["name"].lower() == username.lower()]
    
    if not matched_feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found for this user")
    
    # Combine all feedback items from matched entries into one list
    combined_feedback = []
    for entry in matched_feedbacks:
        combined_feedback.extend(entry.get("feedback", []))
    
    # Return single object with username and all their feedback messages combined
    return {
        "name": username,
        "feedback": combined_feedback
    }

