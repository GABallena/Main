#!/bin/bash

# Read tokens from file
access_token=$(grep 'access_token' ~/.wakatime_tokens | cut -d' ' -f2)
refresh_token=$(grep 'refresh_token' ~/.wakatime_tokens | cut -d' ' -f2)

# Refresh the access token if it's expired
response=$(curl -X POST https://wakatime.com/oauth/token \
    -d "client_id=YOUR_APP_ID" \
    -d "client_secret=YOUR_APP_SECRET" \
    -d "grant_type=refresh_token" \
    -d "refresh_token=$refresh_token")

# Extract new access token and refresh token
access_token=$(echo "$response" | jq -r '.access_token')
refresh_token=$(echo "$response" | jq -r '.refresh_token')

# Save tokens
echo "access_token $access_token" > ~/.wakatime_tokens
echo "refresh_token $refresh_token" >> ~/.wakatime_tokens

echo "New Access Token: $access_token"
