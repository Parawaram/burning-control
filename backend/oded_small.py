import board, busio, time
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

i2c  = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(64, 48, i2c, addr=0x3C)

# создаём «холст»
image = Image.new("1", (oled.width, oled.height))
draw  = ImageDraw.Draw(image)
font  = ImageFont.load_default()

# рисуем текст
draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
draw.text((0, 0), "GTA is GAY", font=font, fill=255)

oled.image(image)
oled.show()
