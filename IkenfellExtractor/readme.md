# Ikenfell Assets Extractor

## Python extractor

* Copy Ikenfell's game directory inside this repository and name it `Ikenfell`
* **Dependencies**: `pip install --user -r requirements.txt`
* **Run**: `./extract.py`

## Image format

```
00000000  f0 00 00 00 a0 00 00 00  ff 05 12 2b ff ff 05 12  |...........+....|
00000010  2b ff ff 05 12 2b ff ff  05 12 2b ff ff 05 12 2b  |+....+....+....+|
00000020  ff ff 05 12 2b ff ff 05  12 2b ff ec 05 12 2b ff  |....+....+....+.|
[...]
```

The images are stored in `Atlas/*.img`. The first step was to try to find what type of image format it was: a standard one? Standard w/ truncated header? Raw? Compressed? I tried `file Atlas/*.img` to find out if this was a standard image format but it did not give any useful information (`data` or `SysEx File -`).

By opening the files in an hexadecimal editor, I noticed the two first uint32 seemed to be in little-endian order and seemed to represent the width and height of the image: 240x160 (resolution of the game) for `ending_*.img` and 4096x2048 for `atlas.img`.

It wasn't a raw format, the file size seemed too small for that. For example, `ending_perty.img` is 5063 Bytes (`stat`). If we assume the image is 240x160, then a raw RGB image image would be at least `240*160*3 = 115200 Bytes`. And sure, if we create a 240x160 white image in GIMP and save it as BMP we obtain a 115322 Bytes file. And if we save it as raw PPM we obtain a 115261 Bytes. The extra bytes are from the headers. So we can assume the image format has some kind of compression.

I noticed there was a lot of `FF` bytes in the files and hypothesized it was opacity. I then assumed the previous bytes where `?RGBA`. After some fumbling around I noticed the first byte was the number of occurrences of a pixel, making this a [Run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding) scheme.

## Tileset format

Individual tilesets are referenced in `Atlas/atlas.bin`. After a few hours of trying to make sense of the binary format, I decided to use the [JetBrains dotPeek](https://www.jetbrains.com/decompiler/) decompiler on `GameEngine.dll` to try to see how this format was loaded/saved in the game code. I found this information in `Atlas.LoadBinary()`, `Sprite.LoadBinary()` and `Tileset.LoadBinary()`. You can find below the python code I wrote to load this format.

```py
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
)
```

## Map format

```json
[
  {
    "room": "5,8,0",
    "area": 46,
    "ents": [
      {
        "type": "GameTiles",
        "id": 22,
        "tilesets0": "forest2_tiles,forest_tiles",
        "tiles0": "0:94,0:76,0:76,0:94,0:105,0:106,0:106,0:106,0:107,0:94,0:83,0:99,1:86,1:86,1:86,0:76,0:94,0:76,0:105,0:107,0:121,0:121,0:121,0:105,0:107,0:95,0:99,1:86,1:86,1:86,0:76,0:105,0:106,0:107,0:137,0:0,0:0,0:0,0:135,0:105,0:84,0:99,1:86,1:86,1:86,0:80,0:81,0:121,0:137,0:3,0:0,0:0,0:0,0:20,0:120,0:128,0:99,1:86,1:86,1:86,0:94,0:77,0:1,0:0,0:0,0:0,0:119,0:4,0:1,0:20,0:98,0:99,1:86,1:86,1:86,0:94,0:77,0:20,0:3,0:0,0:5,0:134,0:3,0:0,0:0,0:113,0:99,1:86,1:86,1:86,0:76,0:77,0:2,0:0,0:1,0:0,0:134,0:5,0:0,0:30,0:98,0:99,1:86,1:86,1:86,0:76,0:95,0:0,0:30,0:4,0:0,0:134,0:0,0:2,0:0,0:98,0:99,1:86,1:86,1:86,0:94,0:77,0:0,0:0,0:20,0:0,0:134,0:0,0:4,0:0,0:143,0:99,1:86,1:86,1:86,0:76,0:77,0:3,0:0,0:0,0:2,0:134,0:1,0:20,0:5,0:98,0:99,1:86,1:86,1:86",
        "tilesets1": "forest2_tiles",
        "tiles1": ",,,0:60,0:62,,,,0:60,0:62,,,,,,,0:60,0:61,0:62,,,,,,0:60,,,,,,,0:62,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0:15,,,,,,,,,0:15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "solids": "SbJdGhEhEhEf10E01fEhEhC",
        "comps": []
      },
      // other entities
    ],
  },
  // other rooms
]
```

* rooms are stored in `Data/map.json`
* `"room": "column,row,floor"`
* my extractor only handles `GameTiles` entities, it doesn't handle animated/interactive doodads
* `tilesets{n}` contains the tilesets used to create the nth layer of the map
* `tiles{n}` contains the 256 tiles constituting the nth layer of the map.
* Each tile is written as `tileset:tileset_position`. For example, in `"tiles0": "0:94,0:76,0:76,0:94,0:105,0:106,[...]"`, the tile `0:105` is the 5th one and so it will be drawn on the 1st line 5th column of the layer. The first tileset from `tilesets0` (`forest2_tiles`) will be used and its 105th tile will be drawn.


## C# extractor (Unfinished)

I then realised I probably could have used the game libraries (`GameEngine.dll` and `LittleWitch.dll`) in a [Mono](https://www.mono-project.com/) project. I started implementing it in `extract.cs` using Mono's `csharp` interpreter but I didn't have the energy to finish it. You can run it with `./extract.cs`.
