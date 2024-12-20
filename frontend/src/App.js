import React, { useState } from "react";
import {
  Box,
  Slider,
  Button,
  Typography,
  Container,
  Grid2,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import AnnotationCanvas from "./components/AnnotationCanvas";

function App() {
  const [brushSize, setBrushSize] = useState(5);
  const [brushColor, setBrushColor] = useState("#000000");
  const [isIgnoreMode, setIsIgnoreMode] = useState(false);
  const [depthValue, setDepthValue] = useState(25);

  // New state for images
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

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

  const handleSave = () => {
    console.log("Saving annotation...");
  };

  // New function to handle image uploads
  const handleImageUpload = (event) => {
    const files = Array.from(event.target.files);

    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImages((prevImages) => [
          ...prevImages,
          {
            id: Date.now(),
            name: file.name,
            url: e.target.result,
          },
        ]);
      };
      reader.readAsDataURL(file);
    });
  };

  // New function to handle image selection
  const handleImageSelect = (event) => {
    const selectedId = event.target.value;
    const selected = images.find((img) => img.id === selectedId);
    setSelectedImage(selected);
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Depth Annotation Application
      </Typography>

      <Grid2 container spacing={2}>
        <Grid2 item xs={9}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 2,
              mb: 2,
            }}
          >
            {/* Image upload and selection controls */}
            <Box
              sx={{
                display: "flex",
                gap: 2,
                alignItems: "center",
              }}
            >
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
            >
              Save Image
            </Button>
          </Box>
        </Grid2>
      </Grid2>
    </Container>
  );
}

export default App;
