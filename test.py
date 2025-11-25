from DrissionPage import Chromium
from auto_challenge import ReCaptchaHandler
driver = Chromium(5345)
page = driver.get_tab()
page.get("https://www.google.com/recaptcha/api2/demo")
recaptcha_handler = ReCaptchaHandler(page)
print(recaptcha_handler.challenge())
