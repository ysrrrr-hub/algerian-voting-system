#!/bin/bash
curl -s -X POST http://localhost/api/admin/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"Admin@2026"}'
