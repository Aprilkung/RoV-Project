from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from predictor import RoVDraftRecommender

# 1. สร้างตัวแอป API
app = FastAPI(title="RoV Draft API")

# อนุญาตให้ Frontend จากคนละเว็บเรียกขอข้อมูลได้ (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. โหลดโมเดลรอไว้เลย (ลดอาการหน่วงตอนเรียกใช้)
print("Initializing Recommender Engine...")
recommender = RoVDraftRecommender()

# 3. กำหนดหน้าตาข้อมูลที่ Frontend ต้องส่งมาให้ (Data Schema)
class DraftRequest(BaseModel):
    my_role: str
    allies: list[str] = []
    enemies: list[str] = []
    bans: list[str] = []

# 4. สร้างเส้นทาง (Endpoint) สำหรับรับค่าไปทำนาย
@app.post("/api/predict")
def predict_draft(req: DraftRequest):
    # เรียกใช้ฟังก์ชันเดิมจาก predictor.py เป๊ะๆ
    top3 = recommender.recommend(
        my_role=req.my_role,
        allies=req.allies,
        enemies=req.enemies,
        mastery_dict={},
        ban_list=req.bans
    )
    
    return {
        "status": "success",
        "recommendations": top3
    }

# เส้นทางสำหรับเช็กว่าเซิร์ฟเวอร์ยังรอดอยู่ไหม
@app.get("/")
def health_check():
    return {"status": "ok", "message": "RoV Draft API is running!"}