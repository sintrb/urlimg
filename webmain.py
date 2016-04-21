# -*- coding: UTF-8 -*
'''
Created on 2015年1月18日

@author: RobinTang
'''
import tornado.web

class KVClient:
    MAX = 200
    def __init__(self):
        self.cache = {}
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None
    def set(self, key, val, min_compress_len=0):
        self.cache[key] = val
        if len(self.cache)>self.MAX:
            # reset 
            self.cache = {}
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

class FiltersHandler(SAERequestHandler):
    def get(self):
        import img, json
        fts = {
            'items': [(v[0], v[2]) for v in img.filters]
        }
        self.set_header("Content-Type", "text/json")
        self.write(json.dumps(fts))
        

class SwitchImg(SAERequestHandler):
    def get(self):
        import img, json
        from urllib import unquote
        argsmap = {
            'width':(int, 0),
            'height':(int, 0),
            'url':(str, ''),
            'sign':(str, ''),
            'signsize':(int, 20),
            'filters':(str, ''),
        }
        
        args = {}
        for k, v in argsmap.items():
            av = unquote(str(self.get_argument(k, '')))
            try:
                av = v[0](av)
            except Exception, e:
                av = v[1]
            args[k] = av

        if args['width'] < 0:
            args['width'] = 0
        if args['height'] < 0:
            args['height'] = 0

        url = args['url']
        usecache = not int(self.get_argument("nocache", 0))
        print 'url: ', url
        if url:
            urlkey = md5(url)
            s = '|'.join(['%s_%s' % (k, v) for (k, v) in args.items() if v])
            # self.write(s)
            # return
            key = md5(s)
            self.set_header("ETag", key)
            if not usecache and self.check_etag_header():
                # 304
                self.set_status(304, 'Not Modified')
                return
            
            res = usecache and self.kv.get(key)
            if res:
                self.set_header("Cached", "Image")
            else:
                bts = usecache and self.kv.get(urlkey)
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
                w = args['width']
                h = args['height']
                if w <= 0:
                    w = sw
                if h <= 0:
                    h = sh
                if w != sw or h != sh or m.format == 'GIF':
                    m = img.fitto(m, w, h)
                if args['filters']:
                    for fk in args['filters'].split(','):
                        if fk.strip() and fk.strip() in img.filtersmap:
                            m = m.filter(img.filtersmap[fk.strip()][0])
                if args['sign']:
                    m = img.watermark(m, args['sign'], size=args['signsize'])

                res = img.getimgbytes(m, "png")
                dats.close()
                self.kv.set(key, res)
            self.set_header("Content-Type", "image/png")
            self.write(res)
        else:
            self.redirect("/edit")
        
class EditHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("demo.html")

url = [
    (r"/", SwitchImg),
    (r"/hi", MainHandler),
    (r"/stc", StcHandler),
    (r"/filters", FiltersHandler),
    (r"/edit", EditHandler),
]

import os
settings = {
    "debug": True,
    "static_path" : os.path.join(os.path.dirname(__file__), "static"),
    "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
}



if __name__ == "__main__":
    import sys
    import tornado.ioloop
    port = int(sys.argv[1]) if len(sys.argv) == 2 else int(sys.argv[2]) if len(sys.argv) == 3 else 9999
    addr = sys.argv[1] if len(sys.argv) == 3 else '127.0.0.1'
    application = tornado.web.Application(url, **settings)
    print 'listen at %s:%d' % (addr,port)
    application.listen(port,addr)
    tornado.ioloop.IOLoop.instance().start()


