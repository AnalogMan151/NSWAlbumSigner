#!/usr/bin/env python3
# Author: AnalogMan
# Modified Date: 2019-12-03
# Purpose: Signs JPG files for use with Nintendo Switch Album app
# Usage: NSWAlbumSigner.py [-h] [-t TITLEID] [-d DATE] file [file ...]
# Requirements: Pillow, piexif, pycypto (pip3 install Pillow piexif pycrypto)

# Credits: 
# - David Buchanan (https://github.com/DavidBuchanan314) for the 
#     example on decrypting/encrypting the title ID for screen shots & the jpg-sign base code
# - cheuble (https://github.com/cheuble) for NSScreenshotMaker, from where many of these functions
#     come from (license included below).
# - ZW Cai (https://github.com/x43x61x69) for the motivation to do this since they never fixed
#     their nxcapsrv application.



# Copyright (c) 2018 cheuble

# Permission is hereby granted, free of charge, to any person obtaining a copy  
# of this software and associated documentation files (the "Software"), to deal  
# in the Software without restriction, including without limitation the rights  
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
# copies of the Software, and to permit persons to whom the Software is  
# furnished to do so, subject to the following conditions:  

# The above copyright notice and this permission notice shall be included in  
# all copies or substantial portions of the Software. 


from sys import version_info
if version_info <= (3,2,0):
    print('\nPython version 3.2.0+ needed to run this script.')
    exit(1)

import os
import io
import hmac
import argparse
from hashlib import sha256
from datetime import datetime, timedelta

try: 
    import piexif # pip3 install piexif
    from PIL import Image # pip3 import Pillow
    from Crypto.Cipher import AES # pip3 install pycrypto
except:
    print('\nDependancies missing:\npip3 install piexif Pillow pycrypto\n')
    exit(1)

# Thumbnail fix
piexif._dump._get_thumbnail = lambda jpeg: jpeg

# https://www.google.com/search?q=%22Nintendo+Switch+capsrv+screenshot+HMAC+secret%22
hmac_secret = bytes.fromhex('REAPLCE ME WITH CAPSRV HAMC SECRET KEY')

# https://www.google.com/search?q=%22mysterious+RNG+seeds%22
captureID_key = bytes.fromhex('REPLACE ME WITH CAPTUREID KEY')

# Home menu captureID if no custom titleID is supplied
titleID_default = '0100000000001000'

date = datetime.now()

# Load an arbitrary image file, scale it, and return jpeg bytes
def resizeImage(path, sizeX, sizeY):
    size = (sizeX, sizeY)
    resizedImage  = Image.new('RGB', size, (0, 0, 0))
    image1 = Image.open(path).convert('RGB')
    image1.thumbnail(size)
    width1, height1 = image1.size
    resizedImage.paste(image1, (int((sizeX - width1) / 2), int((sizeY - height1) / 2)))
    return resizedImage

# Build custom EXIF data to pass Switch validation
def createJPEGExif(exifDict, makerNote, timestamp, thumbnail):
    newExifDict = exifDict.copy()
    newExifDict.update({
        'Exif': {36864: b'0230', 37121: b'\x01\x02\x03\x00', 40962: 1280, 40963: 720, 40960: b'0100', 40961: 1, 37500: makerNote},
        '0th':  {274: 1, 531: 1, 296: 2, 34665: 164, 282: (72, 1), 283: (72, 1), 306: timestamp, 271: 'Nintendo co., ltd'},
        '1st':  {513: 1524, 514: 32253, 259: 6, 296: 2, 282: (72, 1), 283: (72, 1)},
        'thumbnail': thumbnail
        })
    return newExifDict

# Create MAC for image using Switch hmac key
def getImageHmac(input):
    return hmac.new(hmac_secret, input, sha256).digest()

# Create directories, process supplied image, write output
def processFile(fileName, captureID):
    global date
    outputFolder = date.strftime('./Nintendo/Album/%Y/%m/%d/')
    ind = 0
    # increase index for images with same time stamp
    while os.path.isfile(outputFolder + date.strftime('%Y%m%d%H%M%S') + '{:02d}'.format(ind) + '-' + captureID + '.jpg'):
        ind += 1
        if ind > 99:
            date += timedelta(0,-1)
            outputFolder = date.strftime('./Nintendo/Album/%Y/%m/%d/')
            ind = 0
    outputPath = outputFolder + date.strftime('%Y%m%d%H%M%S') + '{:02d}'.format(ind) + '-' + captureID + '.jpg'
    os.makedirs(outputFolder, exist_ok=True)
    inputImage  = io.BytesIO()
    outputImage = io.BytesIO()
    thumbnail   = io.BytesIO()

    # Resize image (1280x720) and create thumbnail image
    resizeImage(fileName, 1280, 720).save(inputImage, 'JPEG', quality = 80) #The screenshots must have a size of 1280x720
    resizeImage(fileName, 320,  180).save(thumbnail,  'JPEG', quality = 40)  #The thumbnails (at least on my screenshots) have a size of 320x180
    
    # Create valid EXIF data
    timestamp = date.strftime('%Y:%m:%d %H:%M:%S')
    makerNoteZero  = b'\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10\x00' + bytes.fromhex(captureID)
    exifData = piexif.dump(createJPEGExif(piexif.load(inputImage.getvalue()), makerNoteZero, timestamp, thumbnail.getvalue()))
    piexif.insert(exifData, inputImage.getvalue(), outputImage)
    makerNote  = b'\x00\x00\x00\x00\x00\x00\x10\x00' + getImageHmac(outputImage.getvalue())[:16] + b'\x01\x00\x10\x00' + bytes.fromhex(captureID)
    outputBytes = outputImage.getvalue().replace(makerNoteZero, makerNote)
    
    # Write file
    with open(outputPath, 'wb') as file:
        file.write(outputBytes)
    date += timedelta(0,-1)

def main():
    global date

    print('\n======== NSW Album Signer ========\n\n')

    # Arg parser for program options
    parser = argparse.ArgumentParser(description='Sign JPG files for use with Nintendo Switch Album')
    parser.add_argument('file', help='Path to JPG file(s)', type=argparse.FileType('rb'), nargs='+')
    parser.add_argument('-t', '--titleid', help='Optional Title ID of game for sorting images in Album applet')
    parser.add_argument('-d', '--date', help='Optional start date (YYYYMMDDHHMMSS) for image timestamp. Affects order of images in Album applet')
    
    # Check passed arguments
    args = parser.parse_args()

    # Convert TitleID to CaptureID
    if args.titleid:
        titleID_str = '0'*16+args.titleid
    else:
        titleID_str = '0'*16+titleID_default
    if len(titleID_str) != 32:
        print('TitleID invalid length')
        return 1
    titleID = bytes.fromhex(titleID_str)
    cipher = AES.new(captureID_key, AES.MODE_ECB)
    captureID = cipher.encrypt(titleID[::-1]).hex().upper()
    
    # Convert & validate datetime string
    if args.date:
        if len(args.date) != 14:
            print('Invalid datetime format: YYYYMMDDHHMMSS')
            return 1
        date = datetime.strptime(args.date, '%Y%m%d%H%M%S')
    
    # Process file(s)
    success = 0
    fail = 0
    for filepath in args.file:
        try:
            processFile(filepath, captureID)
            success += 1
            print('Successfully signed: {}'.format(os.path.basename(filepath.name)))
        except:
            print('Failed to sign: {}'.format(os.path.basename(filepath.name)))
            fail += 1
    print('\nProcess completed.\n\nSuccessful: {}\nFailed: {}'.format(success, fail))

if __name__ == '__main__':
    main()
