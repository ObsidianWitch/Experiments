#!/usr/bin/env python3

import sys, struct, io, re, json
import operator as op
from pathlib import Path
from PIL import Image
import construct as cs

# Convert Ikenfell images to PNGs.
def imgs2pngs(dpin:Path, dpout:Path):
    for fpimg in dpin.glob('*.img'):
        with open(fpimg, 'rb') as f:
            image = Image.frombytes(
                mode = 'RGBA',
                size = struct.unpack('<II', f.read(8)),
                data = b''.join(
                    n * rgba for n, rgba
                    in struct.iter_unpack('B4s', f.read())
                ),
            )
            image.save(dpout / f'i_{fpimg.stem}.png')

class Atlas:
    BINFORMAT = cs.Struct(
        'name' / cs.PascalString(cs.Byte, 'utf8'),
        'whitePixelX' / cs.Float32l,
        'whitePixelY' / cs.Float32l,
        'nSprites' / cs.Int32ul,
        'sprites' / cs.Array(cs.this.nSprites, cs.Struct(
            'name' / cs.PascalString(cs.Byte, 'utf8'),
            'width' / cs.Float32l,
            'height' / cs.Float32l,
            't0X' / cs.Float32l,
            't0Y' / cs.Float32l,
            't2X' / cs.Float32l,
            't2Y' / cs.Float32l,
            'trimWidth' / cs.Float32l,
            'TrimHeight' / cs.Float32l,
            'offsetX' / cs.Float32l,
            'offsetY' / cs.Float32l,
        )),
        'nTilesets' / cs.Int32ul,
        'tilesets' / cs.Array(cs.this.nTilesets, cs.Struct(
            'name' / cs.PascalString(cs.Byte, 'utf8'),
            'tileWidth' / cs.Int32ul,
            'tileHeight' / cs.Int32ul,
            'cols' / cs.Int32ul,
            'rows' / cs.Int32ul,
            'nIds' / cs.Int32ul,
            'spriteIds' / cs.Array(cs.this.nIds, cs.Int32ul),
            'isOptimized' / cs.Flag,
            'optimized' / cs.If(cs.this.isOptimized, cs.Array(
                cs.this.cols * cs.this.rows, cs.Flag)),
        )),
    ).compile()

    # An Atlas is composed of the atlas image itself (`fpimg`) and its data
    # (`fpbin`) containing the references to the original sprites and tilesets.
    def __init__(self, fpbin:Path, fpimg:Path):
        with open(fpbin, 'rb') as fAtlasBin:
            binData = fAtlasBin.read()
        self.bin = self.BINFORMAT.parse(binData)
        self.img = Image.open(fpimg)

        # Tilesets indexed by name and prepare tiles populating.
        self.tilesets = {}
        for ts in self.bin.tilesets:
            ts.sprites = {}
            self.tilesets[ts.name] = ts

        # Populate tilesets with their tiles and populate standalone sprites.
        # Additional attributes are also added to sprites for convenience
        # (col, row, id, img).
        self.standaloneSprites = []
        reTileName = re.compile(r'(.*)_([0-9]*)_([0-9]*)$')
        for sprite in self.bin.sprites:
            sprite.img = self.getSpriteImg(sprite)
            if m := reTileName.match(sprite.name):
                name, col, row = m.groups()
                tileset = self.tilesets[name]
                sprite.col = int(col)
                sprite.row = int(row)
                sprite.id = (sprite.row * tileset.cols) + sprite.col
                tileset.sprites[sprite.id] = sprite
            else:
                self.standaloneSprites.append(sprite)

    def getSpriteImg(self, sprite):
        return self.img.crop((
            int(sprite.t0X * self.img.width),
            int(sprite.t0Y * self.img.height),
            int(sprite.t2X * self.img.width),
            int(sprite.t2Y * self.img.height),
        ))

    def saveStandaloneSprites(self, dpout:Path):
        for sprite in self.standaloneSprites:
            if sprite.name in self.tilesets: continue
            sprite.img.save(dpout / f's_{sprite.name}.png')

    def saveTilesets(self, dpout:Path):
        for tileset in self.bin.tilesets:
            size = (tileset.tileWidth  * tileset.cols,
                    tileset.tileHeight * tileset.rows,)
            img = Image.new('RGBA', size)

            for sprite in tileset.sprites.values():
                position = (sprite.col * tileset.tileWidth,
                             sprite.row * tileset.tileHeight,)
                img.paste(sprite.img, position)
            img.save(dpout / f't_{tileset.name}.png')

class Maps:
    COLS = 15
    ROWS = 10
    TILEWIDTH = 16
    TILEHEIGHT = 16
    WIDTH = COLS * TILEWIDTH
    HEIGHT = ROWS * TILEHEIGHT
    SIZE = (WIDTH, HEIGHT)

    def __init__(self, atlas:Atlas, fpjmaps:Path):
        self.atlas = atlas
        with open(fpjmaps) as fjmaps:
            self.jmaps = json.load(fjmaps)

    def drawLayer(self, gameTiles, i, dstimg):
        tilesets = gameTiles[f'tilesets{i}']
        if not tilesets: return
        tilesets = tuple( self.atlas.tilesets[ts] for ts in tilesets.split(',') )
        tiles = gameTiles[f'tiles{i}'].split(',')

        for j, tile in enumerate(tiles):
            if not tile: continue
            tileseti, tilei = tile.split(':')
            sprite = tilesets[int(tileseti)].sprites[int(tilei)]

            position = ((j %  self.COLS) * self.TILEWIDTH,
                        (j // self.COLS) * self.TILEHEIGHT,)
            dstimg.alpha_composite(sprite.img, position)

    def getRoomImg(self, room):
        roomimg = Image.new('RGBA', self.SIZE, color=(0, 0, 0, 255))
        gameTiles = next(ent for ent in room['ents']
                         if ent['type'] == 'GameTiles')
        self.drawLayer(gameTiles, 0, roomimg)
        self.drawLayer(gameTiles, 1, roomimg)
        return roomimg

    def save(self, dpout:Path):
        for room in self.jmaps:
            if 'area' not in room: continue
            col, row, floor = room['room'].split(',')
            roomimg = self.getRoomImg(room)
            roomimg.save(dpout / f"m_{room['area']},{floor},{row},{col}.png")

dpin = Path('Ikenfell')
dpout = Path('Out')
dpout.mkdir(exist_ok=True)

imgs2pngs(dpin / 'Atlas', dpout)
atlas = Atlas(dpin / 'Atlas/atlas.bin', dpout / 'i_atlas.png')
atlas.saveStandaloneSprites(dpout)
atlas.saveTilesets(dpout)
Maps(atlas, dpin / 'Data/map.json').save(dpout)
