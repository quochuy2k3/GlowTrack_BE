from beanie import PydanticObjectId
from bson import ObjectId

from database.database import add_tracker
from models.tracker import Tracker, ClassEnum
from datetime import datetime
import os
import uuid
from config.jwt_handler import decode_jwt
from fastapi import Depends
from models.routine import Day, Routine
from schemas.routine import DaySchema
from routes.media import upload_scan_image_to_cloudinary
from routes.routine import serialize_day


async def tracker_on_day(token: str, image_data: bytes, class_summary: dict):
    """
    Background task to save tracking data after skin condition detection.
    Checks if user already has a tracker for today and updates it instead of creating new.

    Args:
        token: JWT token for user authentication
        image_data: Image bytes to be stored
        class_summary: Summary of detected skin conditions
    """
    try:
        # Extract user ID from JWT token
        token_data = decode_jwt(token)
        user_id = token_data.get("sub")

        if not user_id:
            print("Error: Unable to extract user_id from token")
            return
        user_id = PydanticObjectId(user_id)  # Convert to PydanticObjectId

        # Upload image to Cloudinary
        img_url = await upload_scan_image_to_cloudinary(image_data)
        print(img_url)
        if "Error" in img_url:
            print(f"Error: {img_url}")
            return

        # Find user's routine
        routine = await Routine.find_one(Routine.user_id == user_id)

        if not routine:
            print(f"Warning: No routine found for user {user_id}")
            day_routine = None
        else:
            # Get current day's routine
            today_name = datetime.now().strftime("%A").lower()
            print(today_name)
            day_routine = None

            for day in routine.days:
                if day.day_of_week.lower() == today_name:
                    today_data = serialize_day(day)
                    day_routine = DaySchema.model_validate(today_data)
                    break

            if not day_routine:
                print(f"Warning: No routine found for today ({today_name}) for user {user_id}")

        today = datetime.now().date()
        existing_tracker = await Tracker.find_one({
            "user_id": ObjectId(str(user_id)),
            "date": today
        })

        if existing_tracker:
            existing_tracker.routine_of_day = day_routine
            existing_tracker.img_url = img_url
            existing_tracker.class_summary = class_summary

            await existing_tracker.save()
        else:
        # Create new tracker document
            tracker = Tracker(
                user_id=user_id,
                routine_of_day=day_routine,
                img_url=img_url,
                class_summary=class_summary,
                date=today
            )
            test_new_tracker = await add_tracker(tracker)

    except Exception as e:
        print(f"Error in tracker_on_day: {str(e)}")
