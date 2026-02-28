#!/bin/bash

echo "🚀 Starting Lare Bot..."
echo ""

echo "🗑️  Step 1: Cleaning global commands..."
node src/utils/clearGlobalCommands.js
echo ""

echo "📦 Step 2: Deploying commands..."
node src/utils/deployCommands.js
echo ""

echo "🤖 Step 3: Starting bot..."
node src/bot/bot.js
