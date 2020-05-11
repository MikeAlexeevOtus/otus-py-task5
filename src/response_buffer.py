import os
import io


class ResponseBuffer(object):
    FILE_READ_BLOCK = 4096
    INDEX_FILE = 'index.html'

    def __init__(self, request, document_root):
        self._request = request
        self._root = document_root
        self._file = None
        self._file_pos = None
        self._file_end = None

    def get_next_chunk(self):
        print('in get next chunk')
        if not os.path.exists(self._make_filepath()):
            return self._make_headers_404()

        chunk = bytearray()
        if not self._file:
            # not data sent yet
            self._open_response_file()
            chunk += self._make_headers_200()

        chunk += self._file.read(self.FILE_READ_BLOCK)
        self._file_pos = self._file.tell()
        return chunk

    def has_unsent_data(self):
        return not self._file or self._file_pos != self._file_end

    def _make_filepath(self):
        filepath = os.path.join(self._root, self._request.url.lstrip('/'))
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, self.INDEX_FILE)

        return filepath

    def _open_response_file(self):
        self._file = open(self._make_filepath(), 'rb')
        self._file.seek(0, io.SEEK_END)
        self._file_end = self._file.tell()
        self._file.seek(0, io.SEEK_SET)

    def _make_headers_200(self):
        resp_headers = b"""HTTP/1.0 200 OK
Date: Mon, 1 Jan 1996 01:01:01 GMT
Content-Type: text/plain
Content-Length: %d

""".replace(b'\n', b'\r\n')
        return resp_headers % self._file_end
