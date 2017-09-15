#! /usr/bin/env python

import os
import pathlib

PWD = pathlib.Path(__file__).parent.resolve()

def ensure_db():
    db_file = PWD.joinpath('db.sqlite3')
    if not db_file.is_file():
        cmd = 'python manage.py migrate'
        print(cmd)
        os.system(cmd)

def ensure_daq_root():
    if not os.path.isdir('/daqroot'):
        msg = (
            '\n\nThere is not /daqroot directory.  Run the following command:\n'
            'ln -s /path/to/link/as/root /daqroot\n'
            '\n\nNote that you might have to use sudo to get it to work properly.\n'
            'If so, then you might need to change owners using the chown command\n\n'
        )
        print(msg)

ensure_db()
ensure_daq_root()


