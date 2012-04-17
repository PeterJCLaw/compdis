### About

These are scripts & other tooling for interacting with the Student Robotics Competition data store.
The data store itself is an instance of [redis](http://redis.io/),
 the data stored is documented at https://www.studentrobotics.org/trac/wiki/Compd.

### Getting Started

You'll need to install redis & the python bindings.
On Ubuntu, this can be achieved using:

~~~~
$ sudo apt-get install redis-server
$ sudo easy_install redis
~~~~

While the python bindings are available via the debian repos,
 they are very out of date, so using the easy-installed ones instead is required.

Once you've installed redis (and the python bindings),
 you can just go ahead and run the scripts (n the bin folder).

### Tests
There are some automated tests in the `tests/` folder,
 and these are documented in their own README there.
