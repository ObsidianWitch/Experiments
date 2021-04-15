#!/usr/bin/env python3

import urllib.parse
import selenium, selenium.webdriver  # https://selenium-python.readthedocs.io

def bypass_age_gate(driver):
    driver.get('https://www.webtoons.com/en/gdpr/ageGate')
    driver.find_element_by_css_selector('input#_day').send_keys('01')
    driver.execute_script("document.querySelector('a.lk_month').innerHTML = '02'")
    driver.find_element_by_css_selector('span.year input').send_keys('1953')
    driver.find_element_by_css_selector('a._btn_enter').click()

def download_webcomic(driver):
    driver.get('https://www.webtoons.com/en/supernatural/muted/episode-1/viewer?title_no=1566&episode_no=1')
    while True:
        url = urllib.parse.urlparse(driver.current_url)
        queries = urllib.parse.parse_qs(url.query)
        episode_no = queries['episode_no'][0].zfill(3)

        driver.execute_script('''
            let epi = arguments[0]
            let promises = []
            document.querySelectorAll('#_imageList img').forEach((img, imgi) => {
                let p = fetch(img.src)
                    .then(response => response.blob())
                    .then(blob => {
                        let a = document.createElement('a')
                        a.href = URL.createObjectURL(blob)
                        imgi = imgi.toString().padStart(3, '0')
                        let path = new URL(img.src).pathname
                        path = path.substring(path.lastIndexOf('/') + 1)
                        a.download = `${epi}_${imgi}_${path}`
                        a.click()
                    })
                promises.push(p)
            })
            return Promise.all(promises)
        ''', episode_no)
        try:
            driver.find_element_by_css_selector('a.pg_next').click()
        except selenium.common.exceptions.ElementNotInteractableException:
            return

profile = selenium.webdriver.FirefoxProfile()
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'image/jpeg,image/png')
driver = selenium.webdriver.Firefox(firefox_profile=profile)
bypass_age_gate(driver)
download_webcomic(driver)
driver.quit()
