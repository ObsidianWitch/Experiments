#!/usr/bin/env -S csharp -pkg:dotnet -lib:Ikenfell -r:GameEngine.dll,LittleWitch.dll -s

using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
using GE = GameEngine;
using LW = LittleWitch;

class Extractor {
    public Extractor() {
        GE.Platform.Init();
        GE.Platform.ContentRoot = "Ikenfell/";
        GE.Platform.SaveRoot = "Out/";
        var game = new Game();
    }

    // Note: Couldn't use GE.Bitmap.Save(), it throws the following exception:
    // "System.DllNotFoundException: utilities.dll [...]". And indeed, the DLL
    // is missing from the game directory.
    public void img2png(GE.Bitmap img, String fileout) {
        var data = img.Data.SelectMany(item =>
            new [] { item.B, item.G, item.R, item.A }).ToArray();

        unsafe { fixed(byte* ptr = data) {
            var bitmap = new Bitmap(
                width:  img.Width,
                height: img.Height,
                stride: 4 * img.Width,
                format: PixelFormat.Format32bppArgb,
                scan0:  (IntPtr) ptr);
            bitmap.Save(fileout);
        }}
    }

    public void imgs2pngs(String dirin, String dirout) {
        var imagePaths = Directory.GetFiles($"{dirin}/Atlas/", "*.img");
        foreach (var path in imagePaths) {
            var img = new GE.Bitmap(path);
            var stem = Path.GetFileNameWithoutExtension(path);
            img2png(img, $"{dirout}/i_{stem}.png");
        }
    }
}

var extractor = new Extractor();
extractor.imgs2pngs(GE.Platform.ContentRoot, GE.Platform.SaveRoot);
