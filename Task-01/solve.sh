    #!/bin/bash

    if [ -z "$1" ]; then
      echo "Usage: $0 <base64_string>"
      exit 1
    fi

    encoded_string="$1"

    decoded_string=$(echo "$encoded_string" | base64 --decode)

    echo "Decoded string: $decoded_string"
