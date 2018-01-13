import subprocess
import os
import getpass

class coder2:
    def __init__( self, key ):
        self.key = key.strip()

    def code( self, raw ):
        my_env = os.environ.copy()
        my_env['somerandomkey'] = self.key
        res = subprocess.check_output("echo %s | openssl enc -base64 -e -aes-256-cbc -pass env:somerandomkey" % raw, env=my_env,shell=True, stderr=subprocess.STDOUT)
        res = res.strip().encode("hex").strip()
        return res

    def decode( self, enc ):
        my_env = os.environ.copy()
        my_env['somerandomkey'] = self.key
        res = subprocess.check_output("echo %s | openssl enc -base64 -d -aes-256-cbc -pass env:somerandomkey" % enc.decode("hex").strip(), env=my_env,shell=True, stderr=subprocess.STDOUT)
        return res.strip()

if __name__ == '__main__':
    # Generates encrypted login / password based on a provided encryption key
    key = getpass.getpass('Encryption Key: ').strip()
    passwd=getpass.getpass('Password: ').strip()
    user = getpass.getpass('User name: ').strip()
    
    cfr = coder2(key)
    
    passwd = cfr.code(passwd)
    user = cfr.code(user)
    
    print
    print "PASSWS: ", passwd
    print "USER: ", user
    print
    
    cfr2 = coder2(key)
    passwd = cfr2.decode(passwd)#getpass.getpass()
    user = cfr2.decode(user)
    
    print "PASSWS: ", passwd
    print "USER: ", user
