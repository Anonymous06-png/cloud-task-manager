# Legacy Node.js Implementation

**Status**: INACTIVE REFERENCE MATERIAL

This directory contains the original Node.js/Express implementation that was created before pivoting to the Django stack.

## Contents

- `backend/` - Node.js Express API source
  - `server.js` - Main Express server
  - `auth.js` - JWT authentication
  - `db.js` - PostgreSQL connection pool
  - `tasks.js` - Task CRUD router
  - `package.json` - Dependencies
- `Dockerfile.node` - Node.js container image
- `docker-compose.node.yml` - Docker Compose with Node.js

## Why Preserved

This code serves as a reference for:
- Database schema design
- API endpoint structure
- Validation logic
- Authentication flow

## DO NOT USE

- Do not run `npm install` or execute this code
- Do not include in active Docker builds
- The active implementation uses Django

**Archived**: 2026-10-17
