#!/usr/bin/env python3
"""Local preview server for the session page.

    ./serve.py            # then open http://localhost:8000

Why not `python3 -m http.server`: it answers every request with the whole
file and no Accept-Ranges header, so the browser cannot seek inside the
breathwork video. Dragging the scrubber silently does nothing. GitHub Pages
serves 206 Partial Content properly, so this only bites locally, which makes
it a confusing thing to debug. This handler adds Range support so local
preview behaves like the deployed site.
"""
import http.server
import os
import re
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(f.fileno()).st_size
        m = RANGE_RE.match(rng.strip())
        if not m:
            f.close()
            self.send_error(400, "Malformed Range header")
            return None

        start_s, end_s = m.groups()
        if start_s:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        else:                                  # suffix form: bytes=-500
            length = int(end_s or 0)
            start = max(size - length, 0)
            end = size - 1
        end = min(end, size - 1)

        if start > end or start >= size:
            f.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f.seek(start)
        self.range_remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "range_remaining", None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        self.range_remaining = None
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)

    def end_headers(self):
        # never cache during preview, so edits show up on reload
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with Server(("", PORT), RangeHandler) as httpd:
        print(f"Serving the session page at http://localhost:{PORT}  (ctrl-c to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
