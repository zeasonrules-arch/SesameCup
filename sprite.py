from PIL import Image

# 8张图片的名称
files = ["sesame_01_Red.png", "sesame_02_Orange.png", "sesame_03_Yellow.png",
         "sesame_04_Green.png", "sesame_05_Blue.png", "sesame_06_Purple.png",
         "sesame_07_White.png", "sesame_08_Black.png"]

# 创建一个 800x800 的画布 (每张图按 80x80 处理)
sprite = Image.new('RGBA', (800, 800), (0, 0, 0, 0))

for i, file in enumerate(files):
    img = Image.open(file).resize((80, 80))
    # 将图片平铺到 10x10 的网格里
    for row in range(10):
        for col in range(10):
            sprite.paste(img, (col * 80, (i * 10 + row) * 80))

sprite.save("sprites.png")
print("合成完毕！sprites.png 已生成，请将其上传至 GitHub")