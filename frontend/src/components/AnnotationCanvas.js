import React, { useRef, useEffect, useState } from "react";
import { Box } from "@mui/material";

const AnnotationCanvas = ({
  width = 800, // Increased default size
  height = 600,
  brushSize,
  brushColor,
  isIgnoreMode,
  selectedImage,
}) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [lastPoint, setLastPoint] = useState(null);
  const [imageData, setImageData] = useState(null); // Store the image data

  // Effect to handle image changes and initial load
  useEffect(() => {
    if (!selectedImage) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const image = new Image();
    image.src = selectedImage.url;

    image.onload = () => {
      // Clear the canvas
      ctx.clearRect(0, 0, width, height);

      // Calculate aspect ratio to maintain image proportions
      const aspectRatio = image.width / image.height;
      let drawWidth = width;
      let drawHeight = height;

      if (aspectRatio > 1) {
        // Landscape image
        drawHeight = width / aspectRatio;
      } else {
        // Portrait image
        drawWidth = height * aspectRatio;
      }

      // Center the image
      const x = (width - drawWidth) / 2;
      const y = (height - drawHeight) / 2;

      // Draw the image
      ctx.drawImage(image, x, y, drawWidth, drawHeight);

      // Store the current canvas state
      setImageData(ctx.getImageData(0, 0, width, height));
    };
  }, [selectedImage, width, height]);

  // Restore the image state before each draw operation
  const restoreImageState = () => {
    if (imageData) {
      const ctx = canvasRef.current.getContext("2d");
      ctx.putImageData(imageData, 0, 0);
    }
  };

  const startDrawing = (e) => {
    if (!selectedImage) return; // Prevent drawing if no image is selected

    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = width / rect.width; // relationship bitmap vs. element for X
    const scaleY = height / rect.height; // relationship bitmap vs. element for Y

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    setIsDrawing(true);
    setLastPoint({ x, y });
  };

  const draw = (e) => {
    if (!isDrawing || !selectedImage) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const rect = canvas.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    ctx.beginPath();
    ctx.moveTo(lastPoint.x, lastPoint.y);
    ctx.lineTo(x, y);
    ctx.strokeStyle = brushColor;
    ctx.lineWidth = brushSize;
    ctx.lineCap = "round";
    ctx.stroke();

    setLastPoint({ x, y });
  };

  const stopDrawing = () => {
    if (isDrawing) {
      setIsDrawing(false);
      // Store the new canvas state after drawing
      const ctx = canvasRef.current.getContext("2d");
      setImageData(ctx.getImageData(0, 0, width, height));
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        bgcolor: "#f5f5f5",
        border: "1px solid #ddd",
        borderRadius: 1,
        overflow: "hidden",
        width: "100%",
        height: "600px", // Fixed height container
      }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseOut={stopDrawing}
        style={{
          maxWidth: "100%",
          maxHeight: "100%",
          objectFit: "contain",
        }}
      />
    </Box>
  );
};

export default AnnotationCanvas;
