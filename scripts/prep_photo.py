"""Prep a photo for ASCII conversion: isolate subject, boost contrast, black background.
The source photo already has a plain white background, so a flood fill from the
corners replaces rembg (no model download needed). The output is a grayscale image
where black = background (prints as blank on the dark card) and brightness = ink."""
import sys
import cv2
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
# crop box as fractions: x0 x1 y0 y1 (head, shoulders and tie)
X0, X1, Y0, Y1 = 0.27, 0.77, 0.0, 0.50
# region (fractions of the crop) that is always subject: the white collar touches
# the background beside the neck, so the flood fill would otherwise eat the shirt
KEEP = (0.36, 0.70, 0.635, 1.0)

img = cv2.imread(src)
h, w = img.shape[:2]
img = img[int(h * Y0):int(h * Y1), int(w * X0):int(w * X1)]
h, w = img.shape[:2]

# background mask: near-white pixels connected to the border
near_white = (img.min(axis=2) > 242).astype(np.uint8)
bg = np.zeros((h, w), np.uint8)
for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0)]:
    if near_white[seed[1], seed[0]]:
        tmp = near_white.copy()
        m = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(tmp, m, seed, 2)
        bg |= (tmp == 2).astype(np.uint8)
bg = cv2.morphologyEx(bg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
kx0, kx1, ky0, ky1 = KEEP
bg[int(h * ky0):int(h * ky1), int(w * kx0):int(w * kx1)] = 0
subject = (1 - bg).astype(bool)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# smooth skin noise but keep edges, lift the shadows so the black suit/beard keep
# structure, then local contrast + an unsharp mask for crisp features
gray = cv2.bilateralFilter(gray, 9, 35, 9)
gray = (255 * (gray / 255.0) ** 0.6).astype(np.uint8)
gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
blur = cv2.GaussianBlur(gray, (0, 0), 3)
gray = cv2.addWeighted(gray, 1.6, blur, -0.6, 0)
# keep a faint floor on the subject so its silhouette survives on a dark background
gray = np.where(subject, np.maximum(gray, 28), 0).astype(np.uint8)
cv2.imwrite(out, gray)
print("wrote", out, gray.shape)
