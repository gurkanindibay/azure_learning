#!/bin/bash
file="$1"
echo "## Table of Contents"
grep -E '^#{1,6}' "$file" | while read -r line; do
  level=$(echo "$line" | sed 's/\(#{1,6}\).*/\1/' | wc -c)
  level=$((level - 1))
  title=$(echo "$line" | sed 's/^#\+ //')
  slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 -]//g' | sed 's/ /-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//')
  indent=""
  for ((i=2; i<=level; i++)); do
    indent="$indent  "
  done
  echo "$indent- [$title](#$slug)"
done
