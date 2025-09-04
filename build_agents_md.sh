#!/bin/bash

# This script builds the AGENTS.md file from the source files in the agents_md_sources/ directory.

set -e

SOURCES_DIR="agents_md_sources"
AGENTS_MD="AGENTS.md"

# Check if the sources directory exists
if [ ! -d "$SOURCES_DIR" ]; then
    echo "Error: Directory $SOURCES_DIR not found." >&2
    exit 1
fi

# Create or clear the AGENTS.md file
> "$AGENTS_MD"

# Concatenate the files in order
cat "$SOURCES_DIR/00_header.md" >> "$AGENTS_MD"
cat "$SOURCES_DIR/01_project_overview.md" >> "$AGENTS_MD"
cat "$SOURCES_DIR/02_core_concepts.md" >> "$AGENTS_MD"

# Add the personas section header
echo -e "\n## The Personas\n" >> "$AGENTS_MD"

# Concatenate the persona files
for f in $(ls $SOURCES_DIR/03_personas/*.md | sort); do
    cat "$f" >> "$AGENTS_MD"
    echo -e "\n---\n" >> "$AGENTS_MD"
done

cat "$SOURCES_DIR/04_development_environment.md" >> "$AGENTS_MD"
cat "$SOURCES_DIR/05_how_to_run_tests.md" >> "$AGENTS_MD"
cat "$SOURCES_DIR/06_workflow_and_interaction.md" >> "$AGENTS_MD"
cat "$SOURCES_DIR/07_tool_usage_guide.md" >> "$AGENTS_MD"

echo "Successfully built $AGENTS_MD"
