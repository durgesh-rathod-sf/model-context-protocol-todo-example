# File: api_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory "database"
todos = []
todo_id_counter = 1

# Pydantic model for input and output
class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

@app.get("/todos", response_model=List[Todo])
def get_todos():
    print("API Called: get_todos")
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    print("API Called: get_todo")
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    print("API Called: create_todo")
    global todo_id_counter
    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    }
    todos.append(new_todo)
    todo_id_counter += 1
    return new_todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoCreate):
    print("API Called: update_todo")
    for todo in todos:
        if todo["id"] == todo_id:
            todo["title"] = updated_todo.title
            todo["description"] = updated_todo.description
            todo["completed"] = updated_todo.completed
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    print("API Called: delete_todo")
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos.pop(i)
            return {"message": f"Todo with id {todo_id} deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")


