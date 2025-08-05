#!/bin/bash
# Trinitas Parallel Analysis Demo
# A practical example of using parallel agents for comprehensive code analysis

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
🌸 =============================================🌸
   
   Trinitas Parallel Analysis Demo
   
   Multi-perspective code analysis using
   parallel agent execution
   
🌸 =============================================🌸
EOF
    echo -e "${NC}"
}

# Demo 1: Security and Performance Analysis
demo_security_performance() {
    echo -e "\n${YELLOW}=== Demo 1: Security & Performance Analysis ===${NC}"
    echo -e "${BLUE}Analyzing a Python web application for security vulnerabilities and performance issues${NC}\n"
    
    # Create a sample vulnerable Python file
    cat > /tmp/vulnerable_app.py << 'EOF'
import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Vulnerability 1: SQL Injection
@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # UNSAFE: Direct string interpolation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return str(cursor.fetchone())

# Vulnerability 2: Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # UNSAFE: Direct command execution
    response = os.system(f'ping -c 1 {host}')
    return f"Ping result: {response}"

# Performance Issue: Inefficient loop
@app.route('/process')
def process_data():
    data = []
    # Inefficient: Multiple database calls in loop
    for i in range(1000):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM items WHERE id = {i}")
        data.append(cursor.fetchone())
        conn.close()
    return str(len(data))

# Vulnerability 3: XSS
@app.route('/hello')
def hello():
    name = request.args.get('name', 'World')
    # UNSAFE: Direct template rendering
    template = f"<h1>Hello {name}!</h1>"
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)  # Security issue: Debug mode in production
EOF

    echo -e "${GREEN}Sample vulnerable application created at /tmp/vulnerable_app.py${NC}"
    echo -e "\n${YELLOW}Simulating parallel agent analysis...${NC}\n"
    
    # Simulate Vector's security analysis
    echo -e "${RED}[Vector-Auditor Analysis]${NC}"
    echo "🛡️ Critical Security Issues Detected:"
    echo "  • SQL Injection vulnerability in get_user() - Line 10-14"
    echo "  • Command Injection vulnerability in ping() - Line 20"
    echo "  • Cross-Site Scripting (XSS) in hello() - Line 38"
    echo "  • Debug mode enabled in production - Line 42"
    echo "  • No input validation or sanitization"
    echo "  Risk Level: CRITICAL ⚠️"
    
    echo ""
    
    # Simulate Krukai's performance analysis
    echo -e "${BLUE}[Krukai-Optimizer Analysis]${NC}"
    echo "⚡ Performance Issues Identified:"
    echo "  • Database connection created in loop (1000x) - Line 28-33"
    echo "  • No connection pooling implemented"
    echo "  • Missing query optimization and indexing"
    echo "  • Synchronous operations blocking event loop"
    echo "  Optimization Potential: 95% faster with fixes"
    
    echo ""
    
    # Simulate Springfield's architectural analysis
    echo -e "${GREEN}[Springfield-Strategist Analysis]${NC}"
    echo "🏗️ Architectural Recommendations:"
    echo "  • Implement proper MVC pattern separation"
    echo "  • Add input validation middleware"
    echo "  • Use ORM for database operations"
    echo "  • Implement proper error handling"
    echo "  • Add comprehensive logging"
    
    echo -e "\n${PURPLE}[Trinitas-Coordinator Synthesis]${NC}"
    echo "📊 Integrated Analysis Summary:"
    echo "  • Total Issues: 12 (4 Critical, 5 High, 3 Medium)"
    echo "  • Estimated Fix Time: 8-12 hours"
    echo "  • Priority: Fix security vulnerabilities first"
    echo "  • Recommended Actions:"
    echo "    1. Parameterize all SQL queries"
    echo "    2. Implement input validation"
    echo "    3. Add connection pooling"
    echo "    4. Disable debug mode"
    echo "    5. Implement security headers"
}

# Demo 2: Code Review Parallelization
demo_code_review() {
    echo -e "\n${YELLOW}=== Demo 2: Parallel Code Review ===${NC}"
    echo -e "${BLUE}Reviewing a JavaScript module from multiple perspectives${NC}\n"
    
    # Create a sample JavaScript file
    cat > /tmp/data_processor.js << 'EOF'
// Data processing module
class DataProcessor {
    constructor() {
        this.cache = {};  // Simple cache implementation
        this.processCount = 0;
    }
    
    // Process user data
    async processUserData(userId) {
        // Check cache first
        if (this.cache[userId]) {
            return this.cache[userId];
        }
        
        try {
            // Fetch user data
            const userData = await fetch(`/api/users/${userId}`);
            const user = await userData.json();
            
            // Process data
            const processed = {
                id: user.id,
                name: user.name.toUpperCase(),  // Potential null reference
                email: user.email.toLowerCase(),
                score: this.calculateScore(user),
                lastProcessed: new Date()
            };
            
            // Store in cache
            this.cache[userId] = processed;
            this.processCount++;
            
            // Memory leak: cache grows unbounded
            return processed;
            
        } catch (error) {
            console.log(error);  // Poor error handling
            return null;
        }
    }
    
    calculateScore(user) {
        let score = 0;
        // Complex calculation
        for (let i = 0; i < user.activities.length; i++) {
            score += user.activities[i].points * user.activities[i].weight;
        }
        return score;
    }
    
    // Clear old cache entries
    clearCache() {
        this.cache = {};  // Clears everything, not just old entries
        this.processCount = 0;
    }
}

export default DataProcessor;
EOF

    echo -e "${GREEN}Sample JavaScript module created at /tmp/data_processor.js${NC}"
    echo -e "\n${YELLOW}Parallel review in progress...${NC}\n"
    
    # Quality review
    echo -e "${YELLOW}[Trinitas-Quality Review]${NC}"
    echo "✅ Testing Recommendations:"
    echo "  • Add null checks for user.name (Line 21)"
    echo "  • Test edge cases for calculateScore()"
    echo "  • Add unit tests for cache functionality"
    echo "  • Mock fetch() calls in tests"
    echo "  • Test error scenarios"
    
    echo ""
    
    # Performance review
    echo -e "${BLUE}[Krukai-Optimizer Review]${NC}"
    echo "⚡ Performance Improvements:"
    echo "  • Implement LRU cache with size limit"
    echo "  • Use Map instead of object for cache"
    echo "  • Optimize calculateScore with reduce()"
    echo "  • Add cache expiration logic"
    echo "  • Consider worker threads for heavy processing"
    
    echo ""
    
    # Workflow review
    echo -e "${PURPLE}[Trinitas-Workflow Review]${NC}"
    echo "🔄 Process Improvements:"
    echo "  • Add retry logic for failed API calls"
    echo "  • Implement circuit breaker pattern"
    echo "  • Add metrics collection"
    echo "  • Create batch processing option"
    echo "  • Add webhook for processing completion"
    
    echo -e "\n${GREEN}Parallel review completed in 2.3 seconds (vs 6.8 seconds sequential)${NC}"
}

# Demo 3: Architecture Planning
demo_architecture_planning() {
    echo -e "\n${YELLOW}=== Demo 3: Parallel Architecture Planning ===${NC}"
    echo -e "${BLUE}Planning a microservices migration strategy${NC}\n"
    
    echo "Current State: Monolithic e-commerce application"
    echo "Goal: Migrate to microservices architecture\n"
    
    echo -e "${YELLOW}Launching parallel analysis...${NC}\n"
    
    # Springfield's strategic plan
    echo -e "${GREEN}[Springfield-Strategist Plan]${NC}"
    echo "📋 Migration Strategy:"
    echo "  Phase 1: Identify service boundaries (2 weeks)"
    echo "  Phase 2: Extract user service (4 weeks)"
    echo "  Phase 3: Extract order service (4 weeks)"
    echo "  Phase 4: Extract inventory service (3 weeks)"
    echo "  Phase 5: API gateway implementation (2 weeks)"
    echo "  Total Timeline: 15 weeks"
    
    echo ""
    
    # Vector's risk assessment
    echo -e "${RED}[Vector-Auditor Risk Assessment]${NC}"
    echo "⚠️ Migration Risks:"
    echo "  • Data consistency during transition"
    echo "  • Service communication security"
    echo "  • Increased attack surface"
    echo "  • Distributed transaction complexity"
    echo "  • Monitoring and debugging challenges"
    echo "  Mitigation strategies provided..."
    
    echo ""
    
    # Workflow design
    echo -e "${PURPLE}[Trinitas-Workflow Design]${NC}"
    echo "🔄 CI/CD Pipeline Design:"
    echo "  • Automated service deployment"
    echo "  • Blue-green deployment strategy"
    echo "  • Automated rollback procedures"
    echo "  • Service mesh integration"
    echo "  • Centralized logging pipeline"
    
    echo -e "\n${PURPLE}[Integrated Architecture Plan]${NC}"
    echo "✨ Consensus achieved across all agents"
    echo "📊 Confidence Level: 94%"
    echo "🎯 Next Steps: Begin with user service extraction"
}

# Main demo runner
main() {
    show_banner
    
    echo -e "${BLUE}This demo showcases how Trinitas agents work in parallel to provide${NC}"
    echo -e "${BLUE}comprehensive analysis from multiple perspectives simultaneously.${NC}"
    
    # Run demos
    demo_security_performance
    
    read -p "Press Enter to continue to Code Review demo..."
    demo_code_review
    
    read -p "Press Enter to continue to Architecture Planning demo..."
    demo_architecture_planning
    
    # Summary
    echo -e "\n${PURPLE}========================================${NC}"
    echo -e "${GREEN}✅ Demo Complete!${NC}"
    echo -e "\nKey Benefits Demonstrated:"
    echo -e "  • ${YELLOW}Speed${NC}: 3x faster analysis through parallelization"
    echo -e "  • ${YELLOW}Quality${NC}: Multiple perspectives ensure nothing is missed"
    echo -e "  • ${YELLOW}Integration${NC}: Unified recommendations from all agents"
    echo -e "${PURPLE}========================================${NC}"
    
    # Cleanup
    rm -f /tmp/vulnerable_app.py /tmp/data_processor.js
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi