import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
} from "@mui/material";

const FocusSelector = ({ open, onClose, image, onSelect }) => {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseMove = (event) => {
    const rect = event.target.getBoundingClientRect();
    setMousePos({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  const handleMouseEnter = () => {
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
  };

  const handleImageClick = (event) => {
    const rect = event.target.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Calculate relative coordinates (0-1)
    const relativeX = x / rect.width;
    const relativeY = y / rect.height;

    onSelect({ x: relativeX, y: relativeY });
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          maxHeight: "90vh",
          m: 2,
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" component="div" gutterBottom>
          Select Focus Point
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
          Click on the image to select a focus point. The selected area will
          remain sharp while the rest of the image will be blurred based on the
          depth map. You can see the results under the "Focus" tab after
          processing.
        </Typography>
      </Box>
      <DialogContent sx={{ p: 2, overflow: "hidden" }}>
        <Box
          sx={{ position: "relative", width: "fit-content", margin: "0 auto" }}
        >
          <Box
            sx={{
              position: "relative",
              display: "inline-block",
            }}
          >
            {isHovering && (
              <Box
                sx={{
                  position: "absolute",
                  width: "20px",
                  height: "20px",
                  border: "2px solid red",
                  borderRadius: "50%",
                  transform: "translate(-50%, -50%)",
                  pointerEvents: "none",
                  left: mousePos.x,
                  top: mousePos.y,
                  zIndex: 2,
                }}
              />
            )}
            <img
              src={image}
              alt="Select focus point"
              style={{
                maxWidth: "100%",
                height: "auto",
                maxHeight: "60vh",
                objectFit: "contain",
                display: "block",
                cursor: "none",
              }}
              onMouseMove={handleMouseMove}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onClick={handleImageClick}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions sx={{ justifyContent: "center", pb: 2 }}>
        <Button onClick={onClose} variant="contained" color="secondary">
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FocusSelector;
