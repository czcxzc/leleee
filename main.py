from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="用户管理CRUD(内存版)", version="1.0")

class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=20, description="用户名 2-20字符")
    email: str = Field(min_length=5, max_length=50, description="邮箱 5-50字符")
    age: Optional[int] = Field(default=None, ge=0, le=120, description="年龄0~120，可选")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=20)
    email: Optional[str] = Field(None, min_length=5, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=120)

class User(UserCreate):
    id: int

fake_users_db: List[User] = []
next_id = 1

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global next_id
    for u in fake_users_db:
        if u.username == user.username:
            raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(id=next_id, **user.model_dump())
    fake_users_db.append(new_user)
    next_id += 1
    return new_user

@app.get("/users", response_model=List[User])
def get_all_users():
    return fake_users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = next((u for u in fake_users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate):
    user = next((u for u in fake_users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_data = user_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    global fake_users_db
    user = next((u for u in fake_users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    fake_users_db = [u for u in fake_users_db if u.id != user_id]
    return

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
