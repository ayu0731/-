from PIL import Image
import easyocr
from selenium import webdriver
from selenium.webdriver.common.by import By

from maker import wd

print("EasyOCR起動")

img = Image.open('photos/hdd.png')

img = img.resize(
    (img.width * 2, img.height * 2)
)

img.save('photos/hdd_big.png')

reader = easyocr.Reader(['en'])

result = reader.readtext(
    'photos/hdd_big.png',
    detail=1
)

print("===== OCR結果 =====")

for box, txt, conf in result:
    print(f"{txt} ({conf:.2f})")

text = " ".join([r[1] for r in result]).upper()

print("結合後:")
print(text)

if "WD BLUE" in text or "WESTERN DIGITAL" in text:
    data = wd.run(text)
else:
    print("メーカー不明")

driver = webdriver.Chrome()

driver.get("https://demoqa.com/text-box")

driver.find_element(
    By.ID,
    "userName"
).send_keys(data["model"])

driver.find_element(
    By.ID,
    "userEmail"
).send_keys(data["model1"])

driver.find_element(
    By.ID,
    "currentAddress"
).send_keys(data["serial"])

driver.find_element(
    By.ID,
    "permanentAddress"
).send_keys(data["dcm"])



input("Enterを押したら終了")
driver.quit()
