# csdb-leech

A script to leech file from CSDb.

Basic use is to first find the ID for a group and then leech files from the group:
~~~
compyx@debian:~/projects/csdb-leech$ ./csdb-leech.py -g focus
 3260 Focus (Canada)
  135 Focus (Netherlands)
~~~

Obviously we want the Dutch demo group with ID 135.
So we use:
~~~
compyx@debian:~/projects/csdb-leech$ ./csdb-leech.py -r 135
~~~
Which will download all files for each release of 'Focus'
