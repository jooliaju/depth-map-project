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
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import ImageIcon from "@mui/icons-material/Image";
import AnnotationCanvas from "./components/AnnotationCanvas";
import {
  uploadImage,
  saveAnnotations,
  processDepth,
  processAnisotropic,
} from "./services/api";

function App() {
  const [brushSize, setBrushSize] = useState(5);
  const [brushColor, setBrushColor] = useState("#000000");
  const [isIgnoreMode, setIsIgnoreMode] = useState(false);
  const [depthValue, setDepthValue] = useState(25);
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const canvasRef = useRef(null);

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
      // Get both canvas data
      const { withScribbles, annotations } = canvasRef.current.saveCanvases();

      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");

      // Send both images to backend
      await saveAnnotations(
        imageName,
        annotations, // White canvas with scribbles (for _annotations.png)
        withScribbles // Image canvas with scribbles (for _with_scribbles.png)
      );
    } catch (error) {
      console.error("Error saving annotations:", error);
    }
  };

  const handleProcessAnisotropic = async () => {
    if (!selectedImage) return;

    try {
      const imageName =
        selectedImage.uploadedName || selectedImage.name.replace(".png", "");

      console.log("Processing anisotropic diffusion...");
      await processAnisotropic(imageName, {
        beta: 0.1,
        iterations: 3000,
      });
      console.log("Anisotropic diffusion completed");
    } catch (error) {
      console.error("Error processing anisotropic:", error);
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
              <Button
                variant="contained"
                onClick={handleProcessAnisotropic}
                disabled={!selectedImage}
                color="secondary"
              >
                Process Anisotropic
              </Button>
            </Stack>
          </Box>
        </Grid2>
      </Grid2>
    </Container>
  );
}

export default App;
