# -*- coding: UTF-8 -*
'''
Created on 2015年1月18日

@author: RobinTang
'''
try:
    import Image
except:
    pass
try:
    from PIL import Image
except:
    pass

import StringIO

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
    print w, h
    nsrc = src.resize((w, h),)
    x = (dw - w) / 2
    y = (dh - h) / 2
    dst.paste(nsrc, (x, y, x + w, y + h))
    return dst

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
#     img = fitto(getimg("./imgs/s6037735.jpg"), 200, 200).show()
    Image.new("RGBA", (100, 100), (255, 255, 255)).show()
    
    
