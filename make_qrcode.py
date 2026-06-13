import qrcode
from PIL import Image, ImageDraw, ImageOps

# 1. 填入您明天的真实网址（务必确认！）
url = "https://zeasonrules-arch.github.io/SesameCup/"

# 2. 生成高容错基础二维码
qr = qrcode.QRCode(
    version=5,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4
)
qr.add_data(url)
qr.make(fit=True)

# 提取黑白蒙版 (L模式：灰度，黑0 白255)
qr_img = qr.make_image(fill_color="black", back_color="white").convert('L')
width, height = qr_img.size


# ==========================================
# 3. 核心：精准提取 Logo 全息色彩的细腻渐变
# ==========================================
def create_logo_gradient(w, h):
    base_size = 200
    grad = Image.new('RGB', (base_size, base_size))
    pixels = grad.load()

    # 完美复刻您 Logo 上的镭射/全息渐变色标
    stops = [
        (0.00, (255, 205, 145)),  # 顶部/左上：柔和的蜜桃金 (提取自眼睫毛外延和水滴尖端)
        (0.30, (85, 225, 185)),  # 左侧：通透的薄荷绿/青色 (提取自左眼)
        (0.65, (95, 145, 255)),  # 中间/偏右：矢车菊蓝 (提取自右眼)
        (1.00, (165, 100, 255))  # 右下：极光紫 (提取自水滴右下方的阴影过度)
    ]

    for y in range(base_size):
        for x in range(base_size):
            # 对角线进度计算 (0.0 到 1.0)
            t = (x + y) / (base_size * 2 - 2)

            # 多段平滑插值
            for i in range(len(stops) - 1):
                t1, c1 = stops[i]
                t2, c2 = stops[i + 1]
                if t1 <= t <= t2:
                    ratio = (t - t1) / (t2 - t1)
                    r = int(c1[0] + (c2[0] - c1[0]) * ratio)
                    g = int(c1[1] + (c2[1] - c1[1]) * ratio)
                    b = int(c1[2] + (c2[2] - c1[2]) * ratio)
                    pixels[x, y] = (r, g, b)
                    break

    # 使用 BICUBIC 双立方插值放大到目标尺寸
    return grad.resize((w, h), Image.Resampling.BICUBIC).convert('RGBA')


logo_gradient = create_logo_gradient(width, height)

# 4. 将提取的高级色“灌”进二维码里
mask = ImageOps.invert(qr_img)
final_img = Image.new('RGBA', (width, height), 'white')
final_img.paste(logo_gradient, (0, 0), mask)

# ==========================================
# 5. 镶嵌“正圆形纯白悬浮底座 + 芝麻 Logo”
# ==========================================
try:
    # 加载您上传的芝麻 Logo
    logo = Image.open("芝麻logo.png").convert('RGBA')

    # 放大 Logo 占比
    logo_size = int(width / 3.2)
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # 绘制完美【正圆形】的纯白底座
    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 0))
    bg_draw = ImageDraw.Draw(logo_bg)
    bg_draw.ellipse((0, 0, logo_size, logo_size), fill="white")

    # 将原 Logo 叠在纯白圆形底座上
    # 确保 Logo 也是居中贴在圆里 (以防原图边缘有留白)
    logo_bg.paste(logo, (0, 0), mask=logo)

    # 将完整的带圆底的 Logo 居中贴在二维码中心
    pos = ((width - logo_size) // 2, (height - logo_size) // 2)
    final_img.paste(logo_bg, pos, mask=logo_bg)

except Exception as e:
    print(f"⚠️ Logo处理失败。报错: {e}")

# 6. 保存出图
final_img.save("芝麻杯高定二维码.png")
print("💎 完美！专属全息定制版二维码已生成！请查看 [芝麻杯高定二维码.png]")