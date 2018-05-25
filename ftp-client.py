import ftplib
from ftplib import FTP
from typing import List
from os.path import join as pathjoin
import hmac


#host = "192.168.1.7"
host = "127.0.0.1"
port = 21
key_length_num_of_bytes = 4
BYTE_ORDER = 'big'

# ftp.retrlines("LIST")
# ftp.quit()

class MyFTP(FTP):
    def add_user(self, username, password):
        '''Add a new user'''
        resp = self.sendcmd('ADDUSER {U} {P}'.format(U=username, P=password))
        print(resp)
        return resp

    def del_user(self, username):
        resp = self.sendcmd('DELUSER {U}'.format(U=username))
        print(resp)
        return resp

# TODO extract class to utils dir
class MACGenerator(object):

    def __init__(self) -> None:
        super().__init__()


    # noinspection PyPep8Naming
    @staticmethod
    def compute_MAC(file):
        """

        :param file: encrypted file open for reading bytes
        :return: the tag that was calculated for the file
        """
        return "A" * 128

# TODO extract class to utils dir
class FileSystemHandler(object):

    def __init__(self, cwd) -> None:
        """

        :param cwd: Current working dir
        """
        super().__init__()
        self.cwd = cwd


    # def is_file_exists(self, f):


class FTPCLient(object):

    def __init__(self, host, port) -> None:
        super().__init__()

        self.port = port
        self.host = host

        self.mac_generator = MACGenerator()
        self.connection_handler = ConnectionHandler(host, port)
        self.input_handler = UserInputHandler()
        self.cmd_handler = FTPcmd()


    def run(self):
        while True:
            new_user = input("from new user type: 'add', and for login type 'login' \n")
            if new_user == 'add':
                # login with admin and he will add the new user
                # self.connection_handler.do_login('admin', 'admin')
                user = input('New username:')
                pw = input('New password:')
                self.connection_handler.add_user(user, pw)
                # self.connection_handler.quit()

            elif new_user == 'login':
                self.connection_handler.login()
                # login
            else:
                print("Wrong command idiot")

            while not self.connection_handler.is_finished():
                user_in = self.input_handler.get_user_input()

                if user_in is not None:
                    processed_in = self.cmd_handler.process_input(user_in)
                else:
                    print("NO GOOD")
                    continue

                self.connection_handler.send_cmd(processed_in)
                response = self.connection_handler.server_response()
                print(response)


class FTPcmd(object):
    command_dict = {
        'delete': 'DELE',
        'upload': 'STOR',
        'ls': 'LIST',
        'download': 'RETR',
        'login': 'login',
        'deluser': 'DELUSER',
    }


    def __init__(self) -> None:
        super().__init__()

    def cmd_to_ftp_command(self, command):

        returnable = FTPcmd.command_dict.get(command)
        if returnable is not None:
            return returnable
        else:
            print("NO GOOD ftp command")
            return None

    def process_input(self, user_in: List[str]):
        ftp_cmd = self.cmd_to_ftp_command(user_in[0])
        args = user_in[1:]

        if ftp_cmd is not None and self.validate_args(ftp_cmd, args):
            return " ".join([ftp_cmd] + args)

    def validate_args(self, ftp_cmd, args):
        return True


class ConnectionHandler(object):

    def __init__(self, host, port) -> None:
        super().__init__()
        self.port = port
        self.host = host

        self.ftp = MyFTP()
        self.ftp.connect(host, port)

        self.recent_response = []

    def is_finished(self):
        return False

    def login(self):
        user = input('Username:')
        pw = input('Password:')

        self.do_login(user, pw)

    def do_login(self, user, pw):
        resp = self.ftp.login(user, pw)
        print("Response: ", resp)

    # def logout(self, user):
    #     self.ftp.close()

    def add_user(self, user, pw):
        self.ftp.add_user(user, pw)

    # def quit(self):
    #     resp = self.ftp.quit()
    #     print(resp)

    def send_cmd(self, processed_in):
        if processed_in == 'ls':
            return_code = self.ftp.retrlines(processed_in, callback=self.response_handle)
            print("Returned: ", return_code)
        elif processed_in.startswith('STOR'):
            with open('new_file.txt', 'rb') as f:
                self.ftp.storbinary('STOR new_file.txt', f)

        elif processed_in == 'login':
            self.login()

        elif processed_in == 'DELUSER':
            self.deluser()

    def response_handle(self, res):
        self.recent_response.append( res)

    def server_response(self):
        return self.recent_response

    def deluser(self):
        user = input('Username:')
        resp = self.ftp.del_user(user)
        print("Response: ", resp)


class UserInputHandler(object):

    def __init__(self) -> None:
        super().__init__()


    def get_user_input(self):
        user_input = input(">>>")
        return self.handle_user_input(user_input)


    def handle_user_input(self, user_input):
        if not self.valid_user_input(user_input):
            self.input_error_print(user_input)
            return None

        return self.basic_process_input(user_input).split()


    def valid_user_input(self, user_input):
        return True


    def input_error_print(self, user_input):
        print("NOT SO GOOD")


    def basic_process_input(self, user_input):
        return user_input


if __name__ == '__main__':
    client = FTPCLient(host, port)
    client.run()