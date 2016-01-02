# coding: utf-8

import subprocess
import threading
import time
from urllib.parse import urljoin

import requests
from celery.utils.log import get_task_logger
from django.conf import settings
from requests_toolbelt import MultipartEncoder

from rlscloud import app


log = get_task_logger(__name__)


class EncoderTask(app.Task):
    def _auth(self):
        login_page = self.session.get(settings.ENCODE_RLSCLOUD_SERVER)
        index_page = self.session.post(login_page.url, data={
            'username': settings.ENCODE_RLSCLOUD_AUTH_USER,
            'password': settings.ENCODE_RLSCLOUD_AUTH_PWD,
            'csrfmiddlewaretoken': self.session.cookies['csrftoken']
        })

        assert index_page.url != login_page.url

    def _remote_stream(self):
        reply = self.session.get(self.release_url, stream=True)
        reply.raw.len = int(reply.headers['content-length'])  # Such an ugly hack
        return reply.raw

    def _encode_stream(self, remote):
        ffmpeg = subprocess.Popen(['ffmpeg', '-y', '-i', 'pipe:0', '-f', 'ogg', 'pipe:1'],
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

        def feed():
            for block in iter(lambda: remote.read(65535), b''):
                ffmpeg.stdin.write(block)

        threading.Thread(target=feed).start()

        return ffmpeg.stdout

    def run(self, url: str) -> None:
        print(url)
        self.session = requests.Session()
        self._auth()
        self.release_url = urljoin(settings.ENCODE_RLSCLOUD_SERVER, url)

        _start = time.time()
        remote_file_stream = self._remote_stream()
        ffmpeg_pipe = self._encode_stream(remote_file_stream)

        data = MultipartEncoder({
            'csrfmiddlewaretoken': self.session.cookies['csrftoken'],
            'file': ('glejd.ogg', ffmpeg_pipe, 'audio/ogg')
        })

        r = self.session.post(settings.ENCODE_RLSCLOUD_UPLOAD,
                              data=data,
                              headers={'Content-Type': data.content_type})
        print(r.content.decode(), time.time() - _start)


encode = EncoderTask()
