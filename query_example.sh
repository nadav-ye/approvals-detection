curl --location 'http://127.0.0.1:8000/get_approvals' \
--header 'Content-Type: application/json' \
--data '{
    "addresses": ["0x005e20fCf757B55D6E27dEA9BA4f90C0B03ef852"],
    "include_token_price": "true"
}'