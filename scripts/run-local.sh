#/usr/bin/env bash


IMAGE_TAG='picnichealth/split-me'

docker run --rm \
    --env FLASK_ENV=development \
    -p 5000:5000 \
    -v "$(pwd)/src:/src" \
    ${IMAGE_TAG}