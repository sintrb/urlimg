# -*- coding: UTF-8 -*
'''
Created on 2015年1月18日

@author: RobinTang
'''
try:
    import Image, ImageDraw, ImageFont, ImageFilter
except:
    pass
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except:
    pass

import StringIO

filters = {
    'blur':(ImageFilter.BLUR, '模糊滤镜'),
    'contour':(ImageFilter.CONTOUR, '轮廓'),
    'edge_enhance':(ImageFilter.EDGE_ENHANCE, '边界加强'),
    'edge_enhance_more':(ImageFilter.EDGE_ENHANCE_MORE, '边界加强(阀值更大)'),
    'emboss':(ImageFilter.EMBOSS, '浮雕滤镜'),
    'find_edges':(ImageFilter.FIND_EDGES, '边界滤镜'),
    'smooth':(ImageFilter.SMOOTH, '平滑滤镜'),
    'smooth_more':(ImageFilter.SMOOTH_MORE, '平滑滤镜(阀值更大)'),
    'sharpen':(ImageFilter.SHARPEN, '锐化滤镜'),
}

font = None
def getfont():
    global font
    if not font:
        import os, sys
        try:
            file_name = os.path.dirname(sys.modules['img'].__file__)
            path = os.path.abspath(file_name)
        except:
            path = ''
            font = ImageFont.truetype(os.path.join(path, "font.ttf"), 20)
    return font

def fitto(src, dw=360, dh=200):
    dst = Image.new("RGBA", (dw, dh), (255, 255, 255, 0))
    sw = src.size[0]
    sh = src.size[1]
    kw = float(sw) / float(dw)
    kh = float(sh) / float(dh)
    w, h = 0, 0
    if kw > kh:
        w, h = int(dw), int(sh / kw)
    else:
        w, h = int(sw / kh), int(dh)
    nsrc = src.resize((w, h),)
    x = (dw - w) / 2
    y = (dh - h) / 2
    dst.paste(nsrc, (x, y, x + w, y + h))
    return dst

def watermark(m, s, color=(0,0,0,255)):
    draw = ImageDraw.Draw(m)
    fsize = draw.textsize(s, font=getfont())
    draw.text((m.size[0]-fsize[0]-5, m.size[1]-fsize[1]), s, font=getfont(), fill=color)
    return m

def getimg(path):
    if path.startswith("http://") or path.startswith("https://"):
        import urllib2
        import io
        dats = io.BytesIO(urllib2.urlopen(path).read())
        m = Image.open(dats)
#         dats.close()
        return m
    else:
        return Image.open(path)

def getimgwithdats(dats):
    m = Image.open(dats)
    return m

def getimgbytes(m, fmt="png"):
    out = StringIO.StringIO()
    m.save(out, fmt)
    out.seek(0)
    dats = out.read()
    out.close()
    return dats

if __name__ == "__main__":
    m = getimg("http://img0.bdstatic.com/img/image/shouye/xinshouye/meishi116.jpg")
    # watermark(m, "Powered by Sin")
    for v in filters.values():
        m = m.filter(v[0])
    m.show()
    
    
