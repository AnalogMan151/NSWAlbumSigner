# NSWAlbumSigner

Author: AnalogMan

Modified Date: 2019-12-03

Purpose: Signs JPG files for use with Nintendo Switch Album app

Usage: `NSWAlbumSigner.py [-h] [-t TITLEID] [-d DATE] file [file ...]`

Requirements: Pillow, piexif, pycypto (`pip3 install Pillow piexif pycrypto`)

Credits: 
- David Buchanan (https://github.com/DavidBuchanan314) for the 
    example on decrypting/encrypting the title ID for screen shots & the jpg-sign base code
- cheuble (https://github.com/cheuble) for NSScreenshotMaker, from where many of these functions
    come from (license included below).
- ZW Cai (https://github.com/x43x61x69) for the motivation to do this since they never fixed
    their nxcapsrv application.
    
> Copyright (c) 2018 cheuble
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  
> 
> The above copyright notice and this permission notice shall be included in  
all copies or substantial portions of the Software. 
