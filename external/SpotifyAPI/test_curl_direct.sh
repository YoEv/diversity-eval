#!/bin/bash

echo "🎵 直接curl测试Spotify API"
echo "================================"

# 从配置文件读取client_id和client_secret
CLIENT_ID="c03779e9cb214e8994c3adff6b58954c"
CLIENT_SECRET="5a547dec11be4e6aaaacc13493157f14"

echo "🔑 获取访问令牌..."

# 获取访问令牌
TOKEN_RESPONSE=$(curl -s -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}")

echo "令牌响应: $TOKEN_RESPONSE"

# 提取访问令牌
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ 无法获取访问令牌"
    exit 1
fi

echo "✅ 成功获取访问令牌: ${ACCESS_TOKEN:0:20}..."

echo ""
echo "🌐 测试API端点..."

# 测试你提供的歌曲ID
TRACK_IDS="7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B"

echo "📊 测试获取歌曲信息 (市场: ES)..."
curl -s --request GET \
  --url "https://api.spotify.com/v1/tracks?market=es&ids=${TRACK_IDS}" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'

echo ""
echo "📊 测试获取歌曲信息 (市场: US)..."
curl -s --request GET \
  --url "https://api.spotify.com/v1/tracks?market=us&ids=${TRACK_IDS}" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.'

echo ""
echo "🔍 测试搜索API..."
curl -s --request GET \
  --url "https://api.spotify.com/v1/search?q=despacito&type=track&market=us&limit=5" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}" | jq '.tracks.items[] | {name: .name, artists: [.artists[].name], preview_url: .preview_url}'