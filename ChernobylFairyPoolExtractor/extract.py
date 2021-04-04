#!/usr/bin/env python3

# Chernobyl Fairy Pool Extractor
# Extract sprites from <https://ocias.com/works/chernobyl-fairy-pool/>.

import base64, json
from pathlib import Path
from selenium import webdriver # https://selenium-python.readthedocs.io
from PIL import Image # https://pypi.org/project/Pillow/

BUILDPATH = Path('build')
BUILDPATH.mkdir(exist_ok=True)

def retrieve_atlas():
    driver = webdriver.Firefox(service_log_path=None)
    driver.get('https://ocias.com/works/chernobyl-fairy-pool/')

    # atlas image
    atlas_b64 = driver.execute_script('return atlasImage.src') \
                      .removeprefix('data:image/png;base64,')
    atlas_png = base64.b64decode(atlas_b64, validate=True)
    with (BUILDPATH / 'atlas.png').open(mode='wb') as f:
        f.write(atlas_png)

    # atlas.json
    atlas_data = driver.execute_script('return JSON.stringify(A.frames)')
    with (BUILDPATH / 'atlas.json').open(mode='w') as f:
        f.write(atlas_data)

    driver.quit()

def extract_sprites():
    atlas_img = Image.open(BUILDPATH / 'atlas.png').convert('RGBA')
    with open(BUILDPATH / 'atlas.json') as f:
        atlas_json = json.load(f)

    for i in range(1, 21):
        out_img = Image.new('RGBA', (400, 400))

        for part_str in ('Wings', 'Hair', 'Arm', 'Leg', 'Torso', 'Head'):
            part_key = f'FairyParts/{part_str}{str(i).zfill(2)}'
            if part_key not in atlas_json: continue
            part_json = atlas_json[part_key]
            out_img.alpha_composite(atlas_img,
                dest = (
                    part_json['spriteSourceSize']['x'],
                    part_json['spriteSourceSize']['y'],
                ),
                source = (
                    part_json['frame']['x'],
                    part_json['frame']['y'],
                    part_json['frame']['x'] + part_json['spriteSourceSize']['w'],
                    part_json['frame']['y'] + part_json['spriteSourceSize']['h']
                ),
            )

        out_bbox = [*out_img.getbbox()]
        out_bbox[2] = 2*out_bbox[2] - out_bbox[0]
        out_img = out_img.crop(out_bbox)
        out_img.alpha_composite(out_img.transpose(Image.FLIP_LEFT_RIGHT))
        out_img.save(BUILDPATH / f'out{str(i).zfill(2)}.png')

retrieve_atlas()
extract_sprites()
