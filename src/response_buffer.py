import os
import io
from email.utils import formatdate


class ResponseBuffer(object):
    FILE_READ_BLOCK = 4096
    INDEX_FILE = 'index.html'
    CONTENT_TYPES = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.swf': 'application/x-shockwave-flash',
    }
    DEFAULT_CONTENT_TYPE = 'text/plain'

    def __init__(self, request, document_root):
        self._request = request
        self._document_root = document_root
        self._file = None
        self._file_pos = None
        self._file_end = None

    def get_next_chunk(self):
        print('in get next chunk')
        if not os.path.exists(self._make_filepath()):
            return self._format_headers(self._make_headers_404())

        chunk = bytearray()
        if not self._file:
            # not data sent yet
            self._open_response_file()
            chunk += self._format_headers(self._make_headers_200())

        chunk += self._file.read(self.FILE_READ_BLOCK)
        self._file_pos = self._file.tell()
        return chunk

    def has_unsent_data(self):
        return not self._file or self._file_pos != self._file_end

    def _make_filepath(self):
        filepath = os.path.join(self._document_root, self._request.url.lstrip('/'))
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, self.INDEX_FILE)

        return filepath

    def _open_response_file(self):
        self._file = open(self._make_filepath(), 'rb')
        self._file.seek(0, io.SEEK_END)
        self._file_end = self._file.tell()
        self._file.seek(0, io.SEEK_SET)

    def _format_headers(self, headers_list):
        return ("\r\n".join(headers_list) + "\r\n\r\n").encode()

    def _make_headers_base(self):
        return [
            "Date: %s" % formatdate(timeval=None, localtime=False, usegmt=True),
            "Server: otus-httpd",
            "Connection: close",
        ]

    def _make_headers_200(self):
        return [
            "HTTP/1.0 200 OK",
            "Content-Type: %s" % self._get_content_type(),
            "Content-Length: %d" % self._file_end
        ] + self._make_headers_base()

    def _make_headers_404(self):
        return [
            "HTTP/1.0 404 Not Found",
            "Content-Type: text/plain",
            "Content-Length: 0"
        ] + self._make_headers_base()

    def _get_content_type(self):
        _, ext = os.path.splitext(self._file.name)
        return self.CONTENT_TYPES.get(ext, self.DEFAULT_CONTENT_TYPE)
