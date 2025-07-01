from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union, Dict, Any
import math

app = FastAPI(
    title="Door Calculator API",
    description="API to process door specifications and calculate dimensions",
    version="1.0.0"
)

class DoorData(BaseModel):
    general: Dict[str, Any] = None
    job: Dict[str, Any] = None
    hardware: Dict[str, Any] = None
    so_horizontal: Dict[str, Union[str, List[str]]]
    so_vertical: Dict[str, str]

class ReinforcementCalculation(BaseModel):
    reinforcement_length: int  # Length of each reinforcement bar (30mm shorter than leaf height)
    reinforcements_per_leaf: int  # Number of reinforcement bars needed per leaf
    total_reinforcements_per_door: int  # Total reinforcements needed per door
    total_reinforcements_all_doors: int  # Total reinforcements for all doors in the order

class CalculationResult(BaseModel):
    vertical_adjusted: int
    horizontal_quantities: List[Dict[str, Union[str, int]]]
    total_horizontal_quantity: int
    door_quantity: int
    reinforcement: ReinforcementCalculation

@app.get("/")
async def root():
    return {"message": "Door Calculator API is running"}

@app.post("/calculate", response_model=CalculationResult)
async def calculate_door_dimensions(data: DoorData):
    """
    Process door JSON data and calculate:
    1. Vertical OA frame minus 30mm
    2. Horizontal leaf quantities (each leaf / 300)
    3. Total horizontal quantity multiplied by door quantity
    4. Internal reinforcement calculations:
       - Reinforcement length (leaf height - 30mm)
       - Reinforcement quantity (leaf width / 300mm intervals)
       - Total reinforcements needed
    """
    try:
        # Extract required data
        so_horizontal = data.so_horizontal
        so_vertical = data.so_vertical
        
        # Get door quantity from job data (default to 1 if not provided)
        door_qty = 1
        if data.job and "qty" in data.job:
            try:
                door_qty = int(data.job["qty"])
            except (ValueError, TypeError):
                door_qty = 1
        
        # 1. Calculate vertical dimension (OA frame - 30mm)
        try:
            vertical_oa_frame = int(so_vertical.get("oa_frame", "0"))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid vertical oa_frame value")
        
        vertical_adjusted = vertical_oa_frame - 30
        
        # 2. Calculate horizontal quantities
        leaf_data = so_horizontal.get("leaf", [])
        
        # Handle both single leaf (string) and multiple leaves (list)
        if isinstance(leaf_data, str):
            leaf_data = [leaf_data]
        elif not isinstance(leaf_data, list):
            raise HTTPException(status_code=400, detail="Invalid leaf data format")
        
        horizontal_quantities = []
        total_leaf_qty = 0
        
        for leaf in leaf_data:
            # Extract numeric value from leaf string (e.g., "994 Leaf" -> 994)
            try:
                leaf_size = int(leaf.split()[0])
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail=f"Invalid leaf format: {leaf}")
            
            # Calculate quantity (leaf size / 300, rounded down)
            leaf_qty = math.floor(leaf_size / 300)
            total_leaf_qty += leaf_qty
            
            horizontal_quantities.append({
                "leaf_size": leaf_size,
                "leaf_description": leaf,
                "quantity": leaf_qty
            })
        
        # 3. Multiply by door quantity
        total_horizontal_quantity = total_leaf_qty * door_qty
        
        # 4. Calculate reinforcement specifications
        # Get leaf height from so_vertical
        try:
            leaf_height = int(so_vertical.get("leaf", "0"))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid leaf height value")
        
        # Reinforcement length = leaf height - 30mm
        reinforcement_length = leaf_height - 30
        
        # Calculate total reinforcements per door
        # Each leaf needs reinforcements every 300mm across its width
        total_reinforcements_per_door = total_leaf_qty
        
        # Total reinforcements for all doors
        total_reinforcements_all_doors = total_reinforcements_per_door * door_qty
        
        # Create reinforcement calculation result
        reinforcement_calc = ReinforcementCalculation(
            reinforcement_length=reinforcement_length,
            reinforcements_per_leaf=total_leaf_qty,
            total_reinforcements_per_door=total_reinforcements_per_door,
            total_reinforcements_all_doors=total_reinforcements_all_doors
        )
        
        return CalculationResult(
            vertical_adjusted=vertical_adjusted,
            horizontal_quantities=horizontal_quantities,
            total_horizontal_quantity=total_horizontal_quantity,
            door_quantity=door_qty,
            reinforcement=reinforcement_calc
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)