import os
import time
import random
import string
import requests
import base64
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from colorama import Fore, init

init(autoreset=True)

# =================== CONFIGURATION ===================
# PASTE YOUR KEY HERE FOR LOCAL USE
CAPTCHA_KEY = "PASTE_YOUR_2CAPTCHA_KEY_HERE" 

# Target Settings
SERVER_INVITE = "https://discord.gg/lovers-arenaa"
TARGET_CHANNEL_ID = "1364803168403193877"
# =====================================================

class DiscordHumanizer:
    def __init__(self):
        for folder in ["./avatars", "./output"]:
            if not os.path.exists(folder): os.makedirs(folder)

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--window-size={random.randint(1280, 1500)},{random.randint(720, 900)}")
        
        self.driver = uc.Chrome(options=options)
        self.solver = TwoCaptcha(CAPTCHA_KEY)
        self.wait = WebDriverWait(self.driver, 25)
        self.token = None

    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))

    def register(self):
        user = "User_" + "".join(random.choices(string.ascii_lowercase, k=4)) + str(random.randint(10, 99))
        email = f"{user}@outlook.com"
        pwd = "Pass" + "".join(random.choices(string.digits, k=6)) + "!"

        print(f"{Fore.CYAN}[*] Navigating to Discord...")
        self.driver.get("https://discord.com/register")
        
        try:
            email_input = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.human_type(email_input, email)
            self.human_type(self.driver.find_element(By.NAME, "username"), user)
            self.human_type(self.driver.find_element(By.NAME, "password"), pwd)

            # Date Selection
            date_selectors = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1hwfws3")))
            dates = [random.randint(1,12), random.randint(1,28), random.randint(1990,2004)]
            for i in range(3):
                ActionChains(self.driver).move_to_element(date_selectors[i]).click().perform()
                time.sleep(0.5)
                self.driver.switch_to.active_element.send_keys(str(dates[i]), Keys.ENTER)
                time.sleep(0.4)
            
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            ActionChains(self.driver).move_to_element(submit_btn).click().perform()
            
            print(f"{Fore.MAGENTA}[*] Solving Captcha...")
            time.sleep(8) 
            sitekey = self.driver.find_element(By.CLASS_NAME, "h-captcha").get_attribute("data-sitekey")
            result = self.solver.hcaptcha(sitekey=sitekey, url=self.driver.current_url)
            self.driver.execute_script(f"document.getElementsByName('h-captcha-response')[0].innerHTML='{result['code']}';")
            
            time.sleep(15)
            self.token = self.driver.execute_script("return (window.localStorage.getItem('token') || '').replace(/\"/g, '');")
            return True if self.token else False

        except Exception as e:
            print(f"{Fore.RED}[!] Registration error: {e}")
            return False

    def customize_profile(self):
        """Sets a unique bio and random avatar image"""
        if not self.token: return
        print(f"{Fore.YELLOW}[*] Customizing Profile (Bio & Avatar)...")
        
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        
        bios = [
            "Just here for the vibes.", "Gaming is life.", "Lovers Arena member.", 
            "Searching for new friends.", "Digital nomad.", "Into music and art."
        ]
        
        payload = {"bio": random.choice(bios)}
        
        # Check for images in avatars folder
        images = [f for f in os.listdir("./avatars") if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            with open(f"./avatars/{random.choice(images)}", "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                payload["avatar"] = f"data:image/png;base64,{encoded_string}"
        
        requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)

    def auto_vote(self):
        if not self.token: return
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        invite_code = SERVER_INVITE.split("/")[-1]
        
        print(f"{Fore.BLUE}[*] Joining Server...")
        requests.post(f"https://discord.com/api/v9/invites/{invite_code}", headers=headers)
        time.sleep(4)
        
        print(f"{Fore.YELLOW}[*] Reacting in Target Channel...")
        msg_req = requests.get(f"https://discord.com/api/v9/channels/{TARGET_CHANNEL_ID}/messages?limit=1", headers=headers)
        
        if msg_req.status_code == 200 and msg_req.json():
            msg_id = msg_req.json()[0]['id']
            emoji = requests.utils.quote("✅")
            url = f"https://discord.com/api/v9/channels/{TARGET_CHANNEL_ID}/messages/{msg_id}/reactions/{emoji}/%40me"
            res = requests.put(url, headers=headers)
            if res.status_code == 204:
                print(f"{Fore.GREEN}[SUCCESS] Voted successfully!")
        else:
            print(f"{Fore.RED}[!] Could not find message to react to.")

    def finish(self):
        if self.token:
            with open("./output/tokens.txt", "a") as f:
                f.write(f"{self.token}\n")
        self.driver.quit()

if __name__ == "__main__":
    bot = DiscordHumanizer()
    if bot.register():
        bot.customize_profile() # Set Bio and Avatar
        bot.auto_vote()        # Join and React
    bot.finish()
