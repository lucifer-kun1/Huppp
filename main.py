import os
import subprocess
import sys

# --- STEP 1: AUTOMATIC ENVIRONMENT SETUP ---
def install_requirements():
    requirements = ['undetected-chromedriver', '2captcha-python', 'requests', 'colorama', 'selenium']
    for lib in requirements:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            print(f"[*] Missing {lib}. Installing now for 2026 environment...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_requirements()

import undetected_chromedriver as uc
import time, random, string, requests, base64
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from twocaptcha import TwoCaptcha
from colorama import Fore, init

init(autoreset=True)

# =================== CONFIGURATION ===================
CAPTCHA_KEY = "YOUR_2CAPTCHA_KEY_HERE"  # <-- PUT YOUR KEY HERE
SERVER_INVITE = "https://discord.gg/yourlink" # <-- YOUR INVITE LINK
# =====================================================

class DiscordAllInOne:
    def __init__(self):
        # Setup Folders Automatically
        if not os.path.exists("./avatars"):
            os.makedirs("./avatars")
        if not os.path.exists("./output"):
            os.makedirs("./output")

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--window-size={random.randint(1280, 1500)},{random.randint(720, 900)}")
        
        self.driver = uc.Chrome(options=options)
        self.solver = TwoCaptcha(CAPTCHA_KEY)
        self.token = None

    def human_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.06, 0.18))

    def human_click(self, element):
        action = ActionChains(self.driver)
        action.move_to_element(element).pause(random.uniform(0.3, 0.6)).click().perform()

    def register(self):
        user = "User" + "".join(random.choices(string.ascii_lowercase, k=5)) + str(random.randint(100, 999))
        email = f"{user}@outlook.com"
        pwd = "Pass" + "".join(random.choices(string.digits, k=7)) + "!"

        print(f"{Fore.CYAN}[*] Registering User: {user}")
        self.driver.get("https://discord.com/register")
        time.sleep(random.uniform(2, 4))
        
        try:
            self.human_type(self.driver.find_element(By.NAME, "email"), email)
            self.human_type(self.driver.find_element(By.NAME, "username"), user)
            self.human_type(self.driver.find_element(By.NAME, "password"), pwd)

            # Date Selection
            inputs = self.driver.find_elements(By.CLASS_NAME, "css-1hwfws3")
            for i, val in enumerate([random.randint(1,12), random.randint(1,28), random.randint(1990,2005)]):
                self.human_click(inputs[i])
                time.sleep(0.5)
                self.driver.switch_to.active_element.send_keys(str(val), Keys.ENTER)
                time.sleep(0.3)

            self.human_click(self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
            
            # Captcha Solving
            print(f"{Fore.YELLOW}[*] Solve Captcha triggered. Please wait...")
            time.sleep(7)
            sitekey = self.driver.find_element(By.CLASS_NAME, "h-captcha").get_attribute("data-sitekey")
            result = self.solver.hcaptcha(sitekey=sitekey, url=self.driver.current_url)
            self.driver.execute_script(f"document.getElementsByName('h-captcha-response')[0].innerHTML='{result['code']}';")
            
            # Extract Token
            time.sleep(15)
            self.token = self.driver.execute_script("return (window.localStorage.getItem('token') || '').replace(/\"/g, '');")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Error: {e}")
            return False

    def setup_profile_and_vote(self):
        if not self.token: return
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        
        # 1. Update Profile (Humanize)
        print(f"{Fore.MAGENTA}[*] Customizing Profile...")
        payload = {"bio": "Automated humanized profile."}
        
        pics = [f for f in os.listdir("./avatars") if f.endswith(('.png', '.jpg', '.jpeg'))]
        if pics:
            with open(f"./avatars/{random.choice(pics)}", "rb") as img:
                b64 = base64.b64encode(img.read()).decode('utf-8')
                payload["avatar"] = f"data:image/png;base64,{b64}"

        requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)

        # 2. Join and Vote
        print(f"{Fore.YELLOW}[*] Joining Server and Voting...")
        invite_code = SERVER_INVITE.split("/")[-1]
        join = requests.post(f"https://discord.com/api/v9/invites/{invite_code}", headers=headers)
        
        if join.status_code == 200:
            chan_id = join.json().get("channel", {}).get("id")
            time.sleep(4)
            msg = requests.get(f"https://discord.com/api/v9/channels/{chan_id}/messages?limit=1", headers=headers)
            if msg.json():
                mid = msg.json()[0]['id']
                # React with ✅
                requests.put(f"https://discord.com/api/v9/channels/{chan_id}/messages/{mid}/reactions/%E2%9C%85/%40me", headers=headers)
                print(f"{Fore.GREEN}[SUCCESS] Voted and Token Saved!")

if __name__ == "__main__":
    bot = DiscordAllInOne()
    if bot.register():
        bot.setup_profile_and_vote()
        with open("./output/tokens.txt", "a") as f:
            f.write(f"{bot.token}\n")
    bot.driver.quit()
