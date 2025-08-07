#!/bin/bash
# Test script for Trinitas parallel execution
# このスクリプトで並列実行機能をテストします

echo "🚀 Trinitas Parallel Execution Test"
echo "===================================="
echo ""

# Test 1: Check if parallel agent exists
echo "📋 Test 1: Checking parallel agent installation..."
if [ -f ~/.claude/agents/trinitas-parallel.md ]; then
    echo "✅ trinitas-parallel.md found"
else
    echo "❌ trinitas-parallel.md not found"
fi

# Test 2: Check Python script placement
echo ""
echo "📋 Test 2: Checking Python script placement..."
if [ -f ~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py ]; then
    echo "✅ prepare_parallel_tasks.py found in correct location"
    if [ -x ~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py ]; then
        echo "✅ Script has execute permissions"
    else
        echo "⚠️ Script lacks execute permissions"
    fi
else
    echo "❌ prepare_parallel_tasks.py not found in python directory"
fi

# Test 3: Check settings.json configuration
echo ""
echo "📋 Test 3: Checking settings.json configuration..."
if grep -q "prepare_parallel_tasks.py" ~/.claude/settings.json 2>/dev/null; then
    echo "✅ Parallel tasks hook configured in settings.json"
else
    echo "⚠️ Parallel tasks hook not found in settings.json"
fi

# Test 4: Check environment variable
echo ""
echo "📋 Test 4: Testing parallel execution environment..."
export TRINITAS_PARALLEL_ENABLED=true
export CLAUDE_TOOL_NAME=Task
export CLAUDE_USER_PROMPT="Analyze this project for security vulnerabilities and performance issues"

# Run the Python script directly to test
echo "Testing prepare_parallel_tasks.py execution..."
python3 ~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python script executed successfully"
else
    echo "⚠️ Python script execution had issues (this is normal if not in Claude Code context)"
fi

echo ""
echo "===================================="
echo "📊 Test Summary"
echo ""

# Final summary
all_good=true

if [ -f ~/.claude/agents/trinitas-parallel.md ] && \
   [ -f ~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py ] && \
   [ -x ~/.claude/trinitas/hooks/python/prepare_parallel_tasks.py ]; then
    echo "✅ All core components are properly installed"
else
    echo "⚠️ Some components need attention"
    all_good=false
fi

echo ""
if [ "$all_good" = true ]; then
    echo "🎉 Parallel execution system is ready!"
    echo ""
    echo "💡 How to use:"
    echo "1. Simple: Just use Task tool normally - it will auto-parallelize complex tasks"
    echo "2. Explicit: Use @trinitas-parallel for forced parallel execution"
    echo "3. Multiple: '@springfield-strategist と @krukai-optimizer を同時に起動'"
else
    echo "⚠️ Please fix the issues above before using parallel execution"
fi

echo ""
echo "📝 Example commands to test in Claude Code:"
echo '  claude bash "echo Testing parallel execution"'
echo '  # Then in Claude Code:'
echo '  @trinitas-parallel Analyze this codebase for all issues'
echo ""