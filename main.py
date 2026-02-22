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
CAPTCHA_KEY = "PASTE_YOUR_2CAPTCHA_KEY_HERE" 
SERVER_INVITE = "https://discord.gg/lovers-arenaa"
TARGET_CHANNEL_ID = "1364803168403193877"
# =====================================================

class DiscordHumanizer:
    def __init__(self):
        for folder in ["./avatars", "./output"]:
            if not os.path.exists(folder): os.makedirs(folder)

        options = uc.ChromeOptions()
        # Enhanced Stealth Arguments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        print(f"{Fore.YELLOW}[*] Starting Undetected Chrome...")
        self.driver = uc.Chrome(options=options)
        self.solver = TwoCaptcha(CAPTCHA_KEY)
        self.wait = WebDriverWait(self.driver, 30) # Increased timeout
        self.token = None

    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.07, 0.15))

    def register(self):
        user = "User_" + "".join(random.choices(string.ascii_lowercase, k=4)) + str(random.randint(10, 99))
        email = f"{user}@outlook.com"
        pwd = "Pass" + "".join(random.choices(string.digits, k=6)) + "!"

        print(f"{Fore.CYAN}[*] Navigating to Discord...")
        self.driver.get("https://discord.com/register")
        
        try:
            # Check if we are stuck on a "Verify you are human" checkbox
            print(f"{Fore.WHITE}[*] Waiting for registration form to load...")
            
            # Explicitly wait for the email field
            email_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "email")))
            
            print(f"{Fore.GREEN}[+] Page loaded! Entering details...")
            self.human_type(email_input, email)
            self.human_type(self.driver.find_element(By.NAME, "username"), user)
            self.human_type(self.driver.find_element(By.NAME, "password"), pwd)

            # Date Selection
            date_selectors = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1hwfws3")))
            dates = [random.randint(1,12), random.randint(1,28), random.randint(1990,2004)]
            for i in range(3):
                ActionChains(self.driver).move_to_element(date_selectors[i]).click().perform()
                time.sleep(0.6)
                self.driver.switch_to.active_element.send_keys(str(dates[i]), Keys.ENTER)
                time.sleep(0.5)
            
            # Submit
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
            time.sleep(1)
            submit_btn.click()
            
            print(f"{Fore.MAGENTA}[*] Form submitted. Solving Captcha (this can take 2 minutes)...")
            time.sleep(10) # Let captcha load
            
            # Captcha Solve
            captcha_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "h-captcha")))
            sitekey = captcha_element.get_attribute("data-sitekey")
            result = self.solver.hcaptcha(sitekey=sitekey, url=self.driver.current_url)
            self.driver.execute_script(f"document.getElementsByName('h-captcha-response')[0].innerHTML='{result['code']}';")
            
            print(f"{Fore.GREEN}[+] Captcha bypass sent. Finalizing...")
            time.sleep(15)
            self.token = self.driver.execute_script("return (window.localStorage.getItem('token') || '').replace(/\"/g, '');")
            return True if self.token else False

        except Exception as e:
            print(f"{Fore.RED}[!] Error: {str(e)[:100]}") # Only show first 100 chars of error
            return False

    def customize_profile(self):
        if not self.token: return
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        bios = ["Just a human.", "Gaming vibes.", "New here!", "Lovers Arena member."]
        payload = {"bio": random.choice(bios)}
        
        images = [f for f in os.listdir("./avatars") if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            with open(f"./avatars/{random.choice(images)}", "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                payload["avatar"] = f"data:image/png;base64,{encoded}"
        
        requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)

    def auto_vote(self):
        if not self.token: return
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        invite_code = SERVER_INVITE.split("/")[-1]
        
        # Join
        requests.post(f"https://discord.com/api/v9/invites/{invite_code}", headers=headers)
        time.sleep(5)
        
        # React
        msg_req = requests.get(f"https://discord.com/api/v9/channels/{TARGET_CHANNEL_ID}/messages?limit=1", headers=headers)
        if msg_req.status_code == 200 and msg_req.json():
            msg_id = msg_req.json()[0]['id']
            emoji = requests.utils.quote("✅")
            requests.put(f"https://discord.com/api/v9/channels/{TARGET_CHANNEL_ID}/messages/{msg_id}/reactions/{emoji}/%40me", headers=headers)
            print(f"{Fore.GREEN}[SUCCESS] Voted!")

    def finish(self):
        if self.token:
            with open("./output/tokens.txt", "a") as f:
                f.write(f"{self.token}\n")
        try:
            self.driver.close()
            self.driver.quit()
        except:
            pass

if __name__ == "__main__":
    bot = DiscordHumanizer()
    if bot.register():
        bot.customize_profile()
        bot.auto_vote()
    bot.finish()
