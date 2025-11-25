import io
import time
import uuid
from typing import Optional, List
import requests
from PIL import Image
import base64
RESAMPLE_FILTER = Image.Resampling.LANCZOS
class ReCaptchaHandler:

    path_map_44 = {
        0: "//table/tbody/tr[1]/td[1]",
        1: "//table/tbody/tr[1]/td[2]",
        2: "//table/tbody/tr[1]/td[3]",
        3: "//table/tbody/tr[1]/td[4]",
        4: "//table/tbody/tr[2]/td[1]",
        5: "//table/tbody/tr[2]/td[2]",
        6: "//table/tbody/tr[2]/td[3]",
        7: "//table/tbody/tr[2]/td[4]",
        8: "//table/tbody/tr[3]/td[1]",
        9: "//table/tbody/tr[3]/td[2]",
        10: "//table/tbody/tr[3]/td[3]",
        11: "//table/tbody/tr[3]/td[4]",
        12: "//table/tbody/tr[4]/td[1]",
        13: "//table/tbody/tr[4]/td[2]",
        14: "//table/tbody/tr[4]/td[3]",
        15: "//table/tbody/tr[4]/td[4]",
    }

    path_map_33 = {
        0: "//table/tbody/tr[1]/td[1]",
        1: "//table/tbody/tr[1]/td[2]",
        2: "//table/tbody/tr[1]/td[3]",
        3: "//table/tbody/tr[2]/td[1]",
        4: "//table/tbody/tr[2]/td[2]",
        5: "//table/tbody/tr[2]/td[3]",
        6: "//table/tbody/tr[3]/td[1]",
        7: "//table/tbody/tr[3]/td[2]",
        8: "//table/tbody/tr[3]/td[3]",
    }

    api_host="http://127.0.0.1:8000/analyze_batch/"
    def __init__(self, driver):
        self.driver = driver
        self.checkbox_iframe = None
        self.challenge_iframe = None
        self.challenge_type = None
        self.challenge_question = None
        self.challenge_i33_first = True
        self.i11s = {}
        self.challenge_44_img = None

    @staticmethod
    def split_image(image_bytes: bytes) -> Optional[List[str]]:
        try:
            image_stream = io.BytesIO(image_bytes)
            img = Image.open(image_stream)
        except:
            return None

        width, height = img.size
        tile_width = width // 3
        tile_height = height // 3

        base64_tiles = []
        for i in range(3):
            for j in range(3):
                left = j * tile_width
                upper = i * tile_height
                right = (j + 1) * tile_width if j < 2 else width
                lower = (i + 1) * tile_height if i < 2 else height

                tile = img.crop((left, upper, right, lower))
                buf = io.BytesIO()
                tile.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                base64_tiles.append(b64)

        return base64_tiles

    def find_checkbox_iframe(self):
        time.sleep(1)
        try:
            iframe = self.driver.ele('css: iframe[title="reCAPTCHA"]')
            if iframe:
                self.checkbox_iframe = iframe
                self.checkbox_iframe.ele("#recaptcha-anchor").click()
                return True
        except:
            pass
        return False

    def find_challenge_iframe(self):
        try:
            iframe = self.driver.ele("@|title=recaptcha challenge expires in two minutes@|title=reCAPTCHA 验证任务将于 2 分钟后过期")
            if iframe:
                self.challenge_iframe = iframe
                return True
        except:
            pass
        return False

    def check_11_refresh(self, check_ele):
        for k, v in self.i11s.items():
            if v.get("new"):
                self.i11s[k]['new'] = False

        check_ele = [i[0] for i in check_ele]

        for idx in check_ele:
            if idx not in self.i11s:
                self.i11s[idx] = {'srcs': [], 'new': False}

            while True:
                ele = self.challenge_iframe.ele('#rc-imageselect-target').ele(
                    f"xpath:{self.path_map_33[idx]}")

                img_ele = ele.ele('.rc-image-tile-11', timeout=0.1)
                if not img_ele:
                    time.sleep(0.1)
                    continue

                byte_data = img_ele.src()
                b64_str = base64.b64encode(byte_data).decode()

                if b64_str not in self.i11s[idx]['srcs']:
                    self.i11s[idx]['srcs'].append(b64_str)
                    self.i11s[idx]['new'] = True
                    break

    def click_answer(self, result, challenge_type):
        if challenge_type == 4:
            for x in result["results"][0]['result']:
                self.challenge_iframe.ele('#rc-imageselect-target').ele(
                    f"xpath:{self.path_map_44[x]}").click()
                time.sleep(0.1)

            # if not result["results"][0]['result']:
            #     try:
            #         image_bytes = base64.b64decode(self.challenge_44_img)
            #         name = str(uuid.uuid4())
            #         with open(rf"{name}.png",'wb') as f:
            #             f.write(image_bytes)
            #     except:
            #         pass

            self.challenge_iframe.ele('#recaptcha-verify-button').click()
            self.i11s.clear()
            return True

        if challenge_type == 3:
            found_ele = []

            for res in result["results"]:
                if res["result"].get('target_found'):
                    idx = int(res["image_id"])
                    self.challenge_iframe.ele('#rc-imageselect-target').ele(
                        f"xpath:{self.path_map_33[idx]}").click()
                    found_ele.append((idx, self.path_map_33[idx]))
                    time.sleep(0.1)

            if found_ele:
                if len(found_ele) <= 2 and self.challenge_i33_first:
                    self.challenge_iframe.ele('#recaptcha-reload-button').click()
                    return False

                cls = self.challenge_iframe.ele('#rc-imageselect-target').ele(
                    f"xpath:{found_ele[0][1]}").attr('class')
                if 'rc-imageselect-tileselected' in cls:
                    self.challenge_iframe.ele('#recaptcha-verify-button').click()
                    self.i11s.clear()
                    return True

                self.check_11_refresh(found_ele)
                return False

            self.challenge_iframe.ele('#recaptcha-verify-button').click()
            self.i11s.clear()
            return True

        return False

    def challenge_i33(self):
        if len(self.challenge_iframe.eles('.rc-image-tile-33', timeout=1)) == 9:
            self.challenge_i33_first = True
            self.i11s.clear()

            first_ele = self.challenge_iframe.eles('.rc-image-tile-33')[0]
            byte_data = first_ele.src()

            tiles = self.split_image(byte_data)
            if tiles:
                images = {i: t for i, t in enumerate(tiles)}
                if res := self.identify_verification_code(images):
                    self.click_answer(res, 3)
        else:
            self.challenge_i33_first = False
            data = {}

            for k, v in self.i11s.items():
                if v['new']:
                    img_b64 = v['srcs'][-1]
                    data[k] = img_b64
            if res := self.identify_verification_code(data):
                self.click_answer(res, 3)

    def challenge_i44(self):
        ele = self.challenge_iframe.eles('.rc-image-tile-44')[0]
        byte_data = ele.src()
        b64_str = base64.b64encode(byte_data).decode()
        self.challenge_44_img = b64_str
        if res := self.identify_verification_code({0: b64_str}):
            self.click_answer(res, 4)
    def identify_verification_code(self, images):
        data = {"images": []}
        for k, img in images.items():
            if img:
                data["images"].append({
                    "image_id": str(k),
                    "image_base64": img,
                    "target_class": self.challenge_question
                })
        if data['images']:
            res = requests.post(self.api_host, json=data)
            return res.json()
        return None

    def challenge(self):
        if not self.find_checkbox_iframe():
            return {"status": False, "message": "no verification code found"}
        url_before = self.driver.url
        self.find_challenge_iframe()
        if not self.challenge_iframe:
            return {"status": False, "message": "no verification code found"}
        while True:
            time.sleep(1)
            try:
                if self.driver.url != url_before:
                    return {"status": True, "message": "验证码自动通过1"}
                if self.checkbox_iframe.ele("#recaptcha-anchor").attr('aria-checked') == 'true':
                    return {"status": True, "message": "验证码自动通过2"}
                if self.challenge_iframe.style('visibility') != 'hidden':
                    break
            except:
                pass
        try:
            while self.challenge_iframe.style('visibility') != 'hidden':
                time.sleep(1)
                if self.driver.url != url_before:
                    return {"status": True, "message": "captcha successfully resolved1"}
                if self.checkbox_iframe.ele("#recaptcha-anchor").attr('aria-checked') == 'true':
                    return {"status": True, "message": "captcha successfully resolved2"}
                # 获取题目
                self.challenge_question = self.challenge_iframe.ele("tag:strong").text

                # 判断 4×4
                if self.challenge_iframe.ele('.rc-image-tile-44', timeout=0.1):
                    self.challenge_i44()

                # 判断 3×3 或 1×1
                elif self.challenge_iframe.ele('.rc-image-tile-33', timeout=0.1) or \
                        self.challenge_iframe.ele('.rc-image-tile-11', timeout=0.1):
                    self.challenge_i33()
        except:
            pass
        return {"status": True, "message": "captcha successfully resolved3"}
