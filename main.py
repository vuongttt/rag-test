from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from typing import Optional
from rag import answer

app = FastAPI()

class Item(BaseModel):
    session_id: str | None = None
    serial_number: str | None = None
    option: int | None = None
    alarm_code: int | None = None

# implement this one using database for saving session_id and serial_number. You can use MongoDB
db = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/retrieve")
def read_item(item: Item = None):
    # print(f"session_id: {session_id}")
    # print(f"AAA: {serial_number}")
    if not item:
        item = Item()
    if item.session_id is None:
        item.session_id = str(uuid.uuid4())
    if item.serial_number:
        db[item.session_id] = item.serial_number
    if not db.get(item.session_id, None):
        return {"session_id": item.session_id, "text": "please provide the serial number"}
    else:
        if item.option is not None:
            if item.option == 1: # this is option for machine report
                # write some code to retrieve the machine report based on serial number
                return {"session_id": item.session_id, "text": "This is your machine report"}
            elif item.option == 2:
                if not item.alarm_code:
                    return {"session_id": item.session_id, "text": "Please provide alarm code"}
                else:
                    # write the code for using Langchain to return relavent document
                    # res = model.predict(serial_number)
                    res, pages = answer(item.alarm_code, serial_number=db[item.session_id])
                    return {"session_id": item.session_id, "text": res, "relevant_page": pages}
    return {"session_id": item.session_id, "serial_number": db[item.session_id]}