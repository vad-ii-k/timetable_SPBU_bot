from datetime import timedelta, date


async def calculator_of_days(day_counter: int) -> tuple:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    next_day = current_date + timedelta(days=1)
    return current_date, next_day


async def calculator_of_week_days(week_counter: int) -> tuple[date, date]:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


async def get_weekday_sticker(day: str) -> str:
    weekday_sticker = ''
    match day.split(",")[0]:
        case 'понедельник' | 'Monday':
            weekday_sticker = '1️⃣'
        case 'вторник' | 'Tuesday':
            weekday_sticker = '2️⃣'
        case 'среда' | 'Wednesday':
            weekday_sticker = '3️⃣'
        case 'четверг' | 'Thursday':
            weekday_sticker = '4️⃣'
        case 'пятница' | 'Friday':
            weekday_sticker = '5️⃣'
        case 'суббота' | 'Saturday':
            weekday_sticker = '6️⃣'
        case 'воскресенье' | 'Sunday':
            weekday_sticker = '7️⃣'
    return weekday_sticker
