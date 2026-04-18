# strings in python are unicode code points
# ord() returns unicode code point of a character
# ord() cant return unicode code point of a string
# thats why we create a list
x = ord('h')
print(x)
y = "Hello everyone! 2 + 2 = 4 capish?"
print([ord(c) for c in y]) # []-> list
