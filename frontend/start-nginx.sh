#!/bin/sh

pwd;
cp /usr/share/nginx/main.*.js .;
for f in main.*.js; do envsubst '$NC2ZARR_BACKEND_URL,$NC2ZARR_CONTENT_URL' < $f | sponge $f; done
nginx -g daemon off;
