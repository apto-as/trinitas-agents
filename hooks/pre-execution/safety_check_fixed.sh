#!/bin/bash
# Trinitas Pre-execution Safety Check Hook (Fixed Version)
# Compliant with Claude Code Hooks Specification

# Read JSON input from stdin
INPUT=$(cat)

# Parse tool name and arguments using jq or basic parsing
TOOL_NAME=$(echo "$INPUT" | grep -o '"tool"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"tool"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
TOOL_ARGS=$(echo "$INPUT" | grep -o '"arguments"[[:space:]]*:[[:space:]]*{[^}]*}')

# Safety check function
is_dangerous() {
    local tool="$1"
    local args="$2"
    
    # Check for dangerous Bash commands
    if [[ "$tool" == "Bash" ]]; then
        # Check for dangerous patterns
        if echo "$args" | grep -qE "rm -rf /|sudo|mkfs|dd.*of=/dev/"; then
            return 0  # Dangerous
        fi
    fi
    
    return 1  # Safe
}

# Main logic
if is_dangerous "$TOOL_NAME" "$TOOL_ARGS"; then
    # Block the operation (Claude Code spec compliant)
    cat <<EOF
{
  "continue": false,
  "error": "Operation blocked for safety reasons",
  "context": "This operation was deemed potentially dangerous and has been blocked.",
  "systemMessage": "⚠️ Safety check failed: The requested operation has been blocked to prevent potential system damage."
}
EOF
    exit 0  # Exit 0 with JSON response to block
else
    # Allow the operation
    cat <<EOF
{
  "continue": true
}
EOF
    exit 0  # Exit 0 to continue
fi