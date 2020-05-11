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
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.swf': 'application/x-shockwave-flash',
    }
    DEFAULT_CONTENT_TYPE = 'text/plain'
    ALLOWED_METHODS = ['GET', 'HEAD']

    def __init__(self, request, document_root):
        self._request = request
        self._document_root = document_root
        self._file = None
        self._file_pos = None
        self._file_end = None

    def get_next_chunk(self):
        print('in get next chunk')
        filepath = self._make_filepath()
        if self._request.method not in self.ALLOWED_METHODS:
            return self._format_headers(self._make_headers_405())

        elif not self._check_if_subpath(filepath):
            return self._format_headers(self._make_headers_403())

        elif not os.path.exists(filepath):
            return self._format_headers(self._make_headers_404())

        chunk = bytearray()
        if not self._file:
            # not data sent yet
            self._open_response_file(filepath)
            chunk += self._format_headers(self._make_headers_200())

        if self._request.method == 'HEAD':
            # emulate that file was read
            # so next time has_unsent_data will return False
            self._file_pos = self._file_end
            return chunk

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

    def _check_if_subpath(self, filepath):
        docs_root = os.path.realpath(self._document_root)
        return os.path.realpath(filepath).startswith(docs_root)

    def _open_response_file(self, filepath):
        self._file = open(filepath, 'rb')
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

    def _make_headers_403(self):
        return [
            "HTTP/1.0 403 Forbidden",
            "Content-Length: 0",
        ] + self._make_headers_base()

    def _make_headers_404(self):
        return [
            "HTTP/1.0 404 Not Found",
            "Content-Length: 0",
        ] + self._make_headers_base()

    def _make_headers_405(self):
        return [
            "HTTP/1.0 405 Method Not Allowed",
            "Content-Length: 0",
        ] + self._make_headers_base()

    def _get_content_type(self):
        _, ext = os.path.splitext(self._file.name)
        return self.CONTENT_TYPES.get(ext, self.DEFAULT_CONTENT_TYPE)
