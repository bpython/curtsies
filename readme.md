"""Marked up text

text should only be marked up with characteristics that don't change the number
of characters (uppercase is fine - spaces between characters is not)

Ideally these objects can be processed like normal strings

Limited to 

Use something like colorama for Windows output? Skip for now

Similar to https://github.com/kennethreitz/clint/blob/master/clint/textui/colored.py

str: printable (and marked up) text in terminal - minimal amount of markup?
repl: representation of tree structure
getitem: array and farray representation
len: length of version
iteration?

Buildable from escape codes
Buildable from array and farry
Buildable from simple init
Buildable by combining into tree structure

which is the true internal representation?
Probably the array one, can build a tree for repr with cool tree combinators!
No, probably the terminal escape one


What to do on unclosed (uncleared) escape code input?
Close it! Shouldn't be called on just an initial section!
"""








