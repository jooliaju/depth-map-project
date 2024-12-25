import React, { useState, useRef } from "react";
import {
  Box,
  Slider,
  Button,
  Typography,
  Container,
  Grid2,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  LinearProgress,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import ImageIcon from "@mui/icons-material/Image";
import AnnotationCanvas from "./components/AnnotationCanvas";
import FocusSelector from "./components/FocusSelector";
import {
  uploadImage,
  saveAnnotations,
  processDepth,
  processAnisotropic,
  processFocus,
} from "./services/api";
import OutputViewer from "./components/OutputViewer";

function App() {
  const [brushSize, setBrushSize] = useState(5);
  const [brushColor, setBrushColor] = useState("#000000");
  const [isIgnoreMode, setIsIgnoreMode] = useState(false);
  const [depthValue, setDepthValue] = useState(25);
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const canvasRef = useRef(null);
  const [showFocusSelector, setShowFocusSelector] = useState(false);
  const [focusPoint, setFocusPoint] = useState(null);
  const [shouldCheckImages, setShouldCheckImages] = useState(false);
  const outputViewerRef = useRef(null);
  const [anisotropicProgress, setAnisotropicProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleBrushSizeChange = (event, newValue) => {
    setBrushSize(newValue);
  };

  const handleDepthChange = (event, newValue) => {
    setDepthValue(newValue);
    const color = `rgb(${newValue},${newValue},${newValue})`;
    setBrushColor(color);
  };

  const toggleIgnoreMode = () => {
    setIsIgnoreMode(!isIgnoreMode);
    setBrushColor(isIgnoreMode ? "#000000" : "#00FF00");
  };

  const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files);

    try {
      for (const file of files) {
        const uploadResponse = await uploadImage(file);

        if (uploadResponse.status === "success") {
          const reader = new FileReader();
          reader.onload = (e) => {
            setImages((prevImages) => [
              ...prevImages,
              {
                id: Date.now(),
                name: file.name,
                url: e.target.result,
                uploadedName: uploadResponse.filename,
              },
            ]);
          };
          reader.readAsDataURL(file);
        } else {
          console.error("Failed to upload image:", uploadResponse.message);
        }
      }
    } catch (error) {
      console.error("Error uploading images:", error);
    }
  };

  const handleImageSelect = (event) => {
    const selectedId = event.target.value;
    const selected = images.find((img) => img.id === selectedId);
    setSelectedImage(selected);
  };

  const handleSave = async () => {
    if (!selectedImage || !canvasRef.current) return;

    try {
      const { withScribbles, annotations } = canvasRef.current.saveCanvases();
      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");

      const result = await saveAnnotations(
        imageName,
        annotations,
        withScribbles
      );
      if (result.status === "success") {
        outputViewerRef.current?.addImages("annotations", result.images);
      }
    } catch (error) {
      console.error("Error saving annotations:", error);
    }
  };

  const handleProcessAnisotropic = async () => {
    if (!selectedImage) return;

    try {
      setIsProcessing(true);
      setAnisotropicProgress(0);
      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");

      const result = await processAnisotropic(
        imageName,
        {
          beta: 0.1,
          iterations: 3000,
        },
        (progress) => {
          setAnisotropicProgress(progress);
        }
      );

      if (result.status === "success") {
        outputViewerRef.current?.addImages("anisotropic", result.images);
      }
    } catch (error) {
      console.error("Error processing anisotropic:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProcessFocus = async () => {
    if (!selectedImage) return;
    try {
      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");
      setShowFocusSelector(true);
    } catch (error) {
      console.error("Error starting focus process:", error);
    }
  };

  const handleFocusPointSelect = async (point) => {
    setFocusPoint(point);
    try {
      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");
      const result = await processFocus(imageName, point, {
        depthRange: 0.1,
        kernelSizeGaus: 5,
        kernelSizeBf: 5,
        sigmaColor: 200,
        sigmaSpace: 200,
        gausSigma: 60,
      });

      if (result.status === "success") {
        outputViewerRef.current?.addImages("focus", result.images);
      }

      setShowFocusSelector(false);
      setFocusPoint(null);
    } catch (error) {
      console.error("Error processing focus:", error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Depth Annotation Application
      </Typography>

      <Grid2 container spacing={2}>
        <Grid2 item xs={9}>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mb: 2 }}>
            {/* Image upload and selection controls */}
            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <Button
                component="label"
                variant="contained"
                startIcon={<UploadIcon />}
              >
                Upload Images
                <input
                  type="file"
                  hidden
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                />
              </Button>

              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Select Image</InputLabel>
                <Select
                  value={selectedImage?.id || ""}
                  onChange={handleImageSelect}
                  label="Select Image"
                >
                  {images.map((image) => (
                    <MenuItem key={image.id} value={image.id}>
                      {image.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* Canvas */}
            <AnnotationCanvas
              ref={canvasRef}
              brushSize={brushSize}
              brushColor={brushColor}
              isIgnoreMode={isIgnoreMode}
              selectedImage={selectedImage}
            />
          </Box>
        </Grid2>

        <Grid2 item xs={3}>
          <Box
            sx={{
              height: "100%",
              display: "flex",
              flexDirection: "column",
              gap: 2,
            }}
          >
            <Typography>Depth Annotation: {depthValue}</Typography>
            <Slider
              orientation="vertical"
              value={depthValue}
              onChange={handleDepthChange}
              min={0}
              max={255}
              sx={{ height: 200 }}
            />

            <Typography>Brush Size: {brushSize}</Typography>
            <Slider
              orientation="vertical"
              value={brushSize}
              onChange={handleBrushSizeChange}
              min={3}
              max={20}
              sx={{ height: 200 }}
            />

            <Stack spacing={2}>
              <Button
                variant="contained"
                onClick={toggleIgnoreMode}
                color={isIgnoreMode ? "success" : "primary"}
              >
                {isIgnoreMode ? "Set Annotation Pen" : "Set Ignore Pen"}
              </Button>

              <Button
                variant="contained"
                onClick={handleSave}
                disabled={!selectedImage}
                color="primary"
              >
                Save Annotations
              </Button>
              <Box>
                <Button
                  variant="contained"
                  onClick={handleProcessAnisotropic}
                  disabled={!selectedImage || isProcessing}
                  color="secondary"
                >
                  Process Anisotropic
                </Button>
                {isProcessing && (
                  <Box sx={{ width: "100%", mt: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={anisotropicProgress}
                    />
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      align="center"
                    >
                      {`${Math.round(anisotropicProgress)}%`}
                    </Typography>
                  </Box>
                )}
              </Box>

              <Button
                variant="contained"
                onClick={handleProcessFocus}
                disabled={!selectedImage}
                color="secondary"
              >
                Process Focus
              </Button>
            </Stack>
          </Box>
        </Grid2>
      </Grid2>

      <OutputViewer
        selectedImage={selectedImage}
        checkTrigger={shouldCheckImages}
        ref={outputViewerRef}
      />

      <FocusSelector
        open={showFocusSelector}
        onClose={() => setShowFocusSelector(false)}
        image={selectedImage?.url}
        onSelect={handleFocusPointSelect}
      />
    </Container>
  );
}

export default App;
