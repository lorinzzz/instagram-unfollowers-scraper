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
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--mp', type=bool, default=False, help='enable multiprocessing')
args = parser.parse_args()

# Complete these 2 fields ==================
USERNAME = 'XXX'
PASSWORD = 'XXX'
# ==========================================
TIMEOUT = 15
FOLLOWINGS = 0
FOLLOWERS = 1
SERIAL_PROCESS = 0 if args.mp else 2

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
    serial = True if scrape == SERIAL_PROCESS else False
    
    if scrape == FOLLOWINGS:
        scrape = "following"
    else:
        scrape = "followers"
    
    bot.get('https://www.instagram.com/{}/'.format(usr))

    time.sleep(2)
    
    element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, f'//a[contains(@href, "/{scrape}")]')))
    
    # get total followings/followers
    total_users = int(((element.text).split(' ')[0]).replace(',', '')) # cover comma separated numbers
    element.click()

    time.sleep(7.5)

    print(f'[Info] - Scraping {total_users} {scrape}...')

    users = set()
    
    while True: # refresh and scrape until found all users
        for _ in range(round(total_users // 12)):
            ActionChains(bot).send_keys(Keys.END).perform()
            time.sleep(1)
            
            
        user_elements = bot.find_elements(By.XPATH,
        "//div[@class='x9f619 xjbqb8w x1rg5ohu x168nmei x13lgxp2 x5pf9jr xo71vjh x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x6s0dn4 x1oa3qoh x1nhvcw1']")
        
        # get ig usernames
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
        time.sleep(7.5)
    
    if serial:
        followers = users
        followings = scrape_follow(bot, usr, FOLLOWINGS)
        return followers, followings
    else:
        return users

def process_differences(usr, followings, followers):
    print('[Info] Processing differences...')

    FollowingsFile = f"{usr}_Followings.txt" # all user's followings
    NewFollowingsFile = f"{usr}_NewFollowings.txt" # all new followings since old
    NewUnfollowingsFile = f"{usr}_NewUnfollowings.txt" # all people don't follow anymore since old
    FollowersFile = f"{usr}_Followers.txt" # all user's followers
    NewFollowersFile = f"{usr}_NewFollowers.txt" # all new followers since old 
    NewUnfollowersFile = f"{usr}_NewUnfollowers.txt" # all people that have unfollowed you since old
    FollowingNotInFollowersFile = f"{usr}_FollowingNotInFollowers.txt" # people you follow that doesn't follow you back
    FollowersNotInFollowingFile = f"{usr}_FollowersNotInFollowing.txt" # people that follow you that you don't follow back
    
    # compare new set with old set if exists
    # then write the new set to file
    try:
        with open(FollowingsFile, 'r') as file:
            old_followings = set(line.strip() for line in file)
            new_followings = followings.difference(old_followings)
            new_unfollowings = old_followings.difference(followings)
            with open(NewFollowingsFile, 'w') as file:
                file.write('\n'.join(new_followings) + "\n")
                print(f'[Done] - Your New Followings are saved in {NewFollowingsFile} file!')
            with open(NewUnfollowingsFile, 'w') as file:
                file.write('\n'.join(new_unfollowings) + "\n")
                print(f'[Done] - Your New Unfollowings are saved in {NewUnfollowingsFile} file!') 
    except:
        print("[Info] - No existing Followings file...")
    with open(FollowingsFile, 'w') as file:
        file.write('\n'.join(followings) + "\n")
        print(f'[Done] - Your Followings are saved in {FollowingsFile} file!')        
    
    try:
        with open(FollowersFile, 'r') as file:
            old_followers = set(line.strip() for line in file)
        new_followers = followers.difference(old_followers)
        new_unfollowers = old_followers.difference(followers)
        with open(NewFollowersFile, 'w') as file:
            file.write('\n'.join(new_followers) + "\n")
            print(f'[Done] - Your New Followers are saved in {NewFollowersFile} file!')
        with open(NewUnfollowersFile, 'w') as file:
            file.write('\n'.join(new_unfollowers) + "\n")
            print(f'[Done] - Your New Unfollowers are saved in {NewUnfollowersFile} file!') 
    except:
        print("[Info] - No existing Followers file...")
    with open(FollowersFile, 'w') as file:
        file.write('\n'.join(followers) + "\n")
        print(f'[Done] - Your Followers are saved in {FollowersFile} file!')
        
    d1 = followings.difference(followers)
    d2 = followers.difference(followings)
    
    with open(FollowingNotInFollowersFile, 'w') as file:
        file.write('\n'.join(d1) + "\n")

    with open(FollowersNotInFollowingFile, 'w') as file:
        file.write('\n'.join(d2) + "\n")  
    
    print(f'[Done] Saved differences to {FollowingNotInFollowersFile}, {FollowersNotInFollowingFile}') 
    

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
    
    if args.mp:
        p = Pool(2)
        res1 = p.apply_async(func=create_bot_and_scrape, args=(usr, FOLLOWERS))
        time.sleep(5) # avoid logging in simulataneously
        res2 = p.apply_async(func=create_bot_and_scrape, args=(usr, FOLLOWINGS))
        
        followers_set = res1.get()
        followings_set = res2.get()
        p.close()
        p.join()
    else:
        followers_set, followings_set = create_bot_and_scrape(usr, SERIAL_PROCESS)
    
    process_differences(usr, followings_set, followers_set)
    
    print('[Done] Scraping all done!!!')

if __name__ == '__main__':
    scrape()