"""Pure OCR geometry helpers; original utils exports remain available."""
import re
import numpy as np
from task_support import TaskIncomplete
from PIL import Image, ImageFilter


def _dilate(mask: np.ndarray, kh: int, kw: int) -> np.ndarray:
    """形态学膨胀：用 kh×kw 矩形核连接相邻像素"""
    ph, pw = kh // 2, kw // 2
    padded = np.pad(mask, ((ph, ph), (pw, pw)), mode="constant", constant_values=False)
    h, w = mask.shape
    result = np.zeros_like(mask)
    for di in range(kh):
        for dj in range(kw):
            result |= padded[di : di + h, dj : dj + w]
    return result

def strip_punct(s):
    return re.sub(r"\W", "", s)

def detect_click_option_boxes(image: np.ndarray) -> list[list[int]]:
    """Locate separate neutral-grey button borders, independent of text length."""
    if image is None or image.shape[:2] != (1280, 720):
        raise TaskIncomplete("点选填空题截图尺寸不受支持")
    crop = image[270:1100, 40:690, :3].astype(np.int16)
    lo, hi = crop.min(axis=2), crop.max(axis=2)
    mask = (lo >= 165) & (hi <= 238) & (hi-lo <= 35)
    # Join antialiased border gaps; adjacent buttons remain separate.
    mask = np.asarray(Image.fromarray(mask.astype(np.uint8)*255).filter(
        ImageFilter.MaxFilter(3))) > 0
    height, width = mask.shape
    boxes = []
    for sy, sx in zip(*np.nonzero(mask)):
        if not mask[sy, sx]:
            continue
        mask[sy, sx] = False
        stack = [(int(sy), int(sx))]
        xmin = xmax = int(sx)
        ymin = ymax = int(sy)
        while stack:
            y, x = stack.pop()
            xmin, xmax = min(xmin,x), max(xmax,x)
            ymin, ymax = min(ymin,y), max(ymax,y)
            for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                if 0 <= ny < height and 0 <= nx < width and mask[ny,nx]:
                    mask[ny,nx] = False
                    stack.append((ny,nx))
        w,h = xmax-xmin+1,ymax-ymin+1
        if 35 <= w <= 330 and 45 <= h <= 130:
            boxes.append([xmin+40,ymin+270,w,h])
    return sorted(boxes,key=lambda box:(box[1],box[0]))
