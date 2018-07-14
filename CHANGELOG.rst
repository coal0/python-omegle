Changelog
=========

1.0.4 (July 14th, 2018)
-----------------------

Added
~~~~~

* Added basic tests for the various chat types.
* Added a 'known issue' on why the typing system may seem to be broken.
* All chat classes now have custom ``.__str__()`` and ``.__repr__()`` methods.

Changed
~~~~~~~

* Various cosmetical changes.
* Expanded type checking to inspect interest types and container length.

Fixed
~~~~~

* Due to an incorrect argument to ``range()``, the random ID was 9 characters
  long, instead of the required 8. Random IDs are now 8 characters long.
* Fixed a bug where the ``.start()`` call would hang indefinitely because of
  an incorrect parameter (a random ID containing illegal characters).
* The ``_AbstractChat`` constructor used to assign the language attribute
  privately, avoiding type and value checks by doing so. The attribute is now
  correctly assigned through the property setter.
* A logical error with the underlying flag system, preventing chat events from
  being handled in a consistent manner, has been fixed.


1.0.3 (July 11th, 2018)
-----------------------

Changed
~~~~~~~

* Improved classifiers, now exclusively Python 3


1.0.2 (June 30th, 2018)
-----------------------

Added
~~~~~

* Added source code
* Added documentation
