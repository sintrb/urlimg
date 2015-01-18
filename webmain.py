# -*- coding: UTF-8 -*
'''
Created on 2015年1月18日

@author: RobinTang
'''
import tornado.web

class KVClient:
    def __init__(self):
        self.cache = {}
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None
    def set(self, key, val, min_compress_len=0):
        self.cache[key] = val
    def add(self, key, val, min_compress_len=0):
        if key not in self.cache:
            self.set(key, val, min_compress_len)
    def replace(self, key, val, min_compress_len=0):
        if key in self.cache:
            self.set(key, val, min_compress_len)
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
    def get_info(self):
        return {
                'count': len(self.cache),
                'keys': [k for k in self.cache.keys()],
                }
    instance = None
    @staticmethod
    def get_instance():
        if not KVClient.instance:
            KVClient.instance = KVClient()
        return KVClient.instance

def md5(v):
    import hashlib
    return hashlib.md5(v).hexdigest()

class SAERequestHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        try:
            import sae.kvdb
            self.kv = sae.kvdb.KVClient()
        except:
            self.kv = KVClient.get_instance()

class MainHandler(SAERequestHandler):
    def get(self):
        import time
        self.write("Hello, world %d" % time.time())

class StcHandler(SAERequestHandler):
    def get(self):
        import json
        self.write(json.dumps(self.kv.get_info()))

class SwitchImg(SAERequestHandler):
    def get(self):
        import img
        w = int(self.get_argument("width", 0))
        h = int(self.get_argument("height", 0))
        url = self.get_argument("url", None)
        usecacache = not int(self.get_argument("nocache", 0))
        urlkey = 'u%s' % (md5(url))
        key = '%s_w%s_h%s' % (urlkey, w, h)
        res = usecacache and self.kv.get(key)
        if res:
            self.set_header("Cached", "Image")
        else:
            bts = usecacache and self.kv.get(urlkey)
            if bts:
                self.set_header("Cached", "Url")
            else:
                import urllib2
                bts = urllib2.urlopen(url).read()
                self.kv.set(urlkey, bts)
                self.set_header("Cached", "False")
            import io
            dats = io.BytesIO(bts)
            m = img.getimgwithdats(dats)
            sw = m.size[0]
            sh = m.size[1]
            if w == 0:
                w = sw
            if h == 0:
                h = sh
            if w != sw or h != sh:
                m = img.fitto(m, w, h)
            res = img.getimgbytes(m, "png")
            dats.close()
            self.kv.set(key, res)
        self.set_header("Content-Type", "image/png")
        self.write(res)
        


url = [
    (r"/", SwitchImg),
    (r"/t/", MainHandler),
    (r"/stc/", StcHandler),
]

settings = {
    "debug": True,
}



if __name__ == "__main__":
    import tornado.ioloop
    application = tornado.web.Application(url, **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


