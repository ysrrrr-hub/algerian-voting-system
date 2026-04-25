#!/bin/bash
for ep in health stats candidates verify-chain blockchain/status blockchain/all audit-log; do
  echo "--- /api/$ep ---"
  curl -s -w "\nHTTP:%{http_code}\n" "http://localhost:5000/api/$ep" | tail -5
  echo ""
done
