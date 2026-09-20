import unicodedata
import re
from dotenv import load_dotenv
import os
# ===================
load_dotenv()
class UserIDs:
    bipl = os.getenv('BIPL')
    noot = os.getenv('NOOT')
    bil = os.getenv('BIL')
    ruku = os.getenv('RUKU')
class ChannelIDs:
    main = os.getenv('MAIN')
# ===================

# Predefined substitutions (you can extend this list as needed)
letter_sub = {
    '3': 'e',
    '@': 'a',
}


def normalizeMsg(msg):
    """
    normalizeMsg normalizes an input 'msg', then encodes/decodes 'msg' through ASCII, and finally
    substitutes a list of characters for letters (e.g., 3->e, @->a)
    :param msg:
    :return:
    """
    # Normalize accented characters to their base form (e.g., 'é' -> 'e')
    msg = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode('ASCII')

    # Apply custom character substitutions (e.g., 3 -> e, @ -> a)
    for key, value in letter_sub.items():
        msg = msg.replace(key, value)

    return msg


async def hugeFunction(message):
    """
    hugeFunction detects if 'message' is the word "huge". If TRUE, the bot sends "Good Bot" with a
    petthebipl emoji. Otherwise, does nothing
    :param message:
    :return:
    """
    # Clean by normalization
    norm_msg = normalizeMsg(message.content.lower().strip())

    # Remove all characters that are not letters
    cleaned = re.sub(r'[^a-z]', '', norm_msg)

    # Only match messages that reduce *exactly* to "huge"
    if cleaned == "huge":
        await message.channel.send("Good Bot")
        await message.channel.send("<a:petthebipl:1441560087369093142>")
