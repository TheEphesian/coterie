"""Import API routes for legacy Grapevine files."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.api.services.import_service import ImportService
from src.api.schemas import ErrorResponse

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post(
    "/legacy",
    summary="Import legacy GV3 file",
    description="Import a legacy Grapevine .gv3 file into the database.",
    responses={
        200: {"description": "Import successful"},
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        500: {"model": ErrorResponse, "description": "Import failed"},
    },
)
async def import_legacy_file(
    file: UploadFile = File(..., description="Legacy GV3 file to import"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import a legacy GV3 file.
    
    This endpoint accepts a .gv3 file (Grapevine 3.x format) and imports all
    data including players, characters, traits, items, locations, actions,
    plots, and rumors into the database.
    """
    # Validate file extension
    if not file.filename or not file.filename.endswith(".gv3"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .gv3 files are supported.",
        )
    
    try:
        # Save uploaded file to temporary location
        with NamedTemporaryFile(delete=False, suffix=".gv3") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        try:
            # Import the file
            service = ImportService(db)
            result = await service.import_gv3(tmp_path)
            
            return {
                "success": True,
                "message": f"Successfully imported {file.filename}",
                "game_name": result["game_name"],
                "stats": result["stats"],
            }
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GV3 file: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}",
        )
