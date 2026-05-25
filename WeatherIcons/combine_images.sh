#!/bin/bash

convert BMPsmall/DAY_snow.bmp -resize 50x50 tmp1.bmp
convert tmp1.bmp -background white -gravity northeast -splice 375x10 tmp2.bmp
convert tmp2.bmp -background white -gravity southwest -splice 375x420 tmp3.bmp

convert BMPsmall/Sunrise.bmp -resize 30x30 tmp4.bmp
convert BMPsmall/Sunset.bmp -resize 30x30 tmp5.bmp
convert tmp3.bmp tmp4.bmp -gravity northwest -geometry 30x30+600+4 -composite tmp6.bmp
convert tmp6.bmp tmp5.bmp -gravity northwest -geometry 30x30+600+38 -composite result.bmp
rm tmp?.bmp
