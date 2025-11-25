import base64
import io
import uvicorn
from typing import List, Union, Optional, Set, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
from ultralytics import YOLO
from PIL import Image
from utils.translations import CLASS_NAMES
MODEL_PATH = r"models\best 9.20.pt"
OCCUPATION_THRESHOLD = 0.03
HOST = "127.0.0.1"
PORT = 8000
app = FastAPI()
try:
    model = YOLO(MODEL_PATH)
    print(f"Model loaded successfully: {MODEL_PATH}")
except Exception as e:
    print(f"error：Model loading failed. {e}")
    quit()
class ImageRequest(BaseModel):
    image_id: str
    image_base64: str
    target_class: Optional[str] = None

class BatchRequest(BaseModel):
    images: List[ImageRequest]

class Result100x100(BaseModel):
    target_found: bool
    other_classes_found: List[str]

class ResultResponse(BaseModel):
    image_id: str
    status: str
    image_size: Optional[str] = None
    result: Optional[Union[Result100x100, List[int]]] = None
    message: Optional[str] = None

class BatchResponse(BaseModel):
    results: List[ResultResponse]

def calculate_intersection_area(box1: Tuple, box2: Tuple) -> float:
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])
    inter_width = max(0, x2_inter - x1_inter)
    inter_height = max(0, y2_inter - y1_inter)
    return inter_width * inter_height

def get_index(target_class:str):
    for index, item, in enumerate(CLASS_NAMES, start=0):
        for values in item.values():
            if target_class.lower() in values:
                return index
    raise ValueError
@app.post("/analyze_batch/", response_model=BatchResponse)
async def analyze_batch_images(request: BatchRequest):
    response_items = []
    for image_req in request.images:
        try:
            base64_string = image_req.image_base64
            img_bytes = base64.b64decode(base64_string)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            width, height = img.size
            if (width, height) == (100, 100):
                if not image_req.target_class:
                    response_items.append(ResultResponse(image_id=image_req.image_id, status="error",message="For 100x100 images, a category must be provided."))
                    continue
                try:
                    target_class_id=get_index(image_req.target_class.lower())
                except ValueError:
                    response_items.append(ResultResponse(image_id=image_req.image_id, status="error",message=f"The target {image_req.target_class} is not in the category list."))
                    continue
                results = model.predict(img, verbose=False, conf=0.2,iou=0.2)
                target_found = False
                other_classes_found: Set[str] = set()  # 使用集合来自动去重
                for box in results[0].boxes:
                    class_id = int(box.cls)
                    if class_id == target_class_id:
                        target_found = True
                    else:
                        if class_id < len(CLASS_NAMES):
                            other_classes_found.add(list(CLASS_NAMES[class_id].keys())[0])

                response_items.append(ResultResponse(
                    image_id=image_req.image_id,
                    status="success",
                    image_size=f"{width}x{height}",
                    result=Result100x100(
                        target_found=target_found,
                        other_classes_found=sorted(list(other_classes_found))
                    )
                ))

            elif (width, height) == (450, 450):
                if not image_req.target_class:
                    response_items.append(ResultResponse(image_id=image_req.image_id, status="error",message="for images of 450x450 resolution, a category must be provided."))
                    continue
                try:
                    target_class_id = get_index(image_req.target_class.lower())
                except ValueError:
                    response_items.append(ResultResponse(image_id=image_req.image_id, status="error",message=f"The target {image_req.target_class} is not in the category list."))
                    continue

                results = model.predict(img, verbose=False, conf=0.35,iou=0.18)
                grid_dim = 4
                cell_width = width / grid_dim
                cell_height = height / grid_dim

                grid_cells = [
                    (c * cell_width, r * cell_height, (c + 1) * cell_width, (r + 1) * cell_height)
                    for r in range(grid_dim) for c in range(grid_dim)
                ]

                locations = set()
                for box in results[0].boxes:
                    if int(box.cls) == target_class_id:
                        bbox_coords = box.xyxy[0].tolist()
                        bbox_area = (bbox_coords[2] - bbox_coords[0]) * (bbox_coords[3] - bbox_coords[1])

                        if bbox_area == 0:
                            continue

                        for i, cell_coords in enumerate(grid_cells):
                            intersection_area = calculate_intersection_area(bbox_coords, cell_coords)

                            occupation_ratio = intersection_area / bbox_area

                            if occupation_ratio >= OCCUPATION_THRESHOLD:
                                locations.add(i)

                response_items.append(ResultResponse(
                    image_id=image_req.image_id,
                    status="success",
                    image_size=f"{width}x{height}",
                    result=sorted(list(locations))
                ))

            else:
                response_items.append(
                    ResultResponse(image_id=image_req.image_id, status="error", image_size=f"{width}x{height}",message="unsupported image sizes"))
        except Exception as e:
            response_items.append(
                ResultResponse(image_id=image_req.image_id, status="error", message=f"server error: {str(e)}"))

    return BatchResponse(results=response_items)

if __name__ == '__main__':
    uvicorn.run(
        "api_server:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_dirs=['.']
    )
