#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import datetime
import hashlib
import json
import logging
import os
import shutil
import urllib.parse
import urllib.request

logging.basicConfig(format="%(asctime)-15s %(name)s %(process)d %(message)s", level=logging.DEBUG)

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "/notebooks")
SALT = os.environ["SALT"]
DST_URL_PREFIX = "https://ipython.anytask.org"
ABSOLUTE_URL_PREFIX = "https://anytask.org/"
URL_PREFIXES_WHITELIST = [ABSOLUTE_URL_PREFIX, "https://www.anytask.org/", "https://storage.yandexcloud.net/anytask-ng/"]
DOWNLOADED_FILES_TTL = datetime.timedelta(days=30)
DEBUG = os.environ.get("DEBUG", False)


class Handler(BaseHTTPRequestHandler):
    @staticmethod
    def get_right_url(url):
        url = url.lstrip("/gate/")

        if not url.startswith("https://"):
            url = ABSOLUTE_URL_PREFIX + url

        for u in URL_PREFIXES_WHITELIST:
            if url.startswith(u):
                return url
        return False

    @staticmethod
    def dst_url(dst_filename):
        slash = ""
        if not dst_filename.startswith("/"):
            slash = "/"

        return DST_URL_PREFIX + slash + dst_filename

    @staticmethod
    def cleanup(dst_dir):
        if not os.path.exists(dst_dir):
            logging.error("Directory to cleanup not found! : '%s'", dst_dir)
            return

        now = datetime.datetime.now()
        deadline = now - DOWNLOADED_FILES_TTL

        for f in os.listdir(dst_dir):
            if f.startswith("."):
                continue

            path = os.path.join(dst_dir, f)
            if not os.path.isdir(path):
                continue

            ctime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            if ctime > deadline:
                logging.info("rmtree path:%s, deadline:%s, ctime:%s", path, deadline, ctime)
                shutil.rmtree(path, ignore_errors=True)


    def do_GET(self):
        self.cleanup(DOWNLOAD_PATH)
        url_to_download = self.path
        url_to_download = self.get_right_url(url_to_download)
        if not url_to_download:
            self.send_response(403)
            self.end_headers()
            return

        dst_filename = url_to_download.split("/")[-1]
        dst_filename = urllib.parse.unquote(dst_filename)
        dst_random = hashlib.sha256((SALT + url_to_download).encode("utf-8")).hexdigest()
        dst_dir = os.path.join(DOWNLOAD_PATH, dst_random)
        dst_path = os.path.join(dst_dir, dst_filename)

        if not os.path.exists(dst_path):
            os.makedirs(dst_dir, exist_ok=True)
            logging.info("Download: %s", url_to_download)
            urllib.request.urlretrieve(url_to_download, dst_path)

        dst_url = self.dst_url(dst_path)

        reply = {
            "ok": True,
            "url": url_to_download,
            "dst_path": dst_path,
            "dst_url": dst_url,
        }

        if DEBUG:
            self.send_response(200)
        else:
            self.send_response(302)
        self.send_header("Content-type", "application/json")
        self.send_header("Location", dst_url)
        self.end_headers()
        self.wfile.write(json.dumps(reply).encode("utf-8"))


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    server = ThreadingSimpleServer(('0.0.0.0', 5555), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
