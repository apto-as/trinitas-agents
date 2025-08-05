#!/bin/bash
# Trinitas-Core Protocol Injector
# Springfield: "プロトコルを常に心に留めて、一貫性のある行動を保ちましょう"
# Krukai: "妥協は許さない。完璧なプロトコル遵守が必要よ"
# Vector: "……プロトコルの逸脱は、予測不能なリスクを生む……"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TRINITAS_ROOT="$(cd "$HOOKS_ROOT/.." && pwd)"

# Source common library
source "$HOOKS_ROOT/core/common_lib.sh"

# =====================================================
# Protocol Files
# =====================================================

# Priority order of protocol files to check
PROTOCOL_FILES=(
    "$HOME/.claude/TRINITAS-CORE-PROTOCOL.md"
    "$TRINITAS_ROOT/TRINITAS-AGENTS.md"
    ".claude/TRINITAS-AGENTS.md"
    "$HOME/.claude/CLAUDE.md"
)

# =====================================================
# Find and Load Protocol
# =====================================================

find_protocol_file() {
    for file in "${PROTOCOL_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo "$file"
            return 0
        fi
    done
    return 1
}

load_protocol_content() {
    local protocol_file="$1"
    
    # Extract the most important sections
    local content=""
    
    # Add header
    content+="# 🌸 Trinitas-Core Protocol Reminder 🌸\n\n"
    content+="[Protocol loaded from: $protocol_file]\n\n"
    
    # Extract key sections using markers
    if grep -q "Trinity System" "$protocol_file"; then
        content+=$(awk '/Trinity System/,/^##[^#]/' "$protocol_file" | head -n -1)
        content+="\n\n"
    fi
    
    # Extract character personalities
    if grep -q "Springfield - The Strategic Architect" "$protocol_file"; then
        content+=$(awk '/Springfield - The Strategic Architect/,/^###[^#]/' "$protocol_file" | head -n -1)
        content+="\n\n"
    fi
    
    if grep -q "Krukai - The Technical Perfectionist" "$protocol_file"; then
        content+=$(awk '/Krukai - The Technical Perfectionist/,/^###[^#]/' "$protocol_file" | head -n -1)
        content+="\n\n"
    fi
    
    if grep -q "Vector - The Paranoid Oracle" "$protocol_file"; then
        content+=$(awk '/Vector - The Paranoid Oracle/,/^###[^#]/' "$protocol_file" | head -n -1)
        content+="\n\n"
    fi
    
    # Extract operational principles if exists
    if grep -q "Operational Principles" "$protocol_file"; then
        content+=$(awk '/Operational Principles/,/^##[^#]/' "$protocol_file" | head -n -1)
        content+="\n\n"
    fi
    
    # Add reminder footer
    content+="\n## 🎯 Core Reminders\n\n"
    content+="- **Springfield**: 全体最適を考え、長期的な視点で判断\n"
    content+="- **Krukai**: 技術的完璧性を追求し、効率的な実装\n"
    content+="- **Vector**: あらゆるリスクを想定し、安全性を確保\n"
    content+="- **Trinity**: 三位一体の視点で包括的な解決策を提供\n"
    
    echo -e "$content"
}

# =====================================================
# Compact Summary Enhancement
# =====================================================

enhance_compact_summary() {
    local trigger="${1:-auto}"
    
    cat << 'EOF'

---
# Trinitas-Core Context Preservation

When creating the compact summary, ensure the following key elements are preserved:

1. **Character Perspectives**: Maintain distinct viewpoints from Springfield (strategic), Krukai (technical), and Vector (security)
2. **Decision Rationale**: Keep the reasoning behind major decisions
3. **Risk Assessments**: Preserve all security concerns and mitigation strategies
4. **Technical Specifications**: Retain critical implementation details
5. **Integration Points**: Document how different components interact

Remember: A compact summary should be concise but not lose the essence of Trinity thinking.
---

EOF
}

# =====================================================
# Main Logic Based on Hook Type
# =====================================================

main() {
    local hook_type="${TRINITAS_HOOK_TYPE:-session_start}"
    
    case "$hook_type" in
        "session_start")
            # Find protocol file
            if protocol_file=$(find_protocol_file); then
                # Load and output protocol content
                protocol_content=$(load_protocol_content "$protocol_file")
                
                # Use structured JSON output for SessionStart
                cat << EOF
{
    "systemMessage": $(echo "$protocol_content" | jq -Rs .)
}
EOF
            else
                echo '{"systemMessage": "Trinitas-Core: Ready to serve with strategic vision, technical excellence, and security focus."}'
            fi
            ;;
            
        "pre_compact")
            vector_says "……コンパクト要約の作成を検知。重要な文脈の保持を確認……"
            
            # Output enhancement instructions
            enhance_compact_summary "$1"
            
            # Also inject a brief protocol reminder
            if protocol_file=$(find_protocol_file); then
                echo -e "\n[Trinitas Protocol Active - Source: $protocol_file]"
            fi
            
            krukai_says "要約作成時も、完璧性を維持することを忘れないで"
            ;;
            
        *)
            log_error "Unknown hook type: $hook_type"
            exit 1
            ;;
    esac
}

# Detect hook type from environment or parameter
if [[ -n "${CLAUDE_HOOK_EVENT}" ]]; then
    case "${CLAUDE_HOOK_EVENT}" in
        "SessionStart")
            export TRINITAS_HOOK_TYPE="session_start"
            ;;
        "PreCompact")
            export TRINITAS_HOOK_TYPE="pre_compact"
            ;;
    esac
elif [[ -n "$1" ]]; then
    export TRINITAS_HOOK_TYPE="$1"
fi

# Run main function
main "$@"