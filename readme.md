# Door Calculator API

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Build and run the container
docker-compose up --build

# Run in detached mode
docker-compose up -d --build
```

### Using Docker directly
```bash
# Build the image
docker build -t door-calculator .

# Run the container
docker run -p 8000:8000 door-calculator
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## API Usage

The API will be available at `http://localhost:8000`

### Endpoints

- `GET /` - Root endpoint
- `POST /calculate` - Main calculation endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Example Requests

#### Test with your first sample data:
```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "general": {
      "Door Type": "Personnel Smartform",
      "Door Infill": "Honeycomb",
      "Fire Rating": "None"
    },
    "job": {
      "customer": "AAES",
      "job_no": "T6099",
      "door_no": "D01 LH",
      "qty": "16",
      "revision": "1"
    },
    "so_horizontal": {
      "so": "1110",
      "oa_frame": "1100",
      "leaf": ["994 Leaf"]
    },
    "so_vertical": {
      "so": "2105",
      "oa_frame": "2098",
      "leaf": "2037"
    }
  }'
```

**Expected Response:**
```json
{
  "vertical_adjusted": 2068,
  "horizontal_quantities": [
    {
      "leaf_size": 994,
      "leaf_description": "994 Leaf",
      "quantity": 3
    }
  ],
  "total_horizontal_quantity": 48,
  "door_quantity": 16,
  "reinforcement": {
    "reinforcement_length": 2007,
    "reinforcements_per_leaf": 3,
    "total_reinforcements_per_door": 3,
    "total_reinforcements_all_doors": 48
  }
}
```

#### Test with your second sample data:
```bash
curl -X POST "http://localhost:8000/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "general": {
      "Door Type": "Personnel Smartform",
      "Door Infill": "Honeycomb",
      "Fire Rating": "FD120"
    },
    "job": {
      "customer": "SAS International",
      "job_no": "C1475",
      "door_no": "DLG01",
      "qty": "1",
      "revision": "2"
    },
    "so_horizontal": {
      "so": "2050",
      "oa_frame": "2030",
      "leaf": ["960 Leaf", "960 Leaf"]
    },
    "so_vertical": {
      "so": "2180",
      "oa_frame": "2170",
      "leaf": "2112"
    }
  }'
```

**Expected Response:**
```json
{
  "vertical_adjusted": 2140,
  "horizontal_quantities": [
    {
      "leaf_size": 960,
      "leaf_description": "960 Leaf",
      "quantity": 3
    },
    {
      "leaf_size": 960,
      "leaf_description": "960 Leaf",
      "quantity": 3
    }
  ],
  "total_horizontal_quantity": 6,
  "door_quantity": 1,
  "reinforcement": {
    "reinforcement_length": 2082,
    "reinforcements_per_leaf": 6,
    "total_reinforcements_per_door": 6,
    "total_reinforcements_all_doors": 6
  }
}
```

## Calculation Logic

1. **Vertical Adjustment**: Takes the `oa_frame` value from `so_vertical` and subtracts 30mm
2. **Horizontal Quantities**: 
   - Extracts numeric value from each leaf description
   - Divides by 300 and rounds down using `math.floor()`
   - Handles both single and double door configurations
3. **Total Quantity**: Multiplies the sum of horizontal quantities by the door quantity from job data
4. **Reinforcement Calculations**:
   - **Length**: Leaf height minus 30mm (from `so_vertical.leaf`)
   - **Quantity per leaf**: Same as horizontal calculation (leaf width ÷ 300mm)
   - **Total per door**: Sum of all reinforcements needed for one complete door
   - **Total for order**: Total reinforcements × door quantity

## Reinforcement Details

- **Purpose**: Internal horizontal reinforcement bars
- **Length**: Always 30mm shorter than the leaf height
- **Spacing**: Every 300mm across the door width
- **Material**: Typically steel bars that span horizontally across the door

## Interactive Documentation

Once the API is running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test the endpoints directly.

## Stopping the Service

```bash
# If using docker-compose
docker-compose down

# If using docker run
docker stop <container-id>
```