#!/bin/bash

# Fetch WakaTime API key from ~/.wakatime.cfg
echo "Fetching WakaTime API key..."
api_key=$(grep 'api_key' ~/.wakatime.cfg | cut -d' ' -f3)

# Debugging: Echo the fetched API key
echo "API Key: $api_key"

# Check if API key is present
if [ -z "$api_key" ]; then
    echo "Error: API key not found!"
    exit 1
else
    echo "API key found!"
fi

# Base64 encode the API key for Basic Authentication
encoded_key=$(echo -n "$api_key" | base64)

# Perform API request to WakaTime using Basic Auth
echo "Performing API request to WakaTime..."
wakatime_stats=$(curl -s -H "Authorization: Basic $encoded_key" https://wakatime.com/api/v1/users/current/heartbeats)

# Check if the response contains an error
if echo "$wakatime_stats" | grep -q '"error"'; then
    echo "Error in API response: $wakatime_stats"
    exit 1
else
    echo "API response received!"
fi

# Save the raw API response to a text file
echo "Outputting raw API response to rawAPI.txt..."
echo "$wakatime_stats" > rawAPI.txt
echo "Raw API response successfully saved to rawAPI.txt."

# Extract coding time
echo "Attempting to parse API response..."
coding_time=$(echo $wakatime_stats | jq -r '.data[0].grand_total.text')

# Check if coding time was successfully parsed
if [ -z "$coding_time" ]; then
    echo "Error: Failed to extract coding time!"
else
    echo "Successfully extracted coding time!"
    echo "Coding time today: $coding_time"
fi

echo "Script finished."
