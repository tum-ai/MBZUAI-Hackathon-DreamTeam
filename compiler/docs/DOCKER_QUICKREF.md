# Docker Quick Reference

## One-Line Commands

```bash
# Start everything
./compiler/docker-start.sh up

# Generate test template
./compiler/docker-start.sh test

# Select variation 1
./compiler/docker-start.sh select 1

# View logs
./compiler/docker-start.sh logs

# Stop everything
./compiler/docker-start.sh down
```

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | REST API |
| Variation 0 | http://localhost:5173 | Professional preview |
| Variation 1 | http://localhost:5174 | Dark preview |
| Variation 2 | http://localhost:5175 | Minimal preview |
| Variation 3 | http://localhost:5176 | Energetic preview |
| Active | http://localhost:5177 | Editable project ⭐ |

## API Calls

```bash
# Generate variations
curl -X POST http://localhost:8000/generate-template-variations \
  -H 'Content-Type: application/json' -d '{
    "template_type": "product",
    "variables": {...}
  }'

# Select variation
curl -X POST http://localhost:8000/select-template-variation \
  -H 'Content-Type: application/json' -d '{"variation_index": 1}'

# Check active status
curl http://localhost:8000/active-project
```

## Docker Commands

```bash
# Start
docker-compose -f compiler/docker-compose.yml up --build

# Stop
docker-compose -f compiler/docker-compose.yml down

# Logs
docker-compose -f compiler/docker-compose.yml logs -f

# Status
docker-compose -f compiler/docker-compose.yml ps

# Clean
docker-compose -f compiler/docker-compose.yml down -v
```

## Troubleshooting

```bash
# Check if variations exist
docker exec compiler-api ls -la /tmp/selection/

# View API logs
docker logs -f compiler-api

# View variations logs
docker logs -f compiler-variations

# Restart a service
docker-compose -f compiler/docker-compose.yml restart compiler-api

# Rebuild from scratch
docker-compose -f compiler/docker-compose.yml build --no-cache
```

## Files

- `compiler/Dockerfile` - API server image
- `compiler/Dockerfile.variations` - Variations viewer image
- `compiler/docker-compose.yml` - Service orchestration
- `compiler/docker-start.sh` - Convenience script
- `compiler/DOCKER_README.md` - Full documentation
- `compiler/DOCKER_ARCHITECTURE.md` - Architecture diagrams
