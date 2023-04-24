# instagram-unfollowers-scraper
This python script automatically scrapes an Instagram users' followers and followings and save them to a text file. It will also
generate a list users that do not follow back as well as users the specific account does not follow back.

The script uses Selenium with the driver as Chrome, and utilizes multiprocessing to scrape in parallel.

# How to use:
1. Install requirements using terminal or command line. You should run this command ```pip install -r requirements.txt```.
2. Open the run.py and enter your IG username/password
2. Open a terminal or cmd again and run the bot using this command: ```python run.py```.
4. Enter the username of the person whose account you want to scrape.
6. After a while, you will find 4 text files containing the results in the folder.
