import argparse
import os
import sys
from de_en_crypter import decrypt, encrypt
# include the code above ...
# ================================================================
# _open_ios
# ================================================================
from getpass import getpass
VERSION = '420'

def _open_ios(args):
    '''
    Open the IO files.
    '''
    ifp = sys.stdin
    ofp = sys.stdout

    if args.input is not None:
        try:
            ifp = open(args.input, 'rb')
        except IOError:
            print('ERROR: cannot read file: {}'.format(args.input))
            sys.exit(1)

    if args.output is not None:
        try:
            ofp = open(args.output, 'wb')
        except IOError:
            print('ERROR: cannot write file: {}'.format(args.output))
            sys.exit(1)

    return ifp, ofp


# ================================================================
# _close_ios
# ================================================================
def _close_ios(ifp, ofp):
    '''
    Close the IO files if necessary.
    '''
    if ifp != sys.stdin:
        ifp.close()

    if ofp != sys.stdout:
        ofp.close()


# ================================================================
# _write
# ================================================================
def _write(ofp, out, newline=False):
    '''
    Write out the data in the correct format.
    '''
    if ofp == sys.stdout and isinstance(out, bytes):
        out = out.decode('utf-8', 'ignored')
        ofp.write(out)
        if newline:
            ofp.write('\n')
    elif isinstance(out, str):
        ofp.write(out)
        if newline:
            ofp.write('\n')
    else:  # assume bytes
        ofp.write(out)
        if newline:
            ofp.write(b'\n')


# ================================================================
# _write
# ================================================================
def _read(ifp):
    '''
    Read the data in the correct format.
    '''
    return ifp.read()


# ================================================================
# _runenc
# ================================================================
def _runenc(args):
    '''
    Encrypt data.
    '''
    if args.passphrase is None:
        while True:
            passphrase = getpass('Passphrase: ')
            tmp = getpass('Re-enter passphrase: ')
            if passphrase == tmp:
                break
            print('')
            print('Passphrases do not match, please try again.')
    else:
        passphrase = args.passphrase

    ifp, ofp = _open_ios(args)
    text = _read(ifp)
    out = encrypt(passphrase, text, msgdgst=args.msgdgst)
    _write(ofp, out, True)
    _close_ios(ifp, ofp)


# ================================================================
# _rundec
# ================================================================
def _rundec(args):
    '''
    Decrypt data.
    '''
    if args.passphrase is None:
        passphrase = getpass('Passphrase: ')
    else:
        passphrase = args.passphrase

    ifp, ofp = _open_ios(args)
    text = _read(ifp)
    out = decrypt(passphrase, text, msgdgst=args.msgdgst)
    _write(ofp, out, False)
    _close_ios(ifp, ofp)


# ================================================================
# _runtest
# ================================================================
def _runtest(args):
    '''
    Run a series of iteration where each iteration generates a random
    password from 8-32 characters and random text from 20 to 256
    characters. The encrypts and decrypts the random data. It then
    compares the results to make sure that everything works correctly.

    The test output looks like this:

    $ crypt 2000
    2000 of 2000 100.00%  15 139 2000    0
    $ #     ^    ^        ^  ^   ^       ^
    $ #     |    |        |  |   |       +-- num failed
    $ #     |    |        |  |   +---------- num passed
    $ #     |    |        |  +-------------- size of text for a test
    $ #     |    |        +----------------- size of passphrase for a test
    $ #     |    +-------------------------- percent completed
    $ #     +------------------------------- total
    # #+------------------------------------ current test

    @param args  The args parse arguments.
    '''
    import string
    import random
    from random import randint

    # Encrypt/decrypt N random sets of plaintext and passwords.
    num = args.test
    ofp = sys.stdout
    if args.output is not None:
        try:
            ofp = open(args.output, 'w')
        except IOError:
            print('ERROR: can open file for writing: {}'.format(args.output))
            sys.exit(1)

    chset = string.printable
    passed = 0
    failed = []
    maxlen = len(str(num))
    for i in range(num):
        ran1 = randint(8, 32)
        password = ''.join(random.choice(chset) for x in range(ran1))

        ran2 = randint(20, 256)
        plaintext = ''.join(random.choice(chset) for x in range(ran2))

        ciphertext = encrypt(password, plaintext, msgdgst=args.msgdgst)
        verification = decrypt(password, ciphertext, msgdgst=args.msgdgst)

        if plaintext != verification:
            failed.append([password, plaintext])
        else:
            passed += 1

        output = '%*d of %d %6.2f%% %3d %3d %*d %*d %s' % (maxlen, i + 1,
                                                           num,
                                                           100 * (i + 1) / num,
                                                           len(password),
                                                           len(plaintext),
                                                           maxlen, passed,
                                                           maxlen, len(failed),
                                                           args.msgdgst)
        if args.output is None:
            ofp.write('\b' * 80)
            ofp.write(output)
            ofp.flush()
        else:
            ofp.write(output + '\n')

    ofp.write('\n')

    if len(failed):
        for i in range(len(failed)):
            ofp.write('%3d %2d %-34s %3d %s\n' % (i,
                                                  len(failed[i][0]),
                                                  '"' + failed[i][0] + '"',
                                                  len(failed[i][1]),
                                                  '"' + failed[i][1] + '"'))
        ofp.write('\n')

    if args.output is not None:
        ofp.close()


# ================================================================
# _cli_opts
# ================================================================
def _cli_opts():
    '''
    Parse command line options.
    @returns the arguments
    '''
    mepath = os.path.abspath(sys.argv[0]).encode('utf-8')
    mebase = os.path.basename(mepath)

    description = '''
Implements encryption/decryption that is compatible with openssl
AES-256 CBC mode.

You can use it as follows:

    EXAMPLE 1: {0} -> {0} (MD5)
        $ # Encrypt and decrypt using {0}.
        $ echo 'Lorem ipsum dolor sit amet' | \\
            {0} -e -p secret | \\
            {0} -d -p secret
        Lorem ipsum dolor sit amet

    EXAMPLE 2: {0} -> openssl (MD5)
        $ # Encrypt using {0} and decrypt using openssl.
        $ echo 'Lorem ipsum dolor sit amet' | \\
            {0} -e -p secret | \\
            openssl enc -d -aes-256-cbc -md md5 -base64 -salt -pass pass:secret
        Lorem ipsum dolor sit amet

    EXAMPLE 3: openssl -> {0} (MD5)
        $ # Encrypt using openssl and decrypt using {0}
        $ echo 'Lorem ipsum dolor sit amet' | \\
            openssl enc -e -aes-256-cbc -md md5 -base64 -salt -pass pass:secret
            {0} -d -p secret
        Lorem ipsum dolor sit amet

    EXAMPLE 4: openssl -> openssl (MD5)
        $ # Encrypt and decrypt using openssl
        $ echo 'Lorem ipsum dolor sit amet' | \\
            openssl enc -e -aes-256-cbc -md md5 -base64 -salt -pass pass:secret
            openssl enc -d -aes-256-cbc -md md5 -base64 -salt -pass pass:secret
        Lorem ipsum dolor sit amet

    EXAMPLE 5: {0} -> {0} (SHA512)
        $ # Encrypt and decrypt using {0}.
        $ echo 'Lorem ipsum dolor sit amet' | \\
            {0} -e -m sha512 -p secret | \\
            {0} -d -m sha512 -p secret
        Lorem ipsum dolor sit amet

    EXAMPLE 6: {0} -> openssl (SHA512)
        $ # Encrypt using {0} and decrypt using openssl.
        $ echo 'Lorem ipsum dolor sit amet' | \\
            {0} -e -m sha512 -p secret | \\
            openssl enc -d -aes-256-cbc -md sha1=512 -base64 -salt -pass pass:secret
        Lorem ipsum dolor sit amet

    EXAMPLE 7:
        $ # Run internal tests.
        $ {0} -t 2000
        2000 of 2000 100.00%%  21 104 2000    0 md5
        $ #     ^    ^        ^  ^   ^       ^ ^
        $ #     |    |        |  |   |       | +- message digest
        $ #     |    |        |  |   |       +--- num failed
        $ #     |    |        |  |   +----------- num passed
        $ #     |    |        |  +--------------- size of text for a test
        $ #     |    |        +------------------ size of passphrase for a test
        $ #     |    +--------------------------- percent completed
        $ #     +-------------------------------- total
        # #+------------------------------------- current test
'''.format(mebase.decode('ascii', 'ignore'))

    parser = argparse.ArgumentParser(prog=mebase,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=description,
                                     )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--decrypt',
                       action='store_true',
                       help='decryption mode')
    group.add_argument('-e', '--encrypt',
                       action='store_true',
                       help='encryption mode')
    parser.add_argument('-i', '--input',
                        action='store',
                        help='input file, default is stdin')
    parser.add_argument('-m', '--msgdgst',
                        action='store',
                        default='md5',
                        help='message digest (md5, sha, sha1, sha256, sha512), default is md5')
    parser.add_argument('-o', '--output',
                        action='store',
                        help='output file, default is stdout')
    parser.add_argument('-p', '--passphrase',
                        action='store',
                        help='passphrase for encrypt/decrypt operations')
    group.add_argument('-t', '--test',
                       action='store',
                       default=-1,
                       type=int,
                       help='test mode (TEST is an integer)')
    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='the level of verbosity')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s ' + VERSION)

    args = parser.parse_args()
    return args


# ================================================================
# main
# ================================================================
def main():
    args = _cli_opts()
    if args.test > 0:
        if args.input is not None:
            print('WARNING: input argument will be ignored.')
        if args.passphrase is not None:
            print('WARNING: passphrase argument will be ignored.')
        _runtest(args)
    elif args.encrypt:
        _runenc(args)
    elif args.decrypt:
        _rundec(args)


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    main()