import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool

# Complete these 2 fields ==================
USERNAME = 'XXX'
PASSWORD = 'XXX'
# ==========================================
TIMEOUT = 15
FOLLOWINGS = 0
FOLLOWERS = 1
RETRY_LIMIT = 10

def automate_login(bot):
    bot.get('https://www.instagram.com/accounts/login/')

    time.sleep(1)
    
    if bot.current_url == "https://www.instagram.com/":
        print("[Info] - Already logged in...")  
        return

    # accept cookie policy
    bot.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    try:
        bot.find_element(By.XPATH,"/html/body/div[4]/div/div/div[3]/div[2]/button").click()
    except:
        # doesn't always show up, or may have been previously accepted/declined
        print("accept cookies policy button not found...")
        
    print("[Info] - Logging in...")  
    
    # target Username
    username = WebDriverWait(
        bot, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[name='username']")))

    # target Password
    password = WebDriverWait(
        bot, 10).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[name='password']")))

    # enter username and password
    username.clear()
    username.send_keys(USERNAME)
    password.clear()
    password.send_keys(PASSWORD)

    # target the login button and click it
    button = WebDriverWait(
        bot, 2).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[type='submit']"))).click()

    print("[Info] - Login Complete...")
    
    time.sleep(5)

def scrape_follow(bot, usr, scrape):
    if scrape == FOLLOWINGS:
        scrape = "following"
    else:
        scrape = "followers"
    
    bot.get('https://www.instagram.com/{}/'.format(usr))

    time.sleep(2)
    
    element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, f"//a[contains(@href, '/{scrape}')]")))
    
    # get total followings/followers
    total_users = int(((element.text).split(' ')[0]).replace(',', '')) # cover comma separated numbers
    element.click()

    time.sleep(2)

    print(f'[Info] - Scraping {total_users} {scrape}...')

    users = set()
    
    for _ in range(RETRY_LIMIT): # retry to find all users
        for _ in range(round(total_users // 15)):
            ActionChains(bot).send_keys(Keys.END).perform()
            time.sleep(1)
            
            
        user_elements = bot.find_elements(By.XPATH,
        "//div[@class='x9f619 xjbqb8w x1rg5ohu x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x6s0dn4 x1oa3qoh x1nhvcw1']")
        
        # get ig username
        for e in user_elements:
            users.add(e.text)
            
        if len(users) == total_users:
            break    
            
        bot.get('https://www.instagram.com/{}/'.format(usr))
        time.sleep(2)
        element = WebDriverWait(bot, TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH, f"//a[contains(@href, '/{scrape}')]")))       
        element.click()
        
     
    print(f'[Info] - Saving {scrape}...')

    with open(f'{scrape}.txt', 'w') as file:
        file.write('\n'.join(users) + "\n")

    print(f'[DONE] - Your {scrape} are saved in {scrape}.txt file!')
    
    return users

def process_differences(followings, followers):
    print('[Info] Processing differences...')
    d1 = followings.difference(followers) # people you follow that doesn't follow you back
    d2 = followers.difference(followings) # people you don't follow that follows you
    
    with open('FollowingNotInFollowers.txt', 'w') as file:
        file.write('\n'.join(d1) + "\n")   

    with open('FollowersNotInFollowing.txt', 'w') as file:
        file.write('\n'.join(d2) + "\n") 
    
    print('[Done] Saved differences to FollowingNotInFollowers.txt and FollowersNotInFollowing.txt files') 
    

def create_bot_and_scrape(usr, scrape):
    # assemble chrome options and parameters
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    
    automate_login(bot)
    
    return scrape_follow(bot, usr, scrape)    


def scrape():

    usr = input('[Required] - Enter username of account to scrape: ')
    
    p = Pool(2)
    res1 = p.apply_async(func=create_bot_and_scrape, args=(usr, FOLLOWERS))
    time.sleep(5) # avoid logging in simulataneously
    res2 = p.apply_async(func=create_bot_and_scrape, args=(usr, FOLLOWINGS))
    
    followers_set = res1.get()
    followings_set = res2.get()
    p.close()
    p.join()
    
    process_differences(followings_set, followers_set)
    
    print('[Done] Scraping all done!!!')

if __name__ == '__main__':
    scrape()