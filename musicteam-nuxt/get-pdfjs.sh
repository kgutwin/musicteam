#!/bin/sh

cd public
curl -L -o pdfjs-5.zip \
     https://github.com/mozilla/pdf.js/releases/download/v5.4.530/pdfjs-5.4.530-legacy-dist.zip

rm -rf pdfjs-5
mkdir pdfjs-5
cd pdfjs-5

unzip ../pdfjs-5.zip
rm ../pdfjs-5.zip
