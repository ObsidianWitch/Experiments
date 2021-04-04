#!/usr/bin/env python3

# Chernobyl Fairy Pool Extractor
# Extract sprites from <https://ocias.com/works/chernobyl-fairy-pool/>.

import base64
from pathlib import Path
from selenium import webdriver # https://selenium-python.readthedocs.io

BUILDPATH = Path('build')
BUILDPATH.mkdir(exist_ok=True)

def retrieve_atlas():
    # webpage
    driver = webdriver.Firefox(service_log_path=BUILDPATH / 'geckodriver.log')
    driver.get('https://ocias.com/works/chernobyl-fairy-pool/')

    # atlas image
    atlas_b64 = driver.execute_script('return atlasImage.src') \
                      .removeprefix('data:image/png;base64,')
    atlas_png = base64.b64decode(atlas_b64, validate=True)
    with (BUILDPATH / 'atlas.png').open(mode='wb') as f:
        f.write(atlas_png)

    driver.quit()

retrieve_atlas()
