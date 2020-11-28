docker build . \
  -t scanlat:latest \
  --build-arg input_file="$1" \
  --build-arg macronized_input="$2"

docker run -p 9000:9000 scanlat
