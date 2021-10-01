import os
import subprocess
from datetime import datetime

pjoin = os.path.join

class LogTimer():
    def __init__(self) -> None:
        pass
    def dump_datetime(self, f):
        f.write(f"Job ran on: {datetime.now().strftime('%m-%d-%Y, %H:%M:%S')}\n")

class MD5Hasher():
    '''
    Record the MD5 hash of the file and dump it into a log file called "version.txt"
    '''
    def __init__(self, filename) -> None:
        self.filename = filename
    
    def get_hash(self):
        try:
            cmd = ['md5', self.filename]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = p.communicate()
        except FileNotFoundError:
            cmd = ['md5sum', self.filename]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = p.communicate()
            
        hash = stdout.split()[-1]
        return hash.decode('utf-8')
    
    def write_hash_to_file(self, outtag):
        outdir = f'./output/{outtag}'
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        outfilepath = pjoin(outdir, 'version.txt')
        
        with open(outfilepath, 'w+') as f:
            LogTimer().dump_datetime(f)
            f.write('Tree version: \n')
            f.write(self.get_hash())