#!/usr/bin/env python3

import argparse, os, subprocess
from collections import deque

# doc: https://www.selenium.dev/documentation
# doc: https://www.selenium.dev/selenium/docs/api/py/
# doc: https://selenium-python.readthedocs.io
# dep: https://pypi.org/project/selenium/
# dep: https://archlinux.org/packages/community/x86_64/geckodriver/
import selenium, selenium.webdriver

def start_driver(headless):
    service = selenium.webdriver.firefox.service.Service(log_path='/dev/null')
    options = selenium.webdriver.firefox.options.Options()
    options.set_preference('browser.helperApps.alwaysAsk.force', False)
    options.set_preference('browser.download.alwaysOpenPanel', False)
    options.set_preference('browser.download.folderList', 2)
    options.set_preference('browser.download.dir', os.getcwd())
    options.headless = headless
    return selenium.webdriver.Firefox(service=service, options=options)

def css_select(driver, selector):
    return driver.find_elements('css selector', selector)

def download_sequence(driver, url, elem_selector, next_selector, rename, **args):
    driver.get(url)
    page_i = 0
    while True:
        driver.execute_script('''
        let promises = []
        document.querySelectorAll(arguments[1]).forEach((elem, elem_i) => {
            elem_i = elem_i.toString().padStart(3, '0')
            let name = arguments[2] ? `${arguments[0]}_${elem_i}_${document.title}`
                                    : ''
            switch (elem.tagName) {
                case 'IMG':
                    promises.push( fetch(elem.src)
                        .then(response => response.blob())
                        .then(blob => {
                            let a = document.createElement('a')
                            a.href = URL.createObjectURL(blob)
                            a.download = name
                            a.click()
                        }) )
                    break
                case 'A':
                    elem.download = name
                    elem.click()
                    break
                default:
                    throw new Error(`case ${elem.tagName} not implemented`)
            }
        })
        return Promise.all(promises)
        ''', str(page_i).zfill(3), elem_selector, rename)

        if next := css_select(driver, next_selector):
            page_i += 1
            next[0].click()
        else:
            break

def bridge_webtoons(driver, url, **args):
    # bypass age gate
    driver.get('https://www.webtoons.com/en/gdpr/ageGate')
    css_select(driver, 'input#_day')[0].send_keys('01')
    driver.execute_script("document.querySelector('a.lk_month').innerHTML = '02'")
    css_select(driver, 'span.year input')[0].send_keys('1953')
    css_select(driver, 'a._btn_enter')[0].click()

    # download
    download_sequence(driver, url=url, elem_selector='#_imageList img',
        next_selector='.paginate.v2 a.pg_next', rename=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--headless', action='store_true')
    subparsers = parser.add_subparsers(required=True)

    parser_sequence = subparsers.add_parser('tree')
    parser_sequence.add_argument('--rename', action='store_true')
    parser_sequence.add_argument('elem_selector')
    parser_sequence.add_argument('next_selector')
    parser_sequence.add_argument('url')
    parser_sequence.set_defaults(func=download_sequence)

    parser_sequence = subparsers.add_parser('bridge')
    parser_sequence.add_argument('name', choices=[ name for name in dir()
        if name.startswith('bridge_') ])
    parser_sequence.add_argument('url')
    parser_sequence.set_defaults(func=lambda **args: globals()[args['name']](**args))

    args = parser.parse_args()
    driver = start_driver(headless=args.headless)
    args.func(driver=driver, **vars(args))

    # wait for all downloads to finish
    subprocess.run('while inotifywait -- *.part; do :; done', shell=True)
    driver.quit()
