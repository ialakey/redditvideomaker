from selenium import webdriver
from selenium.webdriver.common.by import By

post_url = 'https://www.reddit.com/r/AskReddit/comments/1b0b6d7/what_is_the_saddest_fact_you_know_that_most/'

chrome_options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=chrome_options)

driver.get(post_url)

driver.implicitly_wait(5)

post_element = driver.find_element(By.XPATH, '//shreddit-post')

post_element.screenshot('reddit_post_screenshot.png')

# Find all shreddit-comment elements with an 'author' attribute
comment_elements = driver.find_elements(By.XPATH, '//shreddit-comment[@author]')

# Iterate through the shreddit-comment elements and take screenshots
for i, comment_element in enumerate(comment_elements, start=1):
    author_name = comment_element.get_attribute("author")
    comment_element.screenshot(f'reddit_comment_author_{author_name}_screenshot_{i}.png')

driver.quit()
