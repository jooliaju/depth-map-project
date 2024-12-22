import React, {
  useRef,
  useEffect,
  useState,
  forwardRef,
  useImperativeHandle,
} from "react";
import { Box } from "@mui/material";

const AnnotationCanvas = forwardRef(
  (
    {
      width = 800,
      height = 600,
      brushSize,
      brushColor,
      isIgnoreMode,
      selectedImage,
    },
    ref
  ) => {
    const imageCanvasRef = useRef(null); // For image + scribbles
    const whiteCanvasRef = useRef(null); // For white background + scribbles
    const [isDrawing, setIsDrawing] = useState(false);
    const [lastPoint, setLastPoint] = useState(null);

    // Initialize canvases when image is selected
    useEffect(() => {
      if (!selectedImage || !imageCanvasRef.current || !whiteCanvasRef.current)
        return;

      const imageCanvas = imageCanvasRef.current;
      const whiteCanvas = whiteCanvasRef.current;
      const imageCtx = imageCanvas.getContext("2d");
      const whiteCtx = whiteCanvas.getContext("2d");

      const image = new Image();
      image.src = selectedImage.url;

      image.onload = () => {
        // Set both canvases to image size
        imageCanvas.width = image.width;
        imageCanvas.height = image.height;
        whiteCanvas.width = image.width;
        whiteCanvas.height = image.height;

        // IMPORTANT: Make sure white canvas is completely white first
        whiteCtx.fillStyle = "#FFFFFF";
        whiteCtx.fillRect(0, 0, whiteCanvas.width, whiteCanvas.height);

        // Only draw image on the image canvas
        imageCtx.drawImage(image, 0, 0);

        // Debug - check what's being sent
        console.log("White canvas data:", whiteCanvas.toDataURL());
      };
    }, [selectedImage]);

    // Save canvases for backend processing
    useImperativeHandle(
      ref,
      () => ({
        saveCanvases: () => {
          if (!whiteCanvasRef.current || !imageCanvasRef.current) {
            console.error("Canvas refs are null");
            return null;
          }

          return {
            withScribbles: imageCanvasRef.current.toDataURL("image/png"),
            annotations: whiteCanvasRef.current.toDataURL("image/png"),
          };
        },
      }),
      []
    );

    const draw = (e) => {
      if (!isDrawing) return;

      const imageCanvas = imageCanvasRef.current;
      const whiteCanvas = whiteCanvasRef.current;
      const rect = imageCanvas.getBoundingClientRect();

      const scaleX = imageCanvas.width / rect.width;
      const scaleY = imageCanvas.height / rect.height;
      const x = (e.clientX - rect.left) * scaleX;
      const y = (e.clientY - rect.top) * scaleY;

      // Draw on both canvases simultaneously
      const canvases = [
        { canvas: imageCanvas, ctx: imageCanvas.getContext("2d") },
        { canvas: whiteCanvas, ctx: whiteCanvas.getContext("2d") },
      ];

      canvases.forEach(({ ctx }) => {
        ctx.beginPath();
        ctx.strokeStyle = brushColor;
        ctx.lineWidth = brushSize;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";

        if (lastPoint) {
          ctx.moveTo(lastPoint.x, lastPoint.y);
          ctx.lineTo(x, y);
          ctx.stroke();
        }
      });

      setLastPoint({ x, y });
    };

    const startDrawing = (e) => {
      setIsDrawing(true);
      const rect = imageCanvasRef.current.getBoundingClientRect();
      const scaleX = imageCanvasRef.current.width / rect.width;
      const scaleY = imageCanvasRef.current.height / rect.height;

      setLastPoint({
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY,
      });
    };

    const stopDrawing = () => {
      setIsDrawing(false);
      setLastPoint(null);
    };

    return (
      <Box
        sx={{
          position: "relative",
          width: "100%",
          height: "600px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#f0f0f0",
          border: "2px dashed #ccc",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      >
        {!selectedImage ? (
          <Box
            sx={{
              color: "#666",
              fontSize: "1.2rem",
              textAlign: "center",
              padding: "20px",
            }}
          >
            Select an image to begin annotation
          </Box>
        ) : (
          <Box sx={{ position: "relative" }}>
            {/* White canvas - hidden but active */}
            <canvas
              ref={whiteCanvasRef}
              width={selectedImage ? selectedImage.width : width}
              height={selectedImage ? selectedImage.height : height}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                visibility: "hidden", // Hide but keep active
              }}
            />

            {/* Image canvas - visible */}
            <canvas
              ref={imageCanvasRef}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseOut={stopDrawing}
              width={selectedImage ? selectedImage.width : width}
              height={selectedImage ? selectedImage.height : height}
              style={{
                maxWidth: "100%",
                maxHeight: "100%",
                objectFit: "contain",
              }}
            />
          </Box>
        )}
      </Box>
    );
  }
);

export default AnnotationCanvas;
