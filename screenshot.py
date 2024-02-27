from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import configparser

# Config
config = configparser.ConfigParser()
config.read('config.ini')
outputDir = config["General"]["TemplateDirectory"]
global_driver = None
global_wait = None

def getPostScreenshots(filePrefix, script):
    print("Taking screenshots...")
    __setupDriver(script.url)
    script.titleSCFile = __takeScreenshot(filePrefix, global_driver, global_wait, '//shreddit-post')
    for i, commentFrame in enumerate(script.frames, start=1):
        xpath = f'//shreddit-comment[@thingid="t1_{commentFrame.commentId}"]'
        commentFrame.screenShotFile = __takeScreenshot(filePrefix, global_driver, global_wait, xpath)
    global_driver.quit()

def __takeScreenshot(filePrefix, driver, wait, xpath):
    try:
        # Вывод информации о поиске
        print(f"Searching for element with XPath: {xpath}")
        search = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except Exception as e:
        print(f"Exception while waiting for element: {e}")
        return None

    driver.execute_script("window.focus();")

    # Replacing invalid characters in the XPath to create a valid filename
    sanitized_xpath = xpath.replace('/', '_').replace('@', '').replace('=', '_').replace('[', '').replace(']', '').replace('"', '')

    fileName = f"{outputDir}/{filePrefix}-{sanitized_xpath}.png"
    
    # Вывод значений переменных
    print(f"Sanitized XPath: {sanitized_xpath}")
    print(f"FileName: {fileName}")

    try:
        fp = open(fileName, "wb")
        fp.write(search.screenshot_as_png)
        fp.close()
    except Exception as e:
        print(f"Exception while taking screenshot: {e}")
        return None
    
    return fileName

def __setupDriver(url: str):
    global global_driver, global_wait

    if global_driver is None:
        options = webdriver.ChromeOptions()
        options.headless = False  
        options.disable_extensions = False

        # Включение режима разработчика
        # options.add_argument("--auto-open-devtools-for-tabs")

        global_driver = webdriver.Chrome(options=options)
        global_wait = WebDriverWait(global_driver, 5)

        global_driver.maximize_window()

    global_driver.get(url)

    return global_driver, global_wait
