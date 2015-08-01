Permit
==============
  
## Introduction
To make a short story shorter, I discovered [Quickly](https://wiki.ubuntu.com/Quickly) on 07/25/2015 
and thought, 'That looks interesting...'

Which brings us to the present moment. I wanted to write something utilizing Quickly but it had to be simple because:
 
- I don't know GTK
- Its been 20+ years since I worked with Python. 
- The project had to be something useful, otherwise, what's the point?
 
## Introducing Permit
Permit is a GUI interface for Linux **chmod**. It permits (pun intended ?) the user to play with Linux permissions 
without affecting any particular file and/or it permits the user to physically modify the file permissions of a 
selected file/directory.

Please note: I make no apologies for implementing GTK and/or Python inefficiently or incorrectly. I had to start 
somewhere and the program works, as it is, for me.

## ToDo
- ~~Prevent non-Octal values from being entered in the Octal Permissions textbox~~
- ~~Prevent invalid characters (i.e. **not** -, d, r, w, x) from being entered in the Symbolic Permissions textbox~~
- ~~Detect directory for the Symbolic Permissions textbox~~
- ~~Display owner and group names of the loaded file/directory~~
- Enable file dialog to return directory instead of opening the directory _(this might only be possible with GTK+ 3)_
- ~~Refactor switch code~~
- ~~~Prevent user from doing a chmod 000 to himself!~~~

## Implementation Notes
Permit is known to run with:

- Ubuntu Linux v15.04
- Python v2.7.9
- GTK+ v2.24.27

## Using Permit
```bash
python /<INSTALL_PATH>/bin/permit.pyc
```
or
```bash
/<INSTALL_PATH>/bin/permit.pyc
```

Enjoy!