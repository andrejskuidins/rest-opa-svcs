#!/bin/bash

TOTAL=1000
SUCCESS_CREATE=0
SUCCESS_DELETE=0
FAILED=0

echo "Starting Redis performance test: $TOTAL iterations"
echo "================================================"

START_TIME=$(date +%s)

for i in $(seq 1 $TOTAL); do
  # Create user
  RESPONSE=$(curl -kL -X POST \
    'https://localhost/api/users?user=admin&role=admin' \
    -H 'Content-Type: application/json' \
    -d '{"name": "New User", "email": "user@example.com"}' \
    -s -w "%{http_code}" -o /dev/null)

  if [ "$RESPONSE" == "201" ] || [ "$RESPONSE" == "409" ]; then
    ((SUCCESS_CREATE++))
    echo "✅ Iteration $i: CREATE success with code $RESPONSE"
  else
    ((FAILED++))
    echo "❌ Iteration $i: CREATE failed with code $RESPONSE"
  fi

  sleep 1

  # Delete user
  RESPONSE=$(curl -kL -X DELETE \
    'https://localhost/api/users/New%20User?user=admin&role=admin' \
    -s -w "%{http_code}" -o /dev/null)

  if [ "$RESPONSE" == "200" ]; then
    ((SUCCESS_DELETE++))
    echo "✅ Iteration $i: DELETE success with code $RESPONSE"
  else
    ((FAILED++))
    echo "❌ Iteration $i: DELETE failed with code $RESPONSE"
  fi

  sleep 1

  # Progress indicator
  if [ $((i % 100)) -eq 0 ]; then
    echo "✓ Completed $i/$TOTAL iterations"
  fi
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "================================================"
echo "Performance Test Results"
echo "================================================"
echo "Total iterations: $TOTAL"
echo "Successful CREATEs: $SUCCESS_CREATE"
echo "Successful DELETEs: $SUCCESS_DELETE"
echo "Failed operations: $FAILED"
echo "Total time: ${DURATION}s"
echo "Average time per cycle: $((DURATION / TOTAL))s"