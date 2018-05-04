idep
====

'idep' is a set of command line tools to discover
"implemenation dependencies" among c/c++ files. to find these dependencies
helps design a better physical architecture of a project.

== supported compilers
- g++ (4.1.2, 4.2.2)
- ms visual c (7)

== build

=== cmake

to use 'cmake' just:

    % mkdir build
    % cd build
    % cmake ..

and then use your build-tool (make, visualstudio etc)

=== GNU make

if you have 'GNU make', just enter

    % ./configure

in your $SHELL, and after that

    % make


== author(s)

the original author of the code is j. lakos, author of the book "large scale
c++ software design".

i (m. gumz) picked up the code, made it compile again, contacted j. lakos to
choose a license to cover the code (see LICENSE.txt) and put it into a
repository.

the original code is available at:

    ftp://ftp.aw.com/cp/lakos/

you can find the book at amazon or other bookstores as well.

// vim:ft=asciidoc:
