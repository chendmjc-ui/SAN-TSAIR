import os
try:
    from PIL import Image
    import glob
    files = glob.glob('assets/images/**/*.{png,jpg,jpeg}', recursive=True)
    count = 0
    for f in files:
        if not f.endswith('.webp'):
            img = Image.open(f)
            img.save(f.rsplit('.', 1)[0] + '.webp', 'webp')
            count += 1
    print(f"Converted {count} images to WebP.")
except ImportError:
    print("Pillow not installed. Please run `pip install Pillow` to convert images.")
