This is a set of automated tests for compdis.
Currently, it relies upon the [compd_test repo](https://github.com/PeterJCLaw/compd_test) to be run.

#### Manual testing of bin/scores:
~~~~~
$ compd_test/delall.py && compd_test/matchmaker.py && bin/scores < test/data/scores/$TEST$
~~~~~
This will run the bin/scores script with the inputs taken from the file test/data/scores/$TEST$.
The available tests are:

 * forwards: tokens in zone = zone + 1
 * backwards: tokens in zone = 4 - zone
 * tie: first two - 4 in zone, second two - 2 in zone

#### Automated testing of (some) of the scores functions:
~~~~~
$ python test/test-scores.py
~~~~~
This is a pyUnit test suite for a subset of the functionality in the scores script.
