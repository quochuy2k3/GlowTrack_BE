import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os
import uuid
router = APIRouter()

cloudinary.config(
    cloud_name="dxplnavr4",
    api_key="953825491913616",
    api_secret="CpEw3D-ewDAVXyJdHLowM3JBzkY",
    secure=True
)

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Tạo thư mục 'temp' nếu nó chưa tồn tại
        os.makedirs('temp', exist_ok=True)

        # Lưu tạm file ảnh
        file_location = f"temp/{file.filename}"
        with open(file_location, "wb") as buffer:
            buffer.write(await file.read())

        # Tải lên Cloudinary
        response = cloudinary.uploader.upload(file_location)

        # Trả về URL của hình ảnh đã được upload
        return JSONResponse(content={"url": response["secure_url"]})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


async def upload_scan_image_to_cloudinary(image_bytes: bytes):
    try:
        # Tạo thư mục 'temp' nếu nó chưa tồn tại
        os.makedirs('temp', exist_ok=True)
        file_location = f"temp/{uuid.uuid4()}.jpg"

        # Write image bytes to file
        with open(file_location, "wb") as buffer:
            buffer.write(image_bytes)

        # Upload image to Cloudinary
        response = cloudinary.uploader.upload(file_location)

        # Return the secure URL as a string
        return response["secure_url"]

    except Exception as e:
        # In case of an error, return an error message
        return str(e)




