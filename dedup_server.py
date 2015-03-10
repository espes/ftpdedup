#!/usr/bin/env python2.7

import sys
import json
import hashlib
import SocketServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import leveldb

EMPTY_HASH = hashlib.sha256().digest()

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class DedupHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/dedup":
            p = 0
            l = int(self.headers.get("Content-Length", -1))
            
            hits = []
            while l < 0 or p < l:
                hash_ = self.rfile.read(32)
                if not hash_: break
                
                if hash_ != EMPTY_HASH:
                    try:
                        hits.append((hash_, self.server.db.Get(hash_)))
                    except KeyError:
                        pass

                p += len(hash_)

            self.send_response(200)
            self.end_headers()

            self.wfile.write("{\n")
            for i, (h, v) in enumerate(hits):
                self.wfile.write('\t"%s": %s%s\n' % (
                    h.encode("hex"), v,
                        "," if i < len(hits)-1 else ""))
            self.wfile.write("}\n")
        else:
            self.send_error(404)

def main():
    db = leveldb.LevelDB(sys.argv[1])

    port = 8080
    server = ThreadedHTTPServer(('', 8080), DedupHTTPHandler)
    server.db = db

    server.serve_forever()

if __name__ == "__main__":
    main()