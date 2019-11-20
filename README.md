# mysound
Simple sound generation and processing library for Python

# Why
The purpose of tht library is to have a simple to use library
to create and process sound files.

Dedicated langages alredy exists, but I was not 100% satisfied 
with tools like `cmusic` or `nyquist` because they are too much
oriented toward music production (is this real?) and the learning
curve was steep.

Python already have a couple of libraries that somehow overlap
`mysound`. But I was not too keen in requiring huge libraries installation
like `numpy` and `scipy` just to generate  sine wave or extract the
envelope of a sound. Finally, a few other Python sound libraries
alredy exists, but they are more inclined toward playing or recording
sound--something outside of the primary goal of `mysound`

Least, and not last, A great motivation for that project was the
_fun factor_!

# How
I try to follow a gew guidelines while writing `mysound`:

* **imutability** Most importantly, sound are immutable. 
  There is no such thing as in-place trasformations.
* **functionl design** As far as I can, I try to stick a
  a functional approach. Many parts of `mysound` are built
  around higher-order functions rather than OOP paradigme
* **speed is not a problem** Well, this is self explanatory.
  I don't target real time processing nor even _fast_ processing.
  `mymusic` is written 100% in Python based on the assumtion
  it will be fast enougth for the kind of task I need
* **memory is not a problem** Even if I try to not waste memory
  and chase memory leaks, on the other hand, I do not hesitate
  to keep samples--even intermediate proceing result-- in main 
  memory as long as they can still be accessible.
* **one size fits all** Internally, all samples are stored and
  procesed as double floating point numbers.

