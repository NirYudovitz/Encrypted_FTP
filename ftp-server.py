import os
import socket

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, DTPHandler, _FileReadWriteError
from pyftpdlib.ioloop import RetryError
from pyftpdlib.servers import FTPServer

BYTE_ORDER = 'big'
KEY_LENGTH_NUM_OF_BYTES = 4


class MyDTPHandler(DTPHandler):

    def __init__(self, sock, cmd_channel):
        super().__init__(sock, cmd_channel)
        DTPHandler.handle_read_event = MyDTPHandler.handle_read

    def handle_read(self):
        print("!")
        super().handle_read()

    # def handle_read(self):
    #     """Called when there is data waiting to be read."""
    #     print("shtut")
    #     a = 4
    #     b = a + 4
    #     try:
    #         chunk = self.recv(self.ac_in_buffer_size)
    #     except RetryError:
    #         pass
    #     except socket.error:
    #         self.handle_error()
    #     else:
    #         self.tot_bytes_received += len(chunk)
    #         if not chunk:
    #             self.transfer_finished = True
    #             # self.close()  # <-- asyncore.recv() already do that...
    #             return
    #         if self._data_wrapper is not None:
    #             chunk = self._data_wrapper(chunk)
    #         try:
    #             self.file_obj.write(chunk)
    #         except OSError as err:
    #             raise _FileReadWriteError(err)


class MyHandler(FTPHandler):

    self_defined_cmds = {
        'DELUSER': {'perm': 'e', 'auth': True, 'arg': True,
                    'help':'Syntax: DELUSER [<SP> user-name] (delete a fucking user).'}
    }


    def must_login(self, func):
        if not self.authenticated:
            print("cannot do {}")

    def ftp_STOR(self, file, mode='w'):
        print("123")
        return super().ftp_STOR(file, mode)

    def ftp_ADDUSER(self, *args):
        print("adding a new user!!!!!!")
        user = args[0][0]
        pw = args[0][1]
        # create a new folder for the new user
        self.authorizer.add_user(user, pw, "C:/university/F/remote", perm="elradfmwMT")
        print(self.authorizer.user_table)
        resp = "User added successfully."
        self.respond("150 " + resp)


    @must_login
    @user_previlegies('admin')
    def ftp_DELUSER(self, *args):
        print (self.username)

    def pre_process_command(self, line, cmd, arg):
        kwargs = {}

        if cmd == "ADDUSER":
            self.process_command(cmd, arg.split(), **kwargs)
            return

        super().pre_process_command(line, cmd, arg)

    def on_connect(self):
        super().on_connect()

    def on_file_received(self, file):
        print("123")
    #     FTPHandler.on_file_received(self, file)
    #     file_path = os.path.join(handler.authorizer.get_home_dir("3"), file)
    #     with open(file_path, "rb") as f:
    #         tag_length = int.from_bytes(f.read(KEY_LENGTH_NUM_OF_BYTES), BYTE_ORDER)
    #         tag = f.read(tag_length).decode('utf-8')
    #         byte = f.read(1)
    #         while byte != b"":
    #             # Do stuff with byte.
    #             byte = f.read(1)

    def __init__(self, conn, server, ioloop=None):
        FTPHandler.__init__(self, conn, server, ioloop)
        self.proto_cmds.update(MyHandler.self_defined_cmds)

    # handle_read_event = handle_read  # small speedup
    #
    # def handle_read(self):
    #     """Called when there is data waiting to be read."""
    #     try:
    #         chunk = self.recv(self.ac_in_buffer_size)
    #     except RetryError:
    #         pass
    #     except socket.error:
    #         self.handle_error()
    #     else:
    #         self.tot_bytes_received += len(chunk)
    #         if not chunk:
    #             self.transfer_finished = True
    #             # self.close()  # <-- asyncore.recv() already do that...
    #             return
    #         if self._data_wrapper is not None:
    #             chunk = self._data_wrapper(chunk)
    #         try:
    #             self.file_obj.write(chunk)
    #         except OSError as err:
    #             raise _FileReadWriteError(err)


if __name__ == '__main__':
    authorizer = DummyAuthorizer()
    authorizer.add_user("admin", "admin", "C:/university/F/remote", perm="elradfmwMT")
    authorizer.add_anonymous("C:/university/F/remote")

    handler = MyHandler
    handler.authorizer = authorizer
    handler.dtp_handler = MyDTPHandler

    server = FTPServer(("127.0.0.1", 21), handler)
    server.serve_forever()
