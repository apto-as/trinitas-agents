#!/bin/bash

# テスト用のWave入力
wave_input='{
    "strategy": "adaptive",
    "workflow": {
        "name": "Research and Analysis Workflow",
        "steps": [
            {
                "id": "research_1",
                "name": "Research Architecture",
                "persona": "springfield",
                "estimated_tokens": 2000,
                "dependencies": []
            },
            {
                "id": "analyze_1", 
                "name": "Analyze Architecture",
                "persona": "springfield",
                "estimated_tokens": 3000,
                "dependencies": ["research_1"]
            }
        ],
        "validation_rules": {
            "quality_threshold": 0.8,
            "security_check": true
        }
    }
}'

echo "Wave input:"
echo "$wave_input"
echo
echo "Wave result:"
echo "$wave_input" | python3 hooks/python/wave_orchestrator.py
echo
echo "Exit code: $?"