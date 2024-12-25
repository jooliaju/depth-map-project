import React, { useState, useEffect } from "react";
import { Box, Tabs, Tab, Typography } from "@mui/material";

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`output-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const OutputViewer = React.forwardRef(({ selectedImage }, ref) => {
  const [tabValue, setTabValue] = React.useState(0);
  const [images, setImages] = useState({
    annotations: [],
    anisotropic: [],
    focus: [],
  });
  const API_BASE_URL = "http://127.0.0.1:5000";

  // Function to add new images to the state
  const addImages = (category, newImages) => {
    if (!newImages) {
      console.warn("No images provided to addImages");
      return;
    }

    setImages((prev) => ({
      ...prev,
      [category]: Object.entries(newImages)
        .map(([key, imageData]) => ({
          src: imageData.src || "",
          title: imageData.title || key,
        }))
        .filter((img) => img.src), // Filter out any entries without src
    }));

    // Switch to the appropriate tab
    switch (category) {
      case "annotations":
        setTabValue(0);
        break;
      case "anisotropic":
        setTabValue(1);
        break;
      case "focus":
        setTabValue(2);
        break;
      default:
        break;
    }
  };

  // Expose addImages method via ref
  React.useImperativeHandle(ref, () => ({
    addImages,
    getImages: (category) => images[category] || [],
  }));

  // Add back the handleTabChange function
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const renderImages = (type) => {
    if (!images[type] || images[type].length === 0) {
      return <Typography>No images to display</Typography>;
    }

    return images[type].map((img, index) => (
      <Box key={index} sx={{ maxWidth: "300px", margin: "10px" }}>
        <Typography variant="subtitle2" gutterBottom>
          {img.title}
        </Typography>
        <img
          src={img.src}
          alt={img.title}
          style={{
            width: "100%",
            height: "auto",
            objectFit: "contain",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
      </Box>
    ));
  };

  return (
    <Box sx={{ width: "100%", mt: 2 }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Annotations" />
          <Tab label="Anisotropic" />
          <Tab label="Focus" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
          {renderImages("annotations")}
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
          {renderImages("anisotropic")}
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
          {renderImages("focus")}
        </Box>
      </TabPanel>
    </Box>
  );
});

export default OutputViewer;
