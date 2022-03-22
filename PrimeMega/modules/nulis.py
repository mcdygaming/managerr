import os

from PIL import Image, ImageDraw, ImageFont
from PrimeMega.events import register, text_set
from PrimeMega.modules.language import gs

@register(pattern="^/nulis(?: |$)(.*)")
async def writer(event):
    if event.reply_to:
        reply = await event.get_reply_message()
        text = reply.message
    elif event.pattern_match.group(1).strip():
        text = event.text.split(maxsplit=1)[1]
    else:
        return await event.edit("Berikan Beberapa Teks")
    k = await event.reply ("Sedang Memproses..")
    img = Image.open("PrimeMega/resources/kertas.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("PrimeMega/resources/assfont.ttf", 30)
    x, y = 150, 140
    lines = text_set(text)
    line_height = font.getsize("hg")[1]
    for line in lines:
        draw.text((x, y), line, fill=(1, 22, 55), font=font)
        y = y + line_height - 5
    file = "toni.jpg"
    img.save(file)
    await event.reply(file=file)
    os.remove(file)
    await k.delete()

__mod_name__ = "Nulis"
def helps(chat):
    return gs(chat, "nulis_help")
