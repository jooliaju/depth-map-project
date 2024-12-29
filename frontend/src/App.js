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
import AnnotationCanvas from "./components/AnnotationCanvas";
import FocusSelector from "./components/FocusSelector";
import {
  saveAnnotations,
  processAnisotropic,
  processFocus,
} from "./services/api";
import OutputViewer from "./components/OutputViewer";

const DEFAULT_IMAGES = [
  {
    id: 1,
    name: "Girl with Pearl Earring",
    url: "/images/girl_with_pearl_earring.png",
  },
  { id: 2, name: "Horse", url: "/images/horse.png" },
  { id: 3, name: "Arizona", url: "/images/arizona.png" },
  { id: 4, name: "Church", url: "/images/church.png" },
];

const loadImageAsBase64 = async (imageUrl) => {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error("Error loading image:", error);
    throw error;
  }
};

const GRADIENT_STOPS = Array.from({ length: 11 }, (_, i) => {
  const value = i * 25.5;
  return `rgb(${value},${value},${value}) ${i * 10}%`;
}).join(", ");

const buttonStyle = {
  textTransform: "none",
};

function App() {
  const [brushSize, setBrushSize] = useState(5);
  const [brushColor, setBrushColor] = useState("#000000");
  const [isIgnoreMode, setIsIgnoreMode] = useState(false);
  const [depthValue, setDepthValue] = useState(25);
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const canvasRef = useRef(null);
  const [showFocusSelector, setShowFocusSelector] = useState(false);
  const outputViewerRef = useRef(null);
  const [anisotropicProgress, setAnisotropicProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  React.useEffect(() => {
    setImages(DEFAULT_IMAGES);
  }, []);

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

  const handleImageSelect = (event) => {
    const selectedId = event.target.value;
    const selected = images.find((img) => img.id === selectedId);
    setSelectedImage(selected);
  };

  const handleSave = async () => {
    if (!selectedImage || !canvasRef.current) return;

    try {
      const { withScribbles, annotations } = canvasRef.current.saveCanvases();

      const imageData = selectedImage.url.startsWith("data:")
        ? selectedImage.url
        : await loadImageAsBase64(selectedImage.url);

      const result = await saveAnnotations(
        imageData,
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
    if (!selectedImage || !outputViewerRef.current) return;

    try {
      setIsProcessing(true);
      setAnisotropicProgress(0);

      // Get the latest annotation images
      const annotationImages = outputViewerRef.current.getImages("annotations");
      if (!annotationImages || annotationImages.length === 0) {
        throw new Error(
          "No annotation images found. Please save annotations first."
        );
      }

      // Find the required images
      const withScribbles = annotationImages.find(
        (img) => img.title === "With Scribbles"
      )?.src;
      const annotations = annotationImages.find(
        (img) => img.title === "Input Annotations"
      )?.src;
      const mask = annotationImages.find((img) => img.title === "Mask")?.src;
      const ignoreMask = annotationImages.find(
        (img) => img.title === "Ignore Mask"
      )?.src;

      if (!withScribbles || !annotations || !mask || !ignoreMask) {
        throw new Error("Missing required annotation images");
      }

      // Make sure we're sending the full image data
      const imageData = selectedImage.url.startsWith("data:")
        ? selectedImage.url
        : await loadImageAsBase64(selectedImage.url);

      const result = await processAnisotropic(
        imageData, // Send the full base64 string
        {
          annotations,
          mask,
          ignoreMask,
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
    if (!selectedImage || !outputViewerRef.current) return;

    try {
      // Get the anisotropic result image
      const anisotropicImages =
        outputViewerRef.current.getImages("anisotropic");
      if (!anisotropicImages || anisotropicImages.length === 0) {
        throw new Error(
          "No anisotropic result found. Please process anisotropic first."
        );
      }

      const anisotropicResult = anisotropicImages.find(
        (img) => img.title === "Anisotropic Diffusion"
      )?.src;

      if (!anisotropicResult) {
        throw new Error("Anisotropic result not found");
      }

      setShowFocusSelector(true);
    } catch (error) {
      console.error("Error starting focus process:", error);
    }
  };

  const handleFocusPointSelect = async (point) => {
    try {
      // Get the anisotropic result image
      const anisotropicImages =
        outputViewerRef.current.getImages("anisotropic");
      const anisotropicResult = anisotropicImages.find(
        (img) => img.title === "Anisotropic Diffusion"
      )?.src;

      if (!anisotropicResult) {
        throw new Error("Anisotropic result not found");
      }

      // Convert the original image to base64 if needed
      const imageData = selectedImage.url.startsWith("data:")
        ? selectedImage.url
        : await loadImageAsBase64(selectedImage.url);

      const result = await processFocus(
        imageData, // Send base64 image data instead of URL
        anisotropicResult,
        point,
        {
          depthRange: 0.1,
          kernelSizeGaus: 5,
          kernelSizeBf: 5,
          sigmaColor: 200,
          sigmaSpace: 200,
          gausSigma: 60,
        }
      );

      if (result.status === "success") {
        outputViewerRef.current?.addImages("focus", result.images);
      }

      setShowFocusSelector(false);
    } catch (error) {
      console.error("Error processing focus:", error);
    }
  };

  return (
    <Container
      maxWidth="lg"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center", // Center horizontally
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: "1400px", // Limit maximum width
          display: "flex",
          flexDirection: "column",
          alignItems: "center", // Center children horizontally
        }}
      >
        <Typography
          variant="h4"
          gutterBottom
          align="center"
          sx={{ mb: 4 }} // Add more margin below title
        >
          Depth Annotation Application
        </Typography>

        <Grid2
          container
          spacing={2}
          sx={{
            justifyContent: "center", // Center the grid content
            width: "100%",
          }}
        >
          <Grid2 item xs={9}>
            <Box
              sx={{ display: "flex", flexDirection: "column", gap: 2, mb: 2 }}
            >
              {/* Image upload and selection controls */}
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
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
                <Button
                  component="label"
                  variant="contained"
                  startIcon={<UploadIcon />}
                  sx={buttonStyle}
                >
                  ADD IMAGES
                  <input
                    type="file"
                    hidden
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                  />
                </Button>
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

            <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={!selectedImage}
                color="secondary"
                sx={buttonStyle}
              >
                (1) Save annotations
              </Button>
              <Box>
                <Button
                  variant="contained"
                  onClick={handleProcessAnisotropic}
                  disabled={!selectedImage || isProcessing}
                  color="secondary"
                  sx={buttonStyle}
                >
                  (2) Process anisotropic
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
                sx={buttonStyle}
              >
                (3) Process focus
              </Button>
            </Stack>
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
              {!isIgnoreMode && (
                <>
                  <Typography>Depth Annotation: {depthValue}</Typography>
                  <Slider
                    orientation="vertical"
                    value={depthValue}
                    onChange={handleDepthChange}
                    min={0}
                    max={255}
                    sx={{
                      height: 200,
                      "& .MuiSlider-track": {
                        background: `linear-gradient(to top, ${GRADIENT_STOPS})`,
                      },
                      "& .MuiSlider-rail": {
                        background: `linear-gradient(to top, ${GRADIENT_STOPS})`,
                      },
                    }}
                  />
                </>
              )}

              <Typography>Brush Size: {brushSize}px</Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Slider
                  orientation="vertical"
                  value={brushSize}
                  onChange={handleBrushSizeChange}
                  min={3}
                  max={20}
                  sx={{
                    height: 200,
                  }}
                />
                <Box
                  sx={{
                    width: `${brushSize}px`,
                    height: `${brushSize}px`,
                    borderRadius: "50%",
                    backgroundColor: "black",
                    transition: "all 0.1s ease",
                  }}
                />
              </Box>

              <Stack spacing={2}>
                <Button
                  variant="contained"
                  onClick={toggleIgnoreMode}
                  color={isIgnoreMode ? "primary" : "success"}
                  sx={buttonStyle}
                >
                  {isIgnoreMode ? "Set Annotation Pen" : "Set Ignore Pen"}
                </Button>
              </Stack>
            </Box>
          </Grid2>
        </Grid2>

        <OutputViewer selectedImage={selectedImage} ref={outputViewerRef} />

        <FocusSelector
          open={showFocusSelector}
          onClose={() => setShowFocusSelector(false)}
          image={selectedImage?.url}
          onSelect={handleFocusPointSelect}
        />
      </Box>
    </Container>
  );
}

export default App;
