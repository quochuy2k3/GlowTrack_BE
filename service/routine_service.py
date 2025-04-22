import asyncio

import httpx
from beanie import PydanticObjectId
from database.database import add_routine
from models.routine import Day, Routine
from datetime import datetime

async def create_routine_for_new_user(user_id: PydanticObjectId):
    print(user_id)
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    routine_days = []

    for day in all_days:
        routine_days.append(Day(day_of_week=day, sessions=[]))

    routine = Routine(
        user_id=user_id,
        routine_name="Default Routine",
        days=routine_days
    )
    print(routine)

    new_routine = await add_routine(routine)

    return new_routine


async def get_routine_by_user_id(user_id: PydanticObjectId):
    routine = await Routine.find_one(Routine.user_id == user_id)
    return routine

async def send_push_notification(push_token: str, title: str,subtitle:str, body: str):
    print(push_token)
    message = {
        "to": push_token,
        "sound": "default",
        "title": title,
        "body": body,
        "badge": 1,
        # "data": {
        #     "messageId": "123",  # Dữ liệu bổ sung nếu cần
        #     "sender": "Huy"
        # }
    }
    url = "https://exp.host/--/api/v2/push/send"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=message)
        if response.status_code == 200:
            print(f"Notification sent successfully to {push_token}")
        else:
            print(f"Failed to send notification to {push_token}: {response.text}")

async def check_and_send_routine_notifications(user_routine: Routine):
    current_day = datetime.now().strftime('%A')  # Example: 'Monday', 'Tuesday', ...
    current_time = datetime.now().strftime('%I:%M %p').strip()  # Format time correctly and trim spaces

    if not user_routine.push_token:
        return
    
    for day in user_routine.days:
        if day.day_of_week == current_day:
            for session in day.sessions:
                session_time = session.time.strip()
                if session_time == current_time:  # Exact match
                    title =  f"Time for skincare"
                    subtitle =""
                    body = f"You have {len(session.steps)} steps in your skincare routine at {session_time}."
                    await send_push_notification(user_routine.push_token, title, subtitle,body)

async def reset_sessions_status(batch_size=100):
    current_time = datetime.utcnow()

    if current_time.hour == 0 and current_time.minute == 0:
        skip = 0
        while True:
            routines = await Routine.find().skip(skip).limit(batch_size).to_list()
            if not routines:
                break
            tasks = []
            for routine in routines:
                tasks.append(update_routine_sessions(routine))  # Reset session cho mỗi routine
            await asyncio.gather(*tasks)
            skip += batch_size  # Cập nhật skip để lấy lô tiếp theo
    else:
        print("Not time yet for reset.")  # Chỉ reset khi là 12h đêm

# Cập nhật trạng thái session thành "pending"
async def update_routine_sessions(routine: Routine):
    for day in routine.days:
        for session in day.sessions:
            session.status = "pending"
    await routine.save()  # Lưu lại routine đã thay đổi

# Cron job để gửi thông báo push và reset trạng thái session
async def cron_job(batch_size=100):
    print("Cron job is running...")
    skip = 0
    while True:
        # Lấy dữ liệu phân trang (batch_size)
        routines = await Routine.find().skip(skip).limit(batch_size).to_list()

        if not routines:
            break  # Dừng khi không còn dữ liệu

        tasks = []
        for routine in routines:
            tasks.append(check_and_send_routine_notifications(routine))  # Gửi thông báo push cho user

        # Thực thi các tác vụ song song
        await asyncio.gather(*tasks)  # Chạy các tác vụ song song

        skip += batch_size  # Cập nhật skip để lấy lô tiếp theo


