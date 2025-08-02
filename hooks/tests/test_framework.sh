#!/bin/bash
# Trinitas Test Framework - シンプルで実用的
# Springfield: "テスト駆動開発で、確実な品質を保証しましょうね"
# Krukai: "フン、当然よ。完璧なテストなしに完璧なコードは書けないわ"
# Vector: "……テストがないコードは、脆弱性の温床……"

# Don't use set -e in test framework as we expect some commands to fail
set -uo pipefail

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# テスト統計
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# タイマー
TEST_START_TIME=""
SUITE_START_TIME=$(date +%s)

# テストスイート情報
CURRENT_SUITE=""
CURRENT_TEST=""

# =====================================================
# Core Assertion Functions
# =====================================================

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$expected" == "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Expected: $expected"
        echo -e "  Actual:   $actual"
        return 1
    fi
}

assert_not_equals() {
    local not_expected="$1"
    local actual="$2"
    local message="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$not_expected" != "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Should not equal: $not_expected"
        echo -e "  But got:          $actual"
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$haystack" == *"$needle"* ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Expected to contain: $needle"
        echo -e "  In: $haystack"
        return 1
    fi
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$haystack" != *"$needle"* ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Should not contain: $needle"
        echo -e "  But found in: $haystack"
        return 1
    fi
}

assert_true() {
    local condition="$1"
    local message="${2:-}"
    
    ((TESTS_RUN++))
    
    if eval "$condition"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Condition failed: $condition"
        return 1
    fi
}

assert_false() {
    local condition="$1"
    local message="${2:-}"
    
    ((TESTS_RUN++))
    
    if ! eval "$condition"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Condition should have failed: $condition"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local message="${3:-}"
    
    ((TESTS_RUN++))
    
    if [[ "$expected" -eq "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Expected exit code: $expected"
        echo -e "  Actual exit code:   $actual"
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local message="${2:-File should exist: $file}"
    
    ((TESTS_RUN++))
    
    if [[ -f "$file" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  File not found: $file"
        return 1
    fi
}

assert_file_not_exists() {
    local file="$1"
    local message="${2:-File should not exist: $file}"
    
    ((TESTS_RUN++))
    
    if [[ ! -f "$file" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  File should not exist: $file"
        return 1
    fi
}

assert_dir_exists() {
    local dir="$1"
    local message="${2:-Directory should exist: $dir}"
    
    ((TESTS_RUN++))
    
    if [[ -d "$dir" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message"
        echo -e "  Directory not found: $dir"
        return 1
    fi
}

# =====================================================
# Test Suite Management
# =====================================================

describe() {
    local suite_name="$1"
    CURRENT_SUITE="$suite_name"
    echo
    echo -e "${BLUE}▶ ${suite_name}${NC}"
}

it() {
    local test_name="$1"
    CURRENT_TEST="$test_name"
    TEST_START_TIME=$(date +%s)
    echo -e "  ${MAGENTA}↳${NC} ${test_name}"
}

skip() {
    local reason="${1:-No reason provided}"
    ((TESTS_SKIPPED++))
    echo -e "  ${YELLOW}⚠ SKIPPED:${NC} $reason"
}

# =====================================================
# Setup and Teardown
# =====================================================

# These should be overridden in test files
setup() {
    :  # No-op by default
}

teardown() {
    :  # No-op by default
}

before_each() {
    :  # No-op by default
}

after_each() {
    :  # No-op by default
}

# =====================================================
# Test Runner
# =====================================================

run_test_file() {
    local test_file="$1"
    
    if [[ ! -f "$test_file" ]]; then
        echo -e "${RED}Error: Test file not found: $test_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Running tests in: $(basename "$test_file")${NC}"
    
    # Source the test file in a subshell to isolate tests
    (
        # shellcheck source=/dev/null
        source "$test_file"
        
        # Run setup once
        setup
        
        # Find and run all test functions
        for func in $(declare -F | awk '{print $3}' | grep '^test_'); do
            before_each
            "$func" || true  # Continue even if test fails
            after_each
        done
        
        # Run teardown once
        teardown
    )
}

# =====================================================
# Test Report
# =====================================================

print_summary() {
    local suite_end_time=$(date +%s)
    local suite_duration=$((suite_end_time - SUITE_START_TIME))
    
    echo
    echo "======================================"
    echo -e "${BLUE}Test Summary${NC}"
    echo "======================================"
    echo -e "Total:    $TESTS_RUN"
    echo -e "${GREEN}Passed:   $TESTS_PASSED${NC}"
    echo -e "${RED}Failed:   $TESTS_FAILED${NC}"
    echo -e "${YELLOW}Skipped:  $TESTS_SKIPPED${NC}"
    echo -e "Duration: ${suite_duration}s"
    echo "======================================"
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}TESTS FAILED${NC}"
        return 1
    else
        echo -e "${GREEN}ALL TESTS PASSED${NC}"
        return 0
    fi
}

# =====================================================
# Main Test Runner
# =====================================================

# If sourced, don't run anything
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # If called directly, run tests passed as arguments
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 <test_file> [test_file2 ...]"
        exit 1
    fi
    
    for test_file in "$@"; do
        run_test_file "$test_file"
    done
    
    print_summary
fi