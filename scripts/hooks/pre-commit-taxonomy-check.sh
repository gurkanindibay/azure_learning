#!/bin/bash
# Pre-commit hook to check taxonomy reference sync
# 
# Installation:
#   cp scripts/hooks/pre-commit-taxonomy-check.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

echo "🔍 Checking taxonomy reference sync..."

# Check if any README.md files in architecture-general are staged
STAGED_READMES=$(git diff --cached --name-only | grep -E "^architecture-general/.*README\.md$")

if [ -n "$STAGED_READMES" ]; then
    echo "📝 Detected changes to README.md files:"
    echo "$STAGED_READMES"
    echo ""
    
    # Run the sync check
    python scripts/sync_taxonomy_reference.py --check
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  Please run 'python scripts/sync_taxonomy_reference.py' to update the taxonomy"
        echo "   Then stage the updated file: git add architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md"
        exit 1
    fi
fi

echo "✅ Taxonomy reference check passed"
exit 0
