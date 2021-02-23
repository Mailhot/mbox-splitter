# -*- coding: utf-8 -*-

import sys
from os.path import exists
import os

# You may set the read_chunk_size manually if required, this worked for me.
read_chunk_size = 5


if len(sys.argv) != 3:
    print()
    print('Usage: `python mbox-splitter.py filename.mbox size`')
    print('         where `size` is a positive integer in Mb')
    print()
    print('Example: `python mbox-splitter.py inbox_test.mbox 50`')
    print('         where inbox_test.mbox size is about 125 Mb')
    print()
    print('Result:')
    print('Created file `inbox_test_1.mbox`, size=43Mb, messages=35')
    print('Created file `inbox_test_2.mbox`, size=44Mb, messages=2')
    print('Created file `inbox_test_3.mbox`, size=30Mb, messages=73')
    print('Done')
    exit()

filename = sys.argv[1]
if not exists(filename):
    print('File `{}` does not exist.'.format(filename))
    exit()

try:
    split_size = int(sys.argv[2])*1024*1024
except ValueError:
    print('Size must be a positive number')
    exit()

if split_size < 1:
    print('Size must be a positive number')
    exit()

if os.stat(filename).st_size == 0:
    print('Email messages in `{}` not found.'.format(filename))
    exit()

chunk_count = 1
output = filename.replace('.mbox', '_' + str(chunk_count) + '.mbox')
if exists(output):
    print('The file `{}` has already been splitted. Delete chunks to continue.'.format(filename))
    exit()

print('Splitting `{}` into chunks of {}Mb ...\n'.format(filename, sys.argv[2]))

# of = mailbox.mbox(path=output, create=True)

def create_write_file(filename, chunk_count ):
    output_filename_chunk = filename.replace('.mbox', '_' + str(chunk_count) + '.mbox')
    of = open(output_filename_chunk, 'wb')
    return of

def read_in_chunks(file_object, chunk_size_mb=1):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size_mb*1024*1024)
        if not data:
            break
        yield data


mc = 0
of = create_write_file(filename, chunk_count)
total_size = 0

with open(filename,'rb') as original_file:

    for chunk in read_in_chunks(file_object=original_file, chunk_size_mb=read_chunk_size):
        messages = chunk.split(b'\nFrom ')

        if len(messages) > 1:
            i = 0
            for message in messages:
                if i > 0:
                    messages[i] = b'From ' + message
                i += 1

        messages[:] = [x for x in messages if x] # this one remove empty string from the list (if a split happens at benining)

        k = 0
        for message in messages:

            # try:
            #     print(line.decode(encoding='UTF-8'))
            # except UnicodeEncodeError, ValueError:
            #     print('Cant decode string on string #%s' str(mc))
            print('File# %s - Message# %s' %(chunk_count, mc))

            message_size = len(message)
            if total_size + message_size >= split_size and k != 0: # k = 0 so we do not change file between read chunks so that we have full messages all the time.

                of.flush()
                of.close()
                chunk_count += 1
                print('Created file `{}`, size={}Mb, messages={}.'.format(output, total_size/1024/1024, mc))
                total_size = 0
                of = create_write_file(filename, chunk_count)
                mc = 0


            mc += 1
            k += 1


            of.write(message) 
            total_size += message_size

print('Created file `{}`, size={}Mb, messages={}.'.format(output, total_size/1024/1024, mc))
of.flush()
of.close()
print('\nDone')
